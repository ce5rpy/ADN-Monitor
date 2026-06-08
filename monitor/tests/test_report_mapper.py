"""Unit tests for report JSON → legacy shape mapping."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adn_monitor.application.report_mapper import (
    REPORT_PROTOCOL,
    decode_report_payload,
    merge_routing_delta,
    merge_topology_delta,
    routing_table_to_bridges,
    topology_to_config,
    voice_event_to_csv_parts,
)
from adn_monitor.domain import is_fail

_SCHEMA_EXAMPLES = Path("/opt/new-adn-server/schemas/examples")


def _load_example(name: str) -> dict:
    return json.loads((_SCHEMA_EXAMPLES / name).read_text(encoding="utf-8"))


def test_report_protocol_constant():
    assert REPORT_PROTOCOL == 2


def test_topology_to_config_maps_openbridge_network_id():
    topology = {
        "type": "topology",
        "seq": 1,
        "ts": 1.0,
        "systems": [{
            "name": "OBP-CL",
            "mode": "OPENBRIDGE",
            "enabled": True,
            "network_id": 73010,
            "peers": [],
        }],
    }
    config = topology_to_config(topology)
    assert config["OBP-CL"]["NETWORK_ID"] == (73010).to_bytes(4, "big")


def test_topology_to_config_maps_peer_display_fields():
    topology = {
        "type": "topology",
        "seq": 1,
        "ts": 1.0,
        "systems": [{
            "name": "SYS-1",
            "mode": "MASTER",
            "enabled": True,
            "peers": [{
                "id": 3120001,
                "connected": True,
                "callsign": "CE5RPY",
                "rx_freq": "145625000",
                "tx_freq": "145625000",
            }],
        }],
    }
    config = topology_to_config(topology, ts=1.0)
    peer_key = (3120001).to_bytes(4, "big")
    peer = config["SYS-1"]["PEERS"][peer_key]
    assert peer["CALLSIGN"] == "CE5RPY"
    assert peer["RX_FREQ"] == b"145625000"
    assert peer["TX_FREQ"] == b"145625000"


def test_topology_to_config_from_example():
    topology = _load_example("topology.json")
    config = topology_to_config(topology, ts=topology["ts"])
    assert "MASTER-A" in config
    assert config["MASTER-A"]["MODE"] == "MASTER"
    assert config["MASTER-A"]["ENABLED"] is True
    peer_key = (3120001).to_bytes(4, "big")
    assert peer_key in config["MASTER-A"]["PEERS"]
    assert config["MASTER-A"]["PEERS"][peer_key]["CONNECTION"] == "YES"
    assert "OBP-CL" in config
    assert config["OBP-CL"]["MODE"] == "OPENBRIDGE"
    assert config["OBP-CL"]["ENHANCED_OBP"] is True


def test_routing_table_to_bridges_from_example():
    routing = _load_example("routing_table.json")
    bridges = routing_table_to_bridges(routing)
    assert "52090" in bridges
    assert len(bridges["52090"]) == 2
    assert bridges["52090"][0]["SYSTEM"] == "MASTER-A"
    assert bridges["52090"][0]["TO_TYPE"] == "ON"
    assert bridges["52090"][0]["TIMER"] == 1717555320.0
    assert "#310" in bridges


def test_voice_event_to_csv_parts_start():
    voice = _load_example("voice_event.json")
    parts = voice_event_to_csv_parts(voice)
    assert parts == [
        "GROUP VOICE",
        "START",
        "RX",
        "MASTER-A",
        "2155905152",
        "1001",
        "3120001",
        "2",
        "52090",
    ]


def test_voice_event_to_csv_parts_end_with_duration():
    voice = {
        "type": "voice_event",
        "call_family": "GROUP",
        "phase": "END",
        "direction": "RX",
        "system": "SYS",
        "stream_id": 1,
        "peer_id": 2,
        "src_id": 3,
        "slot": 1,
        "dst_id": 4,
        "duration_s": 12.5,
    }
    parts = voice_event_to_csv_parts(voice)
    assert parts[-1] == "12.50"


def test_voice_event_unit_data_header():
    voice = {
        "type": "voice_event",
        "call_family": "UNIT",
        "phase": "DATA",
        "direction": "RX",
        "system": "SYS",
        "stream_id": 1,
        "peer_id": 2,
        "src_id": 3,
        "slot": 1,
        "dst_id": 4,
    }
    parts = voice_event_to_csv_parts(voice)
    assert parts[0] == "UNIT DATA HEADER"


def test_merge_topology_delta():
    full = _load_example("topology.json")
    patch = {"type": "topology", "seq": 2, "ts": 1717555201.0, "systems": [
        {"name": "MASTER-A", "mode": "MASTER", "enabled": True, "peers": [
            {"id": 3120001, "connected": False}
        ]}
    ]}
    merged = merge_topology_delta(full, patch)
    assert merged["seq"] == 2
    master = next(s for s in merged["systems"] if s["name"] == "MASTER-A")
    assert master["peers"][0]["connected"] is False
    assert any(s["name"] == "OBP-CL" for s in merged["systems"])


def test_merge_routing_delta():
    full = _load_example("routing_table.json")
    patch = _load_example("delta.json")["patch"]
    merged = merge_routing_delta(full, patch)
    route = next(r for r in merged["routes"] if r["bridge_key"] == "52090")
    assert route["legs"][0]["active"] is False


def test_decode_report_payload():
    payload = json.dumps({"type": "topology", "seq": 1, "ts": 1.0, "systems": []})
    raw = b"\x10" + payload.encode("utf-8")
    result = decode_report_payload(raw)
    assert not is_fail(result)
    assert result.value["type"] == "topology"


@pytest.mark.skipif(not _SCHEMA_EXAMPLES.is_dir(), reason="server schema examples not available")
def test_examples_dir_available():
    assert (_SCHEMA_EXAMPLES / "topology.json").is_file()
