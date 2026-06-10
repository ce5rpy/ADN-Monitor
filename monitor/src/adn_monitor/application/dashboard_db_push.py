"""Push last_heard / lstheard_log / tgcount from MySQL to WebSocket groups."""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable
from typing import Any

from . import ws_ctable_views
from .dashboard_push import DashboardPusher
from .dashboard_rows import lastheard_rows, tgcount_rows
from .monitor_controller import MonitorState
from .ports import BroadcastPort

logger = logging.getLogger("adn-monitor")


def _payload_hash(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


class DashboardDbPusher:
    """DB-backed dashboard payloads (safety_sync + periodic tgcount)."""

    def __init__(
        self,
        broadcast: BroadcastPort,
        *,
        group_active: Callable[[str], bool],
        sync_select_for_render: Callable[..., list],
        sync_select_tgcount: Callable[..., list[Any] | None],
    ) -> None:
        self._broadcast = broadcast
        self._group_active = group_active
        self._select_rows = sync_select_for_render
        self._select_tgcount = sync_select_tgcount
        self._last_hash: dict[str, str] = {}

    def push_last_heard(
        self,
        state: MonitorState,
        conf_global: dict,
        db_config: dict | None,
        *,
        dedup: bool = True,
    ) -> None:
        if not self._group_active("main"):
            return
        rows = self._select_rows(db_config or {}, "last_heard", conf_global.get("LH_ROWS", 20))
        lh_rows = lastheard_rows(rows, conf_global)
        sem_h = _payload_hash(
            ws_ctable_views.main_dashboard_semantic_fingerprint(lh_rows, state.CTABLE)
        )
        if dedup and self._last_hash.get("main_sem") == sem_h:
            return
        payload = {
            "lastheard": lh_rows,
            "ctable": ws_ctable_views.ctable_for_main(state.CTABLE),
        }
        msg = "i" + json.dumps(payload, default=str)
        self._broadcast.broadcast(msg, "main")
        self._last_hash["main_sem"] = sem_h

    def push_lstheard_log(
        self,
        conf_global: dict,
        db_config: dict | None,
        log_rows: int,
        *,
        dedup: bool = False,
    ) -> None:
        if not self._group_active("lsthrd_log"):
            return
        rows = self._select_rows(db_config or {}, "lstheard_log", log_rows)
        payload = {"rows": lastheard_rows(rows, conf_global)}
        msg = "h" + json.dumps(payload, default=str)
        if dedup and self._last_hash.get("lsthrd_log") == _payload_hash(msg):
            return
        self._broadcast.broadcast(msg, "lsthrd_log")
        self._last_hash["lsthrd_log"] = _payload_hash(msg)

    def push_tgcount(
        self,
        conf_global: dict,
        db_config: dict | None,
        *,
        dedup: bool = False,
    ) -> None:
        if not self._group_active("tgcount"):
            return
        result = self._select_tgcount(db_config or {}, conf_global.get("TGC_ROWS", 20), conf_global)
        payload = {"rows": tgcount_rows(result)}
        msg = "t" + json.dumps(payload, default=str)
        if dedup and self._last_hash.get("tgcount") == _payload_hash(msg):
            return
        self._broadcast.broadcast(msg, "tgcount")
        self._last_hash["tgcount"] = _payload_hash(msg)

    def safety_sync(
        self,
        state: MonitorState,
        conf_global: dict,
        db_config: dict | None,
        pusher: DashboardPusher,
    ) -> None:
        """Periodic full resync: last_heard, lstheard_log (if subscribed), ctable, tgcount."""
        if not state.CONFIG:
            if (
                self._group_active("lnksys")
                or self._group_active("opb")
                or self._group_active("statictg")
            ):
                logger.debug("safety_sync: CONFIG empty, skip ctable")
            return
        from .monitor_controller import build_tgstats

        build_tgstats(state)
        self.push_last_heard(state, conf_global, db_config)
        self.push_lstheard_log(conf_global, db_config, getattr(state, "lastheard_log_rows", 70))
        pusher.broadcast_ctable(dedup=True)
        if conf_global.get("TGC_INC"):
            self.push_tgcount(conf_global, db_config)
