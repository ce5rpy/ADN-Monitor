"""Synchronous MySQL connections for FastAPI REST (no Twisted reactor)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import MySQLdb


class SyncMysqlPool:
    """Thin wrapper around short-lived MySQL connections."""

    def __init__(self, db_config: dict[str, Any]) -> None:
        self._host = str(db_config.get("SERVER", "localhost"))
        self._user = str(db_config.get("USER", ""))
        self._passwd = str(db_config.get("PASSWD", ""))
        self._db = str(db_config.get("NAME", ""))
        self._port = int(db_config.get("PORT", 3306))

    def connect(self) -> Any:
        return MySQLdb.connect(
            host=self._host,
            user=self._user,
            passwd=self._passwd,
            db=self._db,
            port=self._port,
            charset="utf8mb4",
        )

    @contextmanager
    def connection(self, *, autocommit: bool = True) -> Iterator[Any]:
        conn = self.connect()
        try:
            yield conn
            if autocommit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
