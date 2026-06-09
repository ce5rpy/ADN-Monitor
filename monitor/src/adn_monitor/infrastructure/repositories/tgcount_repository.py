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
"""TG count repository (Twisted adbapi pool)."""

from __future__ import annotations

import logging
import time
from typing import Any

from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue

from ...application.ports import TgCountRepository
from ...application.time_utils import format_tgcount_date
from ..persistence.db_pool import sec_time

logger = logging.getLogger("adn-monitor")


class MoniDBTgCountRepository(TgCountRepository):
    """TgCountRepository implemented with adbapi connection pool."""

    def __init__(self, pool: adbapi.ConnectionPool, config_global: dict | None = None) -> None:
        self._pool = pool
        self._config_global = config_global or {}

    def insert_tgcount(self, tg_num: str, dmr_id: str, qso_time: str) -> None:
        def run(txn: Any) -> None:
            d_utc = format_tgcount_date(self._config_global, time.time())
            txn.execute(
                """INSERT INTO tg_count VALUES (%s, %s, 1, %s)
                ON DUPLICATE KEY UPDATE qso_time = qso_time + %s,
                qso_count = qso_count + 1""",
                (d_utc, tg_num, qso_time, qso_time),
            )
            txn.execute(
                """INSERT INTO user_count VALUES(%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE qso_time = qso_time + %s""",
                (d_utc, tg_num, dmr_id, qso_time, qso_time),
            )

        self._pool.runInteraction(run).addErrback(
            lambda f: logger.error("insert_tgcount: %s", f.getTraceback())
        )

    @inlineCallbacks
    def select_tgcount(self, row_num: int) -> list[Any] | None:
        d_today = format_tgcount_date(self._config_global, time.time())
        rows = yield self._pool.runQuery(
            """SELECT tg_num, ifnull(callsign, ''), qso_count, qso_time FROM tg_count
            LEFT JOIN talkgroup_ids ON talkgroup_ids.id = tg_count.tg_num
            WHERE tg_count.date = %s ORDER BY qso_time DESC LIMIT %s""",
            (d_today, row_num),
        )
        if not rows:
            returnValue(None)
        res_lst: list[Any] = []
        for tg_num, name, qso_c, qso_time in rows:
            res = yield self._pool.runQuery(
                """SELECT ifnull(callsign, "N0CALL") FROM user_count
                LEFT JOIN subscriber_ids ON subscriber_ids.id = user_count.dmr_id
                WHERE tg_num = %s AND user_count.date = %s ORDER BY qso_time DESC LIMIT 4""",
                (tg_num, d_today),
            )
            res_lst.append(
                (tg_num, name, qso_c, sec_time(qso_time), tuple(r[0] for r in res))
            )
        returnValue(res_lst)

    def clean_tgcount(self) -> None:
        d_today = format_tgcount_date(self._config_global, time.time())
        d = self._pool.runOperation("DELETE FROM tg_count WHERE date != %s", (d_today,))
        d.addCallback(lambda _: self._pool.runOperation("DELETE FROM user_count WHERE date != %s", (d_today,)))
        d.addCallback(lambda _: logger.info("TG Count tables cleaned successfully"))
        d.addErrback(lambda f: logger.error("clean_tgcount: %s", f.getTraceback()))
