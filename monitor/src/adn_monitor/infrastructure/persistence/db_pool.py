# ADN Monitor - Dashboard and backend for ADN Systems.
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

logger = logging.getLogger("adn-monitor")


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
    """Ensure monitor schema (idempotent; safe if tables already exist)."""
    return (yield _ensure_schema_twisted(pool))


@inlineCallbacks
def updt_table(pool: adbapi.ConnectionPool) -> Result[None, RepositoryError]:
    """Apply pending migrations on an existing DB (same as --create, idempotent)."""
    return (yield _ensure_schema_twisted(pool))


@inlineCallbacks
def _ensure_schema_twisted(pool: adbapi.ConnectionPool) -> Result[None, RepositoryError]:
    from .schema import ensure_schema_on_cursor

    try:
        def run(txn: Any) -> None:
            ensure_schema_on_cursor(txn)

        yield pool.runInteraction(run)
        logger.info("Schema ensure completed.")
        returnValue(Success(None))
    except Exception as err:
        logger.error("ensure_schema: %s", err)
        returnValue(Failure(RepositoryError(str(err))))
