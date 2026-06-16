"""WsHub must broadcast from the Twisted ingest thread (no running asyncio loop there)."""

from __future__ import annotations

import asyncio
import threading
from unittest.mock import AsyncMock, MagicMock

from adn_monitor.infrastructure.fastapi.ws_hub import WsClient, WsHub


async def _run_cross_thread_broadcast() -> list[str]:
    hub = WsHub()
    loop = asyncio.get_running_loop()
    hub.bind_event_loop(loop)

    ws = MagicMock()
    client = WsClient(websocket=ws)
    client.send_text = AsyncMock()
    await hub.register(client, "main")

    received: list[str] = []

    async def capture_send(c: WsClient, msg: str) -> None:
        received.append(msg)
        await c.send_text(msg)

    hub._safe_send = capture_send  # type: ignore[method-assign]

    done = threading.Event()

    def twisted_thread() -> None:
        hub.broadcast("i{}", "main")
        done.set()

    threading.Thread(target=twisted_thread, name="twisted-sim").start()
    assert done.wait(timeout=2.0)

    for _ in range(50):
        if received:
            break
        await asyncio.sleep(0.01)

    return received


def test_broadcast_from_non_asyncio_thread():
    received = asyncio.run(_run_cross_thread_broadcast())
    assert received == ["i{}"]
