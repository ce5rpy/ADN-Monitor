"""FastAPI application factory."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .composition import build_monitor_api
from .runtime import MonitorRuntime
from .routes.aliases_proxy import router as aliases_router
from .routes.auth import router as auth_router
from .routes.config_api import router as config_router
from .routes.health import router as health_router
from .routes.self_service import router as self_service_router
from .routes.servers_status import router as servers_status_router
from .routes.ws import router as ws_router


@asynccontextmanager
async def _lifespan(app: FastAPI):
    config = app.state.monitor_config
    runtime: MonitorRuntime | None = None
    if config.get("APP", {}).get("AUTO_START_INGEST", True):
        runtime = MonitorRuntime(config)
        runtime.start()
        runtime.start_background_tasks()
        app.state.monitor_runtime = runtime
    try:
        yield
    finally:
        if runtime is not None:
            await runtime.stop_background_tasks()
            runtime.stop()
            app.state.monitor_runtime = None


def create_app(config: dict[str, Any]) -> FastAPI:
    """Build the unified monitor HTTP app from ``load_config()`` dict."""
    app_conf = config.get("APP", {})
    title = config.get("DASHBOARD", {}).get("DASHTITLE", "ADN Monitor")

    app = FastAPI(
        title=str(title),
        version="2.0.0-dev",
        lifespan=_lifespan,
    )
    app.state.monitor_config = config
    app.state.monitor_api = build_monitor_api(config)

    db = config.get("DB") or {}
    session_secret = (
        os.environ.get("MONITOR_SESSION_SECRET", "").strip()
        or str(db.get("PBKDF2_SALT", "ADN"))
        + "-monitor-session"
    )
    app.add_middleware(SessionMiddleware, secret_key=session_secret, max_age=3600 * 24 * 30)

    origins = app_conf.get("CORS_ORIGINS") or ["*"]
    if isinstance(origins, str):
        origins = [o.strip() for o in origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(config_router)
    app.include_router(aliases_router)
    app.include_router(servers_status_router)
    app.include_router(auth_router)
    app.include_router(self_service_router)
    app.include_router(ws_router)
    return app
