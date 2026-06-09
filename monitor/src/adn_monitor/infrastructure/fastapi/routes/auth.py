"""Auth HTTP routes (/api/auth)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....domain import is_fail
from ..composition import MonitorApi
from ..session_http import destroy_session, require_session_user, session_to_me_payload, start_session

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
    ip = request.client.host if request.client else ""
    result = api.auth.login_by_ip(ip)
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
    user = require_session_user(request)
    if user is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return JSONResponse(session_to_me_payload(user))
