# ADN Monitor - infrastructure repositories alias bulk importer
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
