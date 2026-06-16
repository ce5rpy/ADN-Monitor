"""DB maintenance loops."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from adn_monitor.application.db_maintenance import maybe_clean_tgcount, run_cleaning_loop


def test_maybe_clean_tgcount_on_day_change():
    repo = MagicMock()
    cfg = {"TIMEZONE": "UTC", "TGC_INC": True}
    d1 = maybe_clean_tgcount(repo, cfg, None)
    assert isinstance(d1, date)
    repo.clean_tgcount.assert_called_once()
    repo.reset_mock()
    maybe_clean_tgcount(repo, cfg, d1)
    repo.clean_tgcount.assert_not_called()


def test_run_cleaning_loop_trims_last_heard():
    lh = MagicMock()
    tg = MagicMock()
    cfg = {"LH_ROWS": 15, "TGC_INC": False}
    run_cleaning_loop(cfg, lh, tg, lastheard_log_rows=50)
    lh.clean_table.assert_any_call("last_heard", 15)
    lh.clean_table.assert_any_call("lstheard_log", 50)
    tg.clean_tgcount.assert_not_called()
