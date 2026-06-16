# ADN Monitor - application dashboard config
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

"""Build dashboard JSON for GET /api/config/dashboard."""

from __future__ import annotations

from typing import Any


def _bool(val: object) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


def _link_items(raw: object) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for entry in raw:
        if isinstance(entry, dict) and "name" in entry:
            out.append({"name": str(entry["name"]), "url": str(entry.get("url", ""))})
        elif isinstance(entry, str):
            parts = entry.split(",", 1)
            out.append({"name": parts[0].strip(), "url": (parts[1] if len(parts) > 1 else "").strip()})
    return out


def _normalize_nav_links(dashboard: dict[str, Any]) -> dict[str, Any]:
    nav = dashboard.get("nav_links") or dashboard.get("NAV_LINKS")
    if isinstance(nav, dict):
        items = nav.get("items") or nav.get("Items") or []
        return {"name": str(nav.get("name") or nav.get("Name") or ""), "items": _link_items(items)}
    name = str(dashboard.get("NAV_LNK_NAME") or dashboard.get("nav_lnk_name") or "")
    items: list[dict[str, str]] = []
    for i in range(1, 100):
        val = dashboard.get(f"LINK{i}") or dashboard.get(f"link{i}")
        if val is None or val == "":
            break
        parts = str(val).split(",", 1)
        items.append({"name": parts[0].strip(), "url": (parts[1] if len(parts) > 1 else "").strip()})
    return {"name": name, "items": items}


def _normalize_footer(dashboard: dict[str, Any]) -> list[dict[str, str]]:
    footer = dashboard.get("footer") or dashboard.get("FOOTER")
    if isinstance(footer, dict):
        return _link_items(footer.get("items") or footer.get("Items") or footer)
    if isinstance(footer, list):
        return _link_items(footer)
    items: list[dict[str, str]] = []
    for i in range(1, 100):
        val = dashboard.get(f"FOOTER{i}") or dashboard.get(f"footer{i}")
        if val is None or val == "":
            break
        parts = str(val).split(",", 1)
        items.append({"name": parts[0].strip(), "url": (parts[1] if len(parts) > 1 else "").strip()})
    return items


def _normalize_news(dashboard: dict[str, Any]) -> list[dict[str, str]]:
    news = dashboard.get("news") or dashboard.get("NEWS")
    if isinstance(news, dict):
        return _link_items(news.get("items") or news.get("Items") or news)
    if isinstance(news, list):
        return _link_items(news)
    items: list[dict[str, str]] = []
    for i in range(1, 100):
        val = dashboard.get(f"NEWS{i}") or dashboard.get(f"news{i}")
        if val is None or val == "":
            break
        parts = str(val).split(",", 1)
        items.append({"name": parts[0].strip(), "url": (parts[1] if len(parts) > 1 else "").strip()})
    return items


def build_dashboard_config(config: dict[str, Any]) -> dict[str, Any]:
    dashboard = config.get("DASHBOARD") or {}
    if not isinstance(dashboard, dict):
        dashboard = {}
    title = dashboard.get("DASHTITLE") or dashboard.get("dashtitle") or "ADN Systems Dashboard"
    return {
        "title": str(title),
        "language": str(dashboard.get("LANGUAGE") or dashboard.get("language") or "en"),
        "background": _bool(dashboard.get("BACKGROUND") if "BACKGROUND" in dashboard else dashboard.get("background", False)),
        "selfService": _bool(
            dashboard.get("SELF_SERVICE") if "SELF_SERVICE" in dashboard else dashboard.get("self_service", False)
        ),
        "showConsole": _bool(
            dashboard.get("SHOW_CONSOLE") if "SHOW_CONSOLE" in dashboard else dashboard.get("show_console", False)
        ),
        "footer": _normalize_footer(dashboard),
        "news": _normalize_news(dashboard),
        "navLinks": _normalize_nav_links(dashboard),
    }
