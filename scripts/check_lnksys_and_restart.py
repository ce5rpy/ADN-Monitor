#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Watchdog: read ADN Monitor WebSocket (lnksys / CTABLE). If **both** online repeater
count and online hotspot count are **zero** (under MASTERS → PEERS only), then:

1. Delete all files in ``/opt/new-adn-server/json`` except ``local_subcriber_ids.json``
   and ``.gitkeep``.
2. Run ``systemctl restart adn-server``.

Classification matches dashboard "Linked systems" (Systems.tsx):

- **Repeater:** peer id length 6, RX/TX freq not ``N/A``, not bridge, ``CONNECTION == YES``.
- **Hotspot:** peer id length ≥ 7, RX/TX freq not ``N/A``, not bridge, ``CONNECTION == YES``.

Root ``PEERS`` (PEER service rows) are **ignored** for the decision.

Requires: ``pip install websocket-client``

Optional CLI: ``--ws-url`` (default ``ws://127.0.0.1:9000``), ``-v``, ``--insecure`` (wss + bad certs).

Example (cron)::

  */5 * * * * /usr/bin/python3 /opt/adn-monitor/scripts/check_lnksys_and_restart.py

"""

from __future__ import annotations

import argparse
import json
import logging
import os
import ssl
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from websocket import create_connection, WebSocketException
except ImportError:  # pragma: no cover
    print(
        "Missing dependency: websocket-client\n"
        "Install: python3 -m pip install websocket-client",
        file=sys.stderr,
    )
    sys.exit(2)

LOG = logging.getLogger("check_lnksys")

# Fixed paths and service (not configurable on purpose).
NEW_ADN_JSON_DIR = "/opt/new-adn-server/json"
_JSON_KEEP = frozenset({"local_subcriber_ids.json", ".gitkeep"})
SYSTEMCTL_RESTART_ADN = ("systemctl", "restart", "adn-server")

DEFAULT_WS_URL = "ws://127.0.0.1:9000"
DEFAULT_WS_TIMEOUT = 15.0


def _peer_id_str(peer_id: Any) -> str:
    return str(peer_id).strip()


def _is_bridge(peer: dict[str, Any]) -> bool:
    rx = str(peer.get("RX_FREQ") or "")
    tx = str(peer.get("TX_FREQ") or "")
    return rx == "N/A" and tx == "N/A"


def _is_repeater(peer_id: str, peer: dict[str, Any]) -> bool:
    rx = str(peer.get("RX_FREQ") or "")
    tx = str(peer.get("TX_FREQ") or "")
    return len(peer_id) == 6 and rx != "N/A" and tx != "N/A"


def _is_hotspot(peer_id: str, peer: dict[str, Any]) -> bool:
    rx = str(peer.get("RX_FREQ") or "")
    tx = str(peer.get("TX_FREQ") or "")
    return len(peer_id) >= 7 and rx != "N/A" and tx != "N/A"


def _master_peer_online(peer: dict[str, Any]) -> bool:
    return str(peer.get("CONNECTION", "")).upper() == "YES"


def count_repeaters_hotspots_masters(ctable: dict[str, Any]) -> tuple[int, int]:
    repeaters = 0
    hotspots = 0
    masters = ctable.get("MASTERS") or {}
    for _mname, master in masters.items():
        if not isinstance(master, dict):
            continue
        peers = master.get("PEERS") or {}
        for pid, p in peers.items():
            if not isinstance(p, dict):
                continue
            if not _master_peer_online(p):
                continue
            if _is_bridge(p):
                continue
            pid_s = _peer_id_str(pid)
            if _is_repeater(pid_s, p):
                repeaters += 1
            elif _is_hotspot(pid_s, p):
                hotspots += 1
    return repeaters, hotspots


def fetch_lnksys_ctable(ws_url: str, timeout: float, insecure: bool) -> dict[str, Any]:
    conn_kw: dict[str, Any] = {"timeout": timeout}
    if ws_url.startswith("wss://") and insecure:
        conn_kw["sslopt"] = {"cert_reqs": ssl.CERT_NONE}

    try:
        ws = create_connection(ws_url, **conn_kw)
    except (OSError, WebSocketException) as e:
        raise RuntimeError(f"WebSocket connect failed: {e}") from e

    try:
        ws.send("conf,lnksys")
        raw = ws.recv()
    except (OSError, WebSocketException) as e:
        raise RuntimeError(f"WebSocket recv failed: {e}") from e
    finally:
        try:
            ws.close()
        except Exception:
            pass

    if not isinstance(raw, str):
        raw = raw.decode("utf-8", errors="replace")
    if not raw or raw[0] != "c":
        raise RuntimeError(f"Unexpected message (expected opcode 'c'): {raw[:80]!r}")
    payload = json.loads(raw[1:])
    ctable = (payload.get("ctable") or {}) if isinstance(payload, dict) else {}
    if not isinstance(ctable, dict):
        raise RuntimeError("Invalid ctable in payload")
    return ctable


def clean_new_adn_json_dir() -> int:
    """Remove all regular files in NEW_ADN_JSON_DIR except _JSON_KEEP."""
    d = Path(NEW_ADN_JSON_DIR)
    if not d.is_dir():
        LOG.warning("JSON dir missing or not a directory: %s", NEW_ADN_JSON_DIR)
        return 0
    removed = 0
    for p in d.iterdir():
        if not p.is_file():
            continue
        if p.name in _JSON_KEEP:
            continue
        try:
            p.unlink()
            LOG.debug("Removed %s", p)
            removed += 1
        except OSError as e:
            LOG.warning("Could not remove %s: %s", p, e)
    if removed:
        LOG.info(
            "Removed %d file(s) under %s (kept: %s)",
            removed,
            NEW_ADN_JSON_DIR,
            ", ".join(sorted(_JSON_KEEP)),
        )
    return removed


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--ws-url",
        default=os.environ.get("ADN_MONITOR_WS_URL", DEFAULT_WS_URL),
        help=f"Monitor WebSocket URL (default: env ADN_MONITOR_WS_URL or {DEFAULT_WS_URL})",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("ADN_MONITOR_WS_TIMEOUT", DEFAULT_WS_TIMEOUT)),
        help="Connect/recv timeout in seconds",
    )
    p.add_argument("--insecure", action="store_true", help="For wss://: do not verify TLS certificate")
    p.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    try:
        ctable = fetch_lnksys_ctable(args.ws_url, args.timeout, args.insecure)
    except RuntimeError as e:
        LOG.error("%s", e)
        return 2

    rpt, hts = count_repeaters_hotspots_masters(ctable)
    LOG.info("Online repeaters=%d hotspots=%d (restart if both are 0)", rpt, hts)

    if rpt > 0 or hts > 0:
        return 0

    LOG.warning("Repeaters=0 and hotspots=0: clearing %s then %s", NEW_ADN_JSON_DIR, " ".join(SYSTEMCTL_RESTART_ADN))

    clean_new_adn_json_dir()

    try:
        subprocess.run(SYSTEMCTL_RESTART_ADN, check=True)
    except subprocess.CalledProcessError as e:
        LOG.error("systemctl failed (exit %s)", e.returncode)
        return 1

    LOG.info("systemctl restart adn-server completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
