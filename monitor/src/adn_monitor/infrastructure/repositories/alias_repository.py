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
"""Alias repository: in-memory cache + DB lookup by ID (Twisted Deferreds)."""

from __future__ import annotations

import logging
from typing import Any

from twisted.enterprise import adbapi

from ...application.ports import AliasRepository
from ...domain.entities import PeerAlias, SubscriberAlias, TalkgroupAlias

logger = logging.getLogger("adn-mon")

# Cap in-memory caches to avoid unbounded growth
MAX_SUBSCRIBER_CACHE = 100_000
MAX_TALKGROUP_CACHE = 20_000
MAX_NOT_IN_DB = 50_000
EVICT_FRACTION = 0.2  # When at cap, evict this fraction of oldest entries


class MoniDBAliasRepository(AliasRepository):
    """Alias repository backed by in-memory cache and DB pool (Twisted)."""

    def __init__(self, pool: adbapi.ConnectionPool) -> None:
        self._pool = pool
        self._subscriber_ids: dict[int, SubscriberAlias] = {}
        self._peer_ids: dict[int, PeerAlias] = {}
        self._talkgroup_ids: dict[int, TalkgroupAlias] = {}
        self._not_in_db: list[int] = []
        self._act_query: list[int] = []

    def _evict_subscriber_cache_if_needed(self) -> None:
        if len(self._subscriber_ids) < MAX_SUBSCRIBER_CACHE:
            return
        n = max(1, int(len(self._subscriber_ids) * EVICT_FRACTION))
        keys = list(self._subscriber_ids.keys())[:n]
        for k in keys:
            del self._subscriber_ids[k]
        logger.info("(alias_repository) evicted %d subscriber cache entries (cap=%d)", n, MAX_SUBSCRIBER_CACHE)

    def _evict_talkgroup_cache_if_needed(self) -> None:
        if len(self._talkgroup_ids) < MAX_TALKGROUP_CACHE:
            return
        n = max(1, int(len(self._talkgroup_ids) * EVICT_FRACTION))
        keys = list(self._talkgroup_ids.keys())[:n]
        for k in keys:
            del self._talkgroup_ids[k]
        logger.info("(alias_repository) evicted %d talkgroup cache entries (cap=%d)", n, MAX_TALKGROUP_CACHE)

    def _cap_not_in_db(self) -> None:
        if len(self._not_in_db) <= MAX_NOT_IN_DB:
            return
        self._not_in_db = self._not_in_db[-MAX_NOT_IN_DB:]
        logger.info("(alias_repository) trimmed _not_in_db to %d entries", MAX_NOT_IN_DB)

    def get_subscriber(self, dmr_id: int) -> SubscriberAlias | None:
        return self._subscriber_ids.get(dmr_id)

    def get_peer(self, peer_id: int) -> PeerAlias | None:
        return self._peer_ids.get(peer_id)

    def get_talkgroup(self, tg_id: int) -> TalkgroupAlias | None:
        return self._talkgroup_ids.get(tg_id)

    def _query_row_by_id(self, row_id: int, table: str):
        """Return Deferred firing first row or None. Table: subscriber_ids | talkgroup_ids."""
        stm = "SELECT * FROM subscriber_ids WHERE id = %s" if table == "subscriber_ids" else "SELECT * FROM talkgroup_ids WHERE id = %s"
        return self._pool.runQuery(stm, (row_id,)).addCallback(lambda rows: rows[0] if rows else None)

    def ensure_subscriber_in_cache(self, dmr_id: int) -> None:
        if dmr_id in self._subscriber_ids or dmr_id in self._not_in_db or dmr_id in self._act_query:
            return
        self._act_query.append(dmr_id)
        d = self._query_row_by_id(dmr_id, "subscriber_ids")
        d.addCallback(self._on_subscriber_loaded, dmr_id)
        d.addErrback(lambda f: logger.error("alias_repository subscriber: %s", f.getTraceback()))
        d.addBoth(self._clear_act_query, dmr_id)

    def _on_subscriber_loaded(self, result: Any, dmr_id: int) -> None:
        if result:
            self._subscriber_ids[result[0]] = SubscriberAlias(
                id=result[0], callsign=result[1], name=result[2]
            )
            self._evict_subscriber_cache_if_needed()
        else:
            self._not_in_db.append(dmr_id)
            self._cap_not_in_db()

    def ensure_talkgroup_in_cache(self, tg_id: int) -> None:
        if tg_id in self._talkgroup_ids or tg_id in self._not_in_db or tg_id in self._act_query:
            return
        self._act_query.append(tg_id)
        d = self._query_row_by_id(tg_id, "talkgroup_ids")
        d.addCallback(self._on_talkgroup_loaded, tg_id)
        d.addErrback(lambda f: logger.error("alias_repository talkgroup: %s", f.getTraceback()))
        d.addBoth(self._clear_act_query, tg_id)

    def _on_talkgroup_loaded(self, result: Any, tg_id: int) -> None:
        if result:
            self._talkgroup_ids[result[0]] = TalkgroupAlias(id=result[0], name=result[1])
            self._evict_talkgroup_cache_if_needed()
        else:
            self._not_in_db.append(tg_id)
            self._cap_not_in_db()

    def _clear_act_query(self, _: Any, id_val: int) -> None:
        if id_val in self._act_query:
            self._act_query.remove(id_val)

    def populate_subscriber(self, dmr_id: int, callsign: str, name: str) -> None:
        self._subscriber_ids[dmr_id] = SubscriberAlias(id=dmr_id, callsign=callsign, name=name)

    def populate_talkgroup(self, tg_id: int, name: str) -> None:
        self._talkgroup_ids[tg_id] = TalkgroupAlias(id=tg_id, name=name)

    def populate_peer(self, peer_id: int, callsign: str) -> None:
        self._peer_ids[peer_id] = PeerAlias(id=peer_id, callsign=callsign)
