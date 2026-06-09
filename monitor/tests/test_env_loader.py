"""Project root .env loader."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from adn_monitor.infrastructure.env_loader import load_project_env


def test_load_project_env_sets_unset_keys():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        monitor = repo / "monitor"
        monitor.mkdir()
        (repo / ".env").write_text(
            "ADN_CONFIG_PATH=/tmp/test.yaml\n# comment\nEXISTING=from_file\n",
            encoding="utf-8",
        )
        os.environ["EXISTING"] = "already"
        loaded = load_project_env(monitor)
        assert loaded == repo / ".env"
        assert os.environ["ADN_CONFIG_PATH"] == "/tmp/test.yaml"
        assert os.environ["EXISTING"] == "already"
        del os.environ["ADN_CONFIG_PATH"]
