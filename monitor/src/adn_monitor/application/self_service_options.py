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
