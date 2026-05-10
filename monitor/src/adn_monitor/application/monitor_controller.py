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

"""Main monitor controller: process report messages and coordinate use cases."""

from __future__ import annotations

import json
import logging
import time
from collections import deque
from ..domain import Failure, ReportProtocolError, ServerMode, Success, unwrap_or
from ..domain.value_objects import Opcode
from .alias_service import AliasService
from .ports import (
    AliasRepository,
    BroadcastPort,
    LastHeardRepository,
    ReportPayloadDecoder,
    TgCountRepository,
)
from .time_utils import format_display_datetime, format_utc_naive_datetime, time_str

logger = logging.getLogger("adn-monitor")

# Orphan START rows in sys_dict: must survive long PTTs (same cap as clean_sys_dict).
# A prior 3s threshold deleted active calls' START before END arrived → no match, wrong LH.
SYS_DICT_MAX_ENTRIES = 20_000
SYS_DICT_MAX_AGE_SEC = 300


def _apply_config_to_state(
    state: MonitorState,
    config_dict: dict,
    config_global: dict,
) -> None:
    """Apply decoded CONFIG to state (build/update CTABLE). Single responsibility."""
    state.CONFIG = config_dict
    state.CONFIG_RX = format_display_datetime(time.time(), config_global)
    if state.CTABLE["MASTERS"]:
        update_hblink_table(state.CONFIG, state.CTABLE, time_str, config_global)
    else:
        build_hblink_table(state.CONFIG, state.CTABLE, time_str, config_global)


def _apply_bridges_to_state(
    state: MonitorState,
    bridges_dict: dict,
    config_global: dict,
) -> None:
    """Apply decoded BRIDGES to state (BTABLE, tgstats). Single responsibility."""
    state.BRIDGES = bridges_dict
    state.BRIDGES_RX = format_display_datetime(time.time(), config_global)
    if config_global.get("BRDG_INC"):
        state.BTABLE["BRIDGES"] = build_bridge_table(state.BRIDGES, time.time())
    build_tgstats(state)


def _ctable_counts(state: MonitorState) -> tuple[int, int, int]:
    """Return (MASTERS count, PEERS count, OPENBRIDGES count) for logging."""
    return (
        len(state.CTABLE.get("MASTERS", {})),
        len(state.CTABLE.get("PEERS", {})),
        len(state.CTABLE.get("OPENBRIDGES", {})),
    )


class MonitorState:
    """Mutable in-memory state for CTABLE, BTABLE, CONFIG, BRIDGES, log buffer."""

    def __init__(
        self,
        lastheard_log_rows: int = 70,
        empty_masters: bool = False,
        brdg_inc: bool = False,
    ) -> None:
        self.CONFIG: dict = {}
        self.CTABLE: dict = {
            "MASTERS": {},
            "PEERS": {},
            "OPENBRIDGES": {},
            "SETUP": {"LASTHEARD": True},
        }
        self.BTABLE: dict = {"BRIDGES": {}, "SETUP": {}}
        self.BRIDGES: dict = {}
        self.CONFIG_RX = ""
        self.BRIDGES_RX = ""
        self.LOGBUF: deque = deque(100 * [""], 100)
        self.lastheard_log_rows = lastheard_log_rows
        self.empty_masters = empty_masters
        self.brdg_inc = brdg_inc
        self.sys_dict: dict = {"lst_clean": 0}
        # Per-peer static TG from Clients.options (self-service DB); int_id -> {TS1_STATIC, TS2_STATIC}
        self.PEER_OPTIONS: dict = {}
        self.server_mode: ServerMode = ServerMode.LEGACY
        self.server_info: dict = {}


def process_message(
    raw_message: bytes,
    state: MonitorState,
    alias_svc: AliasService,
    alias_repo: AliasRepository,
    lastheard_repo: LastHeardRepository,
    tgcount_repo: TgCountRepository,
    broadcast: BroadcastPort | None,
    config_global: dict,
    report_decoder: ReportPayloadDecoder,
) -> Success[None] | Failure[ReportProtocolError]:
    """Dispatch by opcode and update state. Returns Result for protocol errors."""
    try:
        message = raw_message.decode("utf-8", "ignore")
    except Exception as e:
        return Failure(ReportProtocolError(str(e)))
    opcode = Opcode.from_message(raw_message)

    if opcode.value == Opcode.CONFIG_SND:
        if not hasattr(state, "CONFIG"):
            logger.error("CONFIG_SND: state is not MonitorState (got %s), skipping", type(state).__name__)
            return Success(None)
        decode_result = report_decoder.decode_config(raw_message)
        config_dict = unwrap_or(decode_result, {})
        _apply_config_to_state(state, config_dict, config_global)
        n_m, n_p, n_o = _ctable_counts(state)
        logger.info("(REPORT) CONFIG applied: CTABLE MASTERS=%d PEERS=%d OPENBRIDGES=%d", n_m, n_p, n_o)
        return Success(None)

    if opcode.value == Opcode.BRIDGE_SND:
        if not hasattr(state, "BRIDGES"):
            logger.error("BRIDGE_SND: state is not MonitorState (got %s), skipping", type(state).__name__)
            return Success(None)
        decode_result = report_decoder.decode_bridges(raw_message)
        bridges_dict = unwrap_or(decode_result, {})
        _apply_bridges_to_state(state, bridges_dict, config_global)
        n_brg = len(state.BTABLE.get("BRIDGES", {}))
        logger.info("(REPORT) BRIDGES applied: BTABLE BRIDGES=%d", n_brg)
        return Success(None)

    if opcode.value == Opcode.LINK_EVENT:
        return Success(None)

    if opcode.value == Opcode.HELLO:
        if not hasattr(state, "server_mode"):
            logger.warning("HELLO: state has no server_mode attribute; skipping")
            return Success(None)
        try:
            info = json.loads(raw_message[1:].decode("utf-8", errors="replace") or "{}")
            if not isinstance(info, dict):
                info = {}
        except Exception as e:
            logger.warning("(REPORT) HELLO payload not valid JSON (%s); mode=v2 empty info", e)
            info = {}
        state.server_mode = ServerMode.V2
        state.server_info = info
        logger.info("(REPORT) HELLO received: mode=v2 server=%s version=%s features=%s",
                    info.get("server"), info.get("version"), info.get("features"))
        return Success(None)

    if opcode.value == Opcode.BRDG_EVENT:
        parts = message[1:].split(",")
        if len(parts) < 9:
            logger.debug("(REPORT) BRDG_EVENT ignored: parts len=%d (need >= 9)", len(parts))
            return Success(None)
        if not isinstance(state, MonitorState) or not getattr(state, "CTABLE", None):
            logger.warning("(REPORT) BRDG_EVENT ignored: state or CTABLE missing")
            return Success(None)
        logger.debug("(REPORT) BRDG_EVENT parts[0]=%s parts[1]=%s parts[2]=%s", parts[0], parts[1], parts[2])
        # Ensure aliases in cache (async in original: db2dict)
        alias_repo.ensure_subscriber_in_cache(int(parts[6]))
        alias_repo.ensure_talkgroup_in_cache(int(parts[8]))
        if parts[0] in ("GROUP VOICE", "PRIVATE VOICE"):
            _event_ts = time.time()
            rts_update(
                parts,
                state,
                alias_svc,
                time_str,
            )
            skip_persist = parts[2] == "TX" or parts[5] in config_global.get("OPB_FILTER", [])
            if skip_persist:
                logger.debug("(REPORT) BRDG_EVENT GROUP VOICE skip persist: dir=%s src=%s", parts[2], parts[5])
            _now = format_display_datetime(_event_ts, config_global, with_tz_abbr=True)
            _wall_db = format_utc_naive_datetime(_event_ts)
            reported_dur = float(parts[9]) if len(parts) > 9 else 0.0
            duration_sec = int(reported_dur)
            if parts[1] == "INGRESS":
                log_message = _format_log_message(_now, parts, alias_svc, None)
            elif parts[1] == "END" and parts[4] in state.sys_dict and state.sys_dict[parts[4]]["sys"] == parts[3]:
                _sd = state.sys_dict[parts[4]]
                del state.sys_dict[parts[4]]
                if not skip_persist:
                    # Server may send 0.00 on quench/loop/BCSQ; use wall time since START on this monitor.
                    wall_dur = max(0.0, _event_ts - _sd["timeST"])
                    merged_dur = max(reported_dur, wall_dur)
                    duration_sec = int(merged_dur)
                    if config_global.get("TGC_INC") and merged_dur > 5:
                        tgcount_repo.insert_tgcount(parts[8], parts[6], str(int(merged_dur)))
                        logger.debug("(REPORT) BRDG_EVENT saved tgcount tg=%s dmr=%s", parts[8], parts[6])
                    if config_global.get("LH_INC"):
                        # lstheard_log (Last Heard page): all calls
                        lastheard_repo.insert_lstheard_log(
                            merged_dur,
                            parts[0],
                            parts[3],
                            int(parts[8]),
                            int(parts[6]),
                            wall_date_time=_wall_db,
                        )
                        # Dashboard table only: minimum duration (seconds); Last Heard page always shows all
                        min_duration = config_global.get("DASHBOARD_MIN_DURATION", 3)
                        if merged_dur >= min_duration:
                            lastheard_repo.insert_last_heard(
                                merged_dur,
                                parts[0],
                                parts[3],
                                int(parts[8]),
                                int(parts[6]),
                                wall_date_time=_wall_db,
                            )
                        logger.debug("(REPORT) BRDG_EVENT saved lastheard sys=%s tg=%s dmr=%s", parts[3], parts[8], parts[6])
                if not state.sys_dict["lst_clean"] or time.time() - state.sys_dict["lst_clean"] >= 3:
                    state.sys_dict["lst_clean"] = time.time()
                    for k, v in list(state.sys_dict.items()):
                        if k == "lst_clean":
                            continue
                        if time.time() - v["timeST"] >= SYS_DICT_MAX_AGE_SEC:
                            del state.sys_dict[k]
                log_message = _format_log_message(_now, parts, alias_svc, duration_sec)
            elif parts[1] == "START":
                log_message = _format_log_message(_now, parts, alias_svc, None)
                if not skip_persist:
                    # Same time base as _event_ts on END so duration merge is consistent.
                    state.sys_dict[parts[4]] = {"sys": parts[3], "timeST": _event_ts}
            elif parts[1] == "END":
                log_message = _format_log_message(_now, parts, alias_svc, duration_sec)
                # Not the matched branch above (no START, or sys/stream mismatch): still persist RX from server.
                if not skip_persist and config_global.get("LH_INC"):
                    lastheard_repo.insert_lstheard_log(
                        reported_dur,
                        parts[0],
                        parts[3],
                        int(parts[8]),
                        int(parts[6]),
                        wall_date_time=_wall_db,
                    )
                    min_duration = config_global.get("DASHBOARD_MIN_DURATION", 3)
                    if reported_dur >= min_duration:
                        lastheard_repo.insert_last_heard(
                            reported_dur,
                            parts[0],
                            parts[3],
                            int(parts[8]),
                            int(parts[6]),
                            wall_date_time=_wall_db,
                        )
            elif parts[1] == "END WITHOUT MATCHING START":
                log_message = _format_log_message_unknown_end(_now, parts, alias_svc)
            else:
                log_message = f"{_now[10:19]} Unknown voice bridge log message ({parts[0]})."
            state.LOGBUF.append(log_message)
            logger.info("(VOICE) %s", log_message)
            if broadcast:
                broadcast.broadcast("l" + log_message, "log")
        elif parts[0] == "UNIT DATA HEADER" and parts[2] != "TX" and parts[5] not in config_global.get("OPB_FILTER", []):
            _u_ts = time.time()
            _u_utc = format_utc_naive_datetime(_u_ts)
            lastheard_repo.insert_last_heard(
                None, parts[0], parts[3], int(parts[8]), int(parts[6]), wall_date_time=_u_utc
            )
            lastheard_repo.insert_lstheard_log(
                None, parts[0], parts[3], int(parts[8]), int(parts[6]), wall_date_time=_u_utc
            )
        return Success(None)

    if opcode.value == Opcode.SERVER_MSG:
        return Success(None)

    return Failure(ReportProtocolError(f"Unknown opcode: {repr(opcode.value)}"))


def _format_log_message(
    now: str,
    p: list[str],
    alias_svc: AliasService,
    duration_sec: int | None,
) -> str:
    sub_short = alias_svc.alias_short(int(p[6]))
    tg_name = alias_svc.alias_tgid(int(p[8]))
    base = (
        f"{now[10:19]} {p[0][6:]:5.5s} {p[1]:7.7s} {p[2]:2.2s} SYS: {p[3]:10.10s} STREAM: {p[4]} SRC_ID: {p[5]:5.5s} "
        f"TS: {p[7]} TGID: {p[8]:7.7s} {tg_name:17.17s} "
        f"SUB: {p[6]:9.9s}; {sub_short:18.18s}"
    )
    if duration_sec is not None:
        return base + f" Time: {duration_sec}s"
    return base


def _format_log_message_unknown_end(now: str, p: list[str], alias_svc: AliasService) -> str:
    sub_short = alias_svc.alias_short(int(p[6]))
    tg_name = alias_svc.alias_tgid(int(p[8]))
    return (
        f"{now[10:19]} {p[0][6:]:5.5s} {p[1]:5.5s} {p[2]:2.2s} on SYSTEM: {p[3]:10.10s} STREAM: {p[4]} SRC_ID: {p[5]:5.5s} "
        f"TS: {p[7]} TGID: {p[8]:7.7s} {tg_name:17.17s} "
        f"SUB: {p[6]:9.9s}; {sub_short:18.18s}"
    )


def clean_sys_dict(state: MonitorState) -> None:
    """Remove stale and excess entries from state.sys_dict to prevent memory growth.
    Call periodically (e.g. every 60s); BRDG_EVENT END cleanup alone is not sufficient."""
    # TODO: remove after validating memory fix (MEMORY_LEAK_ANALYSIS.md)
    n_sys = len([k for k in state.sys_dict if k != "lst_clean"])
    logger.info("(monitor) sys_dict size: %d entries", n_sys)
    now = time.time()
    to_del = [
        k for k, v in state.sys_dict.items()
        if k != "lst_clean" and isinstance(v, dict) and (now - v.get("timeST", 0) >= SYS_DICT_MAX_AGE_SEC)
    ]
    for k in to_del:
        del state.sys_dict[k]
    if to_del:
        logger.info("(monitor) clean_sys_dict: removed %d stale entries", len(to_del))
    # Hard cap: evict oldest by timeST if over limit
    if len(state.sys_dict) <= SYS_DICT_MAX_ENTRIES + 1:  # +1 for lst_clean
        return
    entries = [(k, v.get("timeST", 0)) for k, v in state.sys_dict.items() if k != "lst_clean" and isinstance(v, dict)]
    entries.sort(key=lambda x: x[1])
    n_evict = len(entries) - SYS_DICT_MAX_ENTRIES
    for k, _ in entries[:n_evict]:
        del state.sys_dict[k]
    logger.info("(monitor) clean_sys_dict: evicted %d entries (cap=%d)", n_evict, SYS_DICT_MAX_ENTRIES)


def int_id(raw: int | bytes) -> int:
    """Normalize peer id from bytes or int."""
    if isinstance(raw, bytes):
        return int.from_bytes(raw[:4], "big") if len(raw) >= 4 else 0
    return int(raw)


def bytes_4(peer_id: int) -> bytes:
    """Peer id as 4-byte big-endian."""
    return peer_id.to_bytes(4, "big")


def build_hblink_table(
    config: dict, stats_table: dict, time_str_fn, config_global: dict | None = None
) -> None:
    """Populate CTABLE from CONFIG (MASTERS, PEERS, OPENBRIDGES)."""
    from .hblink_table import build_hblink_table_impl
    build_hblink_table_impl(config, stats_table, time_str_fn, int_id, config_global)


def update_hblink_table(
    config: dict, stats_table: dict, time_str_fn, config_global: dict | None = None
) -> None:
    """Sync CTABLE with CONFIG (add/remove peers, update connection times)."""
    from .hblink_table import update_hblink_table_impl
    update_hblink_table_impl(config, stats_table, time_str_fn, int_id, bytes_4)


def build_bridge_table(bridges: dict, now: float) -> dict:
    """Build BTABLE from BRIDGES dict."""
    from .bridge_table import build_bridge_table_impl
    return build_bridge_table_impl(bridges, now, int_id)


def build_tgstats(state: MonitorState) -> None:
    """Fill CTABLE SERVER/TS1/TS2 and SINGLE_TS1/SINGLE_TS2 from CONFIG and BRIDGES."""
    from .tgstats import build_tgstats_impl
    build_tgstats_impl(state, time_str)


def rts_update(
    p: list[str],
    state: MonitorState,
    alias_svc: AliasService,
    time_str_fn,
) -> None:
    """Update timeslot state from GROUP VOICE START/END."""
    from .rts_update import rts_update_impl
    rts_update_impl(p, state, alias_svc, time_str_fn)
