# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
# HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
# hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
# HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
# Original works and this derivative are under GPLv3.

"""Domain entities: aliases, peers, bridges, and report state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .value_objects import DmrId, ElapsedTime, decode_utf8_field


@dataclass(frozen=True, slots=True)
class SubscriberAlias:
    """Subscriber (dmr_id) alias: id, callsign, name."""

    id: int
    callsign: str
    name: str


@dataclass(frozen=True, slots=True)
class PeerAlias:
    """Peer alias: id, callsign."""

    id: int
    callsign: str


@dataclass(frozen=True, slots=True)
class TalkgroupAlias:
    """Talkgroup alias: id, name (callsign)."""

    id: int
    name: str


# Null-objects for “not found” to avoid None checks
NullSubscriberAlias = SubscriberAlias(id=0, callsign="", name="")
NullPeerAlias = PeerAlias(id=0, callsign="")
NullTalkgroupAlias = TalkgroupAlias(id=0, name="")


@dataclass
class TimeslotState:
    """State of one timeslot (TS1/TS2) for real-time display."""

    active: bool = False
    call_type: str = ""
    sub_display: str = ""
    call: str = ""
    src: str = ""
    dest: str = ""
    tg: str = ""
    trx: str = ""
    timeout: float = 0.0


@dataclass
class HBPeerInfo:
    """Homebrew peer info for display (from CONFIG)."""

    peer_id: int
    tx_freq: str
    rx_freq: str
    slots: str
    package_id: str
    software_id: str
    location: str
    description: str
    url: str
    callsign: str
    colorcode: str
    tx_power: str
    latitude: str
    longitude: str
    height: str
    connection: str
    connected: str  # elapsed time string
    ip: str
    port: Any
    ts1: TimeslotState = field(default_factory=TimeslotState)
    ts2: TimeslotState = field(default_factory=TimeslotState)


@dataclass
class BridgeSystemState:
    """One system entry in a bridge (for BTABLE)."""

    system: str
    ts: str
    tgid: int
    exp_time: Any  # int seconds or "Expired" / "N/A"
    to_action: str
    active: str  # "Connected" / "Disconnected"
    trig_on: str
    trig_off: str


@dataclass
class LastHeardEntry:
    """One last_heard row for rendering."""

    date_time: str
    qso_time: Any
    qso_type: str
    system: str
    tg_num: int
    tg_callsign: str | None
    dmr_id: int
    subscriber_json: Any  # list [callsign, name] or None
