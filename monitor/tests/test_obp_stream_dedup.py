"""OpenBridge STREAMS dedup by numeric src_id."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.application.monitor_controller import MonitorState
from adn_monitor.application.rts_update import rts_update_impl
from adn_monitor.domain.value_objects import ServerMode


def test_obp_stream_dedup_replaces_numeric_label_with_callsign() -> None:
    state = MonitorState()
    state.server_mode = ServerMode.V2
    state.CTABLE = {
        "MASTERS": {},
        "PEERS": {},
        "OPENBRIDGES": {
            "OBP-CL": {
                "STREAMS": {
                    "111": ("RX", "2226289", "9140", 1000.0, 2226289),
                }
            }
        },
    }
    alias = MagicMock()
    alias.alias_call.return_value = "IK6FBY"
    alias.alias_short.return_value = "IK6FBY"
    alias.alias_tgid.return_value = "TG"

    rts_update_impl(
        "GROUP VOICE,START,RX,OBP-CL,222,73010,2226289,1,9140".split(","),
        state,
        alias,
        lambda: "12:00",
    )

    streams = state.CTABLE["OPENBRIDGES"]["OBP-CL"]["STREAMS"]
    assert "111" not in streams
    assert streams["222"] == ("RX", "IK6FBY", "9140", streams["222"][3], 2226289)
