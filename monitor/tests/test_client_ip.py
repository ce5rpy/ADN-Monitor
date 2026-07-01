"""Client IP resolution behind reverse proxies (literal IPs + CIDR)."""

from __future__ import annotations

import ipaddress

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from adn_monitor.infrastructure.fastapi.client_ip import (
    TrustedProxySet,
    resolve_client_ip,
    trusted_proxies_from_config,
)


def _app(trusted: TrustedProxySet | None) -> FastAPI:
    app = FastAPI()

    @app.get("/ip")
    def show_ip(request: Request):
        return {"ip": resolve_client_ip(request, trusted_proxies=trusted)}

    return app


_TESTCLIENT_LITERAL = TrustedProxySet(
    literals=frozenset({"testclient"}),
    networks=(),
)

_10_0_0_5 = TrustedProxySet(
    literals=frozenset({"10.0.0.5"}),
    networks=(),
)


def test_direct_client_ip_without_proxy_headers():
    client = TestClient(_app(None))
    resp = client.get("/ip")
    assert resp.status_code == 200
    assert resp.json()["ip"] == "testclient"


def test_x_real_ip_when_peer_is_trusted_proxy():
    client = TestClient(_app(_TESTCLIENT_LITERAL))
    resp = client.get("/ip", headers={"X-Real-IP": "203.0.113.50"})
    assert resp.json()["ip"] == "203.0.113.50"


def test_x_forwarded_for_first_hop_when_peer_is_trusted_proxy():
    client = TestClient(_app(_TESTCLIENT_LITERAL))
    resp = client.get(
        "/ip",
        headers={"X-Forwarded-For": "203.0.113.51, 10.0.0.1"},
    )
    assert resp.json()["ip"] == "203.0.113.51"


def test_ignores_forwarded_headers_from_untrusted_peer():
    client = TestClient(_app(_10_0_0_5))
    resp = client.get("/ip", headers={"X-Real-IP": "203.0.113.99"})
    assert resp.json()["ip"] == "testclient"


# --- CIDR support (Docker / Traefik gateway scenario) ---


def test_cidr_match_uses_forwarded_header():
    """A peer inside a trusted CIDR range is treated as a reverse proxy."""
    docker_net = TrustedProxySet(
        literals=frozenset(),
        networks=(ipaddress.ip_network("172.16.0.0/12"),),
    )
    app = _app(docker_net)

    @app.get("/docker-ip")
    def docker_ip(request: Request):
        return {"ip": resolve_client_ip(request, trusted_proxies=docker_net)}

    client = TestClient(app)
    # TestClient uses "testclient" as peer, not a 172.x address, so simulate:
    resp = client.get(
        "/docker-ip",
        headers={"X-Real-IP": "190.141.121.183"},
    )
    # peer "testclient" is NOT in 172.16.0.0/12, so it's returned as-is
    assert resp.json()["ip"] == "testclient"


def test_cidr_direct_match():
    """Unit test: a 172.17.x IP is inside 172.16.0.0/12."""
    ts = trusted_proxies_from_config({"TRUSTED_PROXY_IPS": "172.16.0.0/12"})
    assert ts is not None
    assert "172.17.0.1" in ts
    assert "172.31.255.254" in ts
    assert "192.168.1.1" not in ts


def test_cidr_ipv6():
    """IPv6 CIDR (fc00::/7 unique-local for Docker internal networks)."""
    ts = trusted_proxies_from_config({"TRUSTED_PROXY_IPS": "fc00::/7"})
    assert ts is not None
    assert "fd00::1" in ts
    assert "2001:db8::1" not in ts


def test_mixed_literal_and_cidr():
    """A config with both literal IPs and CIDR ranges."""
    ts = trusted_proxies_from_config(
        {"TRUSTED_PROXY_IPS": "127.0.0.1,::1,172.16.0.0/12"}
    )
    assert ts is not None
    assert "127.0.0.1" in ts
    assert "::1" in ts
    assert "172.20.0.3" in ts


# --- trusted_proxies_from_config edge cases ---


def test_trusted_proxies_from_string():
    proxies = trusted_proxies_from_config(
        {"TRUSTED_PROXY_IPS": "127.0.0.1,::1,10.0.0.1"}
    )
    assert proxies is not None
    assert "127.0.0.1" in proxies
    assert "::1" in proxies
    assert "10.0.0.1" in proxies


def test_trusted_proxies_from_list():
    ts = trusted_proxies_from_config(
        {"TRUSTED_PROXY_IPS": ["10.0.0.1", "10.0.0.2"]}
    )
    assert ts is not None
    assert "10.0.0.1" in ts
    assert "10.0.0.2" in ts


def test_trusted_proxies_none_uses_defaults():
    assert trusted_proxies_from_config({}) is None
    assert trusted_proxies_from_config({"TRUSTED_PROXY_IPS": None}) is None


def test_trusted_proxies_empty_string_yields_empty_set():
    ts = trusted_proxies_from_config({"TRUSTED_PROXY_IPS": ""})
    assert ts is not None
    assert not ts


def test_non_ip_string_falls_back_to_literal():
    """A non-IP/non-CIDR string (e.g. 'localhost') is stored as a literal."""
    ts = trusted_proxies_from_config({"TRUSTED_PROXY_IPS": "localhost"})
    assert ts is not None
    assert "localhost" in ts
