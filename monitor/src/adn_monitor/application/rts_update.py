# ADN Monitor - Dashboard and backend for ADN Systems.
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

"""Real-time timeslot update from GROUP VOICE / PRIVATE VOICE START/END (same CSV shape)."""

from __future__ import annotations

import time

from ..domain.value_objects import ServerMode
from .alias_service import AliasService
from .monitor_controller import MonitorState
from .tgstats import (
    _active_tgid_from_peer_ts,
    _apply_multi_mode_chips,
    _is_echo_service_live_tgid,
    _is_service_voice_tgid,
    _peer_single_mode,
    clear_peer_ua_sessions,
    clear_voice_ts_for_destination,
    lookup_ua_timeout_for_peer,
    register_ua_session,
)
from .time_utils import time_str


def _peer_key_as_int(peer_key) -> int | None:
    try:
        return int(peer_key)
    except (TypeError, ValueError):
        return None


def _peer_keys_equal(source_peer: int, peer_key) -> bool:
    peer_int = _peer_key_as_int(peer_key)
    return peer_int is not None and peer_int == int(source_peer)


def _resolve_master_peer(
    peers: dict,
    source_peer: int,
) -> tuple[int | None, dict | None]:
    """Match voice event peer id to CTABLE peer key (int or bytes)."""
    if source_peer in peers:
        row = peers[source_peer]
        return source_peer, row if isinstance(row, dict) else None
    for peer_key, peer_row in peers.items():
        try:
            peer_int = int(peer_key)
        except (TypeError, ValueError):
            continue
        if peer_int == source_peer and isinstance(peer_row, dict):
            return peer_int, peer_row
    return None, None


def _apply_voice_single_ts(
    state: MonitorState,
    ctable: dict,
    system: str,
    time_slot: int,
    destination: int,
    source_peer: int,
    *,
    trx: str,
) -> None:
    """Track active SINGLE / UA TG on the transmitting peer (RX leg on MASTER)."""
    if trx != "RX" or _is_service_voice_tgid(destination):
        return
    ts_key = f"SINGLE_TS{time_slot}"
    peers = ctable.get("MASTERS", {}).get(system, {}).get("PEERS") or {}
    if not peers:
        return
    peer_id, peer_row = _resolve_master_peer(peers, source_peer)
    if peer_row is None:
        return
    if peer_id is not None:
        register_ua_session(state, system, peer_id, time_slot, destination)
    if peer_id is None:
        return
    if _peer_single_mode(state, system, peer_id):
        existing = peer_row.get(ts_key) if isinstance(peer_row.get(ts_key), dict) else {}
        to_str = lookup_ua_timeout_for_peer(state, system, peer_id, time_slot, destination, time_str)
        if not to_str and isinstance(existing, dict):
            to_str = existing.get("TO", "") if isinstance(existing.get("TO"), str) else ""
        peer_row[ts_key] = {"TGID": destination, "TO": to_str}
        return
    _apply_multi_mode_chips(state, system, peer_id, peer_row)


def _static_tg_slot_for_peer(peer_row: dict, destination: int, event_slot: int) -> int:
    """Map wire timeslot to the peer chip that lists this TG in OPTIONS (TS1/TS2)."""
    tg = str(destination)
    ts1 = [str(x).strip() for x in (peer_row.get("TS1_STATIC") or []) if str(x).strip()]
    ts2 = [str(x).strip() for x in (peer_row.get("TS2_STATIC") or []) if str(x).strip()]
    in_ts1 = tg in ts1
    in_ts2 = tg in ts2
    if in_ts1 and not in_ts2:
        return 1
    if in_ts2 and not in_ts1:
        return 2
    return event_slot


def _is_master_peer_row(system: str) -> bool:
    """Inject-proxy CTABLE row (``SYSTEM-3``): one hotspot radio per upstream slot."""
    if "-" not in system:
        return False
    base, suffix = system.rsplit("-", 1)
    return bool(base) and suffix.isdigit()


def voice_event_skip_master_downlink_log(parts: list[str], ctable: dict) -> bool:
    """True when a MASTER downlink leg should update chips only (no duplicate log line).

    The server announces one call; remapped ``SYSTEM-N`` TX fan-out must not emit
    one log row per connected hotspot.
    """
    if len(parts) < 4 or parts[1] not in ("START", "END") or parts[2] != "TX":
        return False
    system = parts[3]
    if system in ctable.get("OPENBRIDGES", {}):
        return False
    if _is_master_peer_row(system):
        return True
    return system in ctable.get("MASTERS", {})


def _peer_static_lists_include_tg(peer_row: dict, destination: int) -> bool:
    tg = str(destination)
    ts1 = [str(x).strip() for x in (peer_row.get("TS1_STATIC") or []) if str(x).strip()]
    ts2 = [str(x).strip() for x in (peer_row.get("TS2_STATIC") or []) if str(x).strip()]
    return tg in ts1 or tg in ts2


def _peer_slot_busy_other_tg(peer_ts: dict, destination: int) -> bool:
    active = _active_tgid_from_peer_ts(peer_ts)
    return active is not None and int(active) != int(destination)


def _peer_row_shows_destination(peer_row: dict, destination: int) -> bool:
    for slot in (1, 2):
        peer_ts = peer_row.get(slot)
        if isinstance(peer_ts, dict) and _active_tgid_from_peer_ts(peer_ts) == destination:
            return True
    return False


def _voice_event_target_peers(
    system: str,
    peers: dict,
    *,
    action: str,
    trx: str,
    source_peer: int,
    source_sub: int,
    call_type: str,
    event_slot: int,
    destination: int,
) -> list[tuple[int | bytes, dict]]:
    """Peers whose CTABLE chips this voice event should touch."""
    if action == "END":
        if trx == "RX":
            peer_id, peer_row = _resolve_master_peer(peers, source_peer)
            if peer_row is not None and peer_id is not None:
                return [(peer_id, peer_row)]
            return []
        if _is_master_peer_row(system):
            return [
                (peer_key, peer_row)
                for peer_key, peer_row in peers.items()
                if isinstance(peer_row, dict) and _peer_row_shows_destination(peer_row, destination)
            ]
        if _is_echo_service_live_tgid(destination):
            svc_id, svc_row = _resolve_master_peer(peers, destination)
            if svc_row is not None and svc_id is not None:
                return [(svc_id, svc_row)]
            sub_id, sub_row = _resolve_master_peer(peers, source_sub)
            if sub_row is not None and sub_id is not None:
                return [(sub_id, sub_row)]
            return []
        return [
            (peer_key, peer_row)
            for peer_key, peer_row in peers.items()
            if isinstance(peer_row, dict)
            and (
                _peer_row_shows_destination(peer_row, destination)
                or (
                    not _peer_keys_equal(source_peer, peer_key)
                    and _peer_static_lists_include_tg(peer_row, destination)
                )
            )
        ]

    if trx == "RX":
        peer_id, peer_row = _resolve_master_peer(peers, source_peer)
        if peer_row is not None and peer_id is not None:
            return [(peer_id, peer_row)]
        return []

    if _is_master_peer_row(system):
        return [
            (peer_key, peer_row)
            for peer_key, peer_row in peers.items()
            if isinstance(peer_row, dict)
        ]

    if _is_echo_service_live_tgid(destination):
        svc_id, svc_row = _resolve_master_peer(peers, destination)
        if svc_row is not None and svc_id is not None:
            return [(svc_id, svc_row)]
        sub_id, sub_row = _resolve_master_peer(peers, source_sub)
        if sub_row is not None and sub_id is not None:
            return [(sub_id, sub_row)]
        return []

    targets: list[tuple[int | bytes, dict]] = []
    for peer_key, peer_row in peers.items():
        if not isinstance(peer_row, dict):
            continue
        if _peer_keys_equal(source_peer, peer_key):
            continue
        if not _peer_static_lists_include_tg(peer_row, destination):
            continue
        targets.append((peer_key, peer_row))
    return targets


def _peer_display_slot(
    peer_row: dict,
    peer_key,
    *,
    call_type: str,
    source_peer: int,
    event_slot: int,
    destination: int,
    trx: str = "",
) -> int:
    """Timeslot index for CTABLE peer chips (1 or 2)."""
    if _peer_keys_equal(source_peer, peer_key):
        return event_slot
    if (
        call_type == "GROUP VOICE"
        and trx == "TX"
        and _is_echo_service_live_tgid(destination)
    ):
        # Echo/service downlink (bridge TX leg): use wire slot, not OPTIONS static map.
        return event_slot
    if call_type == "GROUP VOICE":
        return _static_tg_slot_for_peer(peer_row, destination, event_slot)
    return event_slot


def rts_update_impl(
    p: list[str],
    state: MonitorState,
    alias_svc: AliasService,
    time_str_fn,
) -> None:
    """Update CTABLE timeslot state from bridge event parts."""
    if not isinstance(state, MonitorState) or not hasattr(state, "CTABLE"):
        return
    call_type = p[0]
    action = p[1]
    trx = p[2]
    system = p[3]
    stream_id = p[4]
    source_peer = int(p[5])
    source_sub = int(p[6])
    time_slot = int(p[7])
    destination = int(p[8])
    timeout = time.time()
    ctable = state.CTABLE
    sub_short = alias_svc.alias_short(source_sub)
    sub_call = alias_svc.alias_call(source_sub)
    tg_dest = f"TG {destination}&nbsp;&nbsp;&nbsp;&nbsp;{alias_svc.alias_tgid(destination)}"
    tg_short = f"TG&nbsp;{destination}"

    # INGRESS: register UA/SINGLE owner early; skip live TRX chips / Active QSO row.
    if call_type == "GROUP VOICE" and action == "INGRESS":
        if system in ctable.get("MASTERS", {}):
            if trx == "RX" and destination == 4000:
                peer_id, _ = _resolve_master_peer(
                    ctable.get("MASTERS", {}).get(system, {}).get("PEERS") or {},
                    source_peer,
                )
                if peer_id is not None:
                    clear_peer_ua_sessions(state, system, peer_id)
            else:
                _apply_voice_single_ts(
                    state, ctable, system, time_slot, destination, source_peer, trx=trx
                )
        return

    if system in ctable.get("MASTERS", {}):
        if (
            call_type == "GROUP VOICE"
            and action == "START"
            and trx == "RX"
            and destination == 4000
        ):
            peer_id, _ = _resolve_master_peer(
                ctable.get("MASTERS", {}).get(system, {}).get("PEERS") or {},
                source_peer,
            )
            if peer_id is not None:
                clear_peer_ua_sessions(state, system, peer_id)
        elif call_type == "GROUP VOICE" and action in ("START", "END"):
            if not (action == "START" and trx == "RX" and destination == 4000):
                _apply_voice_single_ts(
                    state, ctable, system, time_slot, destination, source_peer, trx=trx
                )
        for peer, peer_row in _voice_event_target_peers(
            system,
            ctable["MASTERS"][system]["PEERS"],
            action=action,
            trx=trx,
            source_peer=source_peer,
            source_sub=source_sub,
            call_type=call_type,
            event_slot=time_slot,
            destination=destination,
        ):
            display_slot = _peer_display_slot(
                peer_row,
                peer,
                call_type=call_type,
                source_peer=source_peer,
                event_slot=time_slot,
                destination=destination,
                trx=trx,
            )
            crxstatus = "RX" if _peer_keys_equal(source_peer, peer) else "TX"
            peer_ts = peer_row[display_slot]
            if action == "START":
                if (
                    peer_ts.get("TS")
                    and not _is_echo_service_live_tgid(destination)
                    and _peer_slot_busy_other_tg(peer_ts, destination)
                ):
                    continue
                # Local PTT (TRX=RX / red): do not replace with another peer's downlink (TRX=TX / green).
                if (
                    peer_ts.get("TS")
                    and peer_ts.get("TRX") == "RX"
                    and not _peer_keys_equal(source_peer, peer)
                    and not _is_echo_service_live_tgid(destination)
                ):
                    continue
                peer_ts["TIMEOUT"] = timeout
                peer_ts["TS"] = True
                peer_ts["TYPE"] = call_type
                peer_ts["SUB"] = f"{sub_short} ({source_sub})"
                peer_ts["CALL"] = sub_call
                peer_ts["SRC"] = peer
                peer_ts["DEST"] = tg_dest
                peer_ts["TG"] = tg_short
                peer_ts["TRX"] = crxstatus
            elif action == "END":
                clear_voice_ts_for_destination(peer_row, destination)

    server_mode = getattr(state, "server_mode", ServerMode.LEGACY)
    if system in ctable.get("OPENBRIDGES", {}):
        streams = ctable["OPENBRIDGES"][system]["STREAMS"]
        if server_mode == ServerMode.V2:
            if action == "START":
                tg_str = f"{destination}"
                for sid in list(streams):
                    if sid == stream_id:
                        continue
                    ent = streams[sid]
                    if not isinstance(ent, (list, tuple)) or len(ent) < 3:
                        continue
                    if ent[0] == trx and ent[1] == sub_call and ent[2] == tg_str:
                        del streams[sid]
                streams[stream_id] = (trx, sub_call, tg_str, timeout)
            elif action == "END" and stream_id in streams:
                ent = streams.get(stream_id)
                if isinstance(ent, (list, tuple)) and len(ent) >= 1 and ent[0] == trx:
                    del streams[stream_id]
        else:
            if action == "START":
                streams[stream_id] = (trx, sub_call, f"{destination}", timeout)
            elif action == "END" and stream_id in streams:
                del streams[stream_id]

    if system in ctable.get("PEERS", {}):
        prxstatus = "RX" if trx == "RX" else "TX"
        peer_ts = ctable["PEERS"][system][time_slot]
        if action == "START":
            peer_ts["TIMEOUT"] = timeout
            peer_ts["TS"] = True
            peer_ts["SUB"] = f"{sub_short} ({source_sub})"
            peer_ts["CALL"] = sub_call
            peer_ts["SRC"] = source_peer
            peer_ts["DEST"] = tg_dest
            peer_ts["TG"] = tg_short
            peer_ts["TRX"] = prxstatus
        elif action == "END":
            clear_voice_ts_for_destination(ctable["PEERS"][system], destination)
