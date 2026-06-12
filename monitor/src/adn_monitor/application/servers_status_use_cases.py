# ADN Monitor - application servers status use cases
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

"""World servers status proxy use cases."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

from ..domain import Failure, Result, Success, is_fail
from .ports import HttpFetcherPort

_DEFAULT_URL = "https://adn.systems/servers/status.json"


class ServersStatusUseCases:
    def __init__(self, fetcher: HttpFetcherPort, config: dict[str, Any]) -> None:
        self._fetcher = fetcher
        self._config = config

    def _status_url(self) -> str:
        dashboard = self._config.get("DASHBOARD") or {}
        url = str(
            dashboard.get("SERVER_STATUS_URL")
            or dashboard.get("server_status_url")
            or _DEFAULT_URL
        ).strip()
        return url or _DEFAULT_URL

    @staticmethod
    def _is_allowed_url(url: str) -> bool:
        parts = urlparse(url)
        return bool(parts.scheme in ("http", "https") and parts.netloc)

    def fetch_status(self) -> Result[bytes, str]:
        url = self._status_url()
        if not self._is_allowed_url(url):
            return Failure("Invalid SERVER_STATUS_URL in DASHBOARD config")
        result = self._fetcher.fetch(url)
        if is_fail(result):
            return Failure("Upstream server status request failed")
        body, _ = result.value
        try:
            json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Failure("Upstream response is not valid JSON")
        return Success(body)
