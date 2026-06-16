# ADN Monitor - application peer options merge
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

"""Merge Clients.options into in-memory CTABLE (static TG display)."""

from __future__ import annotations

from typing import Any

from .monitor_controller import MonitorState
from .tgstats import parse_options_to_static


def dmr_id_to_int(dmr_id: Any) -> int | None:
    if dmr_id is None:
        return None
    if isinstance(dmr_id, int):
        return dmr_id
    if isinstance(dmr_id, (bytes, bytearray)) and len(dmr_id) >= 4:
        return int.from_bytes(dmr_id[:4], "big")
    try:
        return int(dmr_id)
    except (TypeError, ValueError):
        return None


def apply_peer_options_rows(state: MonitorState, rows: list[tuple[Any, ...]]) -> bool:
    """Cache Clients.options for admin UI; CTABLE chips use server CONFIG OPTIONS only."""
    state.PEER_OPTIONS.clear()
    for row in rows:
        if len(row) < 2:
            continue
        dmr_int = dmr_id_to_int(row[0])
        if dmr_int is None:
            continue
        state.PEER_OPTIONS[dmr_int] = parse_options_to_static(row[1])
    return False
