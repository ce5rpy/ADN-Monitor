"""Health and readiness (public liveness only — no host/port config)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
@router.get("/api/health")
def health(request: Request) -> dict[str, Any]:
    """Liveness: process up; optional high-level report link status."""
    body: dict[str, Any] = {
        "status": "ok",
        "service": "adn-monitor",
    }
    runtime = getattr(request.app.state, "monitor_runtime", None)
    if runtime is not None:
        body["report"] = {
            "connected": runtime.state.server_mode_confirmed,
            "slim_wire": runtime.state.slim_wire,
            "masters": len(runtime.state.CTABLE.get("MASTERS", {})),
        }
    return body
