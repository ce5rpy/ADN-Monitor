# ADN Monitor - application alias file parser
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

"""Parse alias JSON/CSV files into row tuples for DB import."""

from __future__ import annotations

import logging
from csv import DictReader as csv_dict_reader
from json import load as jload
from pathlib import Path

logger = logging.getLogger("adn-monitor")

SUB_FIELDS = ("id", "callsign", "fname", "surname", "city", "state", "country")
PEER_FIELDS = ("id", "call_sign", "city", "state")
TGID_FIELDS = ("id", "callsign")

_ALLOWED = frozenset({"peer_ids", "subscriber_ids", "talkgroup_ids"})


def parse_alias_file(path: str, file_name: str, table: str) -> list[tuple]:
    """Return rows ready for bulk import; empty if file missing or invalid."""
    if table not in _ALLOWED:
        return []
    file_path = Path(path) / file_name
    if not file_path.exists():
        logger.debug("Alias file not found, skipping: %s", file_path)
        return []
    rows: list[tuple] = []
    try:
        with file_path.open("r", encoding="utf8") as f:
            ext = file_name.rsplit(".", 1)[-1].lower()
            if ext == "csv":
                fields = (
                    SUB_FIELDS
                    if table == "subscriber_ids"
                    else PEER_FIELDS
                    if table == "peer_ids"
                    else TGID_FIELDS
                )
                records = csv_dict_reader(
                    f, fieldnames=fields, restkey="OTHER", dialect="excel", delimiter=","
                )
            else:
                data = jload(f)
                if isinstance(data, dict):
                    if "count" in data:
                        data.pop("count")
                    key = next(iter(data), None)
                    records = data[key] if key is not None else []
                else:
                    records = data

            for record in records:
                if not isinstance(record, dict):
                    continue
                try:
                    if table == "peer_ids":
                        rows.append(
                            (
                                int(record["id"]),
                                record.get("callsign", record.get("call_sign", "")),
                            )
                        )
                    elif table == "subscriber_ids":
                        fname = record.get("fname", "")
                        surname = record.get("surname", "")
                        name = fname or surname or "NO NAME"
                        rows.append((int(record["id"]), record.get("callsign", ""), name))
                    else:
                        rows.append((int(record["id"]), record.get("callsign", "")))
                except (KeyError, TypeError, ValueError):
                    continue
    except Exception as err:
        logger.error("parse_alias_file %s: %s", file_name, err)
        return []
    return rows


def alias_file_is_valid(
    path: str,
    file_name: str,
    table: str,
    *,
    min_rows: int = 1,
) -> bool:
    """True when the alias file exists and parses to at least ``min_rows`` entries."""
    if min_rows < 1:
        return False
    file_path = Path(path) / file_name
    if not file_path.is_file() or file_path.stat().st_size == 0:
        return False
    return len(parse_alias_file(path, file_name, table)) >= min_rows
