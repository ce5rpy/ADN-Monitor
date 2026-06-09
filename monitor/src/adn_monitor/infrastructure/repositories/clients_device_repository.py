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
