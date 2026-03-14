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

"""Report payload decoder (CONFIG_SND / BRIDGE_SND). Implements ReportPayloadDecoder port."""

from __future__ import annotations

import json
import logging
from pickle import loads

from adn_monitor.application.ports import ReportPayloadDecoder
from adn_monitor.domain import Failure, ReportProtocolError, Success

logger = logging.getLogger("adn-mon")

# Payload kind constants (Clean Code: no magic strings in logic)
CONFIG_PAYLOAD = "CONFIG"
BRIDGES_PAYLOAD = "BRIDGES"
CONFIG_KEY = "CONFIG"
BRIDGES_KEY = "BRIDGES"
MAX_HEX_LOG = 200


def _unwrap_dict(obj: object, key: str) -> dict | None:
    """Extract config/bridges dict from wrapped payload (tuple, object, or dict with key)."""
    if isinstance(obj, dict):
        for k in (key, key.lower()):
            if k in obj and isinstance(obj[k], dict):
                return obj[k]
        return obj
    if isinstance(obj, (list, tuple)) and len(obj) >= 1 and isinstance(obj[0], dict):
        return obj[0]
    if hasattr(obj, key):
        v = getattr(obj, key)
        if isinstance(v, dict):
            return v
    return None


def _try_pickle(data: bytes, key: str) -> dict | None:
    """Try to decode payload as pickle; return dict or None."""
    try:
        obj = loads(data)
        if isinstance(obj, dict):
            return obj
        unwrapped = _unwrap_dict(obj, key)
        return unwrapped
    except Exception:
        return None


def _try_json(data: bytes, key: str) -> dict | None:
    """Try to decode payload as JSON; return dict or None."""
    try:
        text = data.decode("utf-8", "replace").strip()
        if not (text.startswith("{") or text.startswith("[")):
            return None
        obj = json.loads(text)
        if isinstance(obj, dict):
            unwrapped = _unwrap_dict(obj, key)
            return unwrapped if unwrapped is not None else obj
        if isinstance(obj, (list, tuple)) and obj and isinstance(obj[0], dict):
            return obj[0]
    except Exception:
        pass
    return None


def _log_decode_success(kind: str, source: str, key_count: int) -> None:
    """Single place for decode success logging (DRY)."""
    logger.info("(REPORT) %s decoded OK (%s), %d keys", kind, source, key_count)


def _log_decode_failure(kind: str, error: Exception, data: bytes) -> None:
    """Single place for decode failure logging (DRY)."""
    head = data[: min(MAX_HEX_LOG, len(data))].hex() if data else ""
    logger.info(
        "(REPORT) %s decode failed (pickle+JSON): %s; payload len=%d head_hex=%s",
        kind,
        error,
        len(data),
        head,
    )


class PickleJsonReportPayloadDecoder(ReportPayloadDecoder):
    """
    Decodes CONFIG_SND / BRIDGE_SND payloads: pickle first (FDMR-Monitor2/HBlink),
    then JSON fallback (ADN Systems). Logging is done in this infrastructure layer.
    """

    def decode_config(self, raw_message: bytes) -> Success[dict] | Failure[ReportProtocolError]:
        """Decode CONFIG_SND payload."""
        return self._decode(raw_message, CONFIG_PAYLOAD, CONFIG_KEY)

    def decode_bridges(self, raw_message: bytes) -> Success[dict] | Failure[ReportProtocolError]:
        """Decode BRIDGE_SND payload."""
        return self._decode(raw_message, BRIDGES_PAYLOAD, BRIDGES_KEY)

    def _decode(
        self, raw_message: bytes, kind: str, key: str
    ) -> Success[dict] | Failure[ReportProtocolError]:
        data = raw_message[1:]
        if not data:
            logger.info("(REPORT) %s payload empty (len=0)", kind)
            return Success({})

        # 1) Pickle (original protocol)
        result = _try_pickle(data, key)
        if result is not None:
            _log_decode_success(kind, "pickle", len(result))
            return Success(result)

        # 2) JSON fallback
        result = _try_json(data, key)
        if result is not None:
            _log_decode_success(kind, "JSON", len(result))
            return Success(result)

        # Both failed: log and return Failure so use case can apply empty dict
        _log_decode_failure(kind, ValueError("pickle and JSON failed"), data)
        return Failure(ReportProtocolError(f"{kind} decode failed"))
