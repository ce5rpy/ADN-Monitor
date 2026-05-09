# Hotspot Proxy for ADN DMR Peer Server.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Load proxy config from YAML (adn-proxy.yaml or legacy monitor adn-monitor.yaml). Reads PROXY, SELF_SERVICE, LOGGER."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..domain import ConfigError, Failure, Result, Success


def _bool(val: object) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


def _int(val: object, default: int = 0) -> int:
    if isinstance(val, int) and not isinstance(val, bool):
        return val
    if isinstance(val, str):
        try:
            return int(val.strip())
        except ValueError:
            return default
    return default


def _str(val: object) -> str:
    if val is None:
        return ""
    return str(val).strip()


def load_config(cfg_file: str) -> Result[dict, ConfigError]:
    """
    Load proxy YAML (typically proxy/adn-proxy.yaml). Legacy installs may pass monitor/adn-monitor.yaml.
    Returns Success(config_dict) or Failure(ConfigError).
    config_dict has keys: PROXY, SELF_SERVICE, LOG (from LOGGER section).
    """
    path = Path(cfg_file)
    if path.suffix.lower() not in (".yaml", ".yml"):
        return Failure(ConfigError(f"Config must be YAML, got: {cfg_file}"))
    if not path.is_file():
        return Failure(ConfigError(f"Configuration file {cfg_file} is not a valid file."))

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as err:
        return Failure(ConfigError(f"Error parsing YAML config: {err}"))
    if not isinstance(data, dict):
        return Failure(ConfigError("YAML config root must be a mapping."))

    CONF: dict = {"PROXY": {}, "SELF_SERVICE": {}, "LOG": {}}

    # PROXY (YAML keys in UPPERCASE)
    px = data.get("PROXY") or {}
    CONF["PROXY"] = {
        "Master": _str(px.get("MASTER") or px.get("Master", "127.0.0.1")),
        "ListenPort": _int(px.get("LISTEN_PORT") or px.get("ListenPort"), 62031),
        "ListenIP": _str(px.get("LISTEN_IP") or px.get("ListenIP", "")),
        "DestportStart": _int(px.get("DESTPORT_START") or px.get("DestportStart"), 54000),
        "DestPortEnd": _int(px.get("DEST_PORT_END") or px.get("DestPortEnd"), 54100),
        "Timeout": _int(px.get("TIMEOUT") or px.get("Timeout"), 30),
        "Stats": _bool(px.get("STATS") if px.get("STATS") is not None else px.get("Stats", False)),
        "Debug": _bool(px.get("DEBUG") if px.get("DEBUG") is not None else px.get("Debug", False)),
        "ClientInfo": _bool(px.get("CLIENT_INFO") if px.get("CLIENT_INFO") is not None else px.get("ClientInfo", False)),
        "BlackList": list(px.get("BLACK_LIST") or px.get("BlackList") or []),
        "IPBlackList": dict(px.get("IP_BLACK_LIST") or px.get("IPBlackList") or {}),
    }

    # SELF_SERVICE (YAML keys in UPPERCASE)
    ss = data.get("SELF_SERVICE") or {}
    CONF["SELF_SERVICE"] = {
        "use_selfservice": _bool(ss.get("USE_SELFSERVICE") if ss.get("USE_SELFSERVICE") is not None else ss.get("use_selfservice", False)),
        "DB_SERVER": _str(ss.get("DB_SERVER", "localhost")),
        "DB_USERNAME": _str(ss.get("DB_USERNAME", "")),
        "DB_PASSWORD": _str(ss.get("DB_PASSWORD", "")),
        "DB_NAME": _str(ss.get("DB_NAME", "")),
        "DB_PORT": _int(ss.get("DB_PORT"), 3306),
        "PBKDF2_SALT": _str(ss.get("PBKDF2_SALT", "ADN")),
        "PBKDF2_ITERATIONS": _int(ss.get("PBKDF2_ITERATIONS"), 2000),
    }

    # LOGGER (proxy uses PROXY_LOG_FILE so it does not share the monitor's LOG_FILE)
    log = data.get("LOGGER") or {}
    log_path = _str(log.get("LOG_PATH", "./log"))
    log_file = _str(log.get("PROXY_LOG_FILE", "hotspot-proxy.log"))
    CONF["LOG"] = {
        "PATH": log_path,
        "LOG_FILE": log_file,
        "LOG_LEVEL": _str(log.get("LOG_LEVEL", "INFO")),
        "P2F_LOG": Path(log_path) / log_file,
    }

    return Success(CONF)
