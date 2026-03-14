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

"""Privileged helper adapter (Pyro5: netfilter blocklist, conntrack flush)."""

from __future__ import annotations

import logging
from typing import Optional

from ..domain import PrivHelperPort

logger = logging.getLogger("adn-proxy")

try:
    import Pyro5.api
    _PYRO_AVAILABLE = True
except ImportError:
    _PYRO_AVAILABLE = False
    Pyro5 = None  # type: ignore


class PyroPrivHelper(PrivHelperPort):
    """PrivHelperPort via Pyro5 (netfilterControl, conntrackControl)."""

    def __init__(
        self,
        netfilter_uri: str = "PYRO:netfilterControl@./u:/run/priv_control/priv_control.unixsocket",
        conntrack_uri: str = "PYRO:conntrackControl@./u:/run/priv_control/priv_control.unixsocket",
        udp_port: int = 62031,
    ) -> None:
        self._netfilter_uri = netfilter_uri
        self._conntrack_uri = conntrack_uri
        self._udp_port = udp_port

    def add_blocklist(self, dport: int, ip: str) -> None:
        if not _PYRO_AVAILABLE:
            return
        try:
            with Pyro5.api.Proxy(self._netfilter_uri) as nf:
                nf.blocklistAdd(dport, ip)
        except Exception as e:
            logger.warning("(PrivError) %s", e)

    def del_blocklist(self, dport: int, ip: str) -> None:
        if not _PYRO_AVAILABLE:
            return
        try:
            with Pyro5.api.Proxy(self._netfilter_uri) as nf:
                nf.blocklistDel(dport, ip)
        except Exception as e:
            logger.warning("(PrivError) %s", e)

    def blocklist_flush(self) -> None:
        if not _PYRO_AVAILABLE:
            return
        try:
            with Pyro5.api.Proxy(self._netfilter_uri) as nf:
                nf.blocklistFlush()
        except Exception as e:
            logger.warning("(PrivError) %s", e)

    def flush_conntrack(self) -> None:
        if not _PYRO_AVAILABLE:
            return
        try:
            with Pyro5.api.Proxy(self._conntrack_uri) as ct:
                ct.flushUDPTarget(self._udp_port)
        except Exception as e:
            logger.warning("(PrivError) %s", e)


def create_priv_helper(
    unix_socket: str = "/run/priv_control/priv_control.unixsocket",
    listen_port: int = 62031,
) -> Optional[PrivHelperPort]:
    """Create PrivHelperPort if socket exists and is a socket; else return None."""
    import os
    import stat
    if not _PYRO_AVAILABLE:
        return None
    if not os.path.exists(unix_socket):
        return None
    if not stat.S_ISSOCK(os.stat(unix_socket).st_mode):
        return None
    uri_base = f"PYRO:{{name}}@./u:{unix_socket}"
    return PyroPrivHelper(
        netfilter_uri=uri_base.format(name="netfilterControl"),
        conntrack_uri=uri_base.format(name="conntrackControl"),
        udp_port=listen_port,
    )
