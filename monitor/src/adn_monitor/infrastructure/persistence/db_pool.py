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
"""
Database connection pool and schema bootstrap.

Twisted adbapi pool; create_tables/updt_table for CLI bootstrap.
Compatible schema with existing ADN/FDMR monitor DBs (schema design from FDMR-Monitor2).
Public API uses Result (Success/Failure) for test_db, create_tables, updt_table.
"""

from __future__ import annotations

import logging
from typing import Any

from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue

from ...domain import Failure, RepositoryError, Result, Success

logger = logging.getLogger("adn-mon")


def sec_time(_time: int | float) -> str:
    """Seconds to a short human-readable duration (e.g. "2m 30s")."""
    t = int(_time)
    seconds = t % 60
    minutes = (t // 60) % 60
    hours = (t // 3600) % 24
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def create_pool(
    host: str,
    user: str,
    psswd: str,
    db_name: str,
    port: int | str,
) -> adbapi.ConnectionPool:
    """Create Twisted adbapi MySQL connection pool."""
    return adbapi.ConnectionPool(
        "MySQLdb",
        host=host,
        user=user,
        passwd=psswd,
        db=db_name,
        port=int(port) if isinstance(port, str) else port,
        charset="utf8mb4",
    )


@inlineCallbacks
def test_db(pool: adbapi.ConnectionPool) -> Result[None, RepositoryError]:
    """Verify DB connectivity. Returns Success(None) or Failure(RepositoryError)."""
    try:
        res = yield pool.runQuery("SELECT 1")
        if res:
            logger.info("Database connection test: OK")
        returnValue(Success(None))
    except Exception as err:
        logger.error("Database connection error: %s", err)
        returnValue(Failure(RepositoryError(str(err))))


@inlineCallbacks
def create_tables(pool: adbapi.ConnectionPool) -> Result[None, RepositoryError]:
    """Create monitor tables if they do not exist (bootstrap). Returns Success(None) or Failure(RepositoryError)."""
    try:
        def run(txn: Any) -> None:
            txn.execute(
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
                    last_seen INT NOT NULL) DEFAULT CHARSET=utf8mb4"""
            )
            txn.execute(
                """CREATE TABLE IF NOT EXISTS talkgroup_ids (
                    id INT PRIMARY KEY UNIQUE NOT NULL,
                    callsign VARCHAR(255) NOT NULL) DEFAULT CHARSET=utf8mb4"""
            )
            txn.execute(
                """CREATE TABLE IF NOT EXISTS subscriber_ids (
                    id INT PRIMARY KEY UNIQUE NOT NULL,
                    callsign VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL) DEFAULT CHARSET=utf8mb4"""
            )
            txn.execute(
                """CREATE TABLE IF NOT EXISTS peer_ids (
                    id INT PRIMARY KEY UNIQUE NOT NULL,
                    callsign VARCHAR(255) NOT NULL) DEFAULT CHARSET=utf8mb4"""
            )
            txn.execute(
                """CREATE TABLE IF NOT EXISTS last_heard (
                    date_time DATETIME NOT NULL,
                    qso_time DECIMAL(5,2),
                    qso_type VARCHAR(20) NOT NULL,
                    system VARCHAR(50) NOT NULL,
                    tg_num INT NOT NULL,
                    dmr_id INT PRIMARY KEY UNIQUE NOT NULL) DEFAULT CHARSET=utf8mb4"""
            )
            txn.execute(
                """CREATE TABLE IF NOT EXISTS lstheard_log (
                    date_time DATETIME NOT NULL,
                    qso_time DECIMAL(5,2),
                    qso_type VARCHAR(20) NOT NULL,
                    system VARCHAR(50) NOT NULL,
                    tg_num INT NOT NULL,
                    dmr_id INT NOT NULL) DEFAULT CHARSET=utf8mb4"""
            )
            txn.execute(
                """CREATE TABLE IF NOT EXISTS tg_count (
                    date DATETIME NOT NULL,
                    tg_num INT PRIMARY KEY NOT NULL,
                    qso_count INT NOT NULL,
                    qso_time DECIMAL(7,2) NOT NULL) DEFAULT CHARSET=utf8mb4"""
            )
            txn.execute(
                """CREATE TABLE IF NOT EXISTS user_count (
                    date DATETIME NOT NULL,
                    tg_num INT NOT NULL,
                    dmr_id INT NOT NULL,
                    qso_time DECIMAL(7,2) NOT NULL,
                    UNIQUE(tg_num, dmr_id)) DEFAULT CHARSET=utf8mb4"""
            )

        yield pool.runInteraction(run)
        logger.info("Tables created successfully.")
        returnValue(Success(None))
    except Exception as err:
        logger.error("create_tables: %s", err)
        returnValue(Failure(RepositoryError(str(err))))


@inlineCallbacks
def updt_table(pool: adbapi.ConnectionPool) -> Result[None, RepositoryError]:
    """Apply schema migrations (e.g. add column if missing). Returns Success(None) or Failure(RepositoryError)."""
    try:
        def run(txn: Any) -> None:
            txn.execute(
                """ALTER TABLE Clients ADD COLUMN IF NOT EXISTS callsign VARCHAR(10)
                DEFAULT 'NOCALL' NOT NULL AFTER dmr_id"""
            )
            txn.execute("ALTER TABLE Clients MODIFY COLUMN options VARCHAR(300)")

        yield pool.runInteraction(run)
        logger.info("Tables updated successfully.")
        returnValue(Success(None))
    except Exception as err:
        logger.error("updt_table: %s", err)
        returnValue(Failure(RepositoryError(str(err))))
