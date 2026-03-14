# Hotspot Proxy for ADN DMR Peer Server.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Domain entities: peer session, config."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PeerSession:
    """Tracked peer (repeater) session: client addr and assigned master port."""

    dport: int
    sport: int
    shost: str
    timer: Any = None  # IDelayedCall
    opt_timer: Any = None  # IDelayedCall for login options
