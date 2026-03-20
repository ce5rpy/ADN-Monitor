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
#
# Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
# HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
# hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
# HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
# Original works and this derivative are under GPLv3.

"""Pure time formatting (no I/O)."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from time import localtime, strftime
from typing import Any
from zoneinfo import ZoneInfo

from ..domain.value_objects import ElapsedTime

logger = logging.getLogger("adn-mon")


def get_display_zone(config_global: dict[str, Any] | None) -> ZoneInfo | None:
    """
    IANA timezone from GLOBAL.TIMEZONE (e.g. Europe/Madrid).
    None or empty => use server local time (legacy behaviour).
    """
    if not config_global:
        return None
    name = config_global.get("TIMEZONE", "")
    if not isinstance(name, str):
        name = str(name) if name is not None else ""
    name = name.strip()
    if not name:
        return None
    try:
        return ZoneInfo(name)
    except Exception:
        logger.warning("Invalid GLOBAL.TIMEZONE %r; falling back to server local time", name)
        return None


def format_display_datetime(ts: float, config_global: dict[str, Any] | None, *, with_tz_abbr: bool = False) -> str:
    """
    Wall-clock string for dashboard/logs. Uses GLOBAL.TIMEZONE when set, else server local.
    with_tz_abbr: append zone abbreviation (e.g. CET).
    """
    zi = get_display_zone(config_global)
    if zi is None:
        if with_tz_abbr:
            return strftime("%Y-%m-%d %H:%M:%S %Z", localtime(ts))
        return strftime("%Y-%m-%d %H:%M:%S", localtime(ts))
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(zi)
    if with_tz_abbr:
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def time_str(seconds_or_timestamp: int | float, direction: str = "since") -> str:
    """Return friendly elapsed time string. direction: 'since' = ago, 'to' = in future."""
    return ElapsedTime.from_seconds(seconds_or_timestamp, direction).value
