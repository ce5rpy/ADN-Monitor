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

"""Use case: resolve DMR IDs to alias strings for display."""

from __future__ import annotations

from ..domain import (
    NullSubscriberAlias,
    NullTalkgroupAlias,
    SubscriberAlias,
    TalkgroupAlias,
)
from .ports import AliasRepository


class AliasService:
    """Resolves numeric IDs to display strings using alias repository."""

    def __init__(self, alias_repo: AliasRepository) -> None:
        self._repo = alias_repo

    def get_subscriber_alias(self, dmr_id: int) -> SubscriberAlias:
        """Return subscriber alias or null object."""
        alias = self._repo.get_subscriber(dmr_id)
        return alias if alias is not None else NullSubscriberAlias

    def get_talkgroup_alias(self, tg_id: int) -> TalkgroupAlias:
        """Return talkgroup alias or null object."""
        alias = self._repo.get_talkgroup(tg_id)
        return alias if alias is not None else NullTalkgroupAlias

    def alias_string(self, dmr_id: int) -> str:
        """Callsign, city, state (for peers) - comma joined, skip None."""
        alias = self.get_subscriber_alias(dmr_id)
        if alias is NullSubscriberAlias:
            return str(dmr_id)
        parts = [alias.callsign, getattr(alias, "city", None), getattr(alias, "state", None)]
        return ", ".join(p for p in parts if p)

    def alias_short(self, dmr_id: int) -> str:
        """Callsign, name - for subscriber display."""
        alias = self.get_subscriber_alias(dmr_id)
        if alias is NullSubscriberAlias:
            return str(dmr_id)
        return ", ".join(filter(None, [alias.callsign, alias.name]))

    def alias_call(self, dmr_id: int) -> str:
        """Callsign only."""
        alias = self.get_subscriber_alias(dmr_id)
        if alias is NullSubscriberAlias:
            return str(dmr_id)
        return alias.callsign

    def alias_tgid(self, tg_id: int) -> str:
        """Talkgroup name only."""
        alias = self.get_talkgroup_alias(tg_id)
        if alias is NullTalkgroupAlias:
            return " "
        return alias.name
