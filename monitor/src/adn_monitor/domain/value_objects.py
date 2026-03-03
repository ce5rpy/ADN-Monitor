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

"""Value objects for the monitor domain."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DmrId:
    """DMR subscriber/peer/talkgroup numeric ID."""

    value: int

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True, slots=True)
class Callsign:
    """Callsign string."""

    value: str


@dataclass(frozen=True, slots=True)
class ElapsedTime:
    """Human-readable elapsed time (e.g. "2h 30m")."""

    value: str

    @staticmethod
    def from_seconds(seconds: int | float, direction: str = "since") -> "ElapsedTime":
        """Build from seconds; direction 'since' = ago, 'to' = in the future."""
        now = int(time.time())
        if direction == "since":
            delta = now - int(seconds)
        else:
            delta = int(seconds) - now
        delta = abs(delta)
        secs = delta % 60
        mins = (delta // 60) % 60
        hours = (delta // 3600) % 24
        days = delta // 86400
        if days:
            return ElapsedTime(f"{days}d {hours}h")
        if hours:
            return ElapsedTime(f"{hours}h {mins}m")
        if mins:
            return ElapsedTime(f"{mins}m {secs}s")
        return ElapsedTime(f"{secs}s")


@dataclass(frozen=True, slots=True)
class Opcode:
    """Report protocol opcode (single byte)."""

    value: bytes

    CONFIG_REQ = b"\x00"
    CONFIG_SND = b"\x01"
    BRIDGE_REQ = b"\x02"
    BRIDGE_SND = b"\x03"
    CONFIG_UPD = b"\x04"
    BRIDGE_UPD = b"\x05"
    LINK_EVENT = b"\x06"
    BRDG_EVENT = b"\x07"
    SERVER_MSG = b"b"

    @classmethod
    def from_message(cls, raw: bytes) -> "Opcode":
        return cls(value=raw[:1] if raw else b"")


def decode_utf8_field(raw: Any) -> str:
    """Decode a field that may be bytes or str."""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace").strip()
    return str(raw).strip() if raw is not None else ""
