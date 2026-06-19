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

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from adn_monitor.cli import main

if __name__ == "__main__":
    main()
