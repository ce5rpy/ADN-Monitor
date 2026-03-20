#!/usr/bin/env python3

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

"""
ADN Systems Monitor

Dependencies: monitor/ + src/adn_monitor (config and logging in infrastructure). Sends JSON over WebSocket.

Run from monitor with:
  python monitor.py [--config adn-mon.yaml]
Default config: monitor/adn-mon.yaml
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional

# This folder (monitor) is the root for the monitor
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

# Std / Twisted / project
from time import time

from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread

# Config and logging (infrastructure, clean architecture)
from adn_monitor.infrastructure import create_logger, load_config

# Persistence: pool + repos
from adn_monitor.domain import is_fail
from adn_monitor.infrastructure.persistence import create_pool, test_db

# dmr_utils3 for try_download (optional fallback when no checksum verification)
try:
    from dmr_utils3.utils import try_download
except ImportError:
    try_download = None

# adn_monitor package (from src)
from adn_monitor.application import (
    AliasService,
    MonitorState,
    clean_sys_dict,
    process_message,
    time_str,
)
from adn_monitor.application.time_utils import format_stored_utc_for_display, utc_calendar_date
from adn_monitor.application.tgstats import parse_options_to_static
from adn_monitor.application.hblink_table import clean_te
from adn_monitor.infrastructure import (
    MoniDBAliasRepository,
    MoniDBAliasTableRepository,
    MoniDBLastHeardRepository,
    MoniDBTgCountRepository,
    PickleJsonReportPayloadDecoder,
    ReportClientFactory,
    make_dashboard_factory,
)

__version__ = "1.0.0"

# Config file: env ADN_CONFIG_PATH, or --config, or this folder
CONFIG_FILE = os.environ.get("ADN_CONFIG_PATH", str(_ROOT / "adn-mon.yaml"))
for i, arg in enumerate(sys.argv[1:]):
    if arg == "--config" and i + 2 <= len(sys.argv):
        CONFIG_FILE = sys.argv[i + 2]
        if not Path(CONFIG_FILE).is_absolute():
            CONFIG_FILE = str(_ROOT / CONFIG_FILE)
        break

_config_result = load_config(CONFIG_FILE)
if is_fail(_config_result):
    sys.exit(f"Config error: {_config_result.error}")
CONF = _config_result.value
logger = None
db_conn = None
dashboard_server = None
build_time = 0
build_deferred = None
TGC_DATE = None

# Lastheard log rows
LASTHEARD_LOG_ROWS = 70


def _lastheard_rows(result, conf_global: dict | None) -> list:
    """Convert DB rows to JSON-serializable list of dicts (date from stored UTC → GLOBAL.TIMEZONE)."""
    out = []
    for row in result or []:
        sub = row[7] if len(row) > 7 else None
        if not isinstance(sub, list):
            sub = [str(sub)] if sub is not None else []
        out.append({
            "date": format_stored_utc_for_display(row[0], conf_global),
            "qso_time": row[1], "qso_type": row[2], "system": row[3],
            "tg_num": row[4], "tg_callsign": row[5] or "", "dmr_id": row[6], "subscriber": sub,
        })
    return out


def _tgcount_rows(result) -> list:
    """Convert tgcount DB rows to JSON-serializable list of dicts."""
    if not result:
        return []
    return [
        {"tg_num": r[0], "name": r[1] or "", "qso_count": r[2], "qso_time_str": r[3], "top_users": list(r[4])}
        for r in result
    ]


def error_hdl(failure):
    if reactor.running:
        logger.error("Loop error: %s, stopping the reactor.", failure.getBriefTraceback())
        reactor.stop()
    else:
        sys.exit(failure)


@inlineCallbacks
def render_fromdb(tbl: str, row_num: int, send_to=None):
    """Load last_heard / lstheard_log / tgcount from DB and send JSON (broadcast or to one client)."""
    try:
        if tbl in ("last_heard", "lstheard_log"):
            result = yield get_lastheard_repo().select_for_render(tbl, row_num)
        elif tbl == "tgcount":
            result = yield get_tgcount_repo().select_tgcount(row_num)
        else:
            result = None
        if not result and tbl != "tgcount":
            return
        state = get_state()
        conf_global = get_config_global()
        if tbl == "last_heard":
            payload = {"lastheard": _lastheard_rows(result, conf_global), "ctable": state.CTABLE}
            msg = "i" + json.dumps(payload, default=str)
            if send_to:
                send_to.sendMessage(msg.encode("utf-8"))
            else:
                dashboard_server.broadcast(msg, "main")
        elif tbl == "lstheard_log":
            payload = {"rows": _lastheard_rows(result, conf_global)}
            msg = "h" + json.dumps(payload, default=str)
            if send_to:
                send_to.sendMessage(msg.encode("utf-8"))
            else:
                dashboard_server.broadcast(msg, "lsthrd_log")
        elif tbl == "tgcount":
            payload = {"rows": _tgcount_rows(result)}
            msg = "t" + json.dumps(payload, default=str)
            if send_to:
                send_to.sendMessage(msg.encode("utf-8"))
            elif get_groups().get("tgcount"):
                dashboard_server.broadcast(msg, "tgcount")
    except Exception as err:
        logger.error("render_fromdb: %s %s", err, type(err))


def build_stats():
    global build_time, build_deferred
    now = time()
    if now - build_time < 1:
        if not build_deferred or build_deferred.called or build_deferred.cancelled:
            build_deferred = reactor.callLater(1, build_stats)
        else:
            build_deferred.reset(1)
        return
    if build_deferred and not build_deferred.called and not build_deferred.cancelled:
        build_deferred.cancel()
    state = get_state()
    conf_global = get_config_global()
    n_masters = len(state.CTABLE.get("MASTERS", {}))
    n_lnksys = len(get_groups().get("lnksys", {}))
    n_opb = len(get_groups().get("opb", {}))
    n_statictg = len(get_groups().get("statictg", {}))
    if state.CONFIG:
        if get_groups().get("main"):
            render_fromdb("last_heard", conf_global.get("LH_ROWS", 20))
        if get_groups().get("lnksys"):
            payload = {"ctable": state.CTABLE, "emaster": conf_global.get("EMPTY_MASTERS", False)}
            dashboard_server.broadcast("c" + json.dumps(payload, default=str), "lnksys")
            logger.debug("build_stats: broadcast lnksys to %d clients (MASTERS=%d)", n_lnksys, n_masters)
        if get_groups().get("opb"):
            payload = {"ctable": state.CTABLE, "dbridges": conf_global.get("BRDG_INC", False)}
            dashboard_server.broadcast("o" + json.dumps(payload, default=str), "opb")
            logger.debug("build_stats: broadcast opb to %d clients", n_opb)
        if get_groups().get("statictg"):
            payload = {"ctable": state.CTABLE, "emaster": conf_global.get("EMPTY_MASTERS", False)}
            dashboard_server.broadcast("s" + json.dumps(payload, default=str), "statictg")
            logger.debug("build_stats: broadcast statictg to %d clients", n_statictg)
        if get_groups().get("lsthrd_log"):
            render_fromdb("lstheard_log", LASTHEARD_LOG_ROWS)
    else:
        if n_lnksys or n_opb or n_statictg:
            logger.debug("build_stats: CONFIG empty, not broadcasting lnksys/opb/statictg (clients lnksys=%d opb=%d statictg=%d)", n_lnksys, n_opb, n_statictg)
    if state.BRIDGES and conf_global.get("BRDG_INC"):
        if get_groups().get("bridge"):
            payload = {"btable": state.BTABLE, "dbridges": True}
            dashboard_server.broadcast("b" + json.dumps(payload, default=str), "bridge")
    build_time = time()


def timeout_clients():
    now = time()
    conf_ws = CONF.get("WS", {})
    to = conf_ws.get("CLT_TO") or 0
    if not to:
        return
    try:
        for group in dashboard_server.clients:
            for client in list(dashboard_server.clients[group]):
                if dashboard_server.clients[group][client] + to < now:
                    logger.info("TIMEOUT: disconnecting client")
                    try:
                        client.sendClose()
                    except Exception as err:
                        logger.error("Exception caught parsing client timeout %s", err)
    except Exception as e:
        logger.info("CLIENT TIMEOUT: %s", e)


def _download_file_http(url: str, dest_path: str, dest_name: str, timeout: int = 30) -> bool:
    """Download url to dest_path/dest_name. Returns True on success. Runs in thread."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ADN-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        Path(dest_path).mkdir(parents=True, exist_ok=True)
        out = Path(dest_path) / dest_name
        out.write_bytes(data)
        return True
    except Exception as e:
        return False


def _fetch_checksums_json(checksum_url: str, timeout: int = 15) -> Optional[dict]:
    """Fetch file_checksums.json and return dict (filename_no_ext -> blake2b hex). Runs in thread."""
    try:
        req = urllib.request.Request(checksum_url, headers={"User-Agent": "ADN-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {k: v for k, v in data.items() if k != "timestamp" and isinstance(v, str)}
    except Exception:
        return None


def _verify_file_blake2b(filepath: Path, expected_hex: str) -> bool:
    """Verify file at filepath has BLAKE2b digest equal to expected_hex (matches ADN server utils.blake2bsum). Runs in thread."""
    try:
        h = hashlib.blake2b()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest() == expected_hex.lower()
    except Exception:
        return False


def _download_and_verify_one(
    path: str,
    file_name: str,
    url: str,
    checksum_url: str,
    checksums: Optional[dict],
) -> str:
    """Download to a .tmp file, verify checksum; only on success replace the final file (so prod is never overwritten by a bad download). Runs in thread."""
    if not url:
        return "no url"
    temp_name = file_name + ".tmp"
    if not _download_file_http(url, path, temp_name):
        return "download failed"
    temp_path = Path(path) / temp_name
    if not temp_path.exists():
        return "download failed (file missing)"
    if checksums is not None:
        key = Path(file_name).stem  # e.g. subscriber_ids.json -> subscriber_ids (matches ADN keys: peer_ids, subscriber_ids, talkgroup_ids, server_ids)
        expected = checksums.get(key)
        if not expected:
            temp_path.unlink(missing_ok=True)
            return "checksum key missing for " + key
        if not _verify_file_blake2b(temp_path, expected):
            temp_path.unlink(missing_ok=True)
            return "checksum verification failed for " + file_name
    final_path = Path(path) / file_name
    os.replace(temp_path, final_path)  # atomic on same filesystem; only then prod is updated
    return "successfully"


@inlineCallbacks
def update_table(path: str, file_name: str, url: str, stale: int, table: str):
    """Download alias file when older than STALE_HOURS or missing; verify checksum, use only if OK."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        count = yield get_alias_table_repo().table_count(table)
        file_path = Path(path) / file_name
        need_download = not file_path.exists() or (time() - file_path.stat().st_mtime) >= stale
        result = None
        conf = CONF.get("FILES", {})
        checksum_url = conf.get("CHECKSUM_URL", "").strip() or None

        if not need_download:
            logger.info("(alias) %s: using existing file (fresh)", table)
        if need_download:
            reason = "missing" if not file_path.exists() else "stale"
            logger.info("(alias) %s: %s, downloading from %s", table, reason, url[:60] + "..." if len(url) > 60 else url)
            if checksum_url:
                checksums = yield deferToThread(_fetch_checksums_json, checksum_url)
                if checksums is None:
                    result = "checksum fetch failed"
                else:
                    result = yield deferToThread(
                        _download_and_verify_one,
                        path,
                        file_name,
                        url,
                        checksum_url,
                        checksums,
                    )
            else:
                if try_download:
                    result = yield deferToThread(try_download, path, file_name, url, stale)
                else:
                    ok = yield deferToThread(_download_file_http, url, path, file_name)
                    result = "successfully" if ok else "download failed"

        if need_download and result and "successfully" in result:
            if checksum_url:
                logger.info("(alias) %s: downloaded and checksum verified", table)
            else:
                logger.info("(alias) %s: downloaded", table)

        use_file = (result and "successfully" in result) or (
            not need_download and count is not None and count <= 2
        )
        if use_file:
            alias_table_repo = get_alias_table_repo()
            alias_table_repo.populate_from_file(path, file_name, table)
            alias_repo = get_alias_repo()
            if hasattr(alias_repo, "_not_in_db"):
                alias_repo._not_in_db.clear()
            reactor.callLater(3, update_local)
        elif result and "successfully" not in result and logger:
            logger.warning("(alias) %s: %s", table, result)
    except Exception as err:
        logger.error("update_table: %s %s", err, type(err))


def _alias_files_path() -> str:
    """Absolute path for alias JSON/CSV dir (FILES.PATH), relative to monitor root if PATH is relative."""
    conf_files = CONF.get("FILES", {})
    base = conf_files.get("PATH", "./json")
    base_p = Path(base)
    if not base_p.is_absolute():
        base_p = _ROOT / base_p
    path = base_p.resolve()
    path.mkdir(parents=True, exist_ok=True)
    # Ensure trailing slash for downstream (e.g. dmr_utils3 try_download)
    return str(path).rstrip("/") + "/"


def update_local(table=None):
    path = _alias_files_path()
    conf_files = CONF.get("FILES", {})
    lcl_lstmod = get_local_lstmod()
    updt = []
    if table == "peer_ids" or (not table and conf_files.get("LCL_PEER")):
        updt.append((conf_files.get("LCL_PEER"), "peer_ids"))
    if table == "subscriber_ids" or (not table and conf_files.get("LCL_SUBS")):
        updt.append((conf_files.get("LCL_SUBS"), "subscriber_ids"))
    if table == "talkgroup_ids" or (not table and conf_files.get("LCL_TGID")):
        updt.append((conf_files.get("LCL_TGID"), "talkgroup_ids"))
    for file_name, tbl in updt:
        p2f = Path(path) / file_name
        if not p2f.exists():
            continue
        mtime = p2f.stat().st_mtime
        if lcl_lstmod.get(tbl) == mtime:
            continue
        alias_table_repo = get_alias_table_repo()
        alias_table_repo.populate_from_file(path, file_name, tbl, wipe=False)
        lcl_lstmod[tbl] = mtime


@inlineCallbacks
def count_db_entries():
    try:
        for tbl in ("peer_ids", "talkgroup_ids", "subscriber_ids"):
            result = yield get_alias_table_repo().table_count(tbl)
            if result is not None:
                logger.info("%s entries: %s", tbl, result)
    except Exception as err:
        logger.error("count_db_entries: %s %s", err, type(err))


def clean_tgcount():
    global TGC_DATE
    today = utc_calendar_date()
    if TGC_DATE is None or today != TGC_DATE:
        TGC_DATE = today
        get_tgcount_repo().clean_tgcount()


def files_update():
    path = _alias_files_path()
    conf = CONF.get("FILES", {})
    reload_time = conf.get("RELOAD_TIME", 24 * 3600)
    for file_name, url_key, tbl in (
        (conf.get("PEER_FILE", conf.get("PEER")), "PEER_URL", "peer_ids"),
        (conf.get("SUBSCRIBER_FILE", conf.get("SUBS")), "SUBSCRIBER_URL", "subscriber_ids"),
        (conf.get("TGID_FILE", conf.get("TGID")), "TGID_URL", "talkgroup_ids"),
    ):
        url = conf.get(url_key, "")
        if file_name and url:
            update_table(path, file_name, url, reload_time, tbl)


def cleaning_loop():
    if CONF.get("GLOBAL", {}).get("TGC_INC"):
        clean_tgcount()
    lh_repo = get_lastheard_repo()
    for tbl, row_num in (("last_heard", CONF.get("GLOBAL", {}).get("LH_ROWS", 20)), ("lstheard_log", LASTHEARD_LOG_ROWS)):
        lh_repo.clean_table(tbl, row_num)


# Globals for wiring (set in main())
_state: MonitorState | None = None
_alias_repo: MoniDBAliasRepository | None = None
_alias_table_repo: MoniDBAliasTableRepository | None = None
_lastheard_repo: MoniDBLastHeardRepository | None = None
_tgcount_repo: MoniDBTgCountRepository | None = None
_groups: dict | None = None
_config_global: dict | None = None
_local_lstmod: dict | None = None


def get_state() -> MonitorState:
    return _state


def get_alias_repo():
    return _alias_repo


def get_alias_table_repo():
    return _alias_table_repo


def get_lastheard_repo():
    return _lastheard_repo


def get_tgcount_repo():
    return _tgcount_repo


def get_groups():
    return _groups


def get_config_global():
    return _config_global


def get_local_lstmod():
    return _local_lstmod


def clean_ctable_streams():
    """Run STREAMS timeout cleanup periodically so we do not depend on CONFIG_SND.
    Prevents unbounded growth of CTABLE OPENBRIDGES STREAMS (memory leak)."""
    state = get_state()
    if state and state.CTABLE:
        clean_te(state.CTABLE)
        # TODO: remove after validating memory fix (MEMORY_LEAK_ANALYSIS.md)
        ob = state.CTABLE.get("OPENBRIDGES", {})
        if ob:
            total = sum(len(ob[s].get("STREAMS", {})) for s in ob)
            logger.info("(monitor) STREAMS sizes: total=%d per_system=%s", total, {s: len(ob[s].get("STREAMS", {})) for s in ob})


def main():
    global logger, dashboard_server, _state, _alias_repo, _alias_table_repo
    global _lastheard_repo, _tgcount_repo, _groups, _config_global, _local_lstmod, build_deferred

    log_conf = {
        "PATH": CONF["LOG"]["PATH"],
        "LOG_FILE": CONF["LOG"]["LOG_FILE"],
        "LOG_LEVEL": CONF["LOG"]["LOG_LEVEL"],
        "LOG_HANDLERS": ["console", "file"],
    }
    logger = create_logger(log_conf)
    logger.info("monitor.py starting")
    logger.info(
        "\n\n\tCopyright (C) Rodrigo Pérez <ce5rpy@qmd.cl>\n\t"
        "License: GPLv3 — ADN Systems Monitor\n\n"
    )

    pool = create_pool(
        CONF["DB"]["SERVER"],
        CONF["DB"]["USER"],
        CONF["DB"]["PASSWD"],
        CONF["DB"]["NAME"],
        CONF["DB"]["PORT"],
    )

    def on_db_test(r) -> None:
        if is_fail(r):
            logger.error("Database connection failed: %s", r.error)
            if reactor.running:
                reactor.stop()
            else:
                sys.exit(1)

    test_db(pool).addCallback(on_db_test)
    conf_global = CONF.get("GLOBAL", {})
    opb = CONF.get("OPB_FLTR", {})
    dash = CONF.get("DASHBOARD", {})
    _config_global = {
        **conf_global,
        "OPB_FILTER": opb.get("OPB_FILTER", []),
        "DASHBOARD_MIN_DURATION": dash.get("MIN_DURATION", 3),
    }

    _state = MonitorState(
        lastheard_log_rows=LASTHEARD_LOG_ROWS,
        empty_masters=conf_global.get("EMPTY_MASTERS", False),
        brdg_inc=conf_global.get("BRDG_INC", False),
    )
    _local_lstmod = {"peer_ids": None, "subscriber_ids": None, "talkgroup_ids": None}

    _alias_repo = MoniDBAliasRepository(pool)
    _alias_table_repo = MoniDBAliasTableRepository(pool)
    _lastheard_repo = MoniDBLastHeardRepository(pool)
    _tgcount_repo = MoniDBTgCountRepository(pool)
    alias_svc = AliasService(_alias_repo)

    _groups = {g: {} for g in (
        "all_clients", "main", "bridge", "lnksys", "opb", "statictg", "log", "lsthrd_log", "tgcount"
    )}

    DashboardFactory, DashboardProtocol = make_dashboard_factory(
        _state,
        conf_global,
        CONF.get("WS", {}),
        _groups,
        lambda tbl, rows, client: render_fromdb(tbl, rows, client),
        lambda rows, client: render_fromdb("lstheard_log", rows, client),
        lambda rows, client: render_fromdb("tgcount", rows, client),
    )

    ws_port = CONF["WS"]["WS_PORT"]
    use_ssl = CONF["WS"].get("USE_SSL", False)
    dashboard_server = DashboardFactory(f"ws://*:{ws_port}" if not use_ssl else f"wss://*:{ws_port}")
    dashboard_server.protocol = DashboardProtocol

    _connection_label = str(CONF.get("DASHBOARD", {}).get("dashtitle", "ADN Systems")).strip() or "ADN Systems"

    def on_report_connection_lost():
        dashboard_server.broadcast("q" + f"Connection to {_connection_label} lost", "all_clients")

    def on_report_connection_established():
        dashboard_server.broadcast("q" + f"Connection to {_connection_label} established", "all_clients")

    def on_ctable_updated():
        """Push updated ctable to dashboard clients after each BRDG_EVENT (VOICE START/END)."""
        state = get_state()
        conf = get_config_global()
        groups = get_groups()
        if groups.get("main"):
            render_fromdb("last_heard", conf.get("LH_ROWS", 20))
        if groups.get("lnksys"):
            dashboard_server.broadcast(
                "c" + json.dumps({"ctable": state.CTABLE, "emaster": conf.get("EMPTY_MASTERS", False)}, default=str),
                "lnksys",
            )
        if groups.get("opb"):
            dashboard_server.broadcast(
                "o" + json.dumps({"ctable": state.CTABLE, "dbridges": conf.get("BRDG_INC", False)}, default=str),
                "opb",
            )

    report_decoder = PickleJsonReportPayloadDecoder()
    report_factory = ReportClientFactory(
        state=_state,
        alias_svc=alias_svc,
        alias_repo=_alias_repo,
        lastheard_repo=_lastheard_repo,
        tgcount_repo=_tgcount_repo,
        broadcast=dashboard_server,
        config_global=_config_global,
        report_decoder=report_decoder,
        on_connection_lost=on_report_connection_lost,
        on_connection_established=on_report_connection_established,
        on_ctable_updated=on_ctable_updated,
    )

    # Loops
    freq = CONF["WS"].get("FREQ", 1)
    task.LoopingCall(build_stats).start(freq).addErrback(error_hdl)
    if CONF["WS"].get("CLT_TO"):
        task.LoopingCall(timeout_clients).start(10).addErrback(error_hdl)
    if conf_global.get("TGC_INC"):
        task.LoopingCall(render_fromdb, "tgcount", conf_global.get("TGC_ROWS", 20)).start(60).addErrback(error_hdl)
    # Alias files: check at startup (1s) and every REVIEW_INTERVAL_MINUTES; if missing or older than STALE_HOURS, download and verify checksum
    review_sec = CONF.get("FILES", {}).get("REVIEW_INTERVAL", 5 * 60)
    reactor.callLater(1, files_update)
    task.LoopingCall(files_update).start(review_sec, now=False).addErrback(error_hdl)
    task.LoopingCall(cleaning_loop).start(900, now=False).addErrback(error_hdl)
    # Memory leak mitigation: clean STREAMS and sys_dict periodically (not only on CONFIG_SND / END)
    task.LoopingCall(clean_ctable_streams).start(60).addErrback(error_hdl)
    task.LoopingCall(lambda: clean_sys_dict(get_state())).start(60).addErrback(error_hdl)

    # Self-service: load Clients.options into PEER_OPTIONS and merge into ctable so Static TG reflects DB
    def merge_peer_options_from_db():
        state = get_state()
        conf = get_config_global()
        groups = get_groups()
        d = pool.runQuery(
            "SELECT dmr_id, options FROM Clients WHERE logged_in=1 AND options IS NOT NULL AND options != ''"
        )

        def _dmr_to_int(dmr_id) -> int | None:
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

        def on_rows(rows):
            state.PEER_OPTIONS.clear()
            for row in rows or []:
                if len(row) >= 2:
                    dmr_int = _dmr_to_int(row[0])
                    opts = row[1]
                    if dmr_int is not None:
                        state.PEER_OPTIONS[dmr_int] = parse_options_to_static(opts)
            # Merge into ctable so dashboard shows DB options (always apply, including empty = clear removed TGs)
            for sys_name in state.CTABLE.get("MASTERS", {}):
                peers = state.CTABLE["MASTERS"][sys_name].get("PEERS", {})
                for peer_id in peers:
                    if peer_id in state.PEER_OPTIONS:
                        po = state.PEER_OPTIONS[peer_id]
                        state.CTABLE["MASTERS"][sys_name]["PEERS"][peer_id]["TS1_STATIC"] = po.get("TS1_STATIC") or []
                        state.CTABLE["MASTERS"][sys_name]["PEERS"][peer_id]["TS2_STATIC"] = po.get("TS2_STATIC") or []
            if groups.get("lnksys"):
                dashboard_server.broadcast(
                    "c" + json.dumps({"ctable": state.CTABLE, "emaster": conf.get("EMPTY_MASTERS", False)}, default=str),
                    "lnksys",
                )
            if groups.get("statictg"):
                dashboard_server.broadcast(
                    "c" + json.dumps({"ctable": state.CTABLE, "emaster": conf.get("EMPTY_MASTERS", False)}, default=str),
                    "statictg",
                )

        d.addCallback(on_rows)
        d.addErrback(lambda f: None)  # ignore DB errors (e.g. no table)

    task.LoopingCall(merge_peer_options_from_db).start(15, now=False).addErrback(error_hdl)
    reactor.callLater(2, merge_peer_options_from_db)  # first load soon after startup

    reactor.callLater(3, update_local)
    reactor.callLater(5, count_db_entries)

    reactor.connectTCP(
        CONF["ADN_CXN"]["ADN_IP"],
        CONF["ADN_CXN"]["ADN_PORT"],
        report_factory,
    )

    ws_interface = CONF["WS"].get("LISTEN_INTERFACE") or ""
    logger.info('Starting websocket on port %s SSL=%s interface=%r', ws_port, use_ssl, ws_interface or "all IPv4")
    if use_ssl:
        from twisted.internet import ssl
        cert = ssl.DefaultOpenSSLContextFactory(
            str(CONF["WS"]["P2F_PKEY"]),
            str(CONF["WS"]["P2F_CERT"]),
        )
        reactor.listenSSL(ws_port, dashboard_server, cert, interface=ws_interface)
    else:
        reactor.listenTCP(ws_port, dashboard_server, interface=ws_interface)

    reactor.run()


if __name__ == "__main__":
    main()
