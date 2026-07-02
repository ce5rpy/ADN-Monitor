# ADN Monitor - infrastructure fastapi routes auth
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

"""Auth HTTP routes (/api/auth)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....domain import is_fail
from ..client_ip import client_ip_from_request
from ..composition import MonitorApi
from ..session_http import destroy_session, session_to_me_payload, session_user, start_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginBody(BaseModel):
    callsign: str = ""
    password: str = ""


def _api(request: Request) -> MonitorApi:
    return request.app.state.monitor_api


@router.post("/login")
async def login(request: Request, body: LoginBody) -> JSONResponse:
    api = _api(request)
    if api.auth is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    result = api.auth.login(body.callsign, body.password)
    if is_fail(result):
        err = str(result.error)
        status = 400 if err == "Missing callsign or password" else 401
        return JSONResponse({"error": err if status == 400 else "Invalid callsign or password"}, status_code=status)
    start_session(request, result.value)
    return JSONResponse({"redirect": "/self-service"})


@router.get("/login-by-ip")
async def login_by_ip(request: Request) -> JSONResponse:
    api = _api(request)
    if api.auth is None:
        return JSONResponse({"error": "Self-service DB not configured"}, status_code=503)
    result = api.auth.login_by_ip(client_ip_from_request(request))
    if is_fail(result):
        return JSONResponse({"error": "No single user for this IP"}, status_code=401)
    start_session(request, result.value)
    return JSONResponse({"redirect": "/self-service"})


@router.post("/logout")
async def logout(request: Request) -> JSONResponse:
    destroy_session(request)
    return JSONResponse({"redirect": "/login"})


@router.get("/me")
async def me(request: Request) -> JSONResponse:
    user = session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return JSONResponse(session_to_me_payload(user))
