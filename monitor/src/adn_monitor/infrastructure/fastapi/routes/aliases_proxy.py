"""TG and bridge list proxy routes (/api/aliases)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from ....domain import is_fail
from ..composition import MonitorApi

router = APIRouter(prefix="/api/aliases", tags=["aliases"])


def _api(request: Request) -> MonitorApi:
    return request.app.state.monitor_api


@router.get("/tg-list")
async def tg_list(request: Request) -> Response:
    result = _api(request).aliases.fetch_tg_list()
    if is_fail(result):
        return JSONResponse({"error": result.error}, status_code=502)
    body, media_type = result.value
    return Response(content=body, media_type=media_type)


@router.get("/bridge-list")
async def bridge_list(request: Request) -> Response:
    result = _api(request).aliases.fetch_bridge_list()
    if is_fail(result):
        return JSONResponse({"error": result.error}, status_code=502)
    body, media_type = result.value
    return Response(content=body, media_type=media_type)
