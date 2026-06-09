"""MONITOR_APP ingest mode validation (tcp xor mqtt)."""

from __future__ import annotations

import tempfile
from pathlib import Path

from adn_monitor.domain import is_fail
from adn_monitor.infrastructure.config_loader import load_config


def _write_yaml(content: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as fh:
        fh.write(content)
        return fh.name


def test_ingest_tcp_default():
    path = _write_yaml(
        """
ADN_CONNECTION:
  ADN_IP: 127.0.0.1
  ADN_PORT: 4321
MONITOR_APP:
  INGEST: tcp
"""
    )
    result = load_config(path)
    assert not is_fail(result)
    assert result.value["APP"]["INGEST"] == "tcp"
    Path(path).unlink(missing_ok=True)


def test_ingest_mqtt_requires_broker_settings():
    path = _write_yaml(
        """
MONITOR_APP:
  INGEST: mqtt
"""
    )
    result = load_config(path)
    assert is_fail(result)
    Path(path).unlink(missing_ok=True)


def test_monitor_app_frequency_from_yaml():
    path = _write_yaml(
        """
MONITOR_APP:
  FREQUENCY: 30
  INGEST: tcp
"""
    )
    result = load_config(path)
    assert not is_fail(result)
    assert result.value["APP"]["FREQUENCY"] == 30
    assert result.value["WS"]["FREQUENCY"] == 30
    Path(path).unlink(missing_ok=True)


def test_legacy_websocket_server_still_supported():
    path = _write_yaml(
        """
WEBSOCKET_SERVER:
  FREQUENCY: 5
MONITOR_APP:
  INGEST: tcp
"""
    )
    result = load_config(path)
    assert not is_fail(result)
    assert result.value["APP"]["FREQUENCY"] == 5
    Path(path).unlink(missing_ok=True)


def test_monitor_app_frequency_overrides_legacy_websocket():
    path = _write_yaml(
        """
WEBSOCKET_SERVER:
  FREQUENCY: 5
MONITOR_APP:
  FREQUENCY: 10
  INGEST: tcp
"""
    )
    result = load_config(path)
    assert not is_fail(result)
    assert result.value["APP"]["FREQUENCY"] == 10
    Path(path).unlink(missing_ok=True)


def test_ingest_mqtt_ok():
    path = _write_yaml(
        """
MONITOR_APP:
  INGEST: mqtt
  MQTT:
    URL: mqtt://127.0.0.1:1883
    TOPIC_PREFIX: adn/7302
"""
    )
    result = load_config(path)
    assert not is_fail(result)
    assert result.value["APP"]["INGEST"] == "mqtt"
    assert result.value["APP"]["MQTT"]["TOPIC_PREFIX"] == "adn/7302"
    Path(path).unlink(missing_ok=True)
