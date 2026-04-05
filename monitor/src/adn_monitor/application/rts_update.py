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

"""Real-time timeslot update from GROUP VOICE / PRIVATE VOICE START/END (same CSV shape)."""

from __future__ import annotations

import time

from .alias_service import AliasService
from .monitor_controller import MonitorState


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

    # INGRESS = pre-loop debug only (adn-server); do not update CTABLE chips / Linked systems / Active QSO.
    if call_type == "GROUP VOICE" and action == "INGRESS":
        return

    if system in ctable.get("MASTERS", {}):
        for peer in ctable["MASTERS"][system]["PEERS"]:
            crxstatus = "RX" if source_peer == peer else "TX"
            peer_ts = ctable["MASTERS"][system]["PEERS"][peer][time_slot]
            if action == "START":
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
                peer_ts["TS"] = False
                peer_ts["TYPE"] = peer_ts["SUB"] = peer_ts["CALL"] = ""
                peer_ts["SRC"] = peer_ts["DEST"] = peer_ts["TG"] = peer_ts["TRX"] = ""

    # One logical call uses the same stream_id on every OBP row (RX on ingress, TX on each dest).
    # END,RX only names the ingress system; per-row END,TX can be missing. Clear this stream_id
    # everywhere so TX chips do not outlive RX.
    if call_type == "GROUP VOICE" and action == "END" and trx == "RX":
        for _obn in list((ctable.get("OPENBRIDGES") or {}).keys()):
            (ctable["OPENBRIDGES"][_obn].get("STREAMS") or {}).pop(stream_id, None)

    if system in ctable.get("OPENBRIDGES", {}):
        streams = ctable["OPENBRIDGES"][system]["STREAMS"]
        if action == "START":
            tg_str = f"{destination}"
            # Report server may emit multiple START lines with different stream_id for the same
            # logical stream; keep one entry per (TRX, callsign, TG) so OPENBRIDGES.STREAMS does not grow duplicates.
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
            peer_ts["TS"] = False
            peer_ts["TYPE"] = peer_ts["SUB"] = peer_ts["CALL"] = ""
            peer_ts["SRC"] = peer_ts["DEST"] = peer_ts["TG"] = peer_ts["TRX"] = ""
