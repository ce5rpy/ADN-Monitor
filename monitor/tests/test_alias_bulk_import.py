"""MySQL bulk alias import unit tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from adn_monitor.infrastructure.persistence.alias_bulk_import import (
    MERGE_BATCH_SIZE,
    STAGING_BATCH_SIZE,
    _executemany_batches,
    merge_alias_table,
    replace_alias_table,
)


def _make_rows(n: int) -> list[tuple]:
    return [(i, f"TG{i}") for i in range(n)]


def test_executemany_batches_commit_each():
    cur = MagicMock()
    conn = MagicMock()
    cur.rowcount = 0
    rows = _make_rows(5)
    n = _executemany_batches(cur, conn, "INSERT ...", rows, 2, commit_each=True)
    assert n == 5
    assert conn.commit.call_count == 3


def test_merge_uses_small_batches():
    pool = MagicMock()
    conn = MagicMock()
    cur = MagicMock()
    pool.connect.return_value = conn
    conn.cursor.return_value = cur
    cur.fetchone.return_value = (1,)
    cur.rowcount = MERGE_BATCH_SIZE
    rows = _make_rows(MERGE_BATCH_SIZE + 50)
    with patch(
        "adn_monitor.infrastructure.persistence.alias_bulk_import._executemany_batches",
        return_value=len(rows),
    ) as batched:
        merge_alias_table(pool, "talkgroup_ids", rows)
    batched.assert_called_once()
    assert batched.call_args.kwargs.get("batch_size") == MERGE_BATCH_SIZE or batched.call_args[0][4] == MERGE_BATCH_SIZE


def test_replace_loads_staging_then_swaps():
    pool = MagicMock()
    conn = MagicMock()
    cur = MagicMock()
    pool.connect.return_value = conn
    conn.cursor.return_value = cur
    cur.fetchone.return_value = (1,)
    rows = _make_rows(3)
    with (
        patch(
            "adn_monitor.infrastructure.persistence.alias_bulk_import._load_staging",
            return_value=3,
        ) as load,
        patch("adn_monitor.infrastructure.persistence.alias_bulk_import._swap_staging") as swap,
    ):
        n = replace_alias_table(pool, "talkgroup_ids", rows)
    assert n == 3
    load.assert_called_once()
    swap.assert_called_once()
