# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
# HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
# hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
# HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
# Original works and this derivative are under GPLv3.

# Copyright (C) Rodrigo Pérez <ce5rpy@qmd.cl>
# License: GPLv3
"""Populate alias tables from CSV/JSON files (MySQL bulk import)."""

from __future__ import annotations

import logging
from typing import Any

from twisted.enterprise import adbapi
from twisted.internet.threads import deferToThread

from ...application.alias_file_parser import parse_alias_file
from ...application.ports import AliasTableRepository
from ..persistence.alias_bulk_import import merge_alias_table, replace_alias_table
from ..persistence.sync_mysql import SyncMysqlPool

logger = logging.getLogger("adn-monitor")


class MoniDBAliasTableRepository(AliasTableRepository):
    """Populates peer_ids, subscriber_ids, talkgroup_ids from files; table_count from DB."""

    def __init__(
        self,
        pool: adbapi.ConnectionPool,
        sync_pool: SyncMysqlPool | None = None,
    ) -> None:
        self._pool = pool
        self._sync_pool = sync_pool

    def populate_from_file(
        self,
        path: str,
        file_name: str,
        table: str,
        wipe: bool = True,
    ) -> None:
        rows = parse_alias_file(path, file_name, table)
        if not rows:
            return
        if self._sync_pool is not None:
            d = deferToThread(self._import_sync, table, rows, wipe)
            d.addErrback(lambda f: logger.error("populate_from_file(%s): %s", file_name, f))
            return
        logger.warning("(alias) no sync_pool; skipping DB import for %s", file_name)

    def _import_sync(self, table: str, rows: list[tuple], wipe: bool) -> int:
        if self._sync_pool is None:
            return 0
        if wipe:
            return replace_alias_table(self._sync_pool, table, rows)
        return merge_alias_table(self._sync_pool, table, rows)

    def table_count(self, table: str) -> Any:
        if table == "talkgroup_ids":
            stm = "SELECT count(*) FROM talkgroup_ids"
        elif table == "subscriber_ids":
            stm = "SELECT count(*) FROM subscriber_ids"
        elif table == "peer_ids":
            stm = "SELECT count(*) FROM peer_ids"
        else:
            return None
        return self._pool.runQuery(stm).addCallback(
            lambda r: r[0][0] if r else None
        ).addErrback(lambda f: logger.error("table_count: %s", f.getTraceback()))
