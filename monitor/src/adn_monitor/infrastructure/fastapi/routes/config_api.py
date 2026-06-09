"""Dashboard config route (GET /api/config/dashboard)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ....application.dashboard_config import build_dashboard_config

router = APIRouter(tags=["config"])


@router.get("/api/config/dashboard")
async def dashboard_config(request: Request) -> dict:
    return build_dashboard_config(request.app.state.monitor_config)
