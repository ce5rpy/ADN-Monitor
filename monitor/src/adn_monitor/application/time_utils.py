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

"""Pure time formatting (no I/O).

Persistence policy: ``last_heard`` / ``lstheard_log`` ``date_time`` columns are **naive UTC**.
``tg_count`` / ``user_count`` ``date`` uses the **calendar day in GLOBAL.TIMEZONE** when set,
otherwise **UTC** (legacy). ``GLOBAL.TIMEZONE`` also controls **display** of stored UTC times.
"""

from __future__ import annotations

import logging
import time
from datetime import date, datetime, timezone
from time import localtime, strftime
from typing import Any

from zoneinfo import ZoneInfo

from ..domain.value_objects import ElapsedTime

logger = logging.getLogger("adn-monitor")


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


def utc_calendar_date(ts: float | None = None) -> date:
    """Calendar date in UTC."""
    t = time.time() if ts is None else ts
    return datetime.fromtimestamp(t, tz=timezone.utc).date()


def dashboard_calendar_date(config_global: dict[str, Any] | None, ts: float | None = None) -> date:
    """Calendar day for TG-count buckets: operator TZ when configured, else UTC."""
    t = time.time() if ts is None else ts
    zi = get_display_zone(config_global)
    dt_utc = datetime.fromtimestamp(t, tz=timezone.utc)
    if zi is not None:
        return dt_utc.astimezone(zi).date()
    return dt_utc.date()


def format_tgcount_date(config_global: dict[str, Any] | None, ts: float | None = None) -> str:
    """YYYY-MM-DD for tg_count.date / user_count.date (dashboard calendar day)."""
    return dashboard_calendar_date(config_global, ts).isoformat()


def format_utc_naive_date(ts: float | None = None) -> str:
    """UTC date as YYYY-MM-DD (legacy helper)."""
    return utc_calendar_date(ts).isoformat()


def format_utc_naive_datetime(ts: float) -> str:
    """UTC wall time as naive YYYY-MM-DD HH:MM:SS (for last_heard / lstheard_log date_time column)."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def format_stored_utc_for_display(db_date: Any, config_global: dict[str, Any] | None) -> str:
    """
    Interpret stored last_heard/lstheard_log date_time as UTC (naive DATETIME in DB) and format
    for the *current* GLOBAL.TIMEZONE (or server local if unset). Changing TIMEZONE therefore
    re-renders older rows correctly.
    """
    if db_date is None:
        return ""
    if isinstance(db_date, datetime):
        dt = db_date
        if dt.tzinfo is not None:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            dt_utc = dt.replace(tzinfo=timezone.utc)
    else:
        raw = db_date.decode("utf-8", "replace") if isinstance(db_date, (bytes, bytearray)) else str(db_date)
        raw = raw.strip()
        if len(raw) == 10:
            try:
                dt_naive = datetime.strptime(raw, "%Y-%m-%d")
            except ValueError:
                return raw
            dt_utc = dt_naive.replace(tzinfo=timezone.utc)
        elif len(raw) < 19:
            return raw
        else:
            head = raw[:19]
            try:
                dt_naive = datetime.strptime(head, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return raw
            dt_utc = dt_naive.replace(tzinfo=timezone.utc)
    zi = get_display_zone(config_global)
    if zi is not None:
        return dt_utc.astimezone(zi).strftime("%Y-%m-%d %H:%M:%S")
    return dt_utc.astimezone().strftime("%Y-%m-%d %H:%M:%S")


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
