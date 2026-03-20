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

# Copyright (C) Rodrigo Pérez <ce5rpy@qmd.cl>
# License: GPLv3
"""Last heard and lstheard_log repository (Twisted adbapi pool)."""

from __future__ import annotations

import logging
import time
from json import loads as jloads
from typing import Any

from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue

from ...application.ports import LastHeardRepository
from ...application.time_utils import format_utc_naive_datetime

logger = logging.getLogger("adn-mon")


class MoniDBLastHeardRepository(LastHeardRepository):
    """LastHeardRepository implemented with adbapi connection pool."""

    def __init__(self, pool: adbapi.ConnectionPool) -> None:
        self._pool = pool

    def insert_last_heard(
        self,
        qso_time: float | None,
        qso_type: str,
        system: str,
        tg_num: int,
        dmr_id: int,
        *,
        wall_date_time: str | None = None,
    ) -> None:
        dt_utc = wall_date_time if wall_date_time is not None else format_utc_naive_datetime(time.time())
        self._pool.runOperation(
            "REPLACE INTO last_heard VALUES (%s, %s, %s, %s, %s, %s)",
            (dt_utc, qso_time, qso_type, system, tg_num, dmr_id),
        ).addErrback(lambda f: logger.error("insert_last_heard: %s", f.getTraceback()))

    def insert_lstheard_log(
        self,
        qso_time: float | None,
        qso_type: str,
        system: str,
        tg_num: int,
        dmr_id: int,
        *,
        wall_date_time: str | None = None,
    ) -> None:
        dt_utc = wall_date_time if wall_date_time is not None else format_utc_naive_datetime(time.time())
        self._pool.runOperation(
            """INSERT INTO lstheard_log (date_time, qso_time, qso_type, system, tg_num, dmr_id)
            VALUES(%s, %s, %s, %s, %s, %s)""",
            (dt_utc, qso_time, qso_type, system, tg_num, dmr_id),
        ).addErrback(lambda f: logger.error("insert_lstheard_log: %s", f.getTraceback()))

    @inlineCallbacks
    def select_for_render(self, table: str, row_num: int) -> list[tuple[Any, ...]]:
        if table == "last_heard":
            stm = """SELECT CONVERT(date_time, CHAR), qso_time, qso_type, system, tg_num,
                (SELECT callsign FROM talkgroup_ids WHERE id = tg_num), dmr_id,
                (SELECT json_array(callsign, name) FROM subscriber_ids WHERE id = dmr_id)
                FROM last_heard ORDER BY date_time DESC LIMIT %s"""
        elif table == "lstheard_log":
            stm = """SELECT CONVERT(date_time, CHAR), qso_time, qso_type, system, tg_num,
                (SELECT callsign FROM talkgroup_ids WHERE id = tg_num), dmr_id,
                (SELECT json_array(callsign, name) FROM subscriber_ids WHERE id = dmr_id)
                FROM lstheard_log ORDER BY date_time DESC LIMIT %s"""
        else:
            returnValue([])
        result = yield self._pool.runQuery(stm, (row_num,))
        out: list[tuple[Any, ...]] = []
        if result:
            for row in result:
                if row[7]:
                    r_lst = list(row)
                    r_lst[7] = jloads(row[7])
                    out.append(tuple(r_lst))
                else:
                    out.append(row)
        returnValue(out)

    def clean_table(self, table: str, keep_rows: int) -> None:
        if table == "last_heard":
            stm = """DELETE FROM last_heard WHERE date_time <= (SELECT date_time FROM (
                SELECT date_time FROM last_heard ORDER BY date_time DESC LIMIT 1 OFFSET %s)
                foo )"""
        elif table == "lstheard_log":
            stm = """DELETE FROM lstheard_log WHERE date_time <= (SELECT date_time FROM (
                SELECT date_time FROM lstheard_log ORDER BY date_time DESC LIMIT 1 OFFSET %s)
                foo )"""
        else:
            return
        n = int(keep_rows * 1.25)
        self._pool.runOperation(stm, (n,)).addCallback(
            lambda _: logger.info("%s DB table cleaned successfully.", table)
        ).addErrback(lambda f: logger.error("clean_table: %s", f.getTraceback()))
