"""WebSocket hub client registry."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.infrastructure.fastapi.ws_hub import WsClient


def test_ws_client_is_hashable_for_hub_sets():
    ws = MagicMock()
    clients = {WsClient(websocket=ws), WsClient(websocket=MagicMock())}
    assert len(clients) == 2
