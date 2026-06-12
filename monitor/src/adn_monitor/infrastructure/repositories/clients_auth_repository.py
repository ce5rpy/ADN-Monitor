# ADN Monitor - infrastructure repositories clients auth repository
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

"""MySQL AuthRepository (Clients table)."""

from __future__ import annotations

from typing import Any

from ...application.ports import AuthRepository
from ..persistence.sync_mysql import SyncMysqlPool


class MysqlAuthRepository(AuthRepository):
    def __init__(self, pool: SyncMysqlPool) -> None:
        self._pool = pool

    def find_by_callsign_and_logged_in(self, callsign: str) -> dict[int, dict[str, str]] | None:
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT int_id, callsign, psswd FROM Clients WHERE callsign = %s AND logged_in = 1",
                (callsign,),
            )
            rows = cur.fetchall()
        if not rows:
            return None
        out: dict[int, dict[str, str]] = {}
        for int_id, cs, psswd in rows:
            out[int(int_id)] = {
                "callsign": str(cs),
                "psswd": psswd.decode("utf-8", errors="ignore") if isinstance(psswd, bytes) else str(psswd),
            }
        return out

    def get_int_ids_for_callsign(self, callsign: str) -> list[int]:
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT int_id FROM Clients WHERE callsign = %s AND logged_in = 1",
                (callsign,),
            )
            rows = cur.fetchall()
        ids = sorted({int(r[0]) for r in rows})
        return ids

    def find_by_host(self, ip: str) -> dict[str, object] | None:
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT callsign FROM Clients WHERE host = %s AND logged_in = 1",
                (ip,),
            )
            rows = [r[0] for r in cur.fetchall()]
        if len(rows) != 1:
            return None
        callsign = str(rows[0])
        int_ids = self.get_int_ids_for_callsign(callsign)
        if not int_ids:
            return None
        return {"callsign": callsign, "int_ids": int_ids}
