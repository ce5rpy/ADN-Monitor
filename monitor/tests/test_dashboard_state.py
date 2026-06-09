"""dashboard_state wire — monitor consumer tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from adn_monitor.application.monitor_controller import (
    MonitorState,
    process_message,
    process_report_json,
)
from adn_monitor.application.report_mapper import dashboard_state_to_config
from adn_monitor.domain import is_fail
from adn_monitor.domain.value_objects import Opcode, ServerMode
from adn_monitor.infrastructure.report_payload_decoder import PickleJsonReportPayloadDecoder


def _deps():
    alias_svc = MagicMock()
    alias_svc.alias_short.return_value = "SUB"
    alias_svc.alias_tgid.return_value = "TG"
    return {
        "alias_svc": alias_svc,
        "alias_repo": MagicMock(),
        "lastheard_repo": MagicMock(),
        "tgcount_repo": MagicMock(),
        "broadcast": None,
        "config_global": {"LH_INC": False, "TGC_INC": False, "BRDG_INC": True, "HB_INC": True},
    }


def _sample_dashboard_state() -> dict:
    return {
        "type": "dashboard_state",
        "ts": 1717555200.0,
        "server_id": "7302",
        "ctable": {
            "MASTERS": {
                "ECHO": {
                    "mode": "MASTER",
                    "ip": "10.0.0.2",
                    "port": 62030,
                    "peers": {
                        2: {
                            "id": 2,
                            "connected": True,
                            "ip": "10.0.0.50",
                            "port": 62031,
                            "connected_at": 1700000000,
                            "ts1_static": ["91", "92"],
                            "ts2_static": ["730"],
                        }
                    },
                }
            },
            "PEERS": {
                "XLX-730": {
                    "mode": "XLXPEER",
                    "connected": True,
                    "connected_at": 1700000001,
                    "callsign": "XLX730",
                    "radio_id": 730,
                }
            },
            "OPENBRIDGES": {
                "OBP-CL": {
                    "mode": "OPENBRIDGE",
                    "network_id": 73010,
                    "ip": "44.31.61.68",
                    "port": 62999,
                    "enhanced_obp": True,
                    "streams": {},
                }
            },
        },
    }


def test_dashboard_state_to_config_maps_linked_systems():
    cfg = dashboard_state_to_config(_sample_dashboard_state())
    assert "ECHO" in cfg
    assert len(cfg["ECHO"]["PEERS"]) == 1
    assert "XLX-730" in cfg
    assert cfg["XLX-730"]["XLXSTATS"]["CONNECTION"] == "YES"
    assert "OBP-CL" in cfg
    assert cfg["OBP-CL"]["ENHANCED_OBP"] is True


def test_process_state_snd_applies_ctable():
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.report_protocol = 2
    deps = _deps()
    deps["report_decoder"] = PickleJsonReportPayloadDecoder()
    frame = Opcode.STATE_SND + json.dumps(_sample_dashboard_state(), separators=(",", ":")).encode()
    result = process_message(frame, state, **deps)
    assert not is_fail(result)
    assert state.slim_wire is True
    assert "ECHO" in state.CTABLE["MASTERS"]
    assert 2 in state.CTABLE["MASTERS"]["ECHO"]["PEERS"]
    assert "XLX-730" in state.CTABLE["PEERS"]
    assert "OBP-CL" in state.CTABLE["OPENBRIDGES"]


def test_process_report_json_dashboard_state():
    state = MonitorState()
    deps = _deps()
    result = process_report_json(_sample_dashboard_state(), state, **deps)
    assert not is_fail(result)
    assert state.slim_wire is True
    assert "ECHO" in state.CONFIG


def test_dashboard_state_update_adds_new_masters_after_first_snapshot():
    """Slim wire applies multiple snapshots; update must create new MASTER rows (proxy SYSTEM-N)."""
    state = MonitorState()
    deps = _deps()
    echo_only = {
        "type": "dashboard_state",
        "ts": 1.0,
        "ctable": {
            "MASTERS": {
                "ECHO": {
                    "mode": "MASTER",
                    "peers": {9990: {"id": 9990, "connected": True, "connected_at": 1000}},
                }
            },
            "PEERS": {},
            "OPENBRIDGES": {},
        },
    }
    process_report_json(echo_only, state, **deps)
    assert list(state.CTABLE["MASTERS"]) == ["ECHO"]

    full = {
        "type": "dashboard_state",
        "ts": 2.0,
        "ctable": {
            "MASTERS": {
                "ECHO": echo_only["ctable"]["MASTERS"]["ECHO"],
                "D-APRS": {
                    "mode": "MASTER",
                    "peers": {730999: {"id": 730999, "connected": True, "connected_at": 1001}},
                },
                "SYSTEM-0": {
                    "mode": "MASTER",
                    "peers": {7300444: {"id": 7300444, "connected": True, "connected_at": 1002}},
                },
            },
            "PEERS": {},
            "OPENBRIDGES": {"OBP-CL": {"mode": "OPENBRIDGE", "streams": {}}},
        },
    }
    process_report_json(full, state, **deps)
    assert set(state.CTABLE["MASTERS"]) == {"ECHO", "D-APRS", "SYSTEM-0"}
    assert state.CTABLE["MASTERS"]["D-APRS"]["PEERS"][730999]["CONNECTION"] == "YES"
    assert state.CTABLE["MASTERS"]["SYSTEM-0"]["PEERS"][7300444]["CONNECTION"] == "YES"


def test_dashboard_state_reapply_preserves_voice_timeslots_and_ob_streams():
    """Slim snapshots must sync topology without wiping active QSO / openbridge streams."""
    state = MonitorState()
    state.server_mode = ServerMode.V2
    deps = _deps()
    deps["alias_svc"].alias_call.return_value = "CE5RPY"
    snap = _sample_dashboard_state()
    process_report_json(snap, state, **deps)

    voice = {
        "type": "voice_event",
        "call_family": "GROUP",
        "phase": "START",
        "direction": "RX",
        "system": "OBP-CL",
        "stream_id": 999001,
        "peer_id": 73010,
        "src_id": 3194716,
        "slot": 1,
        "dst_id": 73458,
    }
    process_report_json(voice, state, **deps)
    assert state.CTABLE["OPENBRIDGES"]["OBP-CL"]["STREAMS"]

    process_report_json({**snap, "ts": snap["ts"] + 1.0}, state, **deps)
    assert state.CTABLE["OPENBRIDGES"]["OBP-CL"]["STREAMS"]
    peer_ts = state.CTABLE["MASTERS"]["ECHO"]["PEERS"][2][1]
    voice_master = {
        **voice,
        "system": "ECHO",
        "stream_id": 888001,
        "peer_id": 2,
        "src_id": 7300444,
        "dst_id": 91,
    }
    process_report_json(voice_master, state, **deps)
    assert state.CTABLE["MASTERS"]["ECHO"]["PEERS"][2][1]["TS"] is True
    process_report_json({**snap, "ts": snap["ts"] + 2.0}, state, **deps)
    assert state.CTABLE["MASTERS"]["ECHO"]["PEERS"][2][1]["TS"] is True
    assert state.CTABLE["OPENBRIDGES"]["OBP-CL"]["STREAMS"]


def test_slim_wire_ignores_topology_after_dashboard_state():
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.report_protocol = 2
    state.slim_wire = True
    deps = _deps()
    deps["report_decoder"] = PickleJsonReportPayloadDecoder()
    topo = Opcode.TOPOLOGY_SND + b'{"type":"topology","seq":99,"systems":[]}'
    result = process_message(topo, state, **deps)
    assert not is_fail(result)
    assert state.topology_seq == 0
