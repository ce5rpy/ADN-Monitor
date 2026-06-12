"""Tests for WebSocket CTABLE fingerprints and lastheard refresh hints."""

from adn_monitor.application import ws_ctable_views


def test_main_dashboard_fingerprint_ignores_timeout() -> None:
    ctable = {
        "MASTERS": {
            "SYSTEM": {
                "PEERS": {
                    "7301": {
                        2: {"TS": True, "TGID": "TG 52090", "TIMEOUT": 1000.0},
                    },
                },
            },
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    ctable2 = {
        "MASTERS": {
            "SYSTEM": {
                "PEERS": {
                    "7301": {
                        2: {"TS": True, "TGID": "TG 52090", "TIMEOUT": 2000.0},
                    },
                },
            },
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    fp1 = ws_ctable_views.main_dashboard_semantic_fingerprint([], ctable)
    fp2 = ws_ctable_views.main_dashboard_semantic_fingerprint([], ctable2)
    assert fp1 == fp2


def test_lastheard_db_refresh_needed() -> None:
    assert ws_ctable_views.lastheard_db_refresh_needed(
        {"call_type": "GROUP VOICE", "action": "START", "direction": "RX"}
    ) is False
    assert ws_ctable_views.lastheard_db_refresh_needed(
        {"call_type": "GROUP VOICE", "action": "END", "direction": "RX"}
    ) is True
    assert ws_ctable_views.lastheard_db_refresh_needed(
        {"call_type": "UNIT DATA HEADER", "action": "DATA", "direction": "RX"}
    ) is True
    assert ws_ctable_views.lastheard_db_refresh_needed(None) is False
