# ADN Monitor - infrastructure repositories clients device repository
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

"""MySQL DeviceRepository (Clients table)."""

from __future__ import annotations

from ...application.ports import DeviceRepository
from ...domain.client import Client
from ..persistence.sync_mysql import SyncMysqlPool


class MysqlDeviceRepository(DeviceRepository):
    def __init__(self, pool: SyncMysqlPool) -> None:
        self._pool = pool

    def get_by_id(self, int_id: int) -> Client | None:
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Clients WHERE int_id = %s", (int_id,))
            row = cur.fetchone()
            if not row:
                return None
            cols = [d[0] for d in cur.description]
            data = dict(zip(cols, row))
        return Client(
            int_id=int(data["int_id"]),
            callsign=str(data.get("callsign") or ""),
            options=str(data.get("options") or ""),
            modified=bool(int(data.get("modified") or 0)),
            mode=int(data.get("mode") or 4),
            host=str(data["host"]) if data.get("host") else None,
        )

    def update_options(self, int_id: int, options: str) -> int:
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE Clients SET options = %s, modified = 1 WHERE int_id = %s",
                (options, int_id),
            )
            return int(cur.rowcount)

    def get_modified(self, int_id: int) -> bool:
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT modified FROM Clients WHERE int_id = %s", (int_id,))
            row = cur.fetchone()
        return row is not None and bool(int(row[0]))
