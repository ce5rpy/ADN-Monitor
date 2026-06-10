"""Merge Clients.options into in-memory CTABLE (static TG display)."""

from __future__ import annotations

from typing import Any

from .monitor_controller import MonitorState
from .tgstats import parse_options_to_static


def dmr_id_to_int(dmr_id: Any) -> int | None:
    if dmr_id is None:
        return None
    if isinstance(dmr_id, int):
        return dmr_id
    if isinstance(dmr_id, (bytes, bytearray)) and len(dmr_id) >= 4:
        return int.from_bytes(dmr_id[:4], "big")
    try:
        return int(dmr_id)
    except (TypeError, ValueError):
        return None


def apply_peer_options_rows(state: MonitorState, rows: list[tuple[Any, ...]]) -> bool:
    """Cache Clients.options for admin UI; CTABLE chips use server CONFIG OPTIONS only."""
    state.PEER_OPTIONS.clear()
    for row in rows:
        if len(row) < 2:
            continue
        dmr_int = dmr_id_to_int(row[0])
        if dmr_int is None:
            continue
        state.PEER_OPTIONS[dmr_int] = parse_options_to_static(row[1])
    return False
