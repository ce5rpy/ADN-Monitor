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
