# ADN Monitor - tests rts display slot
#
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
###############################################################################
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

"""CTABLE timeslot chips follow peer OPTIONS static TG, not wire slot alone."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.application.monitor_controller import MonitorState
from adn_monitor.application.rts_update import rts_update_impl
from adn_monitor.application.tgstats import prune_voice_ts_not_in_static


def _state_with_peer(
    *,
    peer_id: int,
    ts1_static: list[str],
    ts2_static: list[str],
) -> MonitorState:
    state = MonitorState()
    state.CTABLE = {
        "MASTERS": {
            "SYSTEM": {
                "PEERS": {
                    peer_id: {
                        "TS1_STATIC": ts1_static,
                        "TS2_STATIC": ts2_static,
                        1: {"TS": False, "TRX": ""},
                        2: {"TS": False, "TRX": ""},
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    return state


def _alias() -> MagicMock:
    alias = MagicMock()
    alias.alias_short.return_value = "HS"
    alias.alias_call.return_value = "HS"
    alias.alias_tgid.return_value = "TG"
    return alias


def test_wire_ts2_colors_ts2_when_tg_in_ts2_static() -> None:
    state = _state_with_peer(peer_id=730001, ts1_static=[], ts2_static=["73010"])
    rts_update_impl(
        "GROUP VOICE,START,TX,SYSTEM,1,730002,730002,2,73010".split(","),
        state,
        _alias(),
        lambda: "12:00",
    )
    peer = state.CTABLE["MASTERS"]["SYSTEM"]["PEERS"][730001]
    assert peer[2]["TS"] is True
    assert peer[2]["TRX"] == "TX"
    assert peer[1]["TS"] is False


def test_wire_ts2_colors_ts1_when_tg_only_in_ts1_static() -> None:
    state = _state_with_peer(peer_id=730001, ts1_static=["73010"], ts2_static=[])
    rts_update_impl(
        "GROUP VOICE,START,TX,SYSTEM,1,730002,730002,2,73010".split(","),
        state,
        _alias(),
        lambda: "12:00",
    )
    peer = state.CTABLE["MASTERS"]["SYSTEM"]["PEERS"][730001]
    assert peer[1]["TS"] is True
    assert peer[1]["TRX"] == "TX"
    assert peer[2]["TS"] is False


def test_transmitter_rx_uses_wire_slot_not_options() -> None:
    state = _state_with_peer(peer_id=730002, ts1_static=[], ts2_static=["73010"])
    rts_update_impl(
        "GROUP VOICE,START,RX,SYSTEM,1,730002,730002,2,73010".split(","),
        state,
        _alias(),
        lambda: "12:00",
    )
    peer = state.CTABLE["MASTERS"]["SYSTEM"]["PEERS"][730002]
    assert peer[2]["TS"] is True
    assert peer[2]["TRX"] == "RX"


def test_end_clears_cross_slot_when_static_tg_removed() -> None:
    """END must clear the slot lit at START even if OPTIONS no longer map the TG there."""
    state = _state_with_peer(peer_id=730001, ts1_static=["52090"], ts2_static=[])
    rts_update_impl(
        "GROUP VOICE,START,TX,SYSTEM,1,730002,5200386,2,52090".split(","),
        state,
        _alias(),
        lambda: "12:00",
    )
    peer = state.CTABLE["MASTERS"]["SYSTEM"]["PEERS"][730001]
    assert peer[1]["TS"] is True
    peer["TS1_STATIC"] = []
    peer["TS2_STATIC"] = []
    rts_update_impl(
        "GROUP VOICE,END,TX,SYSTEM,99,730002,5200386,2,52090".split(","),
        state,
        _alias(),
        lambda: "12:00",
    )
    assert peer[1]["TS"] is False
    assert peer[2]["TS"] is False


def test_build_tgstats_clears_active_static_tg_removed_from_options() -> None:
    state = _state_with_peer(peer_id=5200386, ts1_static=["52090"], ts2_static=[])
    peer = state.CTABLE["MASTERS"]["SYSTEM"]["PEERS"][5200386]
    peer[1]["TS"] = True
    peer[1]["TRX"] = "TX"
    peer[1]["TG"] = "TG&nbsp;52090"
    peer[1]["DEST"] = "TG 52090"
    peer["TS1_STATIC"] = []
    peer["TS2_STATIC"] = []
    prune_voice_ts_not_in_static(state, "SYSTEM", 5200386, peer)
    assert peer[1]["TS"] is False
    assert peer[1]["TRX"] == ""
