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

"""Proxy self-service repository: Clients table (options, password, log in/out, last_seen)."""

from __future__ import annotations

import logging
from typing import Any

from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue

from ...domain import ProxyDbPort

logger = logging.getLogger("adn-proxy")


class ProxyDbRepository(ProxyDbPort):
    """ProxyDbPort implemented with Twisted adbapi pool (Clients table)."""

    def __init__(self, pool: adbapi.ConnectionPool) -> None:
        self._pool = pool

    def test_db(self) -> Any:
        from .db_pool import test_db
        return test_db(self._pool)

    def ins_conf(
        self,
        int_id: int,
        peer_id_bytes: bytes,
        callsign: str,
        host: str,
        mode: str,
    ) -> None:
        """Insert or update client config (RPTC configure)."""
        self._pool.runOperation(
            """INSERT INTO Clients (int_id, dmr_id, callsign, host, mode, logged_in, last_seen)
               VALUES (%s, %s, %s, %s, %s, 1, UNIX_TIMESTAMP())
               ON DUPLICATE KEY UPDATE callsign=%s, host=%s, mode=%s, logged_in=1, last_seen=UNIX_TIMESTAMP()""",
            (int_id, peer_id_bytes, callsign, host, mode, callsign, host, mode),
        ).addErrback(lambda f: logger.error("ins_conf: %s", f.getTraceback()))

    def updt_tbl(
        self,
        action: str,
        peer_id_bytes: bytes,
        *,
        psswd: str | None = None,
    ) -> None:
        """Update Clients: log_out (logged_in=0), psswd, opt_rcvd, rst_mod (modified=0)."""
        if action == "log_out":
            self._pool.runOperation(
                "UPDATE Clients SET logged_in=0, last_seen=UNIX_TIMESTAMP() WHERE dmr_id=%s",
                (peer_id_bytes,),
            ).addErrback(lambda f: logger.error("updt_tbl log_out: %s", f.getTraceback()))
        elif action == "psswd" and psswd is not None:
            blob = psswd.encode("utf-8") if isinstance(psswd, str) else psswd
            self._pool.runOperation(
                "UPDATE Clients SET psswd=%s WHERE dmr_id=%s",
                (blob, peer_id_bytes),
            ).addErrback(lambda f: logger.error("updt_tbl psswd: %s", f.getTraceback()))
        elif action == "opt_rcvd":
            self._pool.runOperation(
                "UPDATE Clients SET opt_rcvd=1 WHERE dmr_id=%s",
                (peer_id_bytes,),
            ).addErrback(lambda f: logger.error("updt_tbl opt_rcvd: %s", f.getTraceback()))
        elif action == "rst_mod":
            self._pool.runOperation(
                "UPDATE Clients SET modified=0 WHERE dmr_id=%s",
                (peer_id_bytes,),
            ).addErrback(lambda f: logger.error("updt_tbl rst_mod: %s", f.getTraceback()))

    @inlineCallbacks
    def slct_opt(self, peer_id_bytes: bytes) -> Any:
        """Select options for peer. Returns Deferred firing with ((options_str,),) or empty."""
        try:
            rows = yield self._pool.runQuery(
                "SELECT options FROM Clients WHERE dmr_id=%s AND options IS NOT NULL AND options != ''",
                (peer_id_bytes,),
            )
            returnValue(rows)
        except Exception as err:
            logger.error("slct_opt: %s", err)
            returnValue([])

    @inlineCallbacks
    def slct_db(self) -> Any:
        """Select (dmr_id, options) for peers with modified=1 and options set."""
        try:
            rows = yield self._pool.runQuery(
                "SELECT dmr_id, options FROM Clients WHERE modified=1 AND logged_in=1 AND options IS NOT NULL AND options != ''"
            )
            returnValue(rows or [])
        except Exception as err:
            logger.error("slct_db: %s", err)
            returnValue([])

    def updt_lstseen(self, dmrid_list: list[tuple[bytes, ...]]) -> None:
        """Update last_seen for given peer IDs."""
        if not dmrid_list:
            return
        for item in dmrid_list:
            peer_id = item[0]
            self._pool.runOperation(
                "UPDATE Clients SET last_seen=UNIX_TIMESTAMP() WHERE dmr_id=%s",
                (peer_id,),
            ).addErrback(lambda f, pid=peer_id: logger.error("updt_lstseen: %s for %s", f.getTraceback(), pid))

    @inlineCallbacks
    def clean_tbl(self) -> None:
        """Periodic cleanup: optional (e.g. mark old sessions)."""
        yield self._pool.runOperation(
            "UPDATE Clients SET logged_in=0 WHERE logged_in=1 AND last_seen < UNIX_TIMESTAMP() - 86400"
        ).addErrback(lambda f: logger.error("clean_tbl: %s", f.getTraceback()))
