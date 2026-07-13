"""Alias in-memory cache invalidation and STALE_HOURS TTL."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

from adn_monitor.domain.entities import SubscriberAlias
from adn_monitor.infrastructure.repositories.alias_repository import MoniDBAliasRepository


def test_invalidate_cache_clears_table_entries() -> None:
    repo = MoniDBAliasRepository(MagicMock(), stale_seconds=3600)
    repo._subscriber_ids[1] = SubscriberAlias(id=1, callsign="XX1", name="A")
    repo._subscriber_loaded_at[1] = time.monotonic()
    repo._not_in_db.append(99)

    repo.invalidate_cache("subscriber_ids")

    assert repo._subscriber_ids == {}
    assert repo._not_in_db == []


def test_stale_entry_triggers_reload() -> None:
    pool = MagicMock()
    deferred = MagicMock()
    pool.runQuery.return_value = deferred
    repo = MoniDBAliasRepository(pool, stale_seconds=0.01)
    repo._subscriber_ids[42] = SubscriberAlias(id=42, callsign="OLD", name="X")
    repo._subscriber_loaded_at[42] = time.monotonic() - 1.0

    repo.ensure_subscriber_in_cache(42)

    assert 42 not in repo._subscriber_ids
    assert 42 in repo._act_query
    pool.runQuery.assert_called_once()
    deferred.addCallback.assert_called_once()


def test_fresh_entry_skips_reload() -> None:
    repo = MoniDBAliasRepository(MagicMock(), stale_seconds=3600)
    repo._subscriber_ids[7] = SubscriberAlias(id=7, callsign="OK", name="Y")
    repo._touch(7, repo._subscriber_loaded_at)
    repo._pool = MagicMock()

    repo.ensure_subscriber_in_cache(7)

    repo._pool.runQuery.assert_not_called()


def test_resolve_subscriber_sync_loads_from_db() -> None:
    pool = MagicMock()
    sync_pool = MagicMock()
    conn = MagicMock()
    cur = MagicMock()
    sync_pool.connection.return_value.__enter__ = MagicMock(return_value=conn)
    sync_pool.connection.return_value.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cur
    cur.fetchone.return_value = (42, "CE5RPY", "Rod")

    repo = MoniDBAliasRepository(pool, sync_pool=sync_pool)
    repo.resolve_subscriber_sync(42)

    alias = repo.get_subscriber(42)
    assert alias is not None
    assert alias.callsign == "CE5RPY"
    pool.runQuery.assert_not_called()


def test_resolve_subscriber_sync_uses_cache_when_fresh() -> None:
    sync_pool = MagicMock()
    repo = MoniDBAliasRepository(MagicMock(), stale_seconds=3600, sync_pool=sync_pool)
    repo._subscriber_ids[7] = SubscriberAlias(id=7, callsign="OK", name="Y")
    repo._touch(7, repo._subscriber_loaded_at)

    repo.resolve_subscriber_sync(7)

    sync_pool.connection.assert_not_called()
