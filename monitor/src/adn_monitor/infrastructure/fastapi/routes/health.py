# ADN Monitor - infrastructure fastapi routes health
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

"""Health and readiness (public liveness only — no host/port config)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
@router.get("/api/health")
def health(request: Request) -> dict[str, Any]:
    """Liveness: process up; optional high-level report link status."""
    body: dict[str, Any] = {
        "status": "ok",
        "service": "adn-monitor",
    }
    runtime = getattr(request.app.state, "monitor_runtime", None)
    if runtime is not None:
        body["db_connected"] = runtime.db_connected
        body["report"] = {
            "connected": runtime.state.server_mode_confirmed,
            "slim_wire": runtime.state.slim_wire,
            "masters": len(runtime.state.CTABLE.get("MASTERS", {})),
        }
    return body
