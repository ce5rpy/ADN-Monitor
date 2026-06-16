# ADN Monitor - Dashboard and backend for ADN Systems.
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

"""Configure root logger (console + optional file)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from logging.config import dictConfig


def logging_enabled(conf: dict) -> bool:
    """LOGGER.ENABLED — default True when omitted (legacy configs unchanged)."""
    if "ENABLED" not in conf:
        return True
    val = conf.get("ENABLED")
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


def reopen_file_handlers(logger: logging.Logger | None = None) -> int:
    """Reopen all :class:`logging.FileHandler` streams on *logger* (default: root).

    Use after **logrotate** moves/renames the log file (``create`` + ``postrotate``).
    Typically invoked from **SIGUSR2**. Does not reload YAML. Returns handlers reopened.
    """
    target = logger if logger is not None else logging.root
    count = 0
    for handler in target.handlers:
        if not isinstance(handler, logging.FileHandler):
            continue
        handler.acquire()
        try:
            handler.flush()
            if handler.stream:
                handler.stream.close()
            handler.stream = handler._open()
            count += 1
        except OSError as e:
            sys.stderr.write(
                "(LOGGER) Could not reopen log file %s: %s\n" % (getattr(handler, "baseFilename", "?"), e)
            )
        finally:
            handler.release()
    return count


def create_logger(conf: dict) -> logging.Logger:
    """
    Configure logging from conf dict with keys: ENABLED, PATH, LOG_FILE, LOG_LEVEL, LOG_HANDLERS.
    LOG_HANDLERS is a list of handler names, e.g. ['console', 'file'].
    Returns the root logger.
    """
    if not logging_enabled(conf):
        dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {"null": {"class": "logging.NullHandler"}},
            "root": {"handlers": ["null"], "level": "CRITICAL"},
        })
        return logging.getLogger(__name__)

    handlers = conf.get("LOG_HANDLERS", ["console"])
    if "file" in handlers:
        Path(conf["PATH"]).mkdir(parents=True, exist_ok=True)

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
                "filename": Path(conf["PATH"], conf["LOG_FILE"]),
                "level": conf.get("LOG_LEVEL", "INFO"),
            },
        },
        "root": {
            "handlers": handlers,
            "level": "NOTSET",
        },
    })
    return logging.getLogger(__name__)
