"""Self-service client entity (Clients table)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Client:
    int_id: int
    callsign: str
    options: str
    modified: bool
    mode: int
    host: str | None = None
