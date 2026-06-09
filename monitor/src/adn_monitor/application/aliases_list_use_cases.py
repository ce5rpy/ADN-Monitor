"""TG / bridge list proxy use cases (URL resolution + fetch port)."""

from __future__ import annotations

from typing import Any

from ..domain import Failure, Result, Success, is_fail
from .ports import HttpFetcherPort


class AliasesListUseCases:
    def __init__(self, fetcher: HttpFetcherPort, config: dict[str, Any]) -> None:
        self._fetcher = fetcher
        self._config = config

    def _urls(self) -> Result[tuple[str, str], str]:
        aliases = self._config.get("ALIASES") or {}
        files = self._config.get("FILES") or {}
        tg = str(
            aliases.get("TG_LIST_URL") or aliases.get("tg_list_url") or files.get("TG_LIST_URL") or files.get("TGID_URL") or ""
        ).strip()
        bridge = str(
            aliases.get("BRIDGE_LIST_URL")
            or aliases.get("bridge_list_url")
            or files.get("BRIDGE_LIST_URL")
            or files.get("SERVER_ID_URL")
            or ""
        ).strip()
        if not tg:
            return Failure("TG list URL not configured (set ALIASES.TG_LIST_URL or ALIASES.TGID_URL)")
        if not bridge:
            return Failure("Bridge list URL not configured (set ALIASES.BRIDGE_LIST_URL or ALIASES.SERVER_ID_URL)")
        return Success((tg, bridge))

    def fetch_tg_list(self) -> Result[tuple[bytes, str], str]:
        urls = self._urls()
        if is_fail(urls):
            return urls
        url, _ = urls.value
        result = self._fetcher.fetch(url)
        if is_fail(result):
            return Failure(f"Failed to load TG list. Check backend can reach: {url}")
        body, content_type = result.value
        return Success((body, content_type or "application/json"))

    def fetch_bridge_list(self) -> Result[tuple[bytes, str], str]:
        urls = self._urls()
        if is_fail(urls):
            return urls
        _, url = urls.value
        result = self._fetcher.fetch(url)
        if is_fail(result):
            return Failure(f"Failed to load bridge list. Check backend can reach: {url}")
        body, content_type = result.value
        return Success((body, content_type or "text/tab-separated-values; charset=utf-8"))
