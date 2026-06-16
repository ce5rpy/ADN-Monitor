# ADN Monitor - Dashboard and backend for ADN Systems.
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
#
# Derived from FDMR Monitor (OA4DOA), HBMonv2 (SP2ONG), hbmonitor3 (KC1AWV),
# and HBmonitor (Cortney T. Buffington, N0MJS). Original works under GPLv3.

from .entities import (
    BridgeSystemState,
    HBPeerInfo,
    LastHeardEntry,
    NullPeerAlias,
    NullSubscriberAlias,
    NullTalkgroupAlias,
    PeerAlias,
    SubscriberAlias,
    TalkgroupAlias,
    TimeslotState,
)
from .errors import (
    AliasError,
    AliasTableNotFoundError,
    ConfigError,
    AdnMonitorError,
    ReportProtocolError,
    RepositoryError,
)
from .result import Failure, Result, Success, is_fail, is_ok, unwrap_or
from .value_objects import DmrId, Callsign, ElapsedTime, Opcode, ServerMode, decode_utf8_field

__all__ = [
    "BridgeSystemState",
    "Callsign",
    "DmrId",
    "ElapsedTime",
    "Failure",
    "AdnMonitorError",
    "AliasError",
    "AliasTableNotFoundError",
    "ConfigError",
    "ReportProtocolError",
    "RepositoryError",
    "HBPeerInfo",
    "LastHeardEntry",
    "NullPeerAlias",
    "NullSubscriberAlias",
    "NullTalkgroupAlias",
    "Opcode",
    "PeerAlias",
    "Result",
    "ServerMode",
    "SubscriberAlias",
    "Success",
    "TalkgroupAlias",
    "TimeslotState",
    "decode_utf8_field",
    "is_fail",
    "is_ok",
    "unwrap_or",
]
