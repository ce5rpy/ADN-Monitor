"""No-op BroadcastPort (ingest without live WebSocket pushes)."""

from __future__ import annotations


class NullBroadcast:
    """Satisfies ``BroadcastPort`` for report ingest without a live WS fan-out."""

    def broadcast(self, message: str, group: str) -> None:
        return None
