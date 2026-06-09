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
