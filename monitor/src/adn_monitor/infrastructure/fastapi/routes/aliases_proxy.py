# ADN Monitor - infrastructure fastapi routes aliases proxy
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
