# ADN Monitor - application dashboard ws
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

"""WebSocket dashboard protocol (conf,<group> messages)."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable

from ..domain.value_objects import ServerMode
from . import ws_ctable_views
from .monitor_controller import MonitorState, ctable_is_empty, sync_ctable_from_config

logger = logging.getLogger("adn-monitor")

SEND_ALL_GROUPS = (
    "main",
    "lnksys",
    "opb",
    "statictg",
    "lsthrd_log",
    "tgcount",
    "bridge",
    "log",
    "server_info",
)

SendText = Callable[[str], None]


def send_json(send: SendText, opcode: str, payload: dict) -> None:
    send(opcode + json.dumps(payload, default=str))


def parse_conf_message(text: str) -> list[str] | None:
    parts = text.split(",")
    if not parts or parts[0] != "conf":
        return None
    return list(SEND_ALL_GROUPS) if "all" in parts[1:] else parts[1:]


def handle_conf_groups(
    *,
    state: MonitorState,
    conf_global: dict,
    groups: list[str],
    send: SendText,
    render_last_heard: Callable[[], None],
    render_lstheard_log: Callable[[], None],
    render_tgcount: Callable[[], None],
    refresh_from_server: Callable[[], bool] | None = None,
) -> None:
    """Reply to ``conf,<group>`` with dashboard payloads for the requested groups."""
    for group in groups:
        if group == "bridge":
            if state.BRIDGES and conf_global.get("BRDG_INC"):
                send_json(send, "b", {"btable": state.BTABLE, "dbridges": True})
        elif group == "lnksys":
            if ctable_is_empty(state.CTABLE) and state.CONFIG:
                sync_ctable_from_config(state, conf_global)
            emaster = conf_global.get("EMPTY_MASTERS", False)
            send_json(
                send,
                "c",
                {
                    "ctable": ws_ctable_views.ctable_for_lnksys(state.CTABLE, empty_masters=emaster),
                    "emaster": emaster,
                },
            )
        elif group == "opb":
            send_json(
                send,
                "o",
                {
                    "ctable": ws_ctable_views.ctable_for_opb(state.CTABLE),
                    "dbridges": conf_global.get("BRDG_INC", False),
                },
            )
        elif group == "main":
            render_last_heard()
        elif group == "statictg":
            if ctable_is_empty(state.CTABLE) and state.CONFIG:
                sync_ctable_from_config(state, conf_global)
            emaster = conf_global.get("EMPTY_MASTERS", False)
            send_json(
                send,
                "s",
                {
                    "ctable": ws_ctable_views.ctable_for_lnksys(state.CTABLE, empty_masters=emaster),
                    "emaster": emaster,
                },
            )
        elif group == "lsthrd_log":
            render_lstheard_log()
        elif group == "tgcount" and conf_global.get("TGC_INC"):
            render_tgcount()
        elif group == "log":
            for log_message in state.LOGBUF:
                if log_message:
                    send("l" + log_message)
        elif group == "server_info":
            mode = getattr(state, "server_mode", None)
            info = getattr(state, "server_info", {}) or {}
            send_json(
                send,
                "v",
                {
                    "mode": getattr(mode, "value", str(mode) if mode is not None else "legacy"),
                    "info": info,
                },
            )

    if (
        refresh_from_server is not None
        and any(g in ("lnksys", "statictg") for g in groups)
        and getattr(state, "server_mode_confirmed", False)
        and getattr(state, "server_mode", ServerMode.LEGACY) == ServerMode.V2
    ):
        refresh_from_server()
