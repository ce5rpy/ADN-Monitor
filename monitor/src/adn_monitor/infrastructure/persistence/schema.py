# ADN Monitor - infrastructure persistence schema
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

"""Idempotent MySQL schema ensure (existing DBs + orphan staging cleanup).

No Alembic/Flyway: versioned migrations in ``schema_migrations`` table.
Safe to run on every ``monitor.py`` start when SELF_SERVICE is configured.
"""

from __future__ import annotations

import logging
from typing import Any

from ..persistence.sync_mysql import SyncMysqlPool

logger = logging.getLogger("adn-monitor")

_ALIAS_TABLES = ("talkgroup_ids", "subscriber_ids", "peer_ids")

_CREATE_DDL: tuple[str, ...] = (
    """CREATE TABLE IF NOT EXISTS schema_migrations (
        id VARCHAR(64) PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS Clients(
        int_id INT UNIQUE PRIMARY KEY NOT NULL,
        dmr_id TINYBLOB NOT NULL,
        callsign VARCHAR(10) NOT NULL,
        host VARCHAR(15),
        options VARCHAR(300),
        opt_rcvd TINYINT(1) DEFAULT False NOT NULL,
        mode TINYINT(1) DEFAULT 4 NOT NULL,
        logged_in TINYINT(1) DEFAULT False NOT NULL,
        modified TINYINT(1) DEFAULT False NOT NULL,
        psswd BLOB(256),
        last_seen INT NOT NULL) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS talkgroup_ids (
        id INT PRIMARY KEY NOT NULL,
        callsign VARCHAR(255) NOT NULL) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS subscriber_ids (
        id INT PRIMARY KEY NOT NULL,
        callsign VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS peer_ids (
        id INT PRIMARY KEY NOT NULL,
        callsign VARCHAR(255) NOT NULL) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS last_heard (
        date_time DATETIME NOT NULL,
        qso_time DECIMAL(5,2),
        qso_type VARCHAR(20) NOT NULL,
        system VARCHAR(50) NOT NULL,
        tg_num INT NOT NULL,
        dmr_id INT PRIMARY KEY NOT NULL) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS lstheard_log (
        date_time DATETIME NOT NULL,
        qso_time DECIMAL(5,2),
        qso_type VARCHAR(20) NOT NULL,
        system VARCHAR(50) NOT NULL,
        tg_num INT NOT NULL,
        dmr_id INT NOT NULL) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS tg_count (
        date DATETIME NOT NULL,
        tg_num INT PRIMARY KEY NOT NULL,
        qso_count INT NOT NULL,
        qso_time DECIMAL(7,2) NOT NULL) DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS user_count (
        date DATETIME NOT NULL,
        tg_num INT NOT NULL,
        dmr_id INT NOT NULL,
        qso_time DECIMAL(7,2) NOT NULL,
        UNIQUE(tg_num, dmr_id)) DEFAULT CHARSET=utf8mb4""",
)


def _migration_applied(cursor: Any, migration_id: str) -> bool:
    cursor.execute("SELECT 1 FROM schema_migrations WHERE id = %s", (migration_id,))
    return cursor.fetchone() is not None


def _mark_migration(cursor: Any, migration_id: str) -> None:
    cursor.execute(
        "INSERT IGNORE INTO schema_migrations (id) VALUES (%s)",
        (migration_id,),
    )


def _column_exists(cursor: Any, table: str, column: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table, column),
    )
    return cursor.fetchone() is not None


def _table_exists(cursor: Any, table: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
        (table,),
    )
    return cursor.fetchone() is not None


def cleanup_staging_tables(cursor: Any) -> None:
    """Remove leftover ``*_import`` / ``*_old`` from interrupted alias bulk loads."""
    for base in _ALIAS_TABLES:
        for suffix in ("_import", "_old"):
            name = f"{base}{suffix}"
            if _table_exists(cursor, name):
                cursor.execute(f"DROP TABLE `{name}`")
                logger.info("(schema) dropped orphan staging table %s", name)


def apply_migrations(cursor: Any) -> None:
    """Incremental, idempotent migrations for existing production DBs."""
    if not _migration_applied(cursor, "001_clients_callsign"):
        if _table_exists(cursor, "Clients") and not _column_exists(cursor, "Clients", "callsign"):
            cursor.execute(
                "ALTER TABLE Clients ADD COLUMN callsign VARCHAR(10) "
                "DEFAULT 'NOCALL' NOT NULL AFTER dmr_id"
            )
        _mark_migration(cursor, "001_clients_callsign")

    if not _migration_applied(cursor, "002_clients_options_width"):
        if _table_exists(cursor, "Clients"):
            cursor.execute("ALTER TABLE Clients MODIFY COLUMN options VARCHAR(300)")
        _mark_migration(cursor, "002_clients_options_width")

    if not _migration_applied(cursor, "003_alias_pk_only"):
        _verify_alias_primary_keys(cursor)
        _mark_migration(cursor, "003_alias_pk_only")

    if not _migration_applied(cursor, "004_peer_dynamic_tgs"):
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS peer_dynamic_tgs (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                int_id INT NOT NULL,
                system_name VARCHAR(50) NOT NULL,
                slot TINYINT NOT NULL,
                tgid INT NOT NULL,
                single_mode TINYINT(1) NOT NULL,
                expires_at INT NULL,
                updated_at INT NOT NULL,
                UNIQUE KEY uq_peer_dynamic (int_id, system_name, slot, tgid),
                KEY idx_peer_system (int_id, system_name),
                KEY idx_expires (expires_at)
            ) DEFAULT CHARSET=utf8mb4"""
        )
        _mark_migration(cursor, "004_peer_dynamic_tgs")

    cleanup_staging_tables(cursor)


def _verify_alias_primary_keys(cursor: Any) -> None:
    """Alias tables should expose PK on ``id`` only (point lookups; no extra indexes)."""
    for table in _ALIAS_TABLES:
        if not _table_exists(cursor, table):
            continue
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = 'PRIMARY'",
            (table,),
        )
        row = cursor.fetchone()
        if not row or int(row[0]) < 1:
            logger.warning("(schema) %s has no PRIMARY KEY; run db_bootstrap --update", table)


def ensure_schema_on_cursor(cursor: Any) -> None:
    """Create missing tables + apply pending migrations (existing data preserved)."""
    for ddl in _CREATE_DDL:
        cursor.execute(ddl)
    apply_migrations(cursor)


def ensure_schema(pool: SyncMysqlPool) -> None:
    """Sync entry: safe on empty DB or legacy DB with data."""
    with pool.connection() as conn:
        cur = conn.cursor()
        ensure_schema_on_cursor(cur)
    logger.debug("(schema) ensure_schema completed")
