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

"""Resolve the browser/client IP behind reverse proxies (login-by-ip parity).

Supports both literal IPs (``127.0.0.1``) and CIDR ranges (``172.16.0.0/12``)
in ``TRUSTED_PROXY_IPS`` so Docker / Traefik gateway IPs can be trusted without
listing every possible container address.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from fastapi import Request

_DEFAULT_TRUSTED = frozenset({"127.0.0.1", "::1", "localhost"})


@dataclass(frozen=True)
class TrustedProxySet:
    """Pre-compiled trusted-proxy rules (literal IPs + CIDR networks)."""

    literals: frozenset[str]
    networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]

    def __contains__(self, ip: str) -> bool:
        if ip in self.literals:
            return True
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(addr in net for net in self.networks)

    def __bool__(self) -> bool:
        return bool(self.literals) or bool(self.networks)


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
    trusted_proxies: TrustedProxySet | None = None,
) -> str:
    """Return the client IP for auth/self-service.

    When the immediate peer is a trusted reverse proxy (nginx on localhost or
    a Docker gateway in a trusted CIDR), use ``X-Real-IP`` or the first hop
    in ``X-Forwarded-For``. Otherwise use ``request.client.host`` (direct).
    """
    peer = request.client.host if request.client else ""
    if not peer:
        return ""

    if trusted_proxies is not None:
        trusted = peer in trusted_proxies
    else:
        trusted = peer in _DEFAULT_TRUSTED
    if not trusted:
        return peer

    real_ip = (request.headers.get("x-real-ip") or "").strip()
    if real_ip:
        return _normalize_ip(real_ip)

    forwarded = (request.headers.get("x-forwarded-for") or "").strip()
    if forwarded:
        return _normalize_ip(forwarded.split(",")[0])

    return peer


def trusted_proxies_from_config(app_config: dict) -> TrustedProxySet | None:
    """Parse ``APP.TRUSTED_PROXY_IPS`` (comma-separated or list).

    Each entry can be a literal IP (``127.0.0.1``) or a CIDR range
    (``172.16.0.0/12``).  Returns ``None`` when the key is absent so the
    caller falls back to the compile-time defaults.
    """
    raw = app_config.get("TRUSTED_PROXY_IPS")
    if raw is None:
        return None
    if isinstance(raw, str):
        items = [x.strip() for x in raw.split(",") if x.strip()]
    elif isinstance(raw, (list, tuple)):
        items = [str(x).strip() for x in raw if str(x).strip()]
    else:
        return None

    literals: set[str] = set()
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    for item in items:
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            literals.add(item)

    return TrustedProxySet(
        literals=frozenset(literals),
        networks=tuple(networks),
    )
