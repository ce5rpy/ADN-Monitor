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
