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

"""Build and update HBlink CTABLE from CONFIG."""

from __future__ import annotations

import time
from typing import Any, Callable

from ..domain.value_objects import decode_utf8_field


def _decode_freq(freq: Any) -> str:
    if isinstance(freq, bytes):
        s = freq.decode("utf-8", errors="replace").strip()
    else:
        s = str(freq).strip()
    if not s.isdigit():
        return "N/A"
    if s[:3] == "000" or s[:1] == "0":
        return "N/A"
    if len(s) >= 7:
        return f"{s[:3]}.{s[3:7]} MHz"
    return "N/A"


def _decode_slots(slots: Any) -> str:
    if slots == b"0" or slots == "0":
        return "NONE"
    if slots in (b"1", b"2", "1", "2"):
        return decode_utf8_field(slots)
    if slots == b"3" or slots == "3":
        return "Duplex"
    return "Simplex"


def add_hb_peer(
    peer_conf: dict,
    ctable_loc: dict,
    peer_key: Any,
    time_str_fn: Callable[[Any, str], str],
    int_id_fn: Callable[[Any], int],
) -> None:
    """Add one peer to ctable_loc (MASTERS[system][PEERS] or PEERS)."""
    pid = int_id_fn(peer_key)
    ctable_loc[pid] = {}
    peer = ctable_loc[pid]
    tx_freq = peer_conf.get("TX_FREQ", b"")
    rx_freq = peer_conf.get("RX_FREQ", b"")
    peer["TX_FREQ"] = _decode_freq(tx_freq)
    peer["RX_FREQ"] = _decode_freq(rx_freq)
    peer["SLOTS"] = _decode_slots(peer_conf.get("SLOTS", b"0"))
    for key in ("PACKAGE_ID", "SOFTWARE_ID", "LOCATION", "DESCRIPTION", "URL",
                "CALLSIGN", "COLORCODE", "TX_POWER", "LATITUDE", "LONGITUDE", "HEIGHT"):
        peer[key] = decode_utf8_field(peer_conf.get(key, ""))
    peer["CONNECTION"] = peer_conf.get("CONNECTION", "")
    peer["CONNECTED"] = time_str_fn(peer_conf.get("CONNECTED", 0), "since")
    peer["IP"] = peer_conf.get("IP", "")
    peer["PORT"] = peer_conf.get("PORT", "")
    for ts in (1, 2):
        peer[ts] = {
            "TS": "",
            "TYPE": "",
            "SUB": "",
            "SRC": "",
            "DEST": "",
        }


def build_hblink_table_impl(
    config: dict,
    stats_table: dict,
    time_str_fn: Callable[[Any, str], str],
    int_id_fn: Callable[[Any], int],
    conf_global: dict | None = None,
) -> None:
    """Build MASTERS, PEERS, OPENBRIDGES from config. conf_global used for HB_INC."""
    hb_inc = conf_global.get("HB_INC", True) if conf_global else True
    for name, data in list(config.items()):
        if not data.get("ENABLED"):
            continue
        if data.get("MODE") == "MASTER":
            stats_table["MASTERS"][name] = {}
            stats_table["MASTERS"][name]["REPEAT"] = "repeat" if data.get("REPEAT") else "isolate"
            stats_table["MASTERS"][name]["PEERS"] = {}
            for peer_key in data.get("PEERS", {}):
                add_hb_peer(
                    data["PEERS"][peer_key],
                    stats_table["MASTERS"][name]["PEERS"],
                    peer_key,
                    time_str_fn,
                    int_id_fn,
                )
        elif (data.get("MODE") in ("XLXPEER", "PEER")) and hb_inc:
            stats_table["PEERS"][name] = {}
            stats_table["PEERS"][name]["MODE"] = data["MODE"]
            stats_table["PEERS"][name]["LOCATION"] = decode_utf8_field(data.get("LOCATION", ""))
            stats_table["PEERS"][name]["DESCRIPTION"] = decode_utf8_field(data.get("DESCRIPTION", ""))
            stats_table["PEERS"][name]["URL"] = decode_utf8_field(data.get("URL", data.get("DESCRIPTION", "")))
            stats_table["PEERS"][name]["CALLSIGN"] = decode_utf8_field(data.get("CALLSIGN", ""))
            stats_table["PEERS"][name]["RADIO_ID"] = int_id_fn(data.get("RADIO_ID", 0))
            stats_table["PEERS"][name]["MASTER_IP"] = data.get("MASTER_IP", "")
            stats_table["PEERS"][name]["MASTER_PORT"] = data.get("MASTER_PORT", "")
            stats_table["PEERS"][name]["STATS"] = {}
            if data["MODE"] == "XLXPEER":
                xlx = data.get("XLXSTATS", {})
                stats_table["PEERS"][name]["STATS"]["CONNECTION"] = xlx.get("CONNECTION", "NO")
                if xlx.get("CONNECTION") == "YES":
                    stats_table["PEERS"][name]["STATS"]["CONNECTED"] = time_str_fn(xlx.get("CONNECTED", 0), "since")
                    stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = xlx.get("PINGS_SENT", 0)
                    stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = xlx.get("PINGS_ACKD", 0)
                else:
                    stats_table["PEERS"][name]["STATS"]["CONNECTED"] = "--   --"
                    stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = 0
                    stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = 0
            else:
                st = data.get("STATS", {})
                stats_table["PEERS"][name]["STATS"]["CONNECTION"] = st.get("CONNECTION", "NO")
                if st.get("CONNECTION") == "YES":
                    stats_table["PEERS"][name]["STATS"]["CONNECTED"] = time_str_fn(st.get("CONNECTED", 0), "since")
                    stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = st.get("PINGS_SENT", 0)
                    stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = st.get("PINGS_ACKD", 0)
                else:
                    stats_table["PEERS"][name]["STATS"]["CONNECTED"] = "--   --"
                    stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = 0
                    stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = 0
            slot_val = data.get("SLOTS", b"0")
            if slot_val == b"0" or slot_val == "0":
                stats_table["PEERS"][name]["SLOTS"] = "NONE"
            elif slot_val in (b"1", b"2", "1", "2"):
                stats_table["PEERS"][name]["SLOTS"] = decode_utf8_field(slot_val)
            elif slot_val == b"3" or slot_val == "3":
                stats_table["PEERS"][name]["SLOTS"] = "1&2"
            else:
                stats_table["PEERS"][name]["SLOTS"] = "DMO"
            for ts in (1, 2):
                stats_table["PEERS"][name][ts] = {
                    "COLOR": "", "BGCOLOR": "", "TS": "", "TYPE": "", "SUB": "",
                    "SRC": "", "DEST": "",
                }
        elif data.get("MODE") == "OPENBRIDGE":
            stats_table["OPENBRIDGES"][name] = {}
            stats_table["OPENBRIDGES"][name]["NETWORK_ID"] = int_id_fn(data.get("NETWORK_ID", 0))
            # TARGET_IP/TARGET_PORT omitted on purpose: not sent over WebSocket, not shown in UI
            stats_table["OPENBRIDGES"][name]["STREAMS"] = {}


def clean_te(stats_table: dict) -> None:
    """Clear stale timeslot entries (timeout > 3 min)."""
    timeout = time.time()
    for system in list(stats_table.get("MASTERS", {})):
        for peer in list(stats_table["MASTERS"][system].get("PEERS", {})):
            for ts in (1, 2):
                ent = stats_table["MASTERS"][system]["PEERS"][peer][ts]
                if ent.get("TS"):
                    ts_val = ent.get("TIMEOUT", 0)
                    td = abs(ts_val - timeout) / 60
                    if td > 3:
                        ent["TS"] = False
                        ent["TYPE"] = ent["SUB"] = ent["SRC"] = ent["DEST"] = ""
    for system in list(stats_table.get("PEERS", {})):
        for ts in (1, 2):
            ent = stats_table["PEERS"][system][ts]
            if ent.get("TS"):
                ts_val = ent.get("TIMEOUT", 0)
                td = abs(ts_val - timeout) / 60
                if td > 3:
                    ent["TS"] = False
                    ent["TYPE"] = ent["SUB"] = ent["SRC"] = ent["DEST"] = ""
    for system in list(stats_table.get("OPENBRIDGES", {})):
        streams = stats_table["OPENBRIDGES"][system].get("STREAMS", {})
        for stream_id in list(streams):
            ts_val = streams[stream_id][3]
            td = abs(ts_val - timeout) / 60
            if td > 3:
                del streams[stream_id]


def update_hblink_table_impl(
    config: dict,
    stats_table: dict,
    time_str_fn: Callable[[Any, str], str],
    int_id_fn: Callable[[Any], int],
    bytes_4_fn: Callable[[int], bytes],
) -> None:
    """Sync CTABLE with config: add new peers, remove missing, update connection times."""
    for name in config:
        if config[name].get("MODE") != "MASTER":
            continue
        masters_peers = stats_table["MASTERS"].get(name, {}).get("PEERS", {})
        for peer_key in config[name].get("PEERS", {}):
            pid = int_id_fn(peer_key)
            if pid not in masters_peers and config[name]["PEERS"][peer_key].get("CONNECTION") == "YES":
                add_hb_peer(
                    config[name]["PEERS"][peer_key],
                    masters_peers,
                    peer_key,
                    time_str_fn,
                    int_id_fn,
                )
    for name in list(stats_table.get("MASTERS", {})):
        if config.get(name, {}).get("MODE") != "MASTER":
            continue
        remove_list = []
        for peer_id in list(stats_table["MASTERS"][name]["PEERS"]):
            if bytes_4_fn(peer_id) not in config[name].get("PEERS", {}):
                remove_list.append(peer_id)
        for peer_id in remove_list:
            del stats_table["MASTERS"][name]["PEERS"][peer_id]
    for name in stats_table.get("MASTERS", {}):
        for peer_id in list(stats_table["MASTERS"][name]["PEERS"]):
            peer_4 = bytes_4_fn(peer_id)
            if peer_4 in config.get(name, {}).get("PEERS", {}):
                peer_conf = config[name]["PEERS"][peer_4]
                stats_table["MASTERS"][name]["PEERS"][peer_id]["CONNECTED"] = time_str_fn(
                    peer_conf.get("CONNECTED", 0), "since"
                )
    for name in stats_table.get("PEERS", {}):
        if stats_table["PEERS"][name].get("MODE") == "XLXPEER":
            xlx = config.get(name, {}).get("XLXSTATS", {})
            stats_table["PEERS"][name]["STATS"]["CONNECTION"] = xlx.get("CONNECTION", "NO")
            if xlx.get("CONNECTION") == "YES":
                stats_table["PEERS"][name]["STATS"]["CONNECTED"] = time_str_fn(xlx.get("CONNECTED", 0), "since")
                stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = xlx.get("PINGS_SENT", 0)
                stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = xlx.get("PINGS_ACKD", 0)
            else:
                stats_table["PEERS"][name]["STATS"]["CONNECTED"] = "--   --"
                stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = 0
                stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = 0
        else:
            st = config.get(name, {}).get("STATS", {})
            stats_table["PEERS"][name]["STATS"]["CONNECTION"] = st.get("CONNECTION", "NO")
            if st.get("CONNECTION") == "YES":
                stats_table["PEERS"][name]["STATS"]["CONNECTED"] = time_str_fn(st.get("CONNECTED", 0), "since")
                stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = st.get("PINGS_SENT", 0)
                stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = st.get("PINGS_ACKD", 0)
            else:
                stats_table["PEERS"][name]["STATS"]["CONNECTED"] = "--   --"
                stats_table["PEERS"][name]["STATS"]["PINGS_SENT"] = 0
                stats_table["PEERS"][name]["STATS"]["PINGS_ACKD"] = 0
    clean_te(stats_table)
