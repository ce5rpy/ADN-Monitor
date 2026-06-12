# ADN Monitor - infrastructure fastapi routes servers status
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
