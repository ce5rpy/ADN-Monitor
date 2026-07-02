# ADN Monitor - infrastructure fastapi composition
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

"""Composition root: wire application use cases from config (DI)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...application.aliases_list_use_cases import AliasesListUseCases
from ...application.auth_use_cases import AuthUseCases
from ...application.self_service_use_cases import SelfServiceUseCases
from ...application.servers_status_use_cases import ServersStatusUseCases
from ..http.httpx_fetcher import HttpxFetcher
from ..persistence.sync_mysql import SyncMysqlPool
from ..repositories.clients_auth_repository import MysqlAuthRepository
from ..repositories.clients_device_repository import MysqlDeviceRepository


@dataclass
class MonitorApi:
    """Application services exposed to HTTP adapters."""

    auth: AuthUseCases | None
    self_service: SelfServiceUseCases | None
    aliases: AliasesListUseCases
    servers_status: ServersStatusUseCases


def build_monitor_api(config: dict[str, Any]) -> MonitorApi:
    fetcher = HttpxFetcher()
    auth_uc: AuthUseCases | None = None
    self_uc: SelfServiceUseCases | None = None
    db = config.get("DB")
    if db:
        pool = SyncMysqlPool(db)
        auth_repo = MysqlAuthRepository(pool)
        device_repo = MysqlDeviceRepository(pool)
        auth_uc = AuthUseCases(
            auth_repo,
            pbkdf2_salt=str(db.get("PBKDF2_SALT", "ADN")),
            pbkdf2_iterations=int(db.get("PBKDF2_ITERATIONS", 2000)),
        )
        self_uc = SelfServiceUseCases(device_repo, auth_repo=auth_repo)
    return MonitorApi(
        auth=auth_uc,
        self_service=self_uc,
        aliases=AliasesListUseCases(fetcher, config),
        servers_status=ServersStatusUseCases(fetcher, config),
    )
