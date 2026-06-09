"""HTTP session cookie adapter (Starlette SessionMiddleware; no business logic)."""

from __future__ import annotations

import time
from typing import Any

from fastapi import Request

from ...domain.session import UserSession

SESSION_TIMEOUT = 3600 * 24 * 30  # 30 days


def touch_session(request: Request) -> None:
    session = request.session
    last = session.get("last_activity")
    if last is not None and (time.time() - float(last) > SESSION_TIMEOUT):
        request.session.clear()
    request.session["last_activity"] = time.time()


def start_session(request: Request, user: UserSession) -> None:
    touch_session(request)
    request.session["user_id"] = user.callsign
    request.session["int_ids"] = list(user.int_ids)
    request.session["selected_int_id"] = user.selected_int_id


def destroy_session(request: Request) -> None:
    request.session.clear()


def session_user(request: Request) -> UserSession | None:
    touch_session(request)
    callsign = request.session.get("user_id")
    if not callsign:
        return None
    int_ids = [int(x) for x in (request.session.get("int_ids") or [])]
    selected = request.session.get("selected_int_id")
    return UserSession(
        callsign=str(callsign),
        int_ids=int_ids,
        selected_int_id=int(selected) if selected is not None else None,
    )


def require_session_user(request: Request) -> UserSession | None:
    return session_user(request)


def session_to_me_payload(user: UserSession) -> dict[str, Any]:
    return {
        "callsign": user.callsign,
        "int_ids": user.int_ids,
        "selected_int_id": user.selected_int_id,
    }
