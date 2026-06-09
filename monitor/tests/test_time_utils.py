"""Dashboard calendar day (TIMEZONE-aware TG count)."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from adn_monitor.application.time_utils import (
    dashboard_calendar_date,
    format_tgcount_date,
)


def test_tgcount_date_uses_timezone_when_set():
    # 2024-06-03 23:30 UTC = 2024-06-03 19:30 America/Santiago (same calendar day)
    ts = datetime(2024, 6, 3, 23, 30, tzinfo=timezone.utc).timestamp()
    cfg = {"TIMEZONE": "America/Santiago"}
    assert format_tgcount_date(cfg, ts) == "2024-06-03"


def test_tgcount_date_rollover_in_operator_tz():
    # 2024-06-04 02:00 UTC = 2024-06-03 22:00 Chile — still June 3 locally
    ts = datetime(2024, 6, 4, 2, 0, tzinfo=timezone.utc).timestamp()
    cfg = {"TIMEZONE": "America/Santiago"}
    assert dashboard_calendar_date(cfg, ts).isoformat() == "2024-06-03"
    # Same instant is already June 4 in UTC
    assert dashboard_calendar_date(None, ts).isoformat() == "2024-06-04"


def test_tgcount_date_falls_back_to_utc_without_timezone():
    ts = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc).timestamp()
    assert format_tgcount_date({}, ts) == "2024-01-15"
    assert format_tgcount_date({"TIMEZONE": ""}, ts) == "2024-01-15"
