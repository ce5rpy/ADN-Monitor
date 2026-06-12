# ADN Monitor - infrastructure fastapi client ip
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

"""Resolve the browser/client IP behind reverse proxies (login-by-ip parity)."""

from __future__ import annotations

from fastapi import Request

_DEFAULT_TRUSTED = frozenset({"127.0.0.1", "::1", "localhost"})


def _normalize_ip(value: str) -> str:
    value = value.strip()
    if value.startswith("[") and "]" in value:
        return value[1 : value.index("]")]
    if value.count(":") == 1 and value.rsplit(":", 1)[0].count(".") == 3:
        # IPv4:port from X-Forwarded-For edge cases
        return value.rsplit(":", 1)[0]
    return value


def resolve_client_ip(
    request: Request,
    *,
    trusted_proxies: frozenset[str] | None = None,
) -> str:
    """Return the client IP for auth/self-service.

    When the immediate peer is a trusted reverse proxy (nginx on localhost),
    use ``X-Real-IP`` or the first hop in ``X-Forwarded-For``. Otherwise use
    ``request.client.host`` (direct access).
    """
    peer = request.client.host if request.client else ""
    if not peer:
        return ""

    trusted = trusted_proxies if trusted_proxies is not None else _DEFAULT_TRUSTED
    if peer not in trusted:
        return peer

    real_ip = (request.headers.get("x-real-ip") or "").strip()
    if real_ip:
        return _normalize_ip(real_ip)

    forwarded = (request.headers.get("x-forwarded-for") or "").strip()
    if forwarded:
        return _normalize_ip(forwarded.split(",")[0])

    return peer


def trusted_proxies_from_config(app_config: dict) -> frozenset[str] | None:
    """Parse ``APP.TRUSTED_PROXY_IPS`` (comma-separated); ``None`` = defaults."""
    raw = app_config.get("TRUSTED_PROXY_IPS")
    if raw is None:
        return None
    if isinstance(raw, str):
        items = [x.strip() for x in raw.split(",") if x.strip()]
    elif isinstance(raw, (list, tuple)):
        items = [str(x).strip() for x in raw if str(x).strip()]
    else:
        return None
    return frozenset(items) if items else frozenset()
