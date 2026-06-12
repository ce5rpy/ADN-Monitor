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
from .ports import DeviceRepository
from .self_service_options import normalize_options_for_save, parse_options


class SelfServiceUseCases:
    def __init__(self, device_repo: DeviceRepository) -> None:
        self._repo = device_repo

    def get_device(self, user: UserSession, int_id: int | None) -> Result[dict[str, object], str]:
        selected = int(int_id or user.selected_int_id or 0)
        if not selected:
            return Failure("Device not selected")
        if not user.allows_int_id(selected):
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
    ) -> Result[None, str]:
        selected = int(int_id or user.selected_int_id or 0)
        if not selected:
            return Failure("Invalid request")
        if not user.allows_int_id(selected):
            return Failure("Device not allowed")
        options = normalize_options_for_save(options_raw)
        if options is None:
            if not options_raw.strip():
                return Failure("Options cannot be empty")
            return Failure("Options too long")
        if self._repo.update_options(selected, options) < 1:
            return Failure("Update failed")
        return Success(None)

    def get_modified(self, user: UserSession, int_id: int | None) -> int:
        selected = int(int_id or user.selected_int_id or 0)
        if not selected or not user.allows_int_id(selected):
            return 0
        return 1 if self._repo.get_modified(selected) else 0

    def select_device(self, user: UserSession, int_id: int) -> Result[int, str]:
        if not user.allows_int_id(int_id):
            return Failure("Invalid device")
        return Success(int_id)
