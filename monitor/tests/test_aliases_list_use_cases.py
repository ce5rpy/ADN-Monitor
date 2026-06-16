"""Aliases list proxy URL resolution."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.application.aliases_list_use_cases import AliasesListUseCases
from adn_monitor.domain import is_fail


def test_urls_from_aliases_config():
    fetcher = MagicMock()
    uc = AliasesListUseCases(
        fetcher,
        {
            "ALIASES": {
                "TG_LIST_URL": "https://example/tg.json",
                "BRIDGE_LIST_URL": "https://example/bridges.tsv",
            }
        },
    )
    result = uc._urls()
    assert not is_fail(result)
    assert result.value == ("https://example/tg.json", "https://example/bridges.tsv")


def test_urls_fallback_to_files():
    fetcher = MagicMock()
    uc = AliasesListUseCases(
        fetcher,
        {
            "FILES": {
                "TGID_URL": "https://cdn/files/talkgroup_ids.json",
                "SERVER_ID_URL": "https://cdn/files/server_ids.tsv",
            }
        },
    )
    result = uc._urls()
    assert not is_fail(result)
    assert result.value == ("https://cdn/files/talkgroup_ids.json", "https://cdn/files/server_ids.tsv")


def test_urls_missing_returns_failure():
    fetcher = MagicMock()
    uc = AliasesListUseCases(fetcher, {})
    result = uc._urls()
    assert is_fail(result)
