"""Integration-style tests for process_message report opcodes."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from adn_monitor.application.monitor_controller import MonitorState, process_message
from adn_monitor.domain import is_fail
from adn_monitor.domain.value_objects import Opcode
from adn_monitor.infrastructure.report_payload_decoder import PickleJsonReportPayloadDecoder

_SCHEMA_EXAMPLES = Path("/opt/new-adn-server/schemas/examples")


def _frame(opcode: bytes, payload: dict) -> bytes:
    return opcode + json.dumps(payload, separators=(",", ":")).encode("utf-8")


@pytest.fixture
def state() -> MonitorState:
    return MonitorState()


@pytest.fixture
def deps():
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
        "report_decoder": PickleJsonReportPayloadDecoder(),
    }


def _hello_frame() -> bytes:
    return _frame(
        Opcode.HELLO,
        {
            "type": "hello",
            "server": "adn-server",
            "version": "2.0.0",
            "report_protocol": 2,
            "features": ["REPORT_V2"],
        },
    )


@pytest.mark.skipif(not _SCHEMA_EXAMPLES.is_dir(), reason="server schema examples not available")
def test_topology_update_keeps_master_peers(state: MonitorState, deps: dict):
    """Second topology apply must not wipe CTABLE peers (bytes_4 CONFIG keys)."""
    process_message(_hello_frame(), state, **deps)
    topology = json.loads((_SCHEMA_EXAMPLES / "topology.json").read_text())
    process_message(_frame(Opcode.TOPOLOGY_SND, topology), state, **deps)
    peers_after_first = sum(
        len(m.get("PEERS", {})) for m in state.CTABLE.get("MASTERS", {}).values() if isinstance(m, dict)
    )
    topology["seq"] = 2
    process_message(_frame(Opcode.TOPOLOGY_SND, topology), state, **deps)
    peers_after_second = sum(
        len(m.get("PEERS", {})) for m in state.CTABLE.get("MASTERS", {}).values() if isinstance(m, dict)
    )
    assert peers_after_first == 1
    assert peers_after_second == peers_after_first


@pytest.mark.skipif(not _SCHEMA_EXAMPLES.is_dir(), reason="server schema examples not available")
def test_process_topology_and_routing(state: MonitorState, deps: dict):
    process_message(_hello_frame(), state, **deps)
    assert state.report_protocol == 2

    topology = json.loads((_SCHEMA_EXAMPLES / "topology.json").read_text())
    result = process_message(_frame(Opcode.TOPOLOGY_SND, topology), state, **deps)
    assert not is_fail(result)
    assert state.topology_seq == 1
    assert "MASTER-A" in state.CONFIG
    assert state.CTABLE["MASTERS"]

    routing = json.loads((_SCHEMA_EXAMPLES / "routing_table.json").read_text())
    result = process_message(_frame(Opcode.ROUTING_TABLE_SND, routing), state, **deps)
    assert not is_fail(result)
    assert state.routing_seq == 42
    assert state.BRIDGES


def test_process_voice_event(state: MonitorState, deps: dict):
    process_message(_hello_frame(), state, **deps)
    voice = {
        "type": "voice_event",
        "ts": 1.0,
        "call_family": "GROUP",
        "phase": "START",
        "direction": "RX",
        "system": "MASTER-A",
        "stream_id": 99,
        "peer_id": 1001,
        "src_id": 3120001,
        "slot": 2,
        "dst_id": 52090,
    }
    result = process_message(_frame(Opcode.VOICE_EVENT_SND, voice), state, **deps)
    assert not is_fail(result)
    assert len(state.LOGBUF) > 0


@pytest.mark.skipif(not _SCHEMA_EXAMPLES.is_dir(), reason="server schema examples not available")
def test_process_routing_delta(state: MonitorState, deps: dict):
    process_message(_hello_frame(), state, **deps)
    routing = json.loads((_SCHEMA_EXAMPLES / "routing_table.json").read_text())
    process_message(_frame(Opcode.ROUTING_TABLE_SND, routing), state, **deps)

    delta = json.loads((_SCHEMA_EXAMPLES / "delta.json").read_text())
    result = process_message(_frame(Opcode.DELTA_SND, delta), state, **deps)
    assert not is_fail(result)
    assert state.routing_seq == 43
    leg = state.BRIDGES["52090"][0]
    assert leg["ACTIVE"] is False
