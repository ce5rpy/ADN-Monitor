# ADN Monitor - infrastructure persistence alias bulk import
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

"""MySQL/MariaDB bulk alias import with batched commits (minimal live-table locking).

Replace flow:
  1. Load rows into ``{table}_import`` (commits per batch; live ``{table}`` stays readable).
  2. Atomic ``RENAME TABLE`` swap (brief metadata lock only).

Merge flow:
  ``INSERT IGNORE`` in small transactions on the live table (no table-wide lock).

Indexes: alias tables use PRIMARY KEY (``id``) only — sufficient for ``WHERE id = %s`` lookups.
"""

from __future__ import annotations

import logging
from typing import Any

from .sync_mysql import SyncMysqlPool

logger = logging.getLogger("adn-monitor")

STAGING_BATCH_SIZE = 10_000
MERGE_BATCH_SIZE = 2_000

_TABLE_SQL = {
    "talkgroup_ids": {
        "insert": "INSERT INTO `{staging}` (id, callsign) VALUES (%s, %s)",
        "merge": "INSERT IGNORE INTO talkgroup_ids (id, callsign) VALUES (%s, %s)",
    },
    "subscriber_ids": {
        "insert": "INSERT INTO `{staging}` (id, callsign, name) VALUES (%s, %s, %s)",
        "merge": "INSERT IGNORE INTO subscriber_ids (id, callsign, name) VALUES (%s, %s, %s)",
    },
    "peer_ids": {
        "insert": "INSERT INTO `{staging}` (id, callsign) VALUES (%s, %s)",
        "merge": "INSERT IGNORE INTO peer_ids (id, callsign) VALUES (%s, %s)",
    },
}


def _table_exists(cursor: Any, table: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
        (table,),
    )
    return cursor.fetchone() is not None


def _set_bulk_load_session(cursor: Any, enabled: bool) -> None:
    """InnoDB: defer uniqueness/FK checks during staging load (staging is not read by app)."""
    if enabled:
        cursor.execute("SET SESSION unique_checks = 0")
        cursor.execute("SET SESSION foreign_key_checks = 0")
    else:
        cursor.execute("SET SESSION unique_checks = 1")
        cursor.execute("SET SESSION foreign_key_checks = 1")


def _executemany_batches(
    cursor: Any,
    conn: Any,
    sql: str,
    rows: list[tuple],
    batch_size: int,
    *,
    commit_each: bool,
) -> int:
    total = 0
    for offset in range(0, len(rows), batch_size):
        chunk = rows[offset : offset + batch_size]
        cursor.executemany(sql, chunk)
        if commit_each:
            conn.commit()
        rc = getattr(cursor, "rowcount", None)
        total += int(rc) if isinstance(rc, int) and rc > 0 else len(chunk)
    return total


def _load_staging(pool: SyncMysqlPool, table: str, staging: str, rows: list[tuple]) -> int:
    meta = _TABLE_SQL[table]
    insert_sql = meta["insert"].format(staging=staging)
    conn = pool.connect()
    try:
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS `{staging}`")
        cur.execute(f"CREATE TABLE `{staging}` LIKE `{table}`")
        conn.commit()
        _set_bulk_load_session(cur, True)
        try:
            inserted = _executemany_batches(
                cur, conn, insert_sql, rows, STAGING_BATCH_SIZE, commit_each=True
            )
        finally:
            _set_bulk_load_session(cur, False)
            conn.commit()
        return inserted
    finally:
        conn.close()


def _swap_staging(pool: SyncMysqlPool, table: str, staging: str) -> None:
    """Atomic rename; DDL — keep in its own short connection (no multi-minute transaction)."""
    old = f"{table}_old"
    conn = pool.connect()
    try:
        cur = conn.cursor()
        cur.execute("SET SESSION foreign_key_checks = 0")
        cur.execute(f"DROP TABLE IF EXISTS `{old}`")
        cur.execute(f"RENAME TABLE `{table}` TO `{old}`, `{staging}` TO `{table}`")
        cur.execute(f"DROP TABLE `{old}`")
        cur.execute("SET SESSION foreign_key_checks = 1")
        conn.commit()
    finally:
        conn.close()


def replace_alias_table(pool: SyncMysqlPool, table: str, rows: list[tuple]) -> int:
    """Full replace without long locks on the live alias table."""
    meta = _TABLE_SQL.get(table)
    if not meta or not rows:
        return 0
    conn = pool.connect()
    try:
        cur = conn.cursor()
        if not _table_exists(cur, table):
            logger.warning(
                "(alias) skip replace: table %s missing (run db_bootstrap --update)", table
            )
            return 0
    finally:
        conn.close()

    staging = f"{table}_import"
    inserted = _load_staging(pool, table, staging, rows)
    _swap_staging(pool, table, staging)
    logger.info("(alias) replaced %s: %s rows (staging + swap)", table, inserted)
    return inserted


def merge_alias_table(pool: SyncMysqlPool, table: str, rows: list[tuple]) -> int:
    """Incremental merge: batched INSERT IGNORE with commit per batch."""
    meta = _TABLE_SQL.get(table)
    if not meta or not rows:
        return 0
    conn = pool.connect()
    try:
        cur = conn.cursor()
        if not _table_exists(cur, table):
            return 0
        added = _executemany_batches(
            cur, conn, meta["merge"], rows, MERGE_BATCH_SIZE, commit_each=True
        )
        logger.info("(alias) merged %s: %s rows (batched commits)", table, added)
        return added
    finally:
        conn.close()


# Twisted runInteraction adapter (single short interaction — delegates to pool-based impl)
def replace_alias_table_cursor(pool: SyncMysqlPool, table: str, rows: list[tuple]) -> int:
    return replace_alias_table(pool, table, rows)


def merge_alias_table_cursor(pool: SyncMysqlPool, table: str, rows: list[tuple]) -> int:
    return merge_alias_table(pool, table, rows)
