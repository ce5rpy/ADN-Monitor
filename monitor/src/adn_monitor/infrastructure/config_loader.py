# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
# HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
# hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
# HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
# Original works and this derivative are under GPLv3.

"""Load monitor config from YAML (adn-mon.yaml). Returns Result (Success/Failure)."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from ..domain import ConfigError, Failure, Result, Success

logger = logging.getLogger("adn-mon")


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
    Load config from YAML (adn-mon.yaml).
    Returns Success(config_dict) or Failure(ConfigError).
    config_dict has keys: GLOBAL, ADN_CXN, OPB_FLTR, FILES, LOG, WS, DASHBOARD, DB (if present), ALIASES (if present).
    """
    path = Path(cfg_file)
    ext = path.suffix.lower()
    if ext not in (".yaml", ".yml"):
        return Failure(ConfigError(f"Config must be YAML (.yaml or .yml), got: {cfg_file}"))
    if not path.is_file():
        return Failure(ConfigError(f"Configuration file {cfg_file} is not a valid file."))

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as err:
        return Failure(ConfigError(f"Error parsing YAML config: {err}"))
    if not isinstance(data, dict):
        return Failure(ConfigError("YAML config root must be a mapping."))

    CONF: dict = {
        "GLOBAL": {},
        "ADN_CXN": {},
        "OPB_FLTR": {},
        "FILES": {"PATH": "./json"},
        "LOG": {},
        "WS": {},
        "DASHBOARD": {},
    }

    # GLOBAL
    g = data.get("GLOBAL") or {}
    CONF["GLOBAL"] = {
        "HB_INC": _bool(g.get("HOMEBREW_INC", True)),
        "LH_INC": _bool(g.get("LASTHEARD_INC", True)),
        "LH_ROWS": _int(g.get("LASTHEARD_ROWS"), 20),
        "BRDG_INC": _bool(g.get("BRIDGES_INC", True)),
        "EMPTY_MASTERS": _bool(g.get("EMPTY_MASTERS", False)),
        "TGC_INC": _bool(g.get("TGCOUNT_INC", True)),
        "TGC_ROWS": _int(g.get("TGCOUNT_ROWS"), 20),
    }

    # ADN_CONNECTION
    adn = data.get("ADN_CONNECTION") or {}
    CONF["ADN_CXN"] = {
        "ADN_IP": _str(adn.get("ADN_IP", "127.0.0.1")),
        "ADN_PORT": _int(adn.get("ADN_PORT"), 4321),
    }

    # OPB_FILTER
    opb = data.get("OPB_FILTER") or {}
    opb_val = _str(opb.get("OPB_FILTER", ""))
    CONF["OPB_FLTR"] = {
        "OPB_FILTER": [x for x in opb_val.replace(" ", "").split(",") if x],
    }

    # ALIASES / FILES
    aliases = data.get("ALIASES") or {}
    if isinstance(aliases, dict):
        CONF["ALIASES"] = {k: _str(v) for k, v in aliases.items()}
    else:
        CONF["ALIASES"] = {}
    path_val = _str(aliases.get("PATH", "./json")).strip().rstrip("/") or "./json"
    path_val = path_val.rstrip("/") + "/"  # always end with / for downstream (e.g. try_download)
    reload_hours = 24
    try:
        reload_hours = _int(aliases.get("STALE_HOURS"), 24)
    except (TypeError, ValueError):
        pass
    review_minutes = 5
    try:
        review_minutes = _int(aliases.get("REVIEW_INTERVAL_MINUTES"), 5)
    except (TypeError, ValueError):
        pass
    su = _str(aliases.get("SUBSCRIBER_URL", "https://adn.systems/files/subscriber_ids.json"))
    CONF["FILES"] = {
        "PATH": path_val,
        "SUBS": _str(aliases.get("SUBSCRIBER_FILE", "subscriber_ids.json")),
        "PEER": _str(aliases.get("PEER_FILE", "peer_ids.json")),
        "TGID": _str(aliases.get("TGID_FILE", "talkgroup_ids.json")),
        "LCL_SUBS": _str(aliases.get("LOCAL_SUBSCRIBER_FILE", "")),
        "LCL_PEER": _str(aliases.get("LOCAL_PEER_FILE", "")),
        "LCL_TGID": _str(aliases.get("LOCAL_TGID_FILE", "")),
        "RELOAD_TIME": reload_hours * 3600,
        "REVIEW_INTERVAL": review_minutes * 60,
        "PEER_URL": _str(aliases.get("PEER_URL", "https://adn.systems/files/peer_ids.json")),
        "SUBS_URL": su,
        "SUBSCRIBER_URL": su,
        "TGID_URL": _str(aliases.get("TGID_URL", "https://adn.systems/files/talkgroup_ids.json")),
        "CHECKSUM_URL": _str(aliases.get("CHECKSUM_URL", "https://adn.systems/files/file_checksums.json")),
        "CHECKSUM_FILE": _str(aliases.get("CHECKSUM_FILE", "file_checksums.json")),
    }

    # LOGGER
    log = data.get("LOGGER") or {}
    log_path = _str(log.get("LOG_PATH", "./log"))
    log_file = _str(log.get("LOG_FILE", "adn-mon.log"))
    CONF["LOG"] = {
        "PATH": log_path,
        "LOG_FILE": log_file,
        "LOG_LEVEL": _str(log.get("LOG_LEVEL", "INFO")),
        "P2F_LOG": Path(log_path, log_file),
    }

    # WEBSOCKET_SERVER
    ws = data.get("WEBSOCKET_SERVER") or {}
    ssl_path = _str(ws.get("SSL_PATH", "./ssl"))
    CONF["WS"] = {
        "WS_PORT": _int(ws.get("WEBSOCKET_PORT"), 9000),
        "USE_SSL": _bool(ws.get("USE_SSL", False)),
        "SSL_PATH": ssl_path,
        "SSL_CERT": _str(ws.get("SSL_CERTIFICATE", "cert.pem")),
        "P2F_CERT": Path(ssl_path, _str(ws.get("SSL_CERTIFICATE", "cert.pem"))),
        "SSL_PKEY": _str(ws.get("SSL_PRIVATEKEY", "key.pem")),
        "P2F_PKEY": Path(ssl_path, _str(ws.get("SSL_PRIVATEKEY", "key.pem"))),
        "FREQ": _int(ws.get("FREQUENCY"), 1),
        "CLT_TO": _int(ws.get("CLIENT_TIMEOUT"), 0),
    }

    # SELF_SERVICE (DB)
    db = data.get("SELF_SERVICE") or {}
    if db:
        CONF["DB"] = {
            "SERVER": _str(db.get("DB_SERVER", "localhost")),
            "USER": _str(db.get("DB_USERNAME", "")),
            "PASSWD": _str(db.get("DB_PASSWORD", "")),
            "NAME": _str(db.get("DB_NAME", "")),
            "PORT": _int(db.get("DB_PORT"), 3306),
        }

    # DASHBOARD
    dash = data.get("DASHBOARD") or {}
    if isinstance(dash, dict):
        CONF["DASHBOARD"] = {k: _str(v) for k, v in dash.items()}
        CONF["DASHBOARD"]["MIN_DURATION"] = _int(dash.get("MIN_DURATION"), 3)
    else:
        CONF["DASHBOARD"] = {}

    return Success(CONF)
