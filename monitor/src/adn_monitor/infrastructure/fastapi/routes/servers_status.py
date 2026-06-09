"""World servers status proxy (GET /api/servers/status)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from ....domain import is_fail
from ..composition import MonitorApi

router = APIRouter(tags=["servers"])


def _api(request: Request) -> MonitorApi:
    return request.app.state.monitor_api


@router.get("/api/servers/status")
async def servers_status(request: Request) -> Response:
    result = _api(request).servers_status.fetch_status()
    if is_fail(result):
        err = str(result.error)
        status = 500 if "Invalid SERVER_STATUS_URL" in err else 502
        return JSONResponse({"error": err}, status_code=status)
    return Response(content=result.value, media_type="application/json; charset=utf-8")
