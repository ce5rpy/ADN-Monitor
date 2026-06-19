"""VERSION file and CLI --version."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from adn_monitor import __version__, read_version, repo_root


def test_read_version_matches_pyproject():
    root = repo_root()
    pyproject = root / "pyproject.toml"
    assert pyproject.is_file()
    text = pyproject.read_text(encoding="utf-8")
    import re

    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert m, "project.version in pyproject.toml"
    assert read_version() == m.group(1)
    assert __version__ == read_version()


def test_monitor_cli_version():
    monitor_py = Path(__file__).resolve().parents[1] / "monitor.py"
    proc = subprocess.run(
        [sys.executable, str(monitor_py), "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stdout.strip() == f"adn-monitor {read_version()}"


def test_adn_monitor_module_version():
    proc = subprocess.run(
        [sys.executable, "-m", "adn_monitor.cli", "--version"],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
    )
    assert proc.stdout.strip() == f"adn-monitor {read_version()}"
