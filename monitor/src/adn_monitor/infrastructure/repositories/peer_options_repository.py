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
