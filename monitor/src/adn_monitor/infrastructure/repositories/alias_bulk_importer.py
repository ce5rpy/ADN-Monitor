"""Sync MySQL bulk alias import (used from asyncio background tasks)."""

from __future__ import annotations

from ...application.alias_file_parser import parse_alias_file
from ...application.ports import AliasBulkImportPort
from ..persistence.alias_bulk_import import merge_alias_table, replace_alias_table
from ..persistence.sync_mysql import SyncMysqlPool


class MysqlAliasBulkImporter(AliasBulkImportPort):
    def __init__(self, pool: SyncMysqlPool) -> None:
        self._pool = pool

    def import_from_file(
        self,
        path: str,
        file_name: str,
        table: str,
        *,
        replace: bool,
    ) -> int:
        rows = parse_alias_file(path, file_name, table)
        if not rows:
            return 0
        if replace:
            return replace_alias_table(self._pool, table, rows)
        return merge_alias_table(self._pool, table, rows)
