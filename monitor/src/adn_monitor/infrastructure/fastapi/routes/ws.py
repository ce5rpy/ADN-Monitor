# ADN Monitor - infrastructure fastapi routes ws
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

"""WebSocket dashboard endpoint (/ws)."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def dashboard_ws(websocket: WebSocket) -> None:
    runtime = getattr(websocket.app.state, "monitor_runtime", None)
    if runtime is None:
        await websocket.close(code=1013)
        return
    try:
        await runtime.ws_hub.handle_connection(
            websocket,
            state=runtime.state,
            conf_global=runtime.config_global,
            db_config=runtime.config.get("DB"),
            refresh_from_server=runtime.request_refresh,
        )
    except WebSocketDisconnect:
        pass
