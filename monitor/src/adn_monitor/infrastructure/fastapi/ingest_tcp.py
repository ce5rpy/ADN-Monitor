"""Background TCP report client for FastAPI lifespan."""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable

from twisted.internet import reactor

from ...application import AliasService, MonitorState
from ...application.ports import (
    AliasRepository,
    BroadcastPort,
    LastHeardRepository,
    TgCountRepository,
)
from ...infrastructure.report_payload_decoder import PickleJsonReportPayloadDecoder
from ...infrastructure.twisted_adapters.report_client import ReportClientFactory
from .null_broadcast import NullBroadcast

logger = logging.getLogger("adn-monitor")


class TcpReportIngest:
    """Runs ``ReportClientFactory`` on a dedicated Twisted reactor thread."""

    def __init__(
        self,
        config: dict[str, Any],
        state: MonitorState,
        alias_svc: AliasService,
        alias_repo: AliasRepository,
        lastheard_repo: LastHeardRepository,
        tgcount_repo: TgCountRepository,
        *,
        broadcast: BroadcastPort | None = None,
        on_config_applied: Callable[[], None] | None = None,
        on_ctable_updated: Callable[..., None] | None = None,
        on_server_mode_detected: Callable[[Any, dict], None] | None = None,
    ) -> None:
        self._config = config
        self._state = state
        self._alias_svc = alias_svc
        self._alias_repo = alias_repo
        self._lastheard_repo = lastheard_repo
        self._tgcount_repo = tgcount_repo
        self._on_config_applied = on_config_applied
        self._on_ctable_updated = on_ctable_updated
        self._on_server_mode_detected = on_server_mode_detected
        self._broadcast = broadcast or NullBroadcast()
        self._thread: threading.Thread | None = None
        self._factory: ReportClientFactory | None = None
        self._started = False

    @property
    def factory(self) -> ReportClientFactory | None:
        return self._factory

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self._thread = threading.Thread(target=self._run_reactor, name="report-ingest-tcp", daemon=True)
        self._thread.start()
        logger.info("(INGEST) TCP report client thread started")

    def stop(self) -> None:
        if not self._started:
            return
        try:
            if reactor.running:
                reactor.callFromThread(reactor.stop)
        except Exception as e:
            logger.debug("(INGEST) reactor stop: %s", e)
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        self._started = False
        logger.info("(INGEST) TCP report client stopped")

    def request_refresh(self) -> bool:
        factory = self._factory
        if factory is None:
            return False
        try:
            return factory.request_refresh()
        except Exception as e:
            logger.debug("(INGEST) request_refresh failed: %s", e)
            return False

    def _run_reactor(self) -> None:
        adn = self._config.get("ADN_CXN", {})
        global_conf = self._config.get("GLOBAL", {})
        opb = self._config.get("OPB_FLTR", {})
        dash = self._config.get("DASHBOARD", {})
        config_global = {
            **global_conf,
            "OPB_FILTER": opb.get("OPB_FILTER", []),
            "DASHBOARD_MIN_DURATION": dash.get("MIN_DURATION", 3),
        }
        hello_timeout_sec = max(0.0, float(adn.get("HELLO_TIMEOUT_MS", 1500)) / 1000.0)
        self._factory = ReportClientFactory(
            state=self._state,
            alias_svc=self._alias_svc,
            alias_repo=self._alias_repo,
            lastheard_repo=self._lastheard_repo,
            tgcount_repo=self._tgcount_repo,
            broadcast=self._broadcast,
            config_global=config_global,
            report_decoder=PickleJsonReportPayloadDecoder(),
            on_config_applied=self._on_config_applied,
            on_ctable_updated=self._on_ctable_updated,
            on_server_mode_detected=self._on_server_mode_detected,
            hello_timeout_sec=hello_timeout_sec,
        )
        host = str(adn.get("ADN_IP", "127.0.0.1"))
        port = int(adn.get("ADN_PORT", 4321))
        reactor.connectTCP(host, port, self._factory)
        logger.info("(INGEST) connecting report TCP %s:%s", host, port)
        reactor.run(installSignalHandlers=False)
