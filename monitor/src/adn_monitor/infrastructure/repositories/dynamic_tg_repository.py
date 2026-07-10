# ADN Monitor - infrastructure repositories dynamic tg repository
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

"""MySQL ``peer_dynamic_tgs`` reload requests (monitor → server via proxy poll)."""

from __future__ import annotations

import time

from ...application.ports import DynamicTgRepository
from ..persistence.sync_mysql import SyncMysqlPool


class MysqlDynamicTgRepository(DynamicTgRepository):
    def __init__(self, pool: SyncMysqlPool) -> None:
        self._pool = pool

    def mark_need_reload(
        self,
        int_id: int,
        *,
        fallback_system_names: list[str] | None = None,
    ) -> bool:
        """Queue TG-4000-equivalent purge for peer (``need_reload=1`` on all systems)."""
        now = int(time.time())
        names = [str(n).strip() for n in (fallback_system_names or []) if str(n).strip()]
        with self._pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE peer_dynamic_tgs SET need_reload = 1, updated_at = %s WHERE int_id = %s",
                (now, int_id),
            )
            if int(cur.rowcount) > 0:
                return True
            ok = False
            for system_name in dict.fromkeys(names):
                cur.execute(
                    """INSERT INTO peer_dynamic_tgs
                       (int_id, system_name, slot, tgid, single_mode, expires_at, updated_at, need_reload)
                       VALUES (%s, %s, 0, 0, 0, NULL, %s, 1)
                       ON DUPLICATE KEY UPDATE need_reload = 1, updated_at = VALUES(updated_at)""",
                    (int_id, system_name, now),
                )
                ok = ok or int(cur.rowcount) > 0
            return ok
