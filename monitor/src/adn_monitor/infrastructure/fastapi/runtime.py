"""Shared monitor runtime for FastAPI (state + ingest + WebSocket)."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from ...application import AliasService, MonitorState, clean_sys_dict
from ...application.alias_files_sync import AliasFilesSyncUseCases
from ...application.dashboard_db_push import DashboardDbPusher
from ...application.dashboard_push import DashboardPusher
from ...application.db_maintenance import run_cleaning_loop
from ...application.hblink_table import clean_te
from ...application.monitor_controller import build_tgstats
from ...application.peer_options_merge import apply_peer_options_rows
from ...domain.value_objects import ServerMode
from ...infrastructure.aliases.file_downloader import UrllibAliasFileDownloader
from ...infrastructure.persistence import create_pool, ensure_schema
from ...infrastructure.persistence.sync_mysql import SyncMysqlPool
from ...infrastructure.repositories.alias_repository import MoniDBAliasRepository
from ...infrastructure.repositories.alias_bulk_importer import MysqlAliasBulkImporter
from ...infrastructure.repositories.alias_table_repository import MoniDBAliasTableRepository
from ...infrastructure.repositories.alias_table_stats import SyncAliasTableStats
from ...infrastructure.repositories.lastheard_repository import MoniDBLastHeardRepository
from ...infrastructure.repositories.peer_options_repository import MysqlPeerOptionsRepository
from ...infrastructure.repositories.tgcount_repository import MoniDBTgCountRepository
from .db_sync_render import sync_select_for_render, sync_select_tgcount
from .ingest_mqtt import MqttReportIngest
from .ingest_tcp import TcpReportIngest
from .noop_repos import NoOpAliasRepository, NoOpLastHeardRepository, NoOpTgCountRepository
from .ws_hub import WsHub

logger = logging.getLogger("adn-monitor")

_MONITOR_ROOT = Path(__file__).resolve().parents[4]


class MonitorRuntime:
    """In-memory dashboard state, report ingest (tcp xor mqtt), and WebSocket hub."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        global_conf = config.get("GLOBAL", {})
        opb = config.get("OPB_FLTR", {})
        dash = config.get("DASHBOARD", {})
        self.config_global = {
            **global_conf,
            "OPB_FILTER": opb.get("OPB_FILTER", []),
            "DASHBOARD_MIN_DURATION": dash.get("MIN_DURATION", 3),
        }
        self.state = MonitorState(
            lastheard_log_rows=70,
            empty_masters=bool(global_conf.get("EMPTY_MASTERS", False)),
            brdg_inc=bool(global_conf.get("BRDG_INC", True)),
        )
        self.ws_hub = WsHub()
        self._pusher = DashboardPusher(
            self.state,
            self.ws_hub,
            self.config_global,
            group_active=self.ws_hub.is_group_active,
        )
        self._pool = None
        self._alias_repo: MoniDBAliasRepository | None = None
        self._alias_table_repo: MoniDBAliasTableRepository | None = None
        self._alias_sync: AliasFilesSyncUseCases | None = None
        self._lastheard_repo: MoniDBLastHeardRepository | None = None
        self._tgcount_repo: MoniDBTgCountRepository | None = None
        self._alias_svc: AliasService | None = None
        self._tcp_ingest: TcpReportIngest | None = None
        self._mqtt_ingest: MqttReportIngest | None = None
        self._db_pusher = DashboardDbPusher(
            self.ws_hub,
            group_active=self.ws_hub.is_group_active,
            sync_select_for_render=sync_select_for_render,
            sync_select_tgcount=sync_select_tgcount,
        )
        self._safety_task: asyncio.Task | None = None
        self._cleaning_task: asyncio.Task | None = None
        self._tgcount_task: asyncio.Task | None = None
        self._memory_task: asyncio.Task | None = None
        self._peer_opts_task: asyncio.Task | None = None
        self._alias_files_task: asyncio.Task | None = None
        self._peer_opts_repo: MysqlPeerOptionsRepository | None = None
        self._db_ok = False
        self._tg_day = None

    @property
    def ingest_mode(self) -> str:
        return str(self.config.get("APP", {}).get("INGEST", "tcp")).lower()

    def request_refresh(self) -> bool:
        if self._tcp_ingest is not None:
            return self._tcp_ingest.request_refresh()
        return False

    def start_background_tasks(self) -> None:
        app_conf = self.config.get("APP", {})
        interval = float(app_conf.get("FREQUENCY", 1))
        if interval > 0:
            self._safety_task = asyncio.create_task(self._safety_loop(interval))
        if self._db_ok:
            self._cleaning_task = asyncio.create_task(self._cleaning_loop(900.0))
            if self.config_global.get("TGC_INC"):
                self._tgcount_task = asyncio.create_task(self._tgcount_loop(60.0))
            self._memory_task = asyncio.create_task(self._memory_maintenance_loop(60.0))
        if self._peer_opts_repo is not None:
            self._peer_opts_task = asyncio.create_task(self._peer_options_loop(15.0))
        if self._alias_sync is not None:
            self._alias_files_task = asyncio.create_task(self._alias_files_loop())

    async def stop_background_tasks(self) -> None:
        for task in (
            self._safety_task,
            self._cleaning_task,
            self._tgcount_task,
            self._memory_task,
            self._peer_opts_task,
            self._alias_files_task,
        ):
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._safety_task = None
        self._cleaning_task = None
        self._tgcount_task = None
        self._memory_task = None
        self._peer_opts_task = None
        self._alias_files_task = None

    def start(self) -> None:
        self._wire_db()
        if self._alias_svc is None:
            self._alias_repo = NoOpAliasRepository()
            self._lastheard_repo = NoOpLastHeardRepository()
            self._tgcount_repo = NoOpTgCountRepository()
            self._alias_svc = AliasService(self._alias_repo)

        on_config = self._on_config_applied
        on_bridges = self._on_bridges_applied
        on_ctable = self._on_ctable_updated
        on_mode = self._on_server_mode_detected

        mode = self.ingest_mode
        if mode == "tcp":
            self._tcp_ingest = TcpReportIngest(
                self.config,
                self.state,
                self._alias_svc,
                self._alias_repo,
                self._lastheard_repo,
                self._tgcount_repo,
                broadcast=self.ws_hub,
                on_config_applied=on_config,
                on_bridges_applied=on_bridges,
                on_ctable_updated=on_ctable,
                on_server_mode_detected=on_mode,
            )
            self._tcp_ingest.start()
            logger.info("(INGEST) TCP report client (ADN_CONNECTION); MQTT disabled")
        elif mode == "mqtt":
            self._mqtt_ingest = MqttReportIngest(
                self.config,
                self.state,
                self._alias_svc,
                self._alias_repo,
                self._lastheard_repo,
                self._tgcount_repo,
                config_global=self.config_global,
                broadcast=self.ws_hub,
                on_config_applied=on_config,
                on_ctable_updated=on_ctable,
            )
            self._mqtt_ingest.start()
            logger.info("(INGEST) MQTT subscriber; TCP report (ADN_CONNECTION) not used")

    def stop(self) -> None:
        if self._tcp_ingest is not None:
            self._tcp_ingest.stop()
            self._tcp_ingest = None
        if self._mqtt_ingest is not None:
            self._mqtt_ingest.stop()
            self._mqtt_ingest = None

    @property
    def db_connected(self) -> bool:
        return self._db_ok

    def _push_main_dashboard(self) -> None:
        self._db_pusher.push_last_heard(
            self.state,
            self.config_global,
            self.config.get("DB"),
            dedup=False,
        )

    def _on_config_applied(self) -> None:
        """Topology snapshot: linked systems + dashboard main (hotspot connect/disconnect)."""
        self._pusher.on_config_applied()
        self._push_main_dashboard()

    def _on_bridges_applied(self) -> None:
        """BRIDGE_SND / routing_table: UA TG chips (SINGLE_TS*) on Linked Systems."""
        self._pusher.on_bridges_applied()

    def _on_ctable_updated(self, brdg_meta: dict | None = None) -> None:
        """Voice events: lnksys/opb slices + active QSO on main."""
        build_tgstats(self.state)
        self._pusher.on_ctable_updated(brdg_meta)
        self._push_main_dashboard()

    def _on_server_mode_detected(self, mode: ServerMode, info: dict) -> None:
        import json

        payload = {"mode": getattr(mode, "value", str(mode)), "info": info or {}}
        self.ws_hub.broadcast("v" + json.dumps(payload, separators=(",", ":")), "server_info")
        self.ws_hub.broadcast("v" + json.dumps(payload, separators=(",", ":")), "all_clients")

    async def _safety_loop(self, interval: float) -> None:
        while True:
            try:
                await asyncio.sleep(interval)
                await asyncio.to_thread(
                    self._db_pusher.safety_sync,
                    self.state,
                    self.config_global,
                    self.config.get("DB"),
                    self._pusher,
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("safety_loop: %s", e)

    async def _cleaning_loop(self, interval: float) -> None:
        while True:
            try:
                await asyncio.sleep(interval)
                if self._lastheard_repo is None or self._tgcount_repo is None:
                    continue
                self._tg_day = await asyncio.to_thread(
                    run_cleaning_loop,
                    self.config_global,
                    self._lastheard_repo,
                    self._tgcount_repo,
                    lastheard_log_rows=self.state.lastheard_log_rows,
                    last_tg_day=self._tg_day,
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("cleaning_loop: %s", e)

    async def _tgcount_loop(self, interval: float) -> None:
        while True:
            try:
                await asyncio.sleep(interval)
                await asyncio.to_thread(
                    self._db_pusher.push_tgcount,
                    self.config_global,
                    self.config.get("DB"),
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("tgcount_loop: %s", e)

    async def _memory_maintenance_loop(self, interval: float) -> None:
        while True:
            try:
                await asyncio.sleep(interval)
                if self.state.CTABLE:
                    clean_te(self.state.CTABLE)
                clean_sys_dict(self.state)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("memory_maintenance_loop: %s", e)

    async def _peer_options_loop(self, interval: float) -> None:
        await asyncio.sleep(2.0)
        while True:
            try:
                if self._peer_opts_repo is None:
                    return
                rows = await asyncio.to_thread(self._peer_opts_repo.fetch_logged_in_options)
                if apply_peer_options_rows(self.state, rows):
                    if self.ws_hub.is_group_active("lnksys") or self.ws_hub.is_group_active("statictg"):
                        self._pusher.broadcast_ctable()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("peer_options_loop: %s", e)
            await asyncio.sleep(interval)

    async def _alias_files_loop(self) -> None:
        sync = self._alias_sync
        if sync is None:
            return
        await asyncio.sleep(1.0)
        first = True
        while True:
            try:
                await asyncio.to_thread(sync.refresh_remote_files)
                await asyncio.sleep(3.0)
                await asyncio.to_thread(sync.refresh_local_files)
                if first:
                    await asyncio.to_thread(sync.log_table_counts)
                    first = False
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("(alias) refresh failed: %s", e)
            await asyncio.sleep(sync.review_interval_sec)

    def _wire_alias_sync(self, db: dict[str, Any] | None) -> None:
        files = self.config.get("FILES") or {}
        if not files:
            return
        sync_pool = SyncMysqlPool(db) if db else None
        table_count = SyncAliasTableStats(sync_pool).count if sync_pool else None
        bulk = MysqlAliasBulkImporter(sync_pool) if sync_pool else None
        self._alias_sync = AliasFilesSyncUseCases(
            files_config=files,
            monitor_root=_MONITOR_ROOT,
            downloader=UrllibAliasFileDownloader(),
            table_repo=self._alias_table_repo,
            bulk_importer=bulk,
            alias_repo=self._alias_repo,
            table_count=table_count,
        )

    def _wire_db(self) -> None:
        db = self.config.get("DB") or {}
        if not db:
            logger.warning("(RUNTIME) no DB config; Last Heard persistence limited")
            self._wire_alias_sync(None)
            return
        try:
            self._pool = create_pool(
                db.get("SERVER", "localhost"),
                db.get("USER", ""),
                db.get("PASSWD", ""),
                db.get("NAME", "hbmon"),
                int(db.get("PORT", 3306)),
            )
            self._alias_repo = MoniDBAliasRepository(self._pool)
            sync_pool = SyncMysqlPool(db)
            ensure_schema(sync_pool)
            self._alias_table_repo = MoniDBAliasTableRepository(self._pool, sync_pool=sync_pool)
            self._lastheard_repo = MoniDBLastHeardRepository(self._pool)
            self._tgcount_repo = MoniDBTgCountRepository(self._pool, self.config_global)
            self._alias_svc = AliasService(self._alias_repo)
            self._peer_opts_repo = MysqlPeerOptionsRepository(sync_pool)
            self._db_ok = True
            self._wire_alias_sync(db)
        except Exception as e:
            logger.warning("(RUNTIME) DB pool failed (%s); using no-op repos", e)
            self._wire_alias_sync(None)
