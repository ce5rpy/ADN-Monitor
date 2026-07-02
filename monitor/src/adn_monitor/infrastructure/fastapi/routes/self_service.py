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

"""Self-service HTTP routes (/api/self-service/devices)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....domain import is_fail
from ..client_ip import client_ip_from_request
from ..composition import MonitorApi
from ..session_http import session_user

router = APIRouter(prefix="/api/self-service", tags=["self-service"])


class OptionsBody(BaseModel):
    options: str = ""


def _api(request: Request) -> MonitorApi:
    return request.app.state.monitor_api


@router.get("/devices")
async def list_devices(request: Request) -> JSONResponse:
    """Live list of logged-in devices matching the caller's IP (queries DB on every call)."""
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    user = session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    devices = api.self_service.list_devices(user, client_ip_from_request(request))
    int_ids = [int(d["int_id"]) for d in devices]
    selected = (
        user.selected_int_id
        if user.selected_int_id in int_ids
        else (int_ids[0] if int_ids else None)
    )
    return JSONResponse({"devices": devices, "selected_int_id": selected})


@router.get("/devices/{int_id}")
async def get_device(request: Request, int_id: int) -> JSONResponse:
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    user = session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    result = api.self_service.get_device(user, int_id, client_ip_from_request(request))
    if is_fail(result):
        err = str(result.error)
        if err == "Device not found":
            return JSONResponse({"error": err}, status_code=404)
        if err == "Device not allowed":
            return JSONResponse({"error": err}, status_code=403)
        return JSONResponse({"error": err}, status_code=400)
    return JSONResponse(result.value)


@router.patch("/devices/{int_id}")
async def update_device(request: Request, int_id: int, body: OptionsBody) -> JSONResponse:
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    user = session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    result = api.self_service.update_options(user, int_id, body.options, client_ip_from_request(request))
    if is_fail(result):
        err = str(result.error)
        status = 403 if err == "Device not allowed" else 400
        return JSONResponse({"error": err}, status_code=status)
    return JSONResponse({"ok": True})


@router.get("/devices/{int_id}/modified")
async def get_modified(request: Request, int_id: int) -> JSONResponse:
    api = _api(request)
    if api.self_service is None:
        return JSONResponse({"modified": 0})
    user = session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    modified = api.self_service.get_modified(user, int_id, client_ip_from_request(request))
    return JSONResponse({"modified": modified})
