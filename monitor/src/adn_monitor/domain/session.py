"""Authenticated operator session (no HTTP dependency)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserSession:
    callsign: str
    int_ids: list[int]
    selected_int_id: int | None = None

    def allows_int_id(self, int_id: int) -> bool:
        return int_id in self.int_ids
