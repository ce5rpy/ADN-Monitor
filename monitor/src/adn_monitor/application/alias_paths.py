# ADN Monitor - application alias paths
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
