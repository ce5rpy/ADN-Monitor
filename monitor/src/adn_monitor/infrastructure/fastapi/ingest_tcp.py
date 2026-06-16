# ADN Monitor - infrastructure fastapi ingest tcp
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
        on_bridges_applied: Callable[[], None] | None = None,
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
        self._on_bridges_applied = on_bridges_applied
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

    def set_repositories(
        self,
        alias_svc: AliasService,
        alias_repo: AliasRepository,
        lastheard_repo: LastHeardRepository,
        tgcount_repo: TgCountRepository,
    ) -> None:
        self._alias_svc = alias_svc
        self._alias_repo = alias_repo
        self._lastheard_repo = lastheard_repo
        self._tgcount_repo = tgcount_repo
        factory = self._factory
        if factory is None:
            return

        def _apply() -> None:
            factory.set_repositories(alias_svc, alias_repo, lastheard_repo, tgcount_repo)

        try:
            if reactor.running:
                reactor.callFromThread(_apply)
            else:
                _apply()
        except Exception as e:
            logger.debug("(INGEST) set_repositories failed: %s", e)

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
            on_bridges_applied=self._on_bridges_applied,
            on_ctable_updated=self._on_ctable_updated,
            on_server_mode_detected=self._on_server_mode_detected,
            hello_timeout_sec=hello_timeout_sec,
        )
        host = str(adn.get("ADN_IP", "127.0.0.1"))
        port = int(adn.get("ADN_PORT", 4321))
        reactor.connectTCP(host, port, self._factory)
        logger.info("(INGEST) connecting report TCP %s:%s", host, port)
        reactor.run(installSignalHandlers=False)
