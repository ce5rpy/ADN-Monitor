# Hotspot Proxy for ADN DMR Peer Server.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Helpers to extract peer_id from Homebrew / ADN DMR Peer Server packets by command."""

from __future__ import annotations

from ..domain.value_objects import (
    DMRD,
    DMRA,
    MSTC,
    MSTN,
    MSTP,
    RPTA,
    RPTCL,
    RPTK,
    RPTL,
    RPTC,
    RPTO,
    RPTP,
)


def peer_id_from_packet(data: bytes, command: bytes, from_master: bool) -> bytes | None:
    """
    Return peer_id (4 bytes) from packet payload, or None if not applicable.
    from_master: True if packet is from master (peer server), False if from client (repeater).
    """
    if len(data) < 8:
        return None
    if from_master:
        if command == DMRD and len(data) >= 15:
            return data[11:15]
        if command == RPTA:
            if len(data) >= 10 and data[6:10] is not None:
                return data[6:10]  # caller may have to fall back to connTrack[port]
            return None
        if command == MSTN and len(data) >= 10:
            return data[6:10]
        if command == MSTP and len(data) >= 11:
            return data[7:11]
        if command == MSTC and len(data) >= 9:
            return data[5:9]
        return None
    # From client
    if command == DMRD and len(data) >= 15:
        return data[11:15]
    if command in (DMRA, RPTL, RPTK, RPTO) and len(data) >= 8:
        return data[4:8]
    if command == RPTC:
        if len(data) >= 5 and data[:5] == RPTCL:
            return data[5:9] if len(data) >= 9 else None
        return data[4:8] if len(data) >= 8 else None
    if command == RPTP and len(data) >= 11:
        return data[7:11]
    return None
