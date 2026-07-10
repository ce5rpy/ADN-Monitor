"""Migration 006 indexes for peer_dynamic_tgs.need_reload."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.infrastructure.persistence.schema import apply_migrations


def test_migration_006_adds_need_reload_column_and_index() -> None:
    cur = MagicMock()
    seq = iter(
        [
            (1,),  # 001 applied
            (1,),  # 002 applied
            (1,),  # 003 applied
            (1,),  # 004 applied
            (1,),  # 005 applied
            None,  # 006 not applied
            (1,),  # peer_dynamic_tgs exists
            None,  # need_reload column missing
            None,  # idx_need_reload_peer missing
        ]
        + [None] * 10
    )
    cur.fetchone.side_effect = lambda: next(seq, None)
    apply_migrations(cur)
    executed = [c[0][0] for c in cur.execute.call_args_list]
    alters = [sql for sql in executed if sql.startswith("ALTER TABLE peer_dynamic_tgs")]
    assert len(alters) == 2
    assert any("ADD COLUMN need_reload" in sql for sql in alters)
    assert any("idx_need_reload_peer (need_reload, int_id, system_name)" in sql for sql in alters)
