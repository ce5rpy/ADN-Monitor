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

"""Build bridge table (BTABLE) from BRIDGES dict."""


def _int_id(raw: int | bytes) -> int:
    if isinstance(raw, bytes):
        return int.from_bytes(raw[:4], "big") if len(raw) >= 4 else 0
    return int(raw)


def build_bridge_table_impl(bridges: dict, now: float, int_id_fn=None) -> dict:
    """Build stats table for bridges. int_id_fn defaults to _int_id."""
    int_id_fn = int_id_fn or _int_id
    result = {}
    for bridge_name, system_list in list(bridges.items()):
        result[bridge_name] = {}
        for system in system_list:
            sys_name = system["SYSTEM"]
            result[bridge_name][sys_name] = {}
            result[bridge_name][sys_name]["TS"] = system["TS"]
            result[bridge_name][sys_name]["TGID"] = int_id_fn(system["TGID"])
            to_type = system.get("TO_TYPE", "")
            timer = system.get("TIMER", 0)
            if to_type in ("ON", "OFF"):
                if timer - now > 0:
                    result[bridge_name][sys_name]["EXP_TIME"] = int(timer - now)
                else:
                    result[bridge_name][sys_name]["EXP_TIME"] = "Expired"
                result[bridge_name][sys_name]["TO_ACTION"] = "Disconnect" if to_type == "ON" else "Connect"
            else:
                result[bridge_name][sys_name]["EXP_TIME"] = "N/A"
                result[bridge_name][sys_name]["TO_ACTION"] = "None"
            result[bridge_name][sys_name]["ACTIVE"] = "Connected" if system.get("ACTIVE") else "Disconnected"
            on_list = [str(int_id_fn(x)) for x in system.get("ON", [])]
            off_list = [str(int_id_fn(x)) for x in system.get("OFF", [])]
            result[bridge_name][sys_name]["TRIG_ON"] = ", ".join(on_list)
            result[bridge_name][sys_name]["TRIG_OFF"] = ", ".join(off_list)
    return result
