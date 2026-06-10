"""peer_options_merge application tests."""

from __future__ import annotations

from adn_monitor.application.monitor_controller import MonitorState
from adn_monitor.application.peer_options_merge import apply_peer_options_rows


def test_apply_peer_options_caches_db_without_overwriting_ctable():
    state = MonitorState()
    state.CTABLE = {
        "MASTERS": {
            "SYS": {
                "PEERS": {
                    1001: {"TS1_STATIC": [], "TS2_STATIC": []},
                }
            }
        }
    }
    rows = [(b"\x00\x00\x03\xe9", "TS1=1,2;TS2=9;")]  # 1001 big-endian
    assert apply_peer_options_rows(state, rows) is False
    peer = state.CTABLE["MASTERS"]["SYS"]["PEERS"][1001]
    assert peer["TS1_STATIC"] == []
    assert peer["TS2_STATIC"] == []
    assert state.PEER_OPTIONS[1001]["TS2_STATIC"] == ["9"]
