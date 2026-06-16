# ADN Monitor - infrastructure repositories peer options repository
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

"""Read logged-in Clients.options for CTABLE static TG merge."""

from __future__ import annotations

from typing import Any

from ..persistence.sync_mysql import SyncMysqlPool


class MysqlPeerOptionsRepository:
    def __init__(self, pool: SyncMysqlPool) -> None:
        self._pool = pool

    def fetch_logged_in_options(self) -> list[tuple[Any, ...]]:
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT dmr_id, options FROM Clients "
                "WHERE logged_in=1 AND options IS NOT NULL AND options != ''"
            )
            return list(cur.fetchall())
