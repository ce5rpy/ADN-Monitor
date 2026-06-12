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

"""WebSocket dashboard server (Autobahn/Twisted)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

from ...application import ws_ctable_views
from ...application.monitor_controller import MonitorState, ctable_is_empty, sync_ctable_from_config
from ...domain.value_objects import ServerMode
from ...application.ports import BroadcastPort

logger = logging.getLogger("adn-monitor")

# Group names matching original GROUPS
GROUP_NAMES = (
    "all_clients",
    "main",
    "bridge",
    "lnksys",
    "opb",
    "statictg",
    "log",
    "lsthrd_log",
    "tgcount",
    "server_info",
)
# When client sends "conf,all", send current data for these groups immediately (no wait for safety_sync)
SEND_ALL_GROUPS = ("main", "lnksys", "opb", "statictg", "lsthrd_log", "tgcount", "bridge", "log", "server_info")


class DashboardBroadcast(BroadcastPort):
    """Broadcast port implementation that sends to WebSocket clients by group."""

    def __init__(self, clients: dict[str, dict]) -> None:
        self._clients = clients

    def broadcast(self, message: str, group: str) -> None:
        payload = message.encode("utf-8")
        for client in self._clients.get(group, {}):
            try:
                client.sendMessage(payload)
            except Exception as e:
                logger.debug("broadcast to %s failed: %s", group, e)

    def send_to_client(self, client: Any, message: str) -> None:
        try:
            client.sendMessage(message.encode("utf-8"))
        except Exception as e:
            logger.debug("send_to_client failed: %s", e)


def _send_json(protocol: Any, opcode: str, payload: dict) -> None:
    protocol.sendMessage((opcode + json.dumps(payload, default=str)).encode("utf-8"))


def _log_ctable_sent(
    peer: str,
    ctable: dict,
    full_ctable: dict | None = None,
    *,
    config_keys: int = 0,
) -> None:
    """Log ctable stats when sending to a client (single responsibility, DRY)."""
    n_m = len(ctable.get("MASTERS", {}))
    n_p = len(ctable.get("PEERS", {}))
    n_o = len(ctable.get("OPENBRIDGES", {}))
    logger.info(
        "(WS) client %s registered lnksys: sending ctable MASTERS=%d PEERS=%d OPENBRIDGES=%d",
        peer, n_m, n_p, n_o,
    )
    if full_ctable is not None and n_m == 0 and n_p == 0:
        fm = len(full_ctable.get("MASTERS", {}))
        fp = len(full_ctable.get("PEERS", {}))
        fo = len(full_ctable.get("OPENBRIDGES", {}))
        logger.info(
            "(WS) client %s lnksys slice empty; full CTABLE MASTERS=%d PEERS=%d OPENBRIDGES=%d",
            peer, fm, fp, fo,
        )
        if fm == 0 and fp == 0 and fo == 0:
            logger.warning(
                "(WS) client %s CTABLE empty in memory (cached CONFIG keys=%d); "
                "on legacy servers wait for periodic CONFIG_SND (~60s) after report reconnect",
                peer,
                config_keys,
            )


def make_dashboard_factory(
    state: MonitorState,
    conf_global: dict,
    conf_ws: dict,
    groups: dict[str, dict],
    render_last_heard: Callable[[str, int, Any], Any],
    render_lstheard_log: Callable[[int], Any],
    render_tgcount: Callable[[int], Any],
    refresh_from_server: Callable[[], bool] | None = None,
) -> tuple[WebSocketServerFactory, type]:
    """Build WebSocket server factory and protocol class. Sends JSON payloads, no HTML."""

    class DashboardProtocol(WebSocketServerProtocol):
        def onConnect(self, request: Any) -> None:
            logger.info("Client connecting: %s", request.peer)

        def onOpen(self) -> None:
            logger.info("WebSocket connection open.")

        def onMessage(self, payload: bytes, isBinary: bool) -> None:
            if isBinary:
                logger.info("Binary message received: %d bytes", len(payload))
                return
            msg = payload.decode("utf-8").split(",")
            logger.info("Text message received: %s", payload)
            if msg[0] != "conf":
                return
            # "conf,all" => send full config for all groups so client doesn't wait for safety_sync
            requested = list(SEND_ALL_GROUPS) if "all" in msg[1:] else msg[1:]
            for group in requested:
                if group not in groups:
                    continue
                self.factory.register(self, group)
                if group == "bridge":
                    if state.BRIDGES and conf_global.get("BRDG_INC"):
                        _send_json(self, "b", {"btable": state.BTABLE, "dbridges": True})
                elif group == "lnksys":
                    if ctable_is_empty(state.CTABLE) and state.CONFIG:
                        sync_ctable_from_config(state, conf_global)
                    emaster = conf_global.get("EMPTY_MASTERS", False)
                    ctable = ws_ctable_views.ctable_for_lnksys(state.CTABLE, empty_masters=emaster)
                    _log_ctable_sent(
                        self.peer,
                        ctable,
                        state.CTABLE,
                        config_keys=len(state.CONFIG or {}),
                    )
                    _send_json(self, "c", {
                        "ctable": ctable,
                        "emaster": emaster,
                    })
                elif group == "opb":
                    _send_json(self, "o", {
                        "ctable": ws_ctable_views.ctable_for_opb(state.CTABLE),
                        "dbridges": conf_global.get("BRDG_INC", False),
                    })
                elif group == "main":
                    render_last_heard("last_heard", conf_global.get("LH_ROWS", 20), self)
                elif group == "statictg":
                    if ctable_is_empty(state.CTABLE) and state.CONFIG:
                        sync_ctable_from_config(state, conf_global)
                    emaster = conf_global.get("EMPTY_MASTERS", False)
                    _send_json(self, "s", {
                        "ctable": ws_ctable_views.ctable_for_lnksys(state.CTABLE, empty_masters=emaster),
                        "emaster": emaster,
                    })
                elif group == "lsthrd_log":
                    render_lstheard_log(state.lastheard_log_rows, self)
                elif group == "tgcount" and conf_global.get("TGC_INC"):
                    render_tgcount(conf_global.get("TGC_ROWS", 20), self)
                elif group == "log":
                    for log_message in state.LOGBUF:
                        if log_message:
                            self.sendMessage(("l" + log_message).encode("utf-8"))
                elif group == "server_info":
                    mode = getattr(state, "server_mode", None)
                    info = getattr(state, "server_info", {}) or {}
                    _send_json(self, "v", {
                        "mode": getattr(mode, "value", str(mode) if mode is not None else "legacy"),
                        "info": info,
                    })
            if (
                refresh_from_server is not None
                and any(g in ("lnksys", "statictg") for g in requested)
                and getattr(state, "server_mode_confirmed", False)
                and getattr(state, "server_mode", ServerMode.LEGACY) == ServerMode.V2
            ):
                refresh_from_server()

        def onClose(self, wasClean: bool, code: int | None, reason: str | None) -> None:
            self.factory.unregister(self)
            logger.info("WebSocket connection closed: %s", reason)

    class DashboardFactory(WebSocketServerFactory):
        protocol = DashboardProtocol

        def __init__(self, url: str) -> None:
            WebSocketServerFactory.__init__(self, url)
            self.clients = groups

        def register(self, client: Any, group: str) -> None:
            if client not in self.clients[group]:
                self.clients[group][client] = time.time()
                logger.info("registered client %s to group %s", client.peer, group)
            if client not in self.clients["all_clients"]:
                self.clients["all_clients"][client] = time.time()

        def unregister(self, client: Any) -> None:
            logger.info("unregistered client %s", client.peer)
            for group in self.clients:
                if client in self.clients[group]:
                    del self.clients[group][client]

        def broadcast(self, msg: str, group: str) -> None:
            logger.debug("broadcasting message to: %s", list(self.clients.get(group, {})))
            for client in self.clients.get(group, {}):
                try:
                    client.sendMessage(msg.encode("utf-8"))
                except Exception as e:
                    logger.debug("message sent failed: %s", e)

    return DashboardFactory, DashboardProtocol
