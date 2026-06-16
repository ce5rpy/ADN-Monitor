# ADN Monitor - application self service options
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

"""Parse and format Clients.options strings."""

from __future__ import annotations

OPTIONS_MAX_LENGTH = 4096


def parse_options(options: str) -> dict[str, object]:
    out: dict[str, object] = {
        "TS1": [],
        "TS2": [],
        "DIAL": "0",
        "VOICE": "-1",
        "LANG": "0",
        "SINGLE": "-1",
        "TIMER": "0",
    }
    for part in options.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "TS1":
            out["TS1"] = [] if value == "" else [x.strip() for x in value.split(",") if x.strip()]
        elif key == "TS2":
            out["TS2"] = [] if value == "" else [x.strip() for x in value.split(",") if x.strip()]
        elif key in out:
            out[key] = value
    return out


def normalize_options_for_save(options: str) -> str | None:
    options = options.strip()
    if not options:
        return None
    if not options.endswith(";"):
        options += ";"
    if len(options) > OPTIONS_MAX_LENGTH:
        return None
    return options
