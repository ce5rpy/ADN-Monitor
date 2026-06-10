"""MQTT report ingest (mutually exclusive with TCP)."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from ...application import AliasService, MonitorState
from ...application.monitor_controller import process_report_json
from ...application.report_mapper import REPORT_PROTOCOL
from ...application.ports import (
    AliasRepository,
    BroadcastPort,
    LastHeardRepository,
    TgCountRepository,
)
from ...domain import is_fail
from ...domain.value_objects import ServerMode
logger = logging.getLogger("adn-monitor")


class MqttReportIngest:
    """Subscribe to ``{prefix}/state`` and ``{prefix}/voice_event`` only."""

    def __init__(
        self,
        config: dict[str, Any],
        state: MonitorState,
        alias_svc: AliasService,
        alias_repo: AliasRepository,
        lastheard_repo: LastHeardRepository,
        tgcount_repo: TgCountRepository,
        *,
        config_global: dict[str, Any],
        broadcast: BroadcastPort | None = None,
        on_config_applied: Callable[[], None] | None = None,
        on_ctable_updated: Callable[..., None] | None = None,
    ) -> None:
        self._config = config
        self._state = state
        self._alias_svc = alias_svc
        self._alias_repo = alias_repo
        self._lastheard_repo = lastheard_repo
        self._tgcount_repo = tgcount_repo
        self._config_global = config_global
        self._broadcast = broadcast
        self._on_config_applied = on_config_applied
        self._on_ctable_updated = on_ctable_updated
        self._client: Any = None
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        try:
            import paho.mqtt.client as mqtt
        except ImportError as e:
            logger.error(
                "(INGEST) MQTT ingest requires paho-mqtt: pip install paho-mqtt (%s)",
                e,
            )
            return

        mqtt_conf = self._config.get("APP", {}).get("MQTT", {})
        url = str(mqtt_conf.get("URL", "")).strip()
        prefix = str(mqtt_conf.get("TOPIC_PREFIX", "")).strip().rstrip("/")
        qos = int(mqtt_conf.get("QOS", 0))
        if not url or not prefix:
            logger.error("(INGEST) MQTT.URL and MQTT.TOPIC_PREFIX required when INGEST=mqtt")
            return

        try:
            self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except AttributeError:
            self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        try:
            self._client.connect(self._parse_host(url), self._parse_port(url), keepalive=60)
        except Exception as e:
            logger.error("(INGEST) MQTT connect failed: %s", e)
            return

        self._topics = (f"{prefix}/state", f"{prefix}/voice_event")
        self._qos = qos
        self._client.loop_start()
        self._started = True
        logger.info("(INGEST) MQTT subscriber started prefix=%s", prefix)

    def stop(self) -> None:
        if not self._started or self._client is None:
            return
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception as e:
            logger.debug("(INGEST) MQTT stop: %s", e)
        self._started = False
        self._client = None
        logger.info("(INGEST) MQTT subscriber stopped")

    def _on_connect(self, client: Any, userdata: Any, connect_flags: Any, reason_code: Any, properties: Any = None) -> None:
        if getattr(reason_code, "value", reason_code) != 0:
            logger.warning("(INGEST) MQTT connect rejected: %s", reason_code)
            return
        for topic in self._topics:
            client.subscribe(topic, qos=self._qos)
        logger.info("(INGEST) MQTT subscribed %s", list(self._topics))

    def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.warning("(INGEST) MQTT invalid JSON on %s: %s", msg.topic, e)
            return
        if not isinstance(payload, dict):
            return
        self._mark_mqtt_mode()
        msg_type = payload.get("type")
        result = process_report_json(
            payload,
            self._state,
            self._alias_svc,
            self._alias_repo,
            self._lastheard_repo,
            self._tgcount_repo,
            self._broadcast,
            self._config_global,
        )
        if is_fail(result):
            logger.warning("(INGEST) MQTT process_report_json: %s", result.error)
            return
        if msg_type == "dashboard_state" and self._on_config_applied:
            self._on_config_applied()
        elif msg_type == "voice_event" and self._on_ctable_updated:
            voice = payload
            brdg_meta = {
                "call_type": "GROUP VOICE",
                "action": voice.get("phase"),
                "system": voice.get("system"),
            }
            self._on_ctable_updated(brdg_meta)

    def _mark_mqtt_mode(self) -> None:
        self._state.server_mode = ServerMode.V2
        self._state.report_protocol = REPORT_PROTOCOL
        if not self._state.server_mode_confirmed:
            self._state.server_mode_confirmed = True
            logger.info("(INGEST) MQTT ingest active (slim wire, no TCP report)")

    @staticmethod
    def _parse_host(url: str) -> str:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return parsed.hostname or "127.0.0.1"

    @staticmethod
    def _parse_port(url: str) -> int:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.port:
            return int(parsed.port)
        return 8883 if parsed.scheme == "mqtts" else 1883
