"""MySQL reconnect behaviour in MonitorRuntime."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

from adn_monitor.infrastructure.fastapi.noop_repos import NoOpAliasRepository
from adn_monitor.infrastructure.fastapi.runtime import MonitorRuntime


def _config() -> dict:
    return {
        "APP": {"INGEST": "tcp", "AUTO_START_INGEST": False, "DB_RECONNECT_INTERVAL": 0.01},
        "GLOBAL": {},
        "OPB_FLTR": {},
        "DASHBOARD": {},
        "DB": {
            "SERVER": "localhost",
            "USER": "u",
            "PASSWD": "p",
            "NAME": "hbmon",
            "PORT": 3306,
        },
    }


def test_startup_falls_back_to_noop_when_db_unavailable() -> None:
    runtime = MonitorRuntime(_config())
    with patch(
        "adn_monitor.infrastructure.fastapi.runtime.SyncMysqlPool",
        side_effect=OSError("Can't connect to mysqld.sock"),
    ):
        runtime.start()
    assert runtime.db_connected is False
    assert isinstance(runtime._alias_repo, NoOpAliasRepository)


def test_try_wire_db_success_sets_db_ok() -> None:
    runtime = MonitorRuntime(_config())
    mock_pool = MagicMock()
    mock_sync = MagicMock()
    mock_sync.connection.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_sync.connection.return_value.__exit__ = MagicMock(return_value=False)
    with (
        patch("adn_monitor.infrastructure.fastapi.runtime.SyncMysqlPool", return_value=mock_sync),
        patch("adn_monitor.infrastructure.fastapi.runtime.create_pool", return_value=mock_pool),
        patch("adn_monitor.infrastructure.fastapi.runtime.ensure_schema"),
        patch(
            "adn_monitor.infrastructure.fastapi.runtime.MoniDBAliasRepository",
            return_value=MagicMock(),
        ),
        patch(
            "adn_monitor.infrastructure.fastapi.runtime.MoniDBAliasTableRepository",
            return_value=MagicMock(),
        ),
        patch(
            "adn_monitor.infrastructure.fastapi.runtime.MoniDBLastHeardRepository",
            return_value=MagicMock(),
        ),
        patch(
            "adn_monitor.infrastructure.fastapi.runtime.MoniDBTgCountRepository",
            return_value=MagicMock(),
        ),
        patch(
            "adn_monitor.infrastructure.fastapi.runtime.MysqlPeerOptionsRepository",
            return_value=MagicMock(),
        ),
    ):
        assert runtime._try_wire_db() is True
    assert runtime.db_connected is True


def test_db_reconnect_loop_recovers_from_noop() -> None:
    async def _run() -> None:
        runtime = MonitorRuntime(_config())
        runtime._alias_repo = NoOpAliasRepository()
        runtime._lastheard_repo = MagicMock()
        runtime._tgcount_repo = MagicMock()
        runtime._alias_svc = MagicMock()
        assert runtime.db_connected is False

        mock_pool = MagicMock()
        mock_sync = MagicMock()
        mock_sync.connection.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_sync.connection.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("adn_monitor.infrastructure.fastapi.runtime.SyncMysqlPool", return_value=mock_sync),
            patch("adn_monitor.infrastructure.fastapi.runtime.create_pool", return_value=mock_pool),
            patch("adn_monitor.infrastructure.fastapi.runtime.ensure_schema"),
            patch(
                "adn_monitor.infrastructure.fastapi.runtime.MoniDBAliasRepository",
                return_value=MagicMock(),
            ),
            patch(
                "adn_monitor.infrastructure.fastapi.runtime.MoniDBAliasTableRepository",
                return_value=MagicMock(),
            ),
            patch(
                "adn_monitor.infrastructure.fastapi.runtime.MoniDBLastHeardRepository",
                return_value=MagicMock(),
            ),
            patch(
                "adn_monitor.infrastructure.fastapi.runtime.MoniDBTgCountRepository",
                return_value=MagicMock(),
            ),
            patch(
                "adn_monitor.infrastructure.fastapi.runtime.MysqlPeerOptionsRepository",
                return_value=MagicMock(),
            ),
        ):
            task = asyncio.create_task(runtime._db_reconnect_loop())
            await asyncio.sleep(0.05)
            task.cancel()
            await task

        assert runtime.db_connected is True

    asyncio.run(_run())


def test_teardown_db_swaps_back_to_noop() -> None:
    runtime = MonitorRuntime(_config())
    mock_pool = MagicMock()
    runtime._pool = mock_pool
    runtime._db_ok = True
    runtime._alias_repo = MagicMock()
    runtime._lastheard_repo = MagicMock()
    runtime._tgcount_repo = MagicMock()
    runtime._alias_svc = MagicMock()

    runtime._teardown_db()

    assert runtime.db_connected is False
    assert isinstance(runtime._alias_repo, NoOpAliasRepository)
    mock_pool.close.assert_called_once()
