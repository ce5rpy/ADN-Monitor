# ADN Monitor - infrastructure fastapi routes self service
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

"""Self-service HTTP routes (/api/self-service)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....domain import is_fail
from ..composition import MonitorApi
from ..session_http import require_session_user, touch_session

router = APIRouter(prefix="/api/self-service", tags=["self-service"])


class OptionsBody(BaseModel):
    int_id: int = 0
    options: str = ""


class SelectBody(BaseModel):
    int_id: int = 0


def _api(request: Request) -> MonitorApi:
    return request.app.state.monitor_api


@router.get("/device")
async def get_device(request: Request, int_id: int | None = None) -> JSONResponse:
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    user = require_session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    result = api.self_service.get_device(user, int_id)
    if is_fail(result):
        err = str(result.error)
        if err == "Device not found":
            return JSONResponse({"error": err}, status_code=404)
        if err == "Device not allowed":
            return JSONResponse({"error": err}, status_code=403)
        return JSONResponse({"error": err}, status_code=400)
    return JSONResponse(result.value)


@router.post("/device/options")
async def update_options(request: Request, body: OptionsBody) -> JSONResponse:
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    user = require_session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    int_id = body.int_id or None
    result = api.self_service.update_options(user, int_id, body.options)
    if is_fail(result):
        err = str(result.error)
        status = 403 if err == "Device not allowed" else 400
        return JSONResponse({"error": err}, status_code=status)
    return JSONResponse({"ok": True})


@router.get("/device/modified")
async def get_modified(request: Request, int_id: int | None = None) -> JSONResponse:
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"modified": 0})
    user = require_session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    modified = api.self_service.get_modified(user, int_id)
    return JSONResponse({"modified": modified})


@router.post("/device/select")
async def select_device(request: Request, body: SelectBody) -> JSONResponse:
    user = require_session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    result = api.self_service.select_device(user, body.int_id)
    if is_fail(result):
        return JSONResponse({"error": "Invalid device"}, status_code=400)
    touch_session(request)
    request.session["selected_int_id"] = result.value
    return JSONResponse({"ok": True})
