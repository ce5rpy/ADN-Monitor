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
    """Update PEER_OPTIONS and CTABLE static TG lists. Returns True if CTABLE changed."""
    state.PEER_OPTIONS.clear()
    for row in rows:
        if len(row) < 2:
            continue
        dmr_int = dmr_id_to_int(row[0])
        if dmr_int is None:
            continue
        state.PEER_OPTIONS[dmr_int] = parse_options_to_static(row[1])
    changed = False
    for sys_name in state.CTABLE.get("MASTERS", {}):
        peers = state.CTABLE["MASTERS"][sys_name].get("PEERS", {})
        for peer_id in peers:
            if peer_id not in state.PEER_OPTIONS:
                continue
            po = state.PEER_OPTIONS[peer_id]
            peer = peers[peer_id]
            ts1 = po.get("TS1_STATIC") or []
            ts2 = po.get("TS2_STATIC") or []
            if peer.get("TS1_STATIC") != ts1 or peer.get("TS2_STATIC") != ts2:
                peer["TS1_STATIC"] = ts1
                peer["TS2_STATIC"] = ts2
                changed = True
    return changed
