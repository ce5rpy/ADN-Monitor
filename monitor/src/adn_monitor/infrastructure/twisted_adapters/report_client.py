# ADN Monitor - Dashboard and backend for ADN Systems.
#
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
###############################################################################
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################
#
# Derived from FDMR Monitor (OA4DOA), HBMonv2 (SP2ONG), hbmonitor3 (KC1AWV),
# and HBmonitor (Cortney T. Buffington, N0MJS). Original works under GPLv3.

"""HBlink report client (Twisted NetstringReceiver)."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import NetstringReceiver

from ...application.alias_service import AliasService
from ...application.monitor_controller import MonitorState, process_message
from ...application.ports import (
    AliasRepository,
    BroadcastPort,
    LastHeardRepository,
    ReportPayloadDecoder,
    TgCountRepository,
)
from ...domain import is_fail
from ...domain.value_objects import Opcode, ServerMode

_CALL_FAMILY_TO_CSV = {
    "GROUP": "GROUP VOICE",
    "PRIVATE": "PRIVATE VOICE",
    "UNIT": "UNIT DATA",
}


def _voice_event_brdg_meta(data: bytes) -> dict[str, str] | None:
    """Build bridge-event metadata from v2 JSON or legacy CSV voice payloads."""
    body = data[1:]
    if not body:
        return None
    try:
        payload = json.loads(body.decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        payload = None
    if isinstance(payload, dict) and payload.get("type") == "voice_event":
        family = payload.get("call_family")
        csv_family = _CALL_FAMILY_TO_CSV.get(family)
        if csv_family is None:
            return None
        return {
            "call_type": csv_family,
            "action": str(payload.get("phase", "")),
            "system": str(payload.get("system", "")),
            "direction": str(payload.get("direction", "")),
        }
    parts = body.decode("utf-8", errors="replace").split(",")
    if len(parts) < 4:
        return None
    return {
        "call_type": parts[0],
        "action": parts[1],
        "system": parts[3],
        "direction": parts[2] if len(parts) > 2 else "",
    }

logger = logging.getLogger("adn-monitor")

# Increase if HBlink link break occurs
NetstringReceiver.MAX_LENGTH = 5000000

DEFAULT_HELLO_TIMEOUT_SEC = 1.5


class ReportProtocol(NetstringReceiver):
    """Receives report messages from HBlink and delegates to process_message."""

    def __init__(
        self,
        state: MonitorState,
        alias_svc: AliasService,
        alias_repo: AliasRepository,
        lastheard_repo: LastHeardRepository,
        tgcount_repo: TgCountRepository,
        broadcast: BroadcastPort | None,
        config_global: dict,
        report_decoder: ReportPayloadDecoder,
        on_connection_established: Callable[[], None] | None = None,
        on_ctable_updated: Callable[..., None] | None = None,
        on_config_applied: Callable[[], None] | None = None,
        on_bridges_applied: Callable[[], None] | None = None,
        on_server_mode_detected: Callable[[ServerMode, dict], None] | None = None,
        hello_timeout_sec: float = DEFAULT_HELLO_TIMEOUT_SEC,
    ) -> None:
        # Use _monitor_state to avoid NetstringReceiver overwriting self._state (its FSM uses _state)
        self._monitor_state = state
        self._alias_svc = alias_svc
        self._alias_repo = alias_repo
        self._lastheard_repo = lastheard_repo
        self._tgcount_repo = tgcount_repo
        self._broadcast = broadcast
        self._config_global = config_global
        self._report_decoder = report_decoder
        self._on_connection_established = on_connection_established
        self._on_ctable_updated = on_ctable_updated
        self._on_config_applied = on_config_applied
        self._on_bridges_applied = on_bridges_applied
        self._on_server_mode_detected = on_server_mode_detected
        self._hello_timeout_sec = hello_timeout_sec
        self._hello_timer: Any = None  # IDelayedCall or None
        self._mode_signalled = False  # avoid double-firing on_server_mode_detected

    def set_repositories(
        self,
        alias_svc: AliasService,
        alias_repo: AliasRepository,
        lastheard_repo: LastHeardRepository,
        tgcount_repo: TgCountRepository,
    ) -> None:
        self._alias_svc = alias_svc
        self._alias_repo = alias_repo
        self._lastheard_repo = lastheard_repo
        self._tgcount_repo = tgcount_repo

    def connectionMade(self) -> None:
        logger.info("(REPORT) Connection to report server established")
        self._monitor_state.server_mode = ServerMode.LEGACY
        self._monitor_state.server_info = {}
        self._monitor_state.server_mode_confirmed = False
        self._monitor_state.report_protocol = None
        self._monitor_state.topology_snapshot = None
        self._monitor_state.routing_snapshot = None
        self._monitor_state.topology_seq = 0
        self._monitor_state.routing_seq = 0
        self._monitor_state.slim_wire = False
        self._monitor_state.dashboard_state_ts = 0.0
        self._mode_signalled = False
        from twisted.internet import reactor

        try:
            self._hello_timer = reactor.callLater(self._hello_timeout_sec, self._assume_legacy)
        except Exception as e:
            logger.warning("(REPORT) Could not schedule HELLO timeout: %s", e)
            self._hello_timer = None
        if self._on_connection_established:
            self._on_connection_established()

    def _cancel_hello_timer(self) -> None:
        if self._hello_timer is not None:
            try:
                if self._hello_timer.active():
                    self._hello_timer.cancel()
            except Exception:
                pass
            self._hello_timer = None

    def _assume_legacy(self) -> None:
        self._hello_timer = None
        if self._monitor_state.server_mode == ServerMode.V2:
            return
        logger.info(
            "(REPORT) No HELLO in %.2fs; assuming legacy adn-dmr-server (periodic CONFIG/BRIDGE only).",
            self._hello_timeout_sec,
        )
        self._signal_mode_detected()

    def _signal_mode_detected(self) -> None:
        if self._mode_signalled:
            return
        self._mode_signalled = True
        self._monitor_state.server_mode_confirmed = True
        if self._on_server_mode_detected:
            try:
                self._on_server_mode_detected(self._monitor_state.server_mode, dict(self._monitor_state.server_info))
            except Exception as e:
                logger.warning("(REPORT) on_server_mode_detected raised: %s", e)

    def connectionLost(self, reason: Any) -> None:
        self._cancel_hello_timer()
        err_msg = getattr(reason, "getErrorMessage", lambda: str(reason))()
        err_type = getattr(getattr(reason, "type", None), "__name__", type(reason).__name__)
        logger.info("(REPORT) Connection lost: type=%s message=%s", err_type, err_msg)
        if err_type == "ConnectionDone":
            logger.info(
                "(REPORT) Report server closed the connection; check server if this repeats"
            )

    def stringReceived(self, data: bytes) -> None:
        opcode = data[:1] if data else b""
        # Log report messages: CONFIG_SND=0x01, BRIDGE_SND=0x03; BRDG_EVENT=0x07 only at DEBUG (formatted line goes to INFO in controller)
        if opcode in (b"\x01", b"\x03", Opcode.STATE_SND, Opcode.TOPOLOGY_SND, Opcode.ROUTING_TABLE_SND):
            logger.info("(REPORT) stringReceived: opcode=%s len=%d", opcode.hex(), len(data))
        elif opcode in (b"\x07", Opcode.VOICE_EVENT_SND):
            logger.debug("(REPORT) stringReceived: voice opcode=%s len=%d", opcode.hex(), len(data))
        elif opcode == Opcode.DELTA_SND:
            logger.info("(REPORT) stringReceived: DELTA_SND len=%d", len(data))
        elif opcode == Opcode.HELLO:
            logger.info("(REPORT) stringReceived: HELLO opcode=%s len=%d", opcode.hex(), len(data))
        else:
            logger.debug("(REPORT) stringReceived: len=%d opcode=%r", len(data), opcode)
        if opcode == Opcode.HELLO:
            self._cancel_hello_timer()
        result = process_message(
            raw_message=data,
            state=self._monitor_state,
            alias_svc=self._alias_svc,
            alias_repo=self._alias_repo,
            lastheard_repo=self._lastheard_repo,
            tgcount_repo=self._tgcount_repo,
            broadcast=self._broadcast,
            config_global=self._config_global,
            report_decoder=self._report_decoder,
        )
        if is_fail(result):
            logger.warning("process_message error: %s", result.error)
        elif opcode == Opcode.HELLO:
            self._signal_mode_detected()
        elif opcode in (b"\x01", Opcode.STATE_SND, Opcode.TOPOLOGY_SND) and self._on_config_applied:
            self._on_config_applied()
        elif opcode in (Opcode.BRIDGE_SND, Opcode.ROUTING_TABLE_SND) and self._on_bridges_applied:
            self._on_bridges_applied()
        elif opcode == Opcode.DELTA_SND and not is_fail(result):
            patch_type = None
            try:
                payload = json.loads(data[1:].decode("utf-8", errors="replace") or "{}")
                patch = payload.get("patch") if isinstance(payload, dict) else None
                patch_type = patch.get("type") if isinstance(patch, dict) else None
            except Exception:
                pass
            if patch_type == "topology" and self._on_config_applied:
                self._on_config_applied()
            elif patch_type == "routing_table" and self._on_bridges_applied:
                self._on_bridges_applied()
        elif opcode in (b"\x07", Opcode.VOICE_EVENT_SND) and self._on_ctable_updated:
            self._on_ctable_updated(_voice_event_brdg_meta(data))
        logger.debug("(REPORT) process_message done for opcode=%r", opcode)


# Max delay between reconnection attempts (seconds). Twisted default is 3600 (1h).
# Cap at 30s so we never wait longer than that before trying again.
REPORT_RECONNECT_MAX_DELAY = 30


class ReportClientFactory(ReconnectingClientFactory):
    """ReconnectingClientFactory that uses ReportProtocol with injected deps."""

    maxDelay = REPORT_RECONNECT_MAX_DELAY

    def __init__(
        self,
        state: MonitorState,
        alias_svc: AliasService,
        alias_repo: AliasRepository,
        lastheard_repo: LastHeardRepository,
        tgcount_repo: TgCountRepository,
        broadcast: BroadcastPort | None,
        config_global: dict,
        report_decoder: ReportPayloadDecoder,
        on_connection_lost: Callable[[], None] | None = None,
        on_connection_established: Callable[[], None] | None = None,
        on_ctable_updated: Callable[..., None] | None = None,
        on_config_applied: Callable[[], None] | None = None,
        on_bridges_applied: Callable[[], None] | None = None,
        on_server_mode_detected: Callable[[ServerMode, dict], None] | None = None,
        hello_timeout_sec: float = DEFAULT_HELLO_TIMEOUT_SEC,
    ) -> None:
        self._state = state
        self._alias_svc = alias_svc
        self._alias_repo = alias_repo
        self._lastheard_repo = lastheard_repo
        self._tgcount_repo = tgcount_repo
        self._broadcast = broadcast
        self._config_global = config_global
        self._report_decoder = report_decoder
        self._on_connection_lost = on_connection_lost
        self._on_connection_established = on_connection_established
        self._on_ctable_updated = on_ctable_updated
        self._on_config_applied = on_config_applied
        self._on_bridges_applied = on_bridges_applied
        self._on_server_mode_detected = on_server_mode_detected
        self._hello_timeout_sec = hello_timeout_sec

    def set_repositories(
        self,
        alias_svc: AliasService,
        alias_repo: AliasRepository,
        lastheard_repo: LastHeardRepository,
        tgcount_repo: TgCountRepository,
    ) -> None:
        self._alias_svc = alias_svc
        self._alias_repo = alias_repo
        self._lastheard_repo = lastheard_repo
        self._tgcount_repo = tgcount_repo
        proto = getattr(self, "_report_protocol", None)
        if proto is not None:
            proto.set_repositories(alias_svc, alias_repo, lastheard_repo, tgcount_repo)

    def buildProtocol(self, addr: Any) -> ReportProtocol:
        self.resetDelay()
        proto = ReportProtocol(
            state=self._state,
            alias_svc=self._alias_svc,
            alias_repo=self._alias_repo,
            lastheard_repo=self._lastheard_repo,
            tgcount_repo=self._tgcount_repo,
            broadcast=self._broadcast,
            config_global=self._config_global,
            report_decoder=self._report_decoder,
            on_connection_established=self._on_connection_established,
            on_ctable_updated=self._on_ctable_updated,
            on_config_applied=self._on_config_applied,
            on_bridges_applied=self._on_bridges_applied,
            on_server_mode_detected=self._on_server_mode_detected,
            hello_timeout_sec=self._hello_timeout_sec,
        )
        self._report_protocol = proto
        return proto

    def request_refresh(self) -> bool:
        """Request fresh CONFIG + BRIDGE from adn-server only.

        Do not send CONFIG_REQ / BRIDGE_REQ to legacy adn-dmr-server: hblink report
        handles CONFIG_REQ with self.send_config() (missing on the protocol instance;
        only reportFactory.send_config exists), which drops the TCP session. Legacy
        clients rely on periodic CONFIG_SND from REPORT_INTERVAL.
        """
        if not getattr(self._state, "server_mode_confirmed", False):
            logger.debug("(REPORT) skip refresh: server mode not confirmed yet (HELLO wait)")
            return False
        if getattr(self._state, "server_mode", ServerMode.LEGACY) != ServerMode.V2:
            logger.debug("(REPORT) skip refresh opcodes (legacy server; periodic CONFIG only)")
            return False
        proto = getattr(self, "_report_protocol", None)
        if proto is None or proto.transport is None:
            return False
        if getattr(self._state, "slim_wire", False):
            proto.sendString(Opcode.STATE_REQ)
            logger.debug("(REPORT) STATE_REQ sent (slim v2 wire)")
        else:
            proto.sendString(Opcode.CONFIG_REQ)
            proto.sendString(Opcode.BRIDGE_REQ)
            logger.debug("(REPORT) CONFIG_REQ + BRIDGE_REQ sent (v2 interim wire)")
        return True

    def clientConnectionFailed(self, connector: Any, reason: Any) -> None:
        err_msg = getattr(reason, "getErrorMessage", lambda: str(reason))()
        err_type = getattr(getattr(reason, "type", None), "__name__", type(reason).__name__)
        logger.warning(
            "Report server connection failed (server down?). type=%s message=%s. Will retry.",
            err_type,
            err_msg,
        )
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        # Log next retry delay so operators see we keep trying
        if self.continueTrying and getattr(self, "delay", None) is not None:
            logger.info("Next connection attempt in %.0f seconds.", self.delay)

    def clientConnectionLost(self, connector: Any, reason: Any) -> None:
        self._report_protocol = None
        # Keep CTABLE/BTABLE until CONFIG/BRIDGE on reconnect (avoid blank lnksys on brief blip).
        err_msg = getattr(reason, "getErrorMessage", lambda: str(reason))()
        err_type = getattr(getattr(reason, "type", None), "__name__", type(reason).__name__)
        logger.info("Lost connection. type=%s message=%s (full: %s)", err_type, err_msg, reason)
        if self._on_connection_lost:
            self._on_connection_lost()
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        if self.continueTrying and getattr(self, "delay", None) is not None:
            logger.info("Next connection attempt in %.0f seconds.", self.delay)

    def startedConnecting(self, connector: Any) -> None:
        logger.info("Initiating connection to report server.")
