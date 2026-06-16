# ADN Monitor - application dashboard push
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

"""Push CTABLE / BTABLE updates to WebSocket groups."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections.abc import Callable

from . import ws_ctable_views
from .monitor_controller import MonitorState
from .ports import BroadcastPort

logger = logging.getLogger("adn-monitor")

OPB_WIRE_MIN_INTERVAL_SEC = 0.05


def _payload_hash(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


class DashboardPusher:
    """Event-driven WebSocket broadcasts for lnksys / opb / statictg / bridge."""

    def __init__(
        self,
        state: MonitorState,
        broadcast: BroadcastPort,
        conf_global: dict,
        *,
        group_active: Callable[[str], bool] | None = None,
    ) -> None:
        self._state = state
        self._broadcast = broadcast
        self._conf = conf_global
        self._group_active = group_active or (lambda _g: True)
        self._last_hash: dict[str, str] = {}
        self._opb_last_ts = 0.0

    def broadcast_ctable(
        self,
        *,
        dedup: bool = True,
        brdg_meta: dict | None = None,
        groups_filter: tuple[str, ...] | None = None,
    ) -> None:
        state = self._state
        emaster = self._conf.get("EMPTY_MASTERS", False)
        brdg_inc = self._conf.get("BRDG_INC", False)
        if not state.CONFIG:
            return

        def _want(group: str) -> bool:
            return self._group_active(group) and (
                groups_filter is None or group in groups_filter
            )

        if _want("lnksys"):
            msg = "c" + json.dumps(
                {
                    "ctable": ws_ctable_views.ctable_for_lnksys(state.CTABLE, empty_masters=emaster),
                    "emaster": emaster,
                },
                default=str,
            )
            if not dedup or self._last_hash.get("lnksys") != _payload_hash(msg):
                self._broadcast.broadcast(msg, "lnksys")
                self._last_hash["lnksys"] = _payload_hash(msg)

        if _want("opb") and self._should_send_opb(brdg_meta):
            self._emit_opb(dedup=dedup)

        if _want("statictg"):
            msg = "s" + json.dumps(
                {
                    "ctable": ws_ctable_views.ctable_for_lnksys(state.CTABLE, empty_masters=emaster),
                    "emaster": emaster,
                },
                default=str,
            )
            if not dedup or self._last_hash.get("statictg") != _payload_hash(msg):
                self._broadcast.broadcast(msg, "statictg")
                self._last_hash["statictg"] = _payload_hash(msg)

        if state.BRIDGES and brdg_inc and _want("bridge"):
            msg = "b" + json.dumps({"btable": state.BTABLE, "dbridges": True}, default=str)
            if not dedup or self._last_hash.get("bridge") != _payload_hash(msg):
                self._broadcast.broadcast(msg, "bridge")
                self._last_hash["bridge"] = _payload_hash(msg)

    def on_config_applied(self) -> None:
        self.broadcast_ctable(dedup=False, groups_filter=("lnksys", "statictg", "opb"))

    def on_bridges_applied(self) -> None:
        """Routing table / BRIDGE_SND: SINGLE_TS* refreshed; push Linked Systems."""
        self.broadcast_ctable(dedup=False, groups_filter=("lnksys", "statictg"))

    def on_ctable_updated(self, brdg_meta: dict | None = None) -> None:
        self.broadcast_ctable(brdg_meta=brdg_meta)

    def _should_send_opb(self, brdg_meta: dict | None) -> bool:
        if brdg_meta is None:
            return True
        act = brdg_meta.get("action")
        sysn = brdg_meta.get("system")
        if act not in ("START", "END"):
            return False
        return sysn in (self._state.CTABLE.get("OPENBRIDGES") or {})

    def _emit_opb(self, *, dedup: bool) -> None:
        state = self._state
        dbridges = self._conf.get("BRDG_INC", False)
        payload = {"ctable": ws_ctable_views.ctable_for_opb(state.CTABLE), "dbridges": dbridges}
        msg = "o" + json.dumps(payload, default=str)
        sem_h = _payload_hash(ws_ctable_views.opb_semantic_fingerprint(state.CTABLE, dbridges))
        if dedup and self._last_hash.get("opb_sem") == sem_h:
            return
        self._broadcast.broadcast(msg, "opb")
        self._last_hash["opb_sem"] = sem_h
        self._opb_last_ts = time.time()
