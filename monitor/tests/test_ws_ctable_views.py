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


def test_opb_semantic_fingerprint_includes_connected() -> None:
    ctable_online = {
        "OPENBRIDGES": {
            "OBP-CL": {
                "CONNECTED": True,
                "STREAMS": {"1": ["RX", "CE5RPY", "730", 1000.0]},
            },
        },
    }
    ctable_offline = {
        "OPENBRIDGES": {
            "OBP-CL": {
                "CONNECTED": False,
                "STREAMS": {"1": ["RX", "CE5RPY", "730", 1000.0]},
            },
        },
    }
    fp_online = ws_ctable_views.opb_semantic_fingerprint(ctable_online, False)
    fp_offline = ws_ctable_views.opb_semantic_fingerprint(ctable_offline, False)
    assert fp_online != fp_offline


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
