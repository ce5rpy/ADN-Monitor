# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2025  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
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
"""WebSocket dashboard server (Autobahn/Twisted)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

from ...application.monitor_controller import MonitorState
from ...application.ports import BroadcastPort

logger = logging.getLogger("adn-mon")

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
)
# When client sends "conf,all", send current data for these groups immediately (no wait for build_stats)
SEND_ALL_GROUPS = ("main", "lnksys", "opb", "statictg", "lsthrd_log", "tgcount", "bridge", "log")


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


def _log_ctable_sent(peer: str, ctable: dict) -> None:
    """Log ctable stats when sending to a client (single responsibility, DRY)."""
    n_m = len(ctable.get("MASTERS", {}))
    n_p = len(ctable.get("PEERS", {}))
    n_o = len(ctable.get("OPENBRIDGES", {}))
    logger.info("(WS) client %s registered lnksys: sending ctable MASTERS=%d PEERS=%d OPENBRIDGES=%d", peer, n_m, n_p, n_o)


def make_dashboard_factory(
    state: MonitorState,
    conf_global: dict,
    conf_ws: dict,
    groups: dict[str, dict],
    render_last_heard: Callable[[str, int, Any], Any],
    render_lstheard_log: Callable[[int], Any],
    render_tgcount: Callable[[int], Any],
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
            # "conf,all" => send full config for all groups so client doesn't wait for next build_stats tick
            requested = list(SEND_ALL_GROUPS) if "all" in msg[1:] else msg[1:]
            for group in requested:
                if group not in groups:
                    continue
                self.factory.register(self, group)
                if group == "bridge":
                    if state.BRIDGES and conf_global.get("BRDG_INC"):
                        _send_json(self, "b", {"btable": state.BTABLE, "dbridges": True})
                elif group == "lnksys":
                    ctable = state.CTABLE
                    _log_ctable_sent(self.peer, ctable)
                    _send_json(self, "c", {
                        "ctable": ctable,
                        "emaster": conf_global.get("EMPTY_MASTERS", False),
                    })
                elif group == "opb":
                    _send_json(self, "o", {
                        "ctable": state.CTABLE,
                        "dbridges": conf_global.get("BRDG_INC", False),
                    })
                elif group == "main":
                    render_last_heard("last_heard", conf_global.get("LH_ROWS", 20), self)
                elif group == "statictg":
                    _send_json(self, "s", {
                        "ctable": state.CTABLE,
                        "emaster": conf_global.get("EMPTY_MASTERS", False),
                    })
                elif group == "lsthrd_log":
                    render_lstheard_log(state.lastheard_log_rows, self)
                elif group == "tgcount" and conf_global.get("TGC_INC"):
                    render_tgcount(conf_global.get("TGC_ROWS", 20), self)
                elif group == "log":
                    for log_message in state.LOGBUF:
                        if log_message:
                            self.sendMessage(("l" + log_message).encode("utf-8"))

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
