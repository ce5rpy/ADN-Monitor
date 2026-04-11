# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Slim CTABLE slices and semantic fingerprints for WebSocket deduplication."""

from __future__ import annotations

import copy
import json
from typing import Any


def _dict_keys_str(obj: Any) -> Any:
    """Recursively stringify dict keys so json.dumps(sort_keys=True) never compares int vs str."""
    if isinstance(obj, dict):
        return {str(k): _dict_keys_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_dict_keys_str(x) for x in obj]
    if isinstance(obj, tuple):
        return tuple(_dict_keys_str(x) for x in obj)
    return obj


def _fingerprint_dumps(payload: Any) -> str:
    return json.dumps(_dict_keys_str(payload), sort_keys=True, default=str)


def ctable_for_lnksys(ctable: dict[str, Any]) -> dict[str, Any]:
    """Linked Systems / Static TG: masters + homebrew peers (no OPENBRIDGES)."""
    return {
        "MASTERS": ctable.get("MASTERS", {}),
        "PEERS": ctable.get("PEERS", {}),
    }


def ctable_for_opb(ctable: dict[str, Any]) -> dict[str, Any]:
    """OpenBridge page: OPENBRIDGES only."""
    return {"OPENBRIDGES": ctable.get("OPENBRIDGES", {})}


def ctable_for_main(ctable: dict[str, Any]) -> dict[str, Any]:
    """Dashboard / ActiveQsoBox: masters, XLX/homebrew peers, openbridge streams."""
    return {
        "MASTERS": ctable.get("MASTERS", {}),
        "PEERS": ctable.get("PEERS", {}),
        "OPENBRIDGES": ctable.get("OPENBRIDGES", {}),
    }


def opb_semantic_fingerprint(ctable: dict[str, Any], dbridges: bool) -> str:
    """Stable hash input for OpenBridge ``o`` messages (ignore stream timeout churn)."""
    ob = copy.deepcopy(ctable.get("OPENBRIDGES", {}))
    for _sys_name in ob:
        sys_ob = ob[_sys_name]
        if not isinstance(sys_ob, dict):
            continue
        streams = sys_ob.get("STREAMS") or {}
        for sid in list(streams.keys()):
            ent = streams[sid]
            if isinstance(ent, (list, tuple)) and len(ent) >= 3:
                streams[sid] = [ent[0], ent[1], ent[2]]
    return _fingerprint_dumps({"ctable": {"OPENBRIDGES": ob}, "dbridges": dbridges})


def main_dashboard_semantic_fingerprint(lastheard: list, ctable: dict[str, Any]) -> str:
    """Stable string for dedup of WebSocket ``i`` (Dashboard): lastheard + view without TIMEOUT / stream ts."""
    cm = copy.deepcopy(ctable_for_main(ctable))
    for _sn, master in (cm.get("MASTERS") or {}).items():
        if not isinstance(master, dict):
            continue
        for _pid, peer in (master.get("PEERS") or {}).items():
            if not isinstance(peer, dict):
                continue
            for ts in (1, 2, "1", "2"):
                if ts not in peer:
                    continue
                ent = peer[ts]
                if isinstance(ent, dict) and "TIMEOUT" in ent:
                    del ent["TIMEOUT"]
    for _sys, pobj in (cm.get("PEERS") or {}).items():
        if not isinstance(pobj, dict):
            continue
        for ts in (1, 2, "1", "2"):
            if ts not in pobj:
                continue
            ent = pobj[ts]
            if isinstance(ent, dict) and "TIMEOUT" in ent:
                del ent["TIMEOUT"]
    for _ob_name, ob in (cm.get("OPENBRIDGES") or {}).items():
        if not isinstance(ob, dict):
            continue
        streams = ob.get("STREAMS") or {}
        for sid in list(streams.keys()):
            ent = streams[sid]
            if isinstance(ent, (list, tuple)) and len(ent) >= 3:
                streams[sid] = [ent[0], ent[1], ent[2]]
    return _fingerprint_dumps({"lastheard": lastheard, "ctable": cm})
