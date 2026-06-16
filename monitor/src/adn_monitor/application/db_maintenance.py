# ADN Monitor - application db maintenance
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

"""Periodic DB maintenance (trim tables, TG-count day rollover)."""

from __future__ import annotations

from datetime import date
from typing import Any

from .ports import LastHeardRepository, TgCountRepository
from .time_utils import dashboard_calendar_date


def maybe_clean_tgcount(
    tgcount_repo: TgCountRepository,
    config_global: dict[str, Any],
    last_day: date | None,
) -> date:
    """Run clean_tgcount when the dashboard calendar day changes. Returns current day."""
    today = dashboard_calendar_date(config_global)
    if last_day is None or today != last_day:
        tgcount_repo.clean_tgcount()
    return today


def run_cleaning_loop(
    config_global: dict[str, Any],
    lastheard_repo: LastHeardRepository,
    tgcount_repo: TgCountRepository,
    *,
    lastheard_log_rows: int = 70,
    last_tg_day: date | None = None,
) -> date | None:
    """
    Trim last_heard / lstheard_log and roll TG-count tables for the current dashboard day.
    Returns updated TG-day tracker (unchanged if TGC_INC is false).
    """
    tg_day = last_tg_day
    if config_global.get("TGC_INC"):
        tg_day = maybe_clean_tgcount(tgcount_repo, config_global, last_tg_day)
    lh_keep = int(config_global.get("LH_ROWS", 20))
    lastheard_repo.clean_table("last_heard", lh_keep)
    lastheard_repo.clean_table("lstheard_log", lastheard_log_rows)
    return tg_day
