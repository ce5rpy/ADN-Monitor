"""FastAPI application tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from adn_monitor.infrastructure.fastapi import create_app


def _sample_config() -> dict:
    return {
        "APP": {
            "LISTEN_HOST": "",
            "LISTEN_PORT": 8080,
            "INGEST": "tcp",
            "AUTO_START_INGEST": False,
            "MQTT": {"URL": "", "TOPIC_PREFIX": "", "QOS": 0},
        },
        "ADN_CXN": {"ADN_IP": "10.0.0.1", "ADN_PORT": 4321, "HELLO_TIMEOUT_MS": 1500},
        "DB": {
            "SERVER": "localhost",
            "USER": "u",
            "PASSWD": "p",
            "NAME": "hbmon",
            "PORT": 3306,
            "PBKDF2_SALT": "ADN",
            "PBKDF2_ITERATIONS": 2000,
            "USE_SELFSERVICE": True,
        },
        "WS": {"WS_PORT": 9000},
        "DASHBOARD": {"DASHTITLE": "Test Dashboard"},
    }


def test_health_endpoints():
    client = TestClient(create_app(_sample_config()))
    for path in ("/health", "/api/health"):
        resp = client.get(path)
        assert resp.status_code == 200
        body = resp.json()
        assert body == {"status": "ok", "service": "adn-monitor"}


def test_ws_route_registered():
    routes = [getattr(r, "path", None) for r in create_app(_sample_config()).routes]
    assert "/ws" in routes


def test_rest_routes_registered():
    routes = [getattr(r, "path", None) for r in create_app(_sample_config()).routes]
    for path in (
        "/api/config/dashboard",
        "/api/servers/status",
        "/api/aliases/tg-list",
        "/api/auth/me",
        "/api/self-service/device",
    ):
        assert path in routes


def test_dashboard_config_endpoint():
    cfg = _sample_config()
    cfg["DASHBOARD"] = {
        "DASHTITLE": "Test",
        "LANGUAGE": "es",
        "SELF_SERVICE": True,
        "nav_links": {"name": "Links", "items": [{"name": "ADN", "url": "https://adn.systems"}]},
    }
    resp = TestClient(create_app(cfg)).get("/api/config/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Test"
    assert body["monitorVersion"]
    assert body["language"] == "es"
    assert body["selfService"] is True
    assert body["navLinks"]["items"][0]["name"] == "ADN"


def test_health_unchanged_for_mqtt_ingest_config():
    cfg = _sample_config()
    cfg["APP"]["INGEST"] = "mqtt"
    cfg["APP"]["MQTT"] = {
        "URL": "mqtt://broker:1883",
        "TOPIC_PREFIX": "adn/7302",
        "QOS": 1,
    }
    resp = TestClient(create_app(cfg)).get("/api/health")
    assert resp.json() == {"status": "ok", "service": "adn-monitor"}
