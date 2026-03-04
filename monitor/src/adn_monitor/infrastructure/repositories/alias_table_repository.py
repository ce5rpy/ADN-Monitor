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

# Copyright (C) Rodrigo Pérez <ce5rpy@qmd.cl>
# License: GPLv3
"""Populate alias tables from CSV/JSON files (Radioid.net style)."""

from __future__ import annotations

import logging
from csv import DictReader as csv_dict_reader
from json import load as jload
from pathlib import Path
from typing import Any

from twisted.enterprise import adbapi

from ...application.ports import AliasTableRepository

logger = logging.getLogger("adn-mon")

SUB_FIELDS = ("id", "callsign", "fname", "surname", "city", "state", "country")
PEER_FIELDS = ("id", "call_sign", "city", "state")
TGID_FIELDS = ("id", "callsign")


class MoniDBAliasTableRepository(AliasTableRepository):
    """Populates peer_ids, subscriber_ids, talkgroup_ids from files; table_count from DB."""

    def __init__(self, pool: adbapi.ConnectionPool) -> None:
        self._pool = pool

    def populate_from_file(
        self,
        path: str,
        file_name: str,
        table: str,
        wipe: bool = True,
    ) -> None:
        temp_lst: list[tuple] = []
        file_path = Path(path) / file_name
        if not file_path.exists():
            logger.debug("Alias file not found, skipping: %s", file_path)
            return
        try:
            with file_path.open("r", encoding="utf8") as f:
                ext = file_name.split(".")[-1]
                if ext == "csv":
                    fields = SUB_FIELDS if table == "subscriber_ids" else (
                        PEER_FIELDS if table == "peer_ids" else TGID_FIELDS
                    )
                    records = csv_dict_reader(
                        f, fieldnames=fields, restkey="OTHER", dialect="excel", delimiter=","
                    )
                else:
                    data = jload(f)
                    if "count" in data:
                        data.pop("count")
                    records = data[[*data][0]]

                if table == "peer_ids":
                    for record in records:
                        try:
                            temp_lst.append((int(record["id"]), record.get("callsign", record.get("call_sign", ""))))
                        except (KeyError, TypeError, ValueError):
                            pass
                elif table == "subscriber_ids":
                    for record in records:
                        fname = record.get("fname", "")
                        surname = record.get("surname", "")
                        name = fname or surname or "NO NAME"
                        try:
                            temp_lst.append((int(record["id"]), record.get("callsign", ""), name))
                        except (KeyError, TypeError, ValueError):
                            pass
                elif table == "talkgroup_ids":
                    for record in records:
                        try:
                            temp_lst.append((int(record["id"]), record.get("callsign", "")))
                        except (KeyError, TypeError, ValueError):
                            pass

            if temp_lst:
                self._run_populate(table, temp_lst, wipe, file_name)
        except Exception as err:
            logger.error("fill_table error: %s %s", err, type(err))

    def _run_populate(self, table: str, lst_data: list[tuple], wipe_tbl: bool, file_name: str) -> None:
        def run(txn: Any, wipe: bool) -> None:
            if table == "talkgroup_ids":
                stm = "INSERT IGNORE INTO talkgroup_ids VALUES (%s, %s)"
                w_stm = "TRUNCATE TABLE talkgroup_ids"
            elif table == "subscriber_ids":
                stm = "INSERT IGNORE INTO subscriber_ids VALUES (%s, %s, %s)"
                w_stm = "TRUNCATE TABLE subscriber_ids"
            elif table == "peer_ids":
                stm = "INSERT IGNORE INTO peer_ids VALUES (%s, %s)"
                w_stm = "TRUNCATE TABLE peer_ids"
            else:
                return
            if wipe:
                txn.execute(w_stm)
            txn.executemany(stm, lst_data)
            if txn.rowcount > 0:
                logger.info("%s entries added to: %s table from: %s", txn.rowcount, table, file_name)

        self._pool.runInteraction(run, wipe_tbl).addErrback(
            lambda f: logger.error("populate_from_file(%s): %s", file_name, f.getTraceback())
        )

    def table_count(self, table: str) -> Any:
        """Return Deferred firing row count for table, or None."""
        if table == "talkgroup_ids":
            stm = "SELECT count(*) FROM talkgroup_ids"
        elif table == "subscriber_ids":
            stm = "SELECT count(*) FROM subscriber_ids"
        elif table == "peer_ids":
            stm = "SELECT count(*) FROM peer_ids"
        else:
            return None
        return self._pool.runQuery(stm).addCallback(
            lambda rows: rows[0][0] if rows else None
        ).addErrback(lambda f: logger.error("table_count: %s", f.getTraceback()))
