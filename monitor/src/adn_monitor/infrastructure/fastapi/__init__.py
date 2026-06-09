"""Unified FastAPI application (REST + WebSocket)."""

from .app import create_app

__all__ = ["create_app"]
