# ADN Monitor - infrastructure fastapi noop repos
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

"""In-memory no-op repositories when MySQL is unavailable (ingest still runs)."""

from __future__ import annotations

from ...application.ports import AliasRepository, LastHeardRepository, TgCountRepository
from ...domain.entities import PeerAlias, SubscriberAlias, TalkgroupAlias


class NoOpAliasRepository(AliasRepository):
    def get_subscriber(self, dmr_id: int) -> SubscriberAlias | None:
        return None

    def get_peer(self, peer_id: int) -> PeerAlias | None:
        return None

    def get_talkgroup(self, tgid: int) -> TalkgroupAlias | None:
        return None

    def ensure_subscriber_in_cache(self, dmr_id: int) -> None:
        return None

    def ensure_talkgroup_in_cache(self, tg_id: int) -> None:
        return None


class NoOpLastHeardRepository(LastHeardRepository):
    def insert_last_heard(self, *args, **kwargs) -> None:
        return None

    def insert_lstheard_log(self, *args, **kwargs) -> None:
        return None

    def select_for_render(self, table: str, row_num: int) -> list:
        return []

    def clean_table(self, table: str, keep_rows: int) -> None:
        return None


class NoOpTgCountRepository(TgCountRepository):
    def insert_tgcount(self, *args, **kwargs) -> None:
        return None

    def select_tgcount(self, row_num: int):
        return None

    def clean_tgcount(self) -> None:
        return None
