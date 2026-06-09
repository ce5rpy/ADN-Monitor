"""Load project root ``.env`` into ``os.environ`` (unset keys only)."""

from __future__ import annotations

import os
from pathlib import Path


def load_project_env(monitor_root: Path | None = None) -> Path | None:
    """
    Load ``<repo>/.env`` if present. *monitor_root* is the ``monitor/`` directory.
    Returns the path loaded, or None.
    """
    root = (monitor_root or Path(__file__).resolve().parents[3]).parent
    env_path = root / ".env"
    if not env_path.is_file():
        return None
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, sep, val = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val
    return env_path
