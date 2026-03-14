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

"""Application ports (interfaces) for infrastructure adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProxyDbPort(ABC):
    """Port for self-service proxy DB (Clients table: options, password, log in/out, last_seen)."""

    @abstractmethod
    def test_db(self) -> Any:
        """Verify DB connectivity. Returns Deferred that fires with Result."""
        ...

    @abstractmethod
    def ins_conf(
        self,
        int_id: int,
        peer_id_bytes: bytes,
        callsign: str,
        host: str,
        mode: str,
    ) -> None:
        """Insert or update client config on RPTC (configure) from peer."""
        ...

    @abstractmethod
    def updt_tbl(
        self,
        action: str,
        peer_id_bytes: bytes,
        *,
        psswd: str | None = None,
    ) -> None:
        """Update Clients: log_out, psswd, opt_rcvd, rst_mod."""
        ...

    @abstractmethod
    def slct_opt(self, peer_id_bytes: bytes) -> Any:
        """Select options for peer. Returns Deferred that fires with (rows,) e.g. ((options_str,),)."""
        ...

    @abstractmethod
    def slct_db(self) -> Any:
        """Select all (peer_id, options) for peers that need options push. Returns Deferred."""
        ...

    @abstractmethod
    def updt_lstseen(self, dmrid_list: list[tuple[bytes, ...]]) -> None:
        """Update last_seen for given peer IDs."""
        ...

    @abstractmethod
    def clean_tbl(self) -> None:
        """Periodic cleanup (e.g. old records). Returns Deferred."""
        ...


class PrivHelperPort(ABC):
    """Port for privileged operations (netfilter blocklist, conntrack flush)."""

    @abstractmethod
    def add_blocklist(self, dport: int, ip: str) -> None:
        """Add IP to blocklist for given listen port."""
        ...

    @abstractmethod
    def del_blocklist(self, dport: int, ip: str) -> None:
        """Remove IP from blocklist."""
        ...

    @abstractmethod
    def blocklist_flush(self) -> None:
        """Flush blocklist."""
        ...

    @abstractmethod
    def flush_conntrack(self) -> None:
        """Flush conntrack for proxy UDP port."""
        ...
