"""Health and readiness (ops / doctor precursor)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


def _ingest_summary(config: dict[str, Any]) -> dict[str, Any]:
    app_conf = config.get("APP", {})
    adn = config.get("ADN_CXN", {})
    mode = str(app_conf.get("INGEST", "tcp")).lower()
    if mode not in ("tcp", "mqtt"):
        mode = "tcp"
    summary: dict[str, Any] = {
        "mode": mode,
        "exclusive": True,
        "adn_ip": adn.get("ADN_IP", "") if mode == "tcp" else None,
        "adn_port": adn.get("ADN_PORT", 0) if mode == "tcp" else None,
    }
    if mode == "mqtt":
        mqtt = app_conf.get("MQTT", {})
        summary["mqtt_url"] = mqtt.get("URL", "")
        summary["topic_prefix"] = mqtt.get("TOPIC_PREFIX", "")
    return summary


@router.get("/health")
@router.get("/api/health")
def health(request: Request) -> dict[str, Any]:
    """Liveness: process up and config loaded."""
    config: dict[str, Any] = request.app.state.monitor_config
    db = config.get("DB")
    runtime = getattr(request.app.state, "monitor_runtime", None)
    body: dict[str, Any] = {
        "status": "ok",
        "service": "adn-monitor",
        "ingest": _ingest_summary(config),
        "self_service_db": bool(db),
        "listen_port": config.get("APP", {}).get("LISTEN_PORT"),
    }
    if runtime is not None:
        n_m = len(runtime.state.CTABLE.get("MASTERS", {}))
        body["report"] = {
            "connected": runtime.state.server_mode_confirmed,
            "slim_wire": runtime.state.slim_wire,
            "masters": n_m,
        }
    return body
