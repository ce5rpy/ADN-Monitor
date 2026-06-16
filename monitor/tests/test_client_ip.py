"""Client IP resolution behind reverse proxies."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from adn_monitor.infrastructure.fastapi.client_ip import resolve_client_ip


def _app(*, trust_testclient: bool = False) -> FastAPI:
    app = FastAPI()
    trusted = frozenset({"testclient"}) if trust_testclient else None

    @app.get("/ip")
    def show_ip(request: Request):
        return {"ip": resolve_client_ip(request, trusted_proxies=trusted)}

    return app


def test_direct_client_ip_without_proxy_headers():
    client = TestClient(_app())
    resp = client.get("/ip")
    assert resp.status_code == 200
    assert resp.json()["ip"] == "testclient"


def test_x_real_ip_when_peer_is_trusted_proxy():
    client = TestClient(_app(trust_testclient=True))
    resp = client.get("/ip", headers={"X-Real-IP": "203.0.113.50"})
    assert resp.json()["ip"] == "203.0.113.50"


def test_x_forwarded_for_first_hop_when_peer_is_trusted_proxy():
    client = TestClient(_app(trust_testclient=True))
    resp = client.get(
        "/ip",
        headers={"X-Forwarded-For": "203.0.113.51, 10.0.0.1"},
    )
    assert resp.json()["ip"] == "203.0.113.51"


def test_ignores_forwarded_headers_from_untrusted_peer(monkeypatch):
    app = FastAPI()

    @app.get("/ip")
    def show_ip(request: Request):
        return {
            "ip": resolve_client_ip(
                request,
                trusted_proxies=frozenset({"10.0.0.5"}),
            )
        }

    client = TestClient(app)
    resp = client.get("/ip", headers={"X-Real-IP": "203.0.113.99"})
    assert resp.json()["ip"] == "testclient"
