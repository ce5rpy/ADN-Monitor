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
