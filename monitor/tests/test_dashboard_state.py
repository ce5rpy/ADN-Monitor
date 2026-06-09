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
