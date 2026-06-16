"""ALIASES list URL resolution in config_loader."""

from __future__ import annotations

import tempfile
from pathlib import Path

from adn_monitor.domain import is_fail
from adn_monitor.infrastructure.config_loader import load_config


def _write_yaml(content: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as fh:
        fh.write(content)
        return fh.name


def test_config_derives_list_urls_from_tgid():
    path = _write_yaml(
        """
ALIASES:
  TGID_URL: "https://cdn.example/talkgroup_ids.json"
"""
    )
    result = load_config(path)
    Path(path).unlink(missing_ok=True)
    assert not is_fail(result)
    cfg = result.value
    assert cfg["ALIASES"]["TG_LIST_URL"] == "https://cdn.example/talkgroup_ids.json"
    assert cfg["ALIASES"]["BRIDGE_LIST_URL"] == "https://cdn.example/server_ids.tsv"
    assert cfg["FILES"]["SERVER_ID_URL"] == "https://cdn.example/server_ids.tsv"
