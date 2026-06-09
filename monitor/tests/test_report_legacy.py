"""Legacy and v1-HELLO report wire (pickle + CSV)."""

from __future__ import annotations

import json
import pickle
from unittest.mock import MagicMock

from adn_monitor.application.monitor_controller import MonitorState, process_message
from adn_monitor.domain import is_fail
from adn_monitor.domain.value_objects import Opcode, ServerMode
from adn_monitor.infrastructure.report_payload_decoder import PickleJsonReportPayloadDecoder


def _pickle_config(systems: dict) -> bytes:
    return Opcode.CONFIG_SND + pickle.dumps(systems, protocol=2)


def _pickle_bridges(bridges: dict) -> bytes:
    return Opcode.BRIDGE_SND + pickle.dumps(bridges, protocol=2)


def _brdg_event_csv() -> bytes:
    # Minimal GROUP VOICE START RX fields (see monitor_controller._handle_brdg_event_parts)
    return (
        Opcode.BRDG_EVENT
        + b"GROUP VOICE,START,RX,MASTER-A,1001,3120001,2,52090,0.0"
    )


def test_legacy_pickle_config_and_bridge():
    state = MonitorState()
    state.server_mode = ServerMode.LEGACY
    state.server_mode_confirmed = True
    deps = {
        "alias_svc": MagicMock(),
        "alias_repo": MagicMock(),
        "lastheard_repo": MagicMock(),
        "tgcount_repo": MagicMock(),
        "broadcast": None,
        "config_global": {
            "LH_INC": False,
            "TGC_INC": False,
            "BRDG_INC": True,
            "HB_INC": True,
            "OPB_FILTER": [],
        },
        "report_decoder": PickleJsonReportPayloadDecoder(),
    }
    deps["alias_svc"].alias_short.return_value = "SUB"
    deps["alias_svc"].alias_tgid.return_value = "TG"

    systems = {
        "MASTER-A": {
            "MODE": "MASTER",
            "ENABLED": True,
            "PEERS": {},
        }
    }
    result = process_message(_pickle_config(systems), state, **deps)
    assert not is_fail(result)
    assert "MASTER-A" in state.CONFIG

    bridges = {
        "52090": [
            {
                "SYSTEM": "MASTER-A",
                "ACTIVE": True,
                "TS": 2,
                "TGID": 52090,
            }
        ]
    }
    result = process_message(_pickle_bridges(bridges), state, **deps)
    assert not is_fail(result)
    assert state.BRIDGES


def _v1_hello_frame() -> bytes:
    return Opcode.HELLO + json.dumps(
        {
            "server": "adn-server",
            "version": "1.0.0",
            "protocol": 1,
            "features": [],
        },
        separators=(",", ":"),
    ).encode("utf-8")


def test_v1_hello_pickle_config_and_ignores_v2_topology():
    state = MonitorState()
    deps = {
        "alias_svc": MagicMock(),
        "alias_repo": MagicMock(),
        "lastheard_repo": MagicMock(),
        "tgcount_repo": MagicMock(),
        "broadcast": None,
        "config_global": {"LH_INC": False, "TGC_INC": False, "BRDG_INC": True, "HB_INC": True},
        "report_decoder": PickleJsonReportPayloadDecoder(),
    }
    process_message(_v1_hello_frame(), state, **deps)
    assert state.server_mode == ServerMode.V2
    assert state.report_protocol is None

    systems = {"MASTER-A": {"MODE": "MASTER", "ENABLED": True, "PEERS": {}}}
    result = process_message(_pickle_config(systems), state, **deps)
    assert not is_fail(result)
    assert "MASTER-A" in state.CONFIG

    frame = Opcode.TOPOLOGY_SND + b'{"type":"topology","seq":1,"systems":[]}'
    result = process_message(frame, state, **deps)
    assert not is_fail(result)
    assert state.topology_seq == 0


def test_legacy_mode_ignores_v2_topology_opcode():
    state = MonitorState()
    state.server_mode = ServerMode.LEGACY
    state.server_mode_confirmed = True
    deps = {
        "alias_svc": MagicMock(),
        "alias_repo": MagicMock(),
        "lastheard_repo": MagicMock(),
        "tgcount_repo": MagicMock(),
        "broadcast": None,
        "config_global": {},
        "report_decoder": PickleJsonReportPayloadDecoder(),
    }
    frame = Opcode.TOPOLOGY_SND + b'{"type":"topology","seq":1,"systems":[]}'
    result = process_message(frame, state, **deps)
    assert not is_fail(result)
    assert state.topology_seq == 0
