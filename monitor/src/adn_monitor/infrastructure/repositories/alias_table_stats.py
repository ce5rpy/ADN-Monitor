# ADN Monitor - infrastructure repositories alias table stats
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

"""Synchronous alias table row counts (for alias refresh decisions)."""

from __future__ import annotations

from ..persistence.sync_mysql import SyncMysqlPool

_ALLOWED = {
    "peer_ids": "SELECT count(*) FROM peer_ids",
    "subscriber_ids": "SELECT count(*) FROM subscriber_ids",
    "talkgroup_ids": "SELECT count(*) FROM talkgroup_ids",
}


class SyncAliasTableStats:
    def __init__(self, pool: SyncMysqlPool) -> None:
        self._pool = pool

    def count(self, table: str) -> int | None:
        sql = _ALLOWED.get(table)
        if not sql:
            return None
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            row = cur.fetchone()
        return int(row[0]) if row else None
