# ADN Monitor - application peer system lookup
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

"""Resolve which MASTER systems a peer is connected to (live CTABLE)."""

from __future__ import annotations

from typing import Any


def peer_master_names(ctable: dict[str, Any] | None, int_id: int) -> list[str]:
    """Return MASTER names where ``int_id`` appears in ``CTABLE.MASTERS.*.PEERS``."""
    if not ctable:
        return []
    masters = ctable.get("MASTERS")
    if not isinstance(masters, dict):
        return []
    peer_int = int(int_id)
    found: list[str] = []
    for name, master in masters.items():
        if not isinstance(master, dict):
            continue
        peers = master.get("PEERS")
        if not isinstance(peers, dict):
            continue
        if peer_int in peers or str(peer_int) in peers:
            found.append(str(name))
    return sorted(set(found))
