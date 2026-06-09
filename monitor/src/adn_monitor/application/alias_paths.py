"""Resolve alias file directory from config."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def resolve_alias_files_dir(files_config: dict[str, Any], monitor_root: Path) -> str:
    base = str(files_config.get("PATH", "./json")).strip() or "./json"
    base_p = Path(base)
    if not base_p.is_absolute():
        base_p = monitor_root / base_p
    path = base_p.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return str(path).rstrip("/") + "/"
