# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2025  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
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

"""Application ports (interfaces) for infrastructure adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from ..domain import ReportProtocolError, Result, Success
from ..domain.entities import (
    LastHeardEntry,
    PeerAlias,
    SubscriberAlias,
    TalkgroupAlias,
)


class AliasRepository(ABC):
    """Port for alias data (subscriber, peer, talkgroup) by ID."""

    @abstractmethod
    def get_subscriber(self, dmr_id: int) -> SubscriberAlias | None:
        """Return subscriber alias or None if not found."""
        ...

    @abstractmethod
    def get_peer(self, peer_id: int) -> PeerAlias | None:
        """Return peer alias or None if not found."""
        ...

    @abstractmethod
    def get_talkgroup(self, tg_id: int) -> TalkgroupAlias | None:
        """Return talkgroup alias or None if not found."""
        ...

    @abstractmethod
    def ensure_subscriber_in_cache(self, dmr_id: int) -> None:
        """Load subscriber from persistence into cache if not present (async-friendly)."""
        ...

    @abstractmethod
    def ensure_talkgroup_in_cache(self, tg_id: int) -> None:
        """Load talkgroup from persistence into cache if not present (async-friendly)."""
        ...


class AliasTableRepository(ABC):
    """Port for populating alias tables from files (CSV/JSON) and table counts."""

    @abstractmethod
    def populate_from_file(
        self,
        path: str,
        file_name: str,
        table: str,
        wipe: bool = True,
    ) -> None:
        """Load file and populate the given alias table."""
        ...

    @abstractmethod
    def table_count(self, table: str) -> Any:
        """Return a Deferred that fires with row count for the table, or None."""
        ...


class LastHeardRepository(ABC):
    """Port for last_heard and lstheard_log data."""

    @abstractmethod
    def insert_last_heard(
        self,
        qso_time: float | None,
        qso_type: str,
        system: str,
        tg_num: int,
        dmr_id: int,
    ) -> None:
        """Insert or replace last_heard row."""
        ...

    @abstractmethod
    def insert_lstheard_log(
        self,
        qso_time: float | None,
        qso_type: str,
        system: str,
        tg_num: int,
        dmr_id: int,
    ) -> None:
        """Insert lstheard_log row."""
        ...

    @abstractmethod
    def select_for_render(self, table: str, row_num: int) -> list[tuple[Any, ...]]:
        """Select last_heard or lstheard_log for dashboard render."""
        ...

    @abstractmethod
    def clean_table(self, table: str, keep_rows: int) -> None:
        """Trim table to keep approximately keep_rows rows."""
        ...


class TgCountRepository(ABC):
    """Port for TG count feature."""

    @abstractmethod
    def insert_tgcount(self, tg_num: str, dmr_id: str, qso_time: str) -> None:
        """Record a voice QSO for TG count."""
        ...

    @abstractmethod
    def select_tgcount(self, row_num: int) -> list[Any] | None:
        """Select tgcount data for dashboard."""
        ...

    @abstractmethod
    def clean_tgcount(self) -> None:
        """Remove tgcount data older than today."""
        ...


class BroadcastPort(Protocol):
    """Port for broadcasting to WebSocket groups."""

    def broadcast(self, message: str, group: str) -> None:
        """Send message to all clients in group."""
        ...

    def send_to_client(self, client: Any, message: str) -> None:
        """Send message to a single client."""
        ...


class ReportPayloadDecoder(ABC):
    """Port for decoding CONFIG_SND / BRIDGE_SND report payloads (pickle or JSON)."""

    @abstractmethod
    def decode_config(self, raw_message: bytes) -> Result[dict, ReportProtocolError]:
        """Decode CONFIG_SND payload; returns Success(config_dict) or Failure."""
        ...

    @abstractmethod
    def decode_bridges(self, raw_message: bytes) -> Result[dict, ReportProtocolError]:
        """Decode BRIDGE_SND payload; returns Success(bridges_dict) or Failure."""
        ...
