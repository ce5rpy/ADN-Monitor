"""Schema ensure idempotency tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.infrastructure.persistence.schema import (
    apply_migrations,
    cleanup_staging_tables,
    ensure_schema_on_cursor,
)


def test_ensure_runs_create_if_not_exists():
    cur = MagicMock()
    cur.fetchone.return_value = (1,)  # migration already applied / table exists
    ensure_schema_on_cursor(cur)
    executed = [c[0][0] for c in cur.execute.call_args_list]
    assert any("CREATE TABLE IF NOT EXISTS Clients" in s for s in executed)
    assert any("schema_migrations" in s for s in executed)


def test_migration_adds_callsign_only_when_missing():
    cur = MagicMock()
    seq = iter(
        [
            None,  # 001 not applied
            (1,),  # Clients exists
            None,  # callsign column missing
            None,  # 002 not applied
            (1,),  # Clients exists
        ]
        + [None] * 20
    )
    cur.fetchone.side_effect = lambda: next(seq, None)
    apply_migrations(cur)
    alters = [c[0][0] for c in cur.execute.call_args_list if "ADD COLUMN callsign" in c[0][0]]
    assert len(alters) == 1


def test_cleanup_drops_staging():
    cur = MagicMock()
    cur.fetchone.side_effect = [(1,), None, None, None, None, None, None, None]
    cleanup_staging_tables(cur)
    drops = [c[0][0] for c in cur.execute.call_args_list if "DROP TABLE" in c[0][0]]
    assert any("talkgroup_ids_import" in d for d in drops)
