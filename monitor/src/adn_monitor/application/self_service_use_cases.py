# ADN Monitor - application self service use cases
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

"""Self-service device use cases (Clients table)."""

from __future__ import annotations

from ..domain import Failure, Result, Success
from ..domain.session import UserSession
from .ports import AuthRepository, DeviceRepository
from .self_service_options import normalize_options_for_save, parse_options


class SelfServiceUseCases:
    def __init__(
        self,
        device_repo: DeviceRepository,
        auth_repo: AuthRepository | None = None,
    ) -> None:
        self._repo = device_repo
        self._auth_repo = auth_repo

    def list_devices(self, user: UserSession, host: str) -> list[dict[str, object]]:
        """Live list of logged-in devices, branched by login method.

        - login_method="password": all logged-in devices for the callsign.
        - login_method="ip": only logged-in devices matching the caller's IP.
        """
        if self._auth_repo is None:
            return [{"int_id": i, "callsign": user.callsign} for i in user.int_ids]
        if user.login_method == "ip":
            return self._auth_repo.get_logged_in_devices_by_host(host)
        return self._auth_repo.get_logged_in_devices_by_callsign(user.callsign)

    def _allowed_int_ids(self, user: UserSession, host: str) -> set[int]:
        return {int(d["int_id"]) for d in self.list_devices(user, host)}

    def get_device(self, user: UserSession, int_id: int | None, host: str) -> Result[dict[str, object], str]:
        selected = int(int_id or user.selected_int_id or 0)
        if not selected:
            return Failure("Device not selected")
        if selected not in self._allowed_int_ids(user, host):
            return Failure("Device not allowed")
        client = self._repo.get_by_id(selected)
        if client is None:
            return Failure("Device not found")
        return Success(
            {
                "int_id": client.int_id,
                "callsign": client.callsign,
                "mode": client.mode,
                "options": parse_options(client.options),
            }
        )

    def update_options(
        self,
        user: UserSession,
        int_id: int | None,
        options_raw: str,
        host: str,
    ) -> Result[None, str]:
        selected = int(int_id or user.selected_int_id or 0)
        if not selected:
            return Failure("Invalid request")
        if selected not in self._allowed_int_ids(user, host):
            return Failure("Device not allowed")
        options = normalize_options_for_save(options_raw)
        if options is None:
            if not options_raw.strip():
                return Failure("Options cannot be empty")
            return Failure("Options too long")
        if self._repo.update_options(selected, options) < 1:
            return Failure("Update failed")
        return Success(None)

    def get_modified(self, user: UserSession, int_id: int | None, host: str) -> int:
        selected = int(int_id or user.selected_int_id or 0)
        if not selected or selected not in self._allowed_int_ids(user, host):
            return 0
        return 1 if self._repo.get_modified(selected) else 0
