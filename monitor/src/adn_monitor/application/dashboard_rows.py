"""Format DB rows for WebSocket dashboard payloads."""

from __future__ import annotations

import json
from typing import Any

from .time_utils import format_stored_utc_for_display


def lastheard_rows(result: list[tuple[Any, ...]] | None, conf_global: dict | None) -> list[dict]:
    out = []
    for row in result or []:
        sub = row[7] if len(row) > 7 else None
        if not isinstance(sub, list):
            if isinstance(sub, str):
                try:
                    sub = json.loads(sub)
                except json.JSONDecodeError:
                    sub = [sub]
            else:
                sub = [str(sub)] if sub is not None else []
        out.append({
            "date": format_stored_utc_for_display(row[0], conf_global),
            "qso_time": row[1],
            "qso_type": row[2],
            "system": row[3],
            "tg_num": row[4],
            "tg_callsign": row[5] or "",
            "dmr_id": row[6],
            "subscriber": sub,
        })
    return out


def tgcount_rows(result: list[Any] | None) -> list[dict]:
    if not result:
        return []
    return [
        {
            "tg_num": r[0],
            "name": r[1] or "",
            "qso_count": r[2],
            "qso_time_str": r[3],
            "top_users": list(r[4]),
        }
        for r in result
    ]
