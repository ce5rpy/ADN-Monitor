#!/usr/bin/env python3

# ADN Monitor - Dashboard and backend for ADN Systems.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# Unified process: REST (/api/*), WebSocket (/ws), report ingest (TCP or MQTT).

"""
Run from monitor/:

  python monitor.py [--config adn-monitor.yaml] [--host HOST] [--port PORT]

Default config: monitor/adn-monitor.yaml (or ADN_CONFIG_PATH from repo root .env).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from adn_monitor.domain import is_fail
from adn_monitor.infrastructure import create_logger, load_config
from adn_monitor.infrastructure.env_loader import load_project_env
from adn_monitor.infrastructure.fastapi import create_app

load_project_env(_ROOT)


def _default_config_path() -> str:
    env = os.environ.get("ADN_CONFIG_PATH", "").strip()
    if env and Path(env).is_file():
        return env
    return str(_ROOT / "adn-monitor.yaml")


def main() -> None:
    parser = argparse.ArgumentParser(description="ADN Monitor (FastAPI)")
    parser.add_argument("-c", "--config", default=_default_config_path(), help="adn-monitor.yaml path")
    parser.add_argument("--host", default=None, help="Override MONITOR_APP.LISTEN_HOST")
    parser.add_argument("--port", type=int, default=None, help="Override MONITOR_APP.LISTEN_PORT")
    args = parser.parse_args()

    result = load_config(args.config)
    if is_fail(result):
        print(f"Config error: {result.error}", file=sys.stderr)
        sys.exit(1)
    config = result.value

    log_conf = config.get("LOG", {})
    create_logger(log_conf)

    app_conf = config.get("APP", {})
    host = args.host if args.host is not None else app_conf.get("LISTEN_HOST", "")
    port = args.port if args.port is not None else int(app_conf.get("LISTEN_PORT", 8080))
    bind = host or "0.0.0.0"

    import uvicorn

    uvicorn.run(
        create_app(config),
        host=bind,
        port=port,
        log_level=str(log_conf.get("LOG_LEVEL", "info")).lower(),
    )


if __name__ == "__main__":
    main()
