# ADN Monitor - UA dynamic TG timer sentinel
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

"""Legacy ``TIMER=0`` means no UA expiry (same sentinel as adn-server)."""

from __future__ import annotations

import time

UA_TIMER_INFINITE_MINUTES = 35_791_394.0
UA_SESSION_NEVER_EXPIRES_AT = 0.0


def ua_timer_is_infinite(minutes: float) -> bool:
    return float(minutes) >= UA_TIMER_INFINITE_MINUTES - 1.0


def ua_session_never_expires(expires_at: float) -> bool:
    return float(expires_at) == UA_SESSION_NEVER_EXPIRES_AT


def normalize_ua_timer_minutes(raw: float, *, default_minutes: float) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = float(default_minutes)
    if value <= 0:
        return UA_TIMER_INFINITE_MINUTES
    return value


def ua_session_expires_is_infinite(expires_at: float, *, now: float | None = None) -> bool:
    """True when absolute expiry matches the legacy infinite TIMER sentinel."""
    pkt_time = time.time() if now is None else now
    remaining = float(expires_at) - pkt_time
    return remaining >= (UA_TIMER_INFINITE_MINUTES * 60.0) * 0.99
