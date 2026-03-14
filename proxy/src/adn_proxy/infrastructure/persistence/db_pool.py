# Hotspot Proxy for ADN DMR Peer Server.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Database connection pool. Twisted adbapi; test_db for connectivity."""

from __future__ import annotations

import logging
from typing import Any

from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue

from ...domain import Failure, RepositoryError, Result, Success

logger = logging.getLogger("adn-proxy")


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
