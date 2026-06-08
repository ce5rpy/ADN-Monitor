# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
# HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
# hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
# HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
# Original works and this derivative are under GPLv3.

"""Build TG stats (SERVER TS1/TS2, SINGLE_TS1/SINGLE_TS2) for CTABLE."""

from __future__ import annotations

from .monitor_controller import MonitorState


def parse_options_to_static(options_str: str | None) -> dict:
    """Parse Clients.options string (e.g. TS1=1,2;TS2=730,7304;TIMER=15;) into TS1_STATIC/TS2_STATIC lists."""
    out: dict = {"TS1_STATIC": [], "TS2_STATIC": []}
    if not options_str or not isinstance(options_str, str):
        return out
    for part in options_str.strip().split(";"):
        part = part.strip()
        if part.upper().startswith("TS1=") and len(part) > 4:
            out["TS1_STATIC"] = [x.strip() for x in part[4:].split(",") if x.strip()]
        elif part.upper().startswith("TS2=") and len(part) > 4:
            out["TS2_STATIC"] = [x.strip() for x in part[4:].split(",") if x.strip()]
    return out


def _tgid_to_int(raw) -> int:
    """Normalize TGID from int, str, or bytes (e.g. BRIDGES pickle)."""
    if isinstance(raw, int):
        return raw
    if isinstance(raw, bytes):
        return int.from_bytes(raw[:4], "big") if len(raw) >= 4 else 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def build_tgstats_impl(state: MonitorState, time_str_fn) -> None:
    """Fill CTABLE SERVER and per-peer SINGLE_TS1/SINGLE_TS2 from CONFIG and BRIDGES."""
    config = state.CONFIG
    ctable = state.CTABLE
    bridges = state.BRIDGES
    if not config or not ctable:
        return
    ctable["SERVER"] = {"TS1": [], "TS2": []}
    tmp_dict = {}
    for system in ctable.get("MASTERS", {}):
        if not ctable["MASTERS"][system].get("PEERS"):
            continue
        for peer in ctable["MASTERS"][system]["PEERS"]:
            if peer == 4294967295:
                continue
            if system not in tmp_dict:
                tmp_dict[system] = [peer]
            else:
                tmp_dict[system].append(peer)
    srv_info = 0
    for system in config:
        if system not in tmp_dict:
            continue
        if not srv_info and "_default_options" in config[system]:
            ctable["SERVER"]["SINGLE_MODE"] = config[system].get("SINGLE_MODE", False)
            for item in (config[system].get("_default_options") or "").split(";")[:2]:
                if len(item) > 11 and item.startswith("TS1_STATIC="):
                    ctable["SERVER"]["TS1"] = item[11:].split(",")
                if len(item) > 11 and item.startswith("TS2_STATIC="):
                    ctable["SERVER"]["TS2"] = item[11:].split(",")
            srv_info = 1
        for peer in ctable["MASTERS"][system]["PEERS"]:
            ctable["MASTERS"][system]["PEERS"][peer]["SINGLE_TS1"] = {"TGID": "", "TO": ""}
            ctable["MASTERS"][system]["PEERS"][peer]["SINGLE_TS2"] = {"TGID": "", "TO": ""}
            peer_key = peer.to_bytes(4, "big") if isinstance(peer, int) else peer
            peer_cfg = config[system].get("PEERS", {}).get(peer_key, {})
            ts1 = peer_cfg.get("TS1_STATIC") if isinstance(peer_cfg, dict) else None
            ts2 = peer_cfg.get("TS2_STATIC") if isinstance(peer_cfg, dict) else None
            if not ts1 and not ts2:
                ts1 = config[system].get("TS1_STATIC")
                ts2 = config[system].get("TS2_STATIC")
            ctable["MASTERS"][system]["PEERS"][peer]["TS1_STATIC"] = (
                [x.strip() for x in ts1.split(",") if x.strip()]
                if isinstance(ts1, str)
                else (ts1 if isinstance(ts1, list) else [])
            )
            ctable["MASTERS"][system]["PEERS"][peer]["TS2_STATIC"] = (
                [x.strip() for x in ts2.split(",") if x.strip()]
                if isinstance(ts2, str)
                else (ts2 if isinstance(ts2, list) else [])
            )
            # Override with per-peer options from self-service DB (Clients.options)
            # Always apply when peer in PEER_OPTIONS, including empty lists (clears removed TGs)
            peer_opts = getattr(state, "PEER_OPTIONS", None) or {}
            if peer in peer_opts:
                ctable["MASTERS"][system]["PEERS"][peer]["TS1_STATIC"] = peer_opts[peer].get("TS1_STATIC") or []
                ctable["MASTERS"][system]["PEERS"][peer]["TS2_STATIC"] = peer_opts[peer].get("TS2_STATIC") or []
    for bridge_name in bridges or []:
        for system in bridges[bridge_name]:
            if not system.get("ACTIVE") or (system.get("SYSTEM") or "")[:3] == "OBP" or system.get("TO_TYPE") == "OFF":
                continue
            sys_name = system["SYSTEM"]
            if sys_name not in tmp_dict:
                continue
            ts_key = f"SINGLE_TS{system['TS']}"
            tgid = _tgid_to_int(system["TGID"])
            to_str = time_str_fn(system.get("TIMER", 0), "to")
            for peer in ctable["MASTERS"][sys_name]["PEERS"]:
                ctable["MASTERS"][sys_name]["PEERS"][peer][ts_key] = {"TGID": tgid, "TO": to_str}
