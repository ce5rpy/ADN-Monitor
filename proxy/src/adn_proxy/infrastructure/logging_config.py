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

"""Configure root logger (console + optional file)."""

from __future__ import annotations

import logging
from pathlib import Path

from logging.config import dictConfig


def create_logger(conf: dict) -> logging.Logger:
    """
    Configure logging from conf dict with keys: PATH, LOG_FILE, LOG_LEVEL, LOG_HANDLERS.
    LOG_HANDLERS is a list of handler names, e.g. ['console', 'file'].
    Returns the root logger.
    """
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "std_format": {
                "format": "%(asctime)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "std_format",
                "level": conf.get("LOG_LEVEL", "INFO"),
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "std_format",
                "filename": Path(conf["PATH"]) / conf["LOG_FILE"],
                "level": conf.get("LOG_LEVEL", "INFO"),
            },
        },
        "root": {
            "handlers": conf.get("LOG_HANDLERS", ["console"]),
            "level": "NOTSET",
        },
    })
    return logging.getLogger("adn-proxy")
