"""dashboard_state wire — monitor consumer tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from adn_monitor.application.monitor_controller import (
    MonitorState,
    build_tgstats,
    process_message,
    process_report_json,
)
from adn_monitor.application.report_mapper import dashboard_state_to_config
from adn_monitor.domain import is_fail
from adn_monitor.domain.value_objects import Opcode, ServerMode
from adn_monitor.infrastructure.report_payload_decoder import PickleJsonReportPayloadDecoder


def _peer_options_bytes(
    *,
    single: str = "1",
    timer: float | None = None,
    ts2: str = "730,7305",
) -> bytes:
    opts = f"TS2={ts2};SINGLE={single};"
    if timer is not None:
        opts += f"TIMER={timer:g};"
    return opts.encode()


def _config_with_peer_options(
    *peer_specs: tuple[int, str, float | None],
    master: str = "SYSTEM",
    yaml_single: bool = False,
    yaml_timer: float = 10,
    extra_peer_fields: dict[int, dict] | None = None,
) -> dict:
    peers: dict = {}
    for peer_id, single, timer in peer_specs:
        peer_key = peer_id.to_bytes(4, "big")
        entry: dict = {"OPTIONS": _peer_options_bytes(single=single, timer=timer)}
        if extra_peer_fields and peer_id in extra_peer_fields:
            entry.update(extra_peer_fields[peer_id])
        peers[peer_key] = entry
    return {
        master: {
            "MODE": "MASTER",
            "SINGLE_MODE": yaml_single,
            "DEFAULT_UA_TIMER": yaml_timer,
            "PEERS": peers,
        }
    }


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


def test_slim_wire_accepts_routing_table_for_ua_chips():
    import time as _time

    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.report_protocol = 2
    state.slim_wire = True
    state.UA_DYNAMIC_OWNERS = {("SYSTEM-2", 730039101, 2): 7304}
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", 730039101, 2): (7304, _time.time() + 300)}
    state.CONFIG = _config_with_peer_options((730039101, "1", 5.0))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    730039101: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    routing = {
        "type": "routing_table",
        "seq": 1,
        "ts": 1000.0,
        "routes": [
            {
                "bridge_key": "7304",
                "legs": [
                    {
                        "system": "SYSTEM",
                        "ts": 2,
                        "tgid": 7304,
                        "active": True,
                        "to_type": "ON",
                        "timer_expires_at": 2000.0,
                    }
                ],
            }
        ],
    }
    frame = Opcode.ROUTING_TABLE_SND + json.dumps(routing, separators=(",", ":")).encode()
    deps = _deps()
    deps["report_decoder"] = PickleJsonReportPayloadDecoder()
    result = process_message(frame, state, **deps)
    assert not is_fail(result)
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][730039101]
    assert peer["SINGLE_TS2"]["TGID"] == 7304


def test_slim_wire_static_single_active_sets_single_ts_for_owner_only() -> None:
    import time as _time

    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.report_protocol = 2
    state.slim_wire = True
    state.UA_DYNAMIC_OWNERS = {("SYSTEM-2", 730039101, 2): 7305}
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", 730039101, 2): (7305, _time.time() + 300)}
    state.CONFIG = _config_with_peer_options((730039101, "1", 5.0))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    730039101: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    routing = {
        "type": "routing_table",
        "seq": 2,
        "ts": 1001.0,
        "routes": [
            {
                "bridge_key": "7305",
                "legs": [
                    {
                        "system": "SYSTEM",
                        "ts": 2,
                        "tgid": 7305,
                        "active": True,
                        "to_type": "OFF",
                        "timer_expires_at": 2000.0,
                    }
                ],
            }
        ],
    }
    frame = Opcode.ROUTING_TABLE_SND + json.dumps(routing, separators=(",", ":")).encode()
    deps = _deps()
    deps["report_decoder"] = PickleJsonReportPayloadDecoder()
    process_message(frame, state, **deps)
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][730039101]
    assert peer["SINGLE_TS2"]["TGID"] == 7305


def test_other_peer_activity_keeps_single_ts_on_first_peer() -> None:
    """UA/SINGLE chip on peer A must not clear when peer B transmits on another TG."""
    import time as _time

    peer_a = 730039101
    peer_b = 730088888
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.report_protocol = 2
    state.slim_wire = True
    state.UA_DYNAMIC_OWNERS = {("SYSTEM-2", peer_a, 2): 7305}
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", peer_a, 2): (7305, _time.time() + 300)}
    state.CONFIG = _config_with_peer_options(
        (peer_a, "1", 5.0),
        (peer_b, "1", 5.0),
    )
    state.CONFIG["SYSTEM"]["PEERS"][peer_b.to_bytes(4, "big")]["OPTIONS"] = _peer_options_bytes(
        timer=5.0, ts2="730"
    )
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    },
                    peer_b: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730"],
                        1: {},
                        2: {},
                    },
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    routing = {
        "type": "routing_table",
        "seq": 3,
        "ts": 1002.0,
        "routes": [
            {
                "bridge_key": "7305",
                "legs": [
                    {
                        "system": "SYSTEM",
                        "ts": 2,
                        "tgid": 7305,
                        "active": True,
                        "to_type": "OFF",
                        "timer_expires_at": 3000.0,
                    }
                ],
            },
            {
                "bridge_key": "7304",
                "legs": [
                    {
                        "system": "SYSTEM",
                        "ts": 2,
                        "tgid": 7304,
                        "active": True,
                        "to_type": "ON",
                        "timer_expires_at": 3100.0,
                    }
                ],
            },
        ],
    }
    deps = _deps()
    deps["report_decoder"] = PickleJsonReportPayloadDecoder()
    frame = Opcode.ROUTING_TABLE_SND + json.dumps(routing, separators=(",", ":")).encode()
    process_message(frame, state, **deps)
    assert state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]["SINGLE_TS2"]["TGID"] == 7305

    voice_b = {
        "type": "voice_event",
        "ts": 1003.0,
        "call_family": "GROUP",
        "phase": "START",
        "direction": "RX",
        "system": "SYSTEM-2",
        "stream_id": 9001,
        "peer_id": peer_b,
        "src_id": 3120002,
        "slot": 2,
        "dst_id": 7304,
    }
    process_message(Opcode.VOICE_EVENT_SND + json.dumps(voice_b, separators=(",", ":")).encode(), state, **deps)
    build_tgstats(state)

    peers = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"]
    assert peers[peer_a]["SINGLE_TS2"]["TGID"] == 7305
    assert peers[peer_b]["SINGLE_TS2"]["TGID"] == 7304
    assert state.UA_DYNAMIC_OWNERS[("SYSTEM-2", peer_a, 2)] == 7305
    assert state.UA_DYNAMIC_OWNERS[("SYSTEM-2", peer_b, 2)] == 7304


def test_build_tgstats_hides_expired_ua_bridge() -> None:
    import time as _time

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_DYNAMIC_OWNERS = {("SYSTEM-2", peer_a, 2): 7304}
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", peer_a, 2): (7304, _time.time() - 1)}
    state.CONFIG = _config_with_peer_options((peer_a, "1", 5.0))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    state.BRIDGES = {
        "7304": [
            {
                "SYSTEM": "SYSTEM",
                "TS": 2,
                "TGID": 7304,
                "ACTIVE": True,
                "TO_TYPE": "ON",
                "TIMER": 1_000_000_000.0,
            }
        ]
    }
    build_tgstats(state)
    assert state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]["SINGLE_TS2"]["TGID"] == ""


def test_build_tgstats_shows_ua_from_server_bridge_only() -> None:
    import time as _time

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_DYNAMIC_OWNERS = {("SYSTEM-2", peer_a, 2): 7304}
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", peer_a, 2): (7304, _time.time() + 300)}
    state.CONFIG = _config_with_peer_options((peer_a, "1", 5.0))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    build_tgstats(state)
    row = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]["SINGLE_TS2"]
    assert row["TGID"] == 7304
    assert row["TO"]


def test_build_tgstats_static_off_active_from_server_bridge() -> None:
    """Static SINGLE chip uses per-peer session timer, not shared BRIDGES leg."""
    import time as _time

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_DYNAMIC_OWNERS = {("SYSTEM-2", peer_a, 2): 7305}
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", peer_a, 2): (7305, _time.time() + 300)}
    state.CONFIG = _config_with_peer_options((peer_a, "1", 5.0))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    state.BRIDGES = {
        "7305": [
            {
                "SYSTEM": "SYSTEM",
                "TS": 2,
                "TGID": 7305,
                "ACTIVE": True,
                "TO_TYPE": "OFF",
                "TIMER": 1_000_000_000.0,
            }
        ],
    }
    build_tgstats(state)
    assert state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]["SINGLE_TS2"]["TGID"] == 7305


def test_build_tgstats_keeps_chip_when_bridge_inactive_but_session_valid() -> None:
    """SINGLE=1 chip follows per-peer timer; other peers must not clear it via BRIDGES."""
    import time as _time

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_DYNAMIC_OWNERS = {("SYSTEM-2", peer_a, 2): 7304}
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", peer_a, 2): (7304, _time.time() + 300)}
    state.CONFIG = _config_with_peer_options((peer_a, "1", 5.0))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    state.BRIDGES = {
        "7304": [
            {
                "SYSTEM": "SYSTEM",
                "TS": 2,
                "TGID": 7304,
                "ACTIVE": False,
                "TO_TYPE": "ON",
                "TIMER": 9_999_999_999.0,
            }
        ],
    }
    build_tgstats(state)
    assert state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]["SINGLE_TS2"]["TGID"] == 7304


def test_build_tgstats_single_zero_static_never_highlighted() -> None:
    """SINGLE=0: static TGs stay gray; no SINGLE_TS chip on static bridge."""
    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_MULTI_TGS = {("SYSTEM-2", peer_a, 2): {7305}}
    state.CONFIG = _config_with_peer_options((peer_a, "0", None))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    build_tgstats(state)
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]
    assert peer["SINGLE_TS2"]["TGID"] == ""
    assert peer["UA_MULTI_TS2"] == []


def test_build_tgstats_single_zero_multiple_dynamics_until_4000() -> None:
    """SINGLE=0: several dynamic TGs in UA_MULTI_TS until TG 4000 clears session."""
    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_MULTI_TGS = {("SYSTEM-2", peer_a, 2): {7304, 7306}}
    state.CONFIG = _config_with_peer_options((peer_a, "0", None))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    build_tgstats(state)
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]
    assert peer["SINGLE_TS2"]["TGID"] == ""
    multi = {int(e["TGID"]) for e in peer["UA_MULTI_TS2"]}
    assert multi == {7304, 7306}

    from adn_monitor.application.tgstats import clear_peer_ua_sessions

    clear_peer_ua_sessions(state, "SYSTEM-2", peer_a)
    build_tgstats(state)
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]
    assert peer["UA_MULTI_TS2"] == []


def test_voice_ua_session_not_overwritten_by_stale_config_on_build_tgstats() -> None:
    """Voice events update indigo; periodic build_tgstats must not restore stale CONFIG UA_SESSIONS."""
    import time as _time

    from adn_monitor.application.tgstats import register_ua_session

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.CONFIG = _config_with_peer_options(
        (peer_a, "1", 5.0),
        extra_peer_fields={
            peer_a: {"UA_SESSIONS": {"2": {"tgid": 7305, "expires_at": _time.time() + 300}}},
        },
    )
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    register_ua_session(state, "SYSTEM-2", peer_a, 2, 730)
    build_tgstats(state)
    row = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]["SINGLE_TS2"]
    assert row["TGID"] == 730


def test_dashboard_state_empty_ua_sessions_clears_indigo() -> None:
    """Server snapshot with ``ua_sessions: {}`` clears stale monitor indigo."""
    import time as _time

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_SESSION_EXPIRES = {("SYSTEM-2", peer_a, 2): (7305, _time.time() + 300)}
    state.CONFIG = _config_with_peer_options((peer_a, "1", None))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    config = dashboard_state_to_config(
        {
            "type": "dashboard_state",
            "ts": _time.time(),
            "ctable": {
                "MASTERS": {
                    "SYSTEM-2": {
                        "mode": "MASTER",
                        "peers": {
                            peer_a: {
                                "id": peer_a,
                                "connected": True,
                                "connected_at": int(_time.time()),
                                "options": _peer_options_bytes(single="1").decode(),
                                "ua_sessions": {},
                            }
                        },
                    }
                },
                "PEERS": {},
                "OPENBRIDGES": {},
            },
        }
    )
    from adn_monitor.application.tgstats import sync_server_ua_sessions_from_config

    state.CONFIG = config
    sync_server_ua_sessions_from_config(state, config)
    build_tgstats(state)
    assert ("SYSTEM-2", peer_a, 2) not in state.UA_SESSION_EXPIRES
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]
    assert peer["SINGLE_TS2"]["TGID"] == ""


def test_dashboard_state_empty_ua_sessions_preserves_single_zero_multi() -> None:
    """SINGLE=0: periodic dashboard_state with ``ua_sessions: {}`` must not wipe voice multi-TG."""
    import time as _time

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.UA_MULTI_TGS = {("SYSTEM-2", peer_a, 2): {7304, 7306}}
    state.CONFIG = _config_with_peer_options((peer_a, "0", None))
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730", "7305"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    config = dashboard_state_to_config(
        {
            "type": "dashboard_state",
            "ts": _time.time(),
            "ctable": {
                "MASTERS": {
                    "SYSTEM-2": {
                        "mode": "MASTER",
                        "peers": {
                            peer_a: {
                                "id": peer_a,
                                "connected": True,
                                "connected_at": int(_time.time()),
                                "options": _peer_options_bytes(single="0").decode(),
                                "ua_sessions": {},
                            }
                        },
                    }
                },
                "PEERS": {},
                "OPENBRIDGES": {},
            },
        }
    )
    from adn_monitor.application.tgstats import sync_server_ua_sessions_from_config

    state.CONFIG = config
    sync_server_ua_sessions_from_config(state, config)
    build_tgstats(state)
    assert state.UA_MULTI_TGS[("SYSTEM-2", peer_a, 2)] == {7304, 7306}
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]
    multi = {int(e["TGID"]) for e in peer["UA_MULTI_TS2"]}
    assert multi == {7304, 7306}


def test_yaml_defaults_when_peer_options_omit_single_and_timer() -> None:
    """Without SINGLE/TIMER in OPTIONS, YAML SYSTEM config applies (any values)."""
    from adn_monitor.application.tgstats import _resolve_peer_single_and_timer

    state = MonitorState()
    state.CONFIG = {
        "SYSTEM": {
            "MODE": "MASTER",
            "SINGLE_MODE": True,
            "DEFAULT_UA_TIMER": 15,
            "PEERS": {},
        }
    }
    state.PEER_OPTIONS = {
        730039101: {"TS1_STATIC": [], "TS2_STATIC": ["730444"]},
    }
    single, timer = _resolve_peer_single_and_timer(state, "SYSTEM-2", 730039101)
    assert single is True
    assert timer == 15.0


def test_runtime_options_override_yaml_single_and_timer() -> None:
    from adn_monitor.application.tgstats import _resolve_peer_single_and_timer

    state = MonitorState()
    state.CONFIG = _config_with_peer_options(
        (730039101, "1", 5.0),
        yaml_single=False,
        yaml_timer=60,
    )
    single, timer = _resolve_peer_single_and_timer(state, "SYSTEM-2", 730039101)
    assert single is True
    assert timer == 5.0


def test_peer_chips_ignore_merged_system_static_list() -> None:
    """Inject SYSTEM union TS2 must not appear on peers with their own OPTIONS."""
    peer_a = 730039210
    peer_b = 7301795
    state = MonitorState()
    state.CONFIG = {
        "SYSTEM-2": {
            "MODE": "MASTER",
            "TS2_STATIC": "730,3340,5202,7305,214091,730170,730444,8730444",
            "PEERS": {
                peer_a.to_bytes(4, "big"): {
                    "OPTIONS": b"TS2=730,7305,730170,730444;SINGLE=1;",
                    "TS2_STATIC": "730,7305,730170,730444",
                },
            },
        },
        "SYSTEM-3": {
            "MODE": "MASTER",
            "TS2_STATIC": "730,3340,5202,7305,214091,730170,730444,8730444",
            "PEERS": {
                peer_b.to_bytes(4, "big"): {"OPTIONS": b"Type=HBlink;"},
            },
        },
    }
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {"TS1_STATIC": [], "TS2_STATIC": [], 1: {}, 2: {}},
                }
            },
            "SYSTEM-3": {
                "PEERS": {
                    peer_b: {"TS1_STATIC": [], "TS2_STATIC": [], 1: {}, 2: {}},
                }
            },
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    build_tgstats(state)
    assert state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]["TS2_STATIC"] == [
        "730",
        "7305",
        "730170",
        "730444",
    ]
    assert state.CTABLE["MASTERS"]["SYSTEM-3"]["PEERS"][peer_b]["TS2_STATIC"] == []


def test_mysql_peer_options_do_not_fill_dashboard_chips() -> None:
    """PEER_OPTIONS from MySQL must not override empty runtime OPTIONS on master."""
    peer_a = 7301795
    state = MonitorState()
    state.PEER_OPTIONS = {
        peer_a: {"TS1_STATIC": [], "TS2_STATIC": ["730", "7305"], "SINGLE": "1"},
    }
    state.CONFIG = {
        "SYSTEM": {
            "MODE": "MASTER",
            "PEERS": {
                peer_a.to_bytes(4, "big"): {"OPTIONS": b"Type=HBlink;"},
            },
        }
    }
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {"TS1_STATIC": [], "TS2_STATIC": [], 1: {}, 2: {}},
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    build_tgstats(state)
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]
    assert peer["TS2_STATIC"] == []


def test_register_ua_session_uses_peer_timer_minutes() -> None:
    import time as _time

    from adn_monitor.application.tgstats import register_ua_session

    state = MonitorState()
    before = _time.time()
    state.CONFIG = _config_with_peer_options(
        (730039101, "1", 5.0),
        yaml_single=True,
        yaml_timer=60,
    )
    register_ua_session(state, "SYSTEM-2", 730039101, 2, 730444)
    entry = state.UA_SESSION_EXPIRES[("SYSTEM-2", 730039101, 2)]
    assert entry[0] == 730444
    assert entry[1] >= before + 5 * 60 - 1


def test_build_tgstats_omits_to_for_infinite_ua_timer() -> None:
    """TIMER=0 (legacy no-expiry) must not show ~24855d on the indigo chip."""
    import time as _time

    from adn_monitor.application.tgstats import build_tgstats_impl, register_ua_session
    from adn_monitor.application.time_utils import time_str

    peer_a = 730039101
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.CONFIG = _config_with_peer_options((peer_a, "1", 0.0), yaml_single=True, yaml_timer=60)
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    peer_a: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["730"],
                        1: {},
                        2: {},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    register_ua_session(state, "SYSTEM-2", peer_a, 2, 730444)
    build_tgstats_impl(state, time_str)
    peer = state.CTABLE["MASTERS"]["SYSTEM-2"]["PEERS"][peer_a]
    assert peer["SINGLE_TS2"]["TGID"] == 730444
    assert peer["SINGLE_TS2"]["TO"] == ""


def test_register_ua_session_infinite_timer_static_tg_no_absurd_to() -> None:
    """SINGLE=1 + TIMER=0 on static TG: chip shows TG without ~24855d countdown."""
    from adn_monitor.application.rts_update import rts_update_impl

    state = MonitorState()
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM-0": {
                "PEERS": {
                    730001: {
                        "TS1_STATIC": [],
                        "TS2_STATIC": ["7144", "730444"],
                        1: {"TS": False, "TRX": ""},
                        2: {"TS": False, "TRX": ""},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    state.CONFIG = {
        "SYSTEM": {
            "MODE": "MASTER",
            "SINGLE_MODE": True,
            "DEFAULT_UA_TIMER": 60,
            "PEERS": {
                (730001).to_bytes(4, "big"): {
                    "OPTIONS": b"TS2=7144,730444;SINGLE=1;TIMER=0;",
                }
            },
        }
    }
    alias = MagicMock()
    alias.alias_short.return_value = "HS"
    alias.alias_call.return_value = "HS"
    alias.alias_tgid.return_value = "TG"
    rts_update_impl(
        "GROUP VOICE,START,RX,SYSTEM-0,1,730001,730001,2,7144".split(","),
        state,
        alias,
        lambda: "12:00",
    )
    peer = state.CTABLE["MASTERS"]["SYSTEM-0"]["PEERS"][730001]
    assert peer["SINGLE_TS2"]["TGID"] == 7144
    assert peer["SINGLE_TS2"]["TO"] == ""


def test_register_ua_session_ignores_echo_9990() -> None:
    from adn_monitor.application.tgstats import register_ua_session

    state = MonitorState()
    state.CONFIG = _config_with_peer_options(
        (730039101, "1", 5.0),
        yaml_single=True,
        yaml_timer=60,
    )
    register_ua_session(state, "SYSTEM-2", 730039101, 2, 9990)
    assert ("SYSTEM-2", 730039101, 2) not in getattr(state, "UA_SESSION_EXPIRES", {})
    assert ("SYSTEM-2", 730039101, 2) not in getattr(state, "UA_DYNAMIC_OWNERS", {})
