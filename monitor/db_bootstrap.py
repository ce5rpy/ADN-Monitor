#!/usr/bin/env python3

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

"""
Bootstrap DB schema (create or update tables).

Usage:
  python db_bootstrap.py --config adn-mon.yaml --create   # create tables
  python db_bootstrap.py --config adn-mon.yaml --update  # run migrations
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from twisted.internet import reactor

from adn_monitor.domain import is_fail
from adn_monitor.infrastructure import load_config
from adn_monitor.infrastructure.persistence import create_pool, test_db, create_tables, updt_table

CONFIG_FILE = os.environ.get("ADN_CONFIG_PATH", str(_ROOT / "adn-mon.yaml"))
for i, arg in enumerate(sys.argv[1:]):
    if arg == "--config" and i + 2 <= len(sys.argv):
        CONFIG_FILE = sys.argv[i + 2]
        if not Path(CONFIG_FILE).is_absolute():
            CONFIG_FILE = str(_ROOT / CONFIG_FILE)
        break

_config_result = load_config(CONFIG_FILE)
if is_fail(_config_result):
    print(_config_result.error, file=sys.stderr)
    sys.exit(1)
CONF = _config_result.value


def main() -> None:
    if "DB" not in CONF:
        sys.exit("No DB stanza in config file")
    pool = create_pool(
        CONF["DB"]["SERVER"],
        CONF["DB"]["USER"],
        CONF["DB"]["PASSWD"],
        CONF["DB"]["NAME"],
        CONF["DB"]["PORT"],
    )

    def on_result(r) -> None:
        """Handle Result: Success -> stop reactor; Failure -> print error and exit."""
        if is_fail(r):
            print(r.error, file=sys.stderr)
            reactor.stop()
            sys.exit(1)
        reactor.stop()

    def run_bootstrap() -> None:
        if "--create" in sys.argv:
            create_tables(pool).addCallback(on_result)
        elif "--update" in sys.argv:
            updt_table(pool).addCallback(on_result)
        else:
            sys.exit("Use --create or --update")

    def on_test_done(r) -> None:
        if is_fail(r):
            print("Database connection failed:", r.error, file=sys.stderr)
            reactor.stop()
            sys.exit(1)
        reactor.callLater(1, run_bootstrap)

    test_db(pool).addCallback(on_test_done)
    reactor.callLater(10, reactor.stop)
    reactor.run()


if __name__ == "__main__":
    main()
