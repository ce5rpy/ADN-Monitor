"""httpx adapter for HttpFetcherPort."""

from __future__ import annotations

import httpx

from ...application.ports import HttpFetcherPort
from ...domain import Failure, Result, Success


class HttpxFetcher(HttpFetcherPort):
    def __init__(self, *, timeout: float = 25.0, user_agent: str = "ADN-Monitor-FastAPI/2.0") -> None:
        self._timeout = timeout
        self._user_agent = user_agent

    def fetch(self, url: str) -> Result[tuple[bytes, str | None], str]:
        try:
            with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
                resp = client.get(url, headers={"User-Agent": self._user_agent})
            if resp.status_code != 200:
                return Failure(f"HTTP {resp.status_code}")
            ct = resp.headers.get("content-type")
            return Success((resp.content, ct))
        except Exception as exc:
            return Failure(str(exc))
