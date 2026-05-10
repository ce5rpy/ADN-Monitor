#!/usr/bin/env python3
# Hotspot Proxy for ADN DMR Peer Server.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Based on the hotspot proxy by Simon Adlem, G7RZU (Copyright (C) 2020);
# credits: Jon Lee G4TSN, Norman Williams M6NBP, Christian OA4DOA.
# Original and this derivative are free software under GPLv3.

"""
Hotspot Proxy for ADN DMR Peer Server.

UDP proxy between repeaters (Homebrew protocol) and the ADN DMR Peer Server.
Default config: proxy/adn-proxy.yaml. Set ADN_PROXY_CONFIG_PATH in .env, or use
ADN_CONFIG_PATH to reuse the monitor YAML (legacy single-file install).

  python proxy.py
  python proxy.py --config /path/to/adn-proxy.yaml
"""

from __future__ import annotations

import logging
import os
import socket
import signal
import sys
from pathlib import Path
from time import time

# Project root (proxy directory)
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from twisted.internet import reactor, task

from adn_proxy.domain import is_fail
from adn_proxy.infrastructure import (
    ProxyProtocol,
    create_logger,
    create_pool,
    create_priv_helper,
    load_config,
    reopen_file_handlers,
    test_db,
)
from adn_proxy.infrastructure.persistence import ProxyDbRepository

__version__ = "2.0.0"

# Config: ADN_PROXY_CONFIG_PATH, else ADN_CONFIG_PATH (legacy one YAML), else proxy/adn-proxy.yaml
_DEFAULT_CONFIG = str(_ROOT / "adn-proxy.yaml")
CONFIG_FILE = (
    os.environ.get("ADN_PROXY_CONFIG_PATH")
    or os.environ.get("ADN_CONFIG_PATH")
    or _DEFAULT_CONFIG
)
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
pool = None
db_proxy = None
priv_helper = None
proxy_protocol = None


def _looping_err(failure):
    if logger:
        logger.error("Loop error: %s", failure.getBriefTraceback())
    reactor.stop()


def main() -> None:
    global logger, pool, db_proxy, priv_helper, proxy_protocol

    Path(CONF["LOG"]["PATH"]).mkdir(parents=True, exist_ok=True)
    log_conf = {
        "PATH": CONF["LOG"]["PATH"],
        "LOG_FILE": CONF["LOG"]["LOG_FILE"],
        "LOG_LEVEL": CONF["LOG"]["LOG_LEVEL"],
        "LOG_HANDLERS": ["console", "file"],
    }
    logger = create_logger(log_conf)
    logger.info("proxy.py starting")
    logger.info(
        "\n\n\tCopyright (C) Rodrigo Pérez <ce5rpy@qmd.cl>\n\t"
        "License: GPLv3 — Hotspot Proxy for ADN DMR Peer Server\n\n"
    )

    px = CONF["PROXY"]
    ss = CONF["SELF_SERVICE"]
    master_raw = px["Master"]
    master = _resolve_master(master_raw)
    if master != master_raw:
        logger.info("Resolved MASTER %r to %s", master_raw, master)
    listen_port = px["ListenPort"]
    listen_ip = px["ListenIP"] or ""
    dest_start = px["DestportStart"]
    dest_end = px["DestPortEnd"]
    logger.info(
        "Proxy UDP pool on MASTER (same as adn-server SYSTEM PORT+GENERATOR): %s..%s inclusive "
        "(%d UDP listeners, GENERATOR=%s)",
        dest_start,
        dest_end,
        dest_end - dest_start + 1,
        px["GENERATOR"],
    )
    timeout_sec = px["Timeout"]
    stats_enabled = px["Stats"]
    debug = px["Debug"]
    client_info = px["ClientInfo"]
    black_list = list(px["BlackList"])
    ip_black_list = dict(px["IPBlackList"])
    use_selfservice = ss["use_selfservice"]

    # IPv6
    if listen_ip == "" and os.environ.get("ADN_PROXY_IPV6"):
        listen_ip = "::"
    if listen_ip == "::" and _is_ipv4(master):
        master = "::ffff:" + master

    # Env overrides (optional). Only override when ADN_PROXY_DEBUG is set: 1/true/yes => True; 0/false/no => False
    if "ADN_PROXY_DEBUG" in os.environ:
        _debug_env = os.environ.get("ADN_PROXY_DEBUG", "").strip().lower()
        if _debug_env in ("1", "true", "yes"):
            debug = True
        elif _debug_env in ("0", "false", "no"):
            debug = False
        # empty string: keep value from YAML
    if os.environ.get("ADN_PROXY_STATS"):
        stats_enabled = bool(os.environ.get("ADN_PROXY_STATS"))
    if os.environ.get("ADN_PROXY_CLIENTINFO"):
        client_info = bool(os.environ.get("ADN_PROXY_CLIENTINFO"))
    if os.environ.get("ADN_PROXY_LISTENPORT"):
        listen_port = int(os.environ["ADN_PROXY_LISTENPORT"])

    # So you can confirm in journalctl that the env was passed (e.g. from systemd)
    logger.info(
        "Debug=%s (config=%s, ADN_PROXY_DEBUG=%r)",
        debug, px["Debug"], os.environ.get("ADN_PROXY_DEBUG", "not set"),
    )
    if debug:
        logger.setLevel(logging.DEBUG)
        root = logging.getLogger()
        for h in root.handlers:
            h.setLevel(logging.DEBUG)
        # Ensure our logger's effective handlers show DEBUG (it propagates to root)
        logger.info(
            "(DEBUG) Proxy debug enabled — raw packets will be logged (ADN_PROXY_DEBUG=%s)",
            os.environ.get("ADN_PROXY_DEBUG", "not set"),
        )

    conn_track = {p: False for p in range(dest_start, dest_end + 1)}
    peer_track = {}
    rptl_track = {}

    # Privileged helper (netfilter/conntrack)
    unix_socket = "/run/priv_control/priv_control.unixsocket"
    priv_helper = create_priv_helper(unix_socket, listen_port)
    if priv_helper:
        logger.info("(PRIV) Found UNIX socket. Enabling priv helper")
        priv_helper.flush_conntrack()
        priv_helper.blocklist_flush()
    else:
        priv_helper = None

    # Database (self-service)
    if use_selfservice:
        pool = create_pool(
            ss["DB_SERVER"],
            ss["DB_USERNAME"],
            ss["DB_PASSWORD"],
            ss["DB_NAME"],
            ss["DB_PORT"],
        )
        db_proxy = ProxyDbRepository(pool)
    else:
        pool = None
        db_proxy = None

    ss_conf = CONF["SELF_SERVICE"]
    proxy_protocol = ProxyProtocol(
        master=master,
        listen_port=listen_port,
        conn_track=conn_track,
        peer_track=peer_track,
        rptl_track=rptl_track,
        black_list=black_list,
        ip_black_list=ip_black_list,
        timeout_sec=timeout_sec,
        debug=debug,
        client_info=client_info,
        dest_port_start=dest_start,
        dest_port_end=dest_end,
        priv_helper=priv_helper,
        db_proxy=db_proxy,
        use_selfservice=use_selfservice,
        pbkdf2_salt=ss_conf.get("PBKDF2_SALT", "ADN"),
        pbkdf2_iterations=int(ss_conf.get("PBKDF2_ITERATIONS", 2000)),
        logger=logger,
    )

    def sig_handler(sig, _frame):
        logger.info("(GLOBAL) SHUTDOWN: PROXY IS TERMINATING WITH SIGNAL %s", sig)
        reactor.stop()

    def sigusr2_reopen_logs(_sig, _frame):
        """Logrotate: reopen file log handlers (does not reload config)."""
        n = reopen_file_handlers()
        logger.info("(LOGGER) Reopened %s file log handler(s) after SIGUSR2", n)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGUSR2, sigusr2_reopen_logs)

    def start_server():
        reactor.listenUDP(listen_port, proxy_protocol, interface=listen_ip)
        def blacklist_trimmer():
            now = time()
            to_del = [ip for ip, expire in list(ip_black_list.items()) if expire and expire < now]
            for ip in to_del:
                ip_black_list.pop(ip, None)
                if client_info:
                    logger.info("Remove dynamic blacklist entry for %s", ip)
                if priv_helper:
                    logger.info("Ask priv helper to remove blacklist entry for %s from iptables", ip)
                    reactor.callInThread(priv_helper.del_blocklist, listen_port, ip)
        def rptl_trimmer():
            rptl_track.clear()
            logger.info("Purge RPTL table")
        task.LoopingCall(blacklist_trimmer).start(15).addErrback(_looping_err)
        task.LoopingCall(rptl_trimmer).start(60).addErrback(_looping_err)
        if stats_enabled:
            def stats():
                count = sum(1 for p in conn_track if conn_track[p])
                total = dest_end - dest_start
                logger.info("%s ports out of %s in use (%s free)", count, total, total - count)
            task.LoopingCall(stats).start(30).addErrback(_looping_err)
        if use_selfservice and db_proxy:
            task.LoopingCall(proxy_protocol.send_opts).start(10).addErrback(_looping_err)
            task.LoopingCall(db_proxy.clean_tbl).start(3600).addErrback(_looping_err)
            task.LoopingCall(proxy_protocol.lst_seen).start(120).addErrback(_looping_err)

    if use_selfservice and pool:
        logger.info(
            "Self-service enabled; DB options at login, send_opts every 10s, clean_tbl every 1h, lst_seen every 2min."
        )
        def on_db_test(r):
            if is_fail(r):
                logger.error("Database connection failed: %s", r.error)
                reactor.stop()
            else:
                start_server()
        test_db(pool).addCallback(on_db_test)
    else:
        start_server()

    reactor.run()


def _is_ipv4(ip: str) -> bool:
    try:
        import ipaddress
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False


def _resolve_master(host: str) -> str:
    """Resolve MASTER to an IP. Twisted UDP write() accepts only IPs, not hostnames."""
    import ipaddress
    if not host or not host.strip():
        return host
    host = host.strip()
    try:
        ipaddress.IPv4Address(host)
        return host
    except ValueError:
        pass
    try:
        ipaddress.IPv6Address(host)
        return host
    except ValueError:
        pass
    try:
        # Prefer IPv4 for compatibility with existing IPv4-mapped logic
        infos = socket.getaddrinfo(host, None, socket.AF_UNSPEC, socket.SOCK_DGRAM)
        for family, _, _, _, sockaddr in infos:
            if family == socket.AF_INET:
                return sockaddr[0]
        if infos:
            return infos[0][4][0]
    except (socket.gaierror, OSError) as e:
        raise SystemExit(f"Could not resolve MASTER hostname {host!r}: {e}") from e
    raise SystemExit(f"Could not resolve MASTER hostname {host!r}: no address returned")


if __name__ == "__main__":
    try:
        from setproctitle import setproctitle
        setproctitle(Path(__file__).name)
    except ImportError:
        pass
    main()
