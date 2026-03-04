# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) Rodrigo Pérez <ce5rpy@qmd.cl>
# License: GPLv3
"""HBlink report client (Twisted NetstringReceiver)."""

from __future__ import annotations

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

logger = logging.getLogger("adn-mon")

# Increase if HBlink link break occurs
NetstringReceiver.MAX_LENGTH = 5000000


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
        on_ctable_updated: Callable[[], None] | None = None,
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

    def connectionMade(self) -> None:
        logger.info("(REPORT) Connection to report server established")
        if self._on_connection_established:
            self._on_connection_established()

    def connectionLost(self, reason: Any) -> None:
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
        if opcode in (b"\x01", b"\x03"):
            logger.info("(REPORT) stringReceived: opcode=%s len=%d", opcode.hex(), len(data))
        elif opcode == b"\x07":
            logger.debug("(REPORT) stringReceived: BRDG_EVENT opcode=07 len=%d", len(data))
        else:
            logger.debug("(REPORT) stringReceived: len=%d opcode=%r", len(data), opcode)
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
        elif opcode == b"\x07" and self._on_ctable_updated:
            self._on_ctable_updated()
        logger.debug("(REPORT) process_message done for opcode=%r", opcode)


class ReportClientFactory(ReconnectingClientFactory):
    """ReconnectingClientFactory that uses ReportProtocol with injected deps."""

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
        on_ctable_updated: Callable[[], None] | None = None,
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

    def buildProtocol(self, addr: Any) -> ReportProtocol:
        self.resetDelay()
        return ReportProtocol(
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
        )

    def clientConnectionLost(self, connector: Any, reason: Any) -> None:
        self._state.CTABLE["MASTERS"].clear()
        self._state.CTABLE["PEERS"].clear()
        self._state.CTABLE["OPENBRIDGES"].clear()
        self._state.BTABLE["BRIDGES"].clear()
        err_msg = getattr(reason, "getErrorMessage", lambda: str(reason))()
        err_type = getattr(getattr(reason, "type", None), "__name__", type(reason).__name__)
        logger.info("Lost connection. type=%s message=%s (full: %s)", err_type, err_msg, reason)
        if self._on_connection_lost:
            self._on_connection_lost()
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def startedConnecting(self, connector: Any) -> None:
        logger.info("Initiating connection to report server.")
