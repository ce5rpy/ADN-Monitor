# ADN Monitor - peer RF mode (simplex/duplex parity with adn-server)
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

"""Simplex/duplex classification and voice slot mapping (server downlink parity)."""

from __future__ import annotations

from typing import Any

RF_MODE_SIMPLEX = "simplex"
RF_MODE_DUPLEX = "duplex"
SIMPLEX_VOICE_SLOT = 2


def _freq_text(raw: Any) -> str:
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace").strip()
    return str(raw or "").strip()


def _parse_slots_code(raw: Any) -> int | None:
    text = _freq_text(raw)
    if not text.isdigit():
        return None
    try:
        return int(text)
    except ValueError:
        return None


def derive_peer_rf_mode(peer: dict[str, Any]) -> str:
    """Classify hotspot RF from ``SLOTS`` and matching RX/TX frequencies."""
    slots_i = _parse_slots_code(peer.get("SLOTS"))
    if slots_i == 4:
        return RF_MODE_SIMPLEX
    rx = _freq_text(peer.get("RX_FREQ"))
    tx = _freq_text(peer.get("TX_FREQ"))
    if rx and tx and rx == tx:
        return RF_MODE_SIMPLEX
    return RF_MODE_DUPLEX


def peer_rf_mode(peer: dict[str, Any]) -> str:
    """Cached ``RF_MODE`` from report/config or derived from peer fields."""
    cached = peer.get("RF_MODE")
    if cached in (RF_MODE_SIMPLEX, RF_MODE_DUPLEX):
        return str(cached)
    mode = peer.get("rf_mode")
    if mode in (RF_MODE_SIMPLEX, RF_MODE_DUPLEX):
        return str(mode)
    return derive_peer_rf_mode(peer)


def peer_is_simplex(peer: dict[str, Any]) -> bool:
    return peer_rf_mode(peer) == RF_MODE_SIMPLEX


def normalize_ua_voice_slot(peer: dict[str, Any], wire_slot: int) -> int:
    """UA / SINGLE dynamics use TS2 on simplex hotspots (MMDVMHost DMO parity)."""
    if peer_is_simplex(peer):
        return SIMPLEX_VOICE_SLOT
    return int(wire_slot)


def peer_downlink_display_slot(
    peer_row: dict[str, Any],
    destination: int,
    event_slot: int,
) -> int:
    """Map wire timeslot to the CTABLE chip for this TG (OPTIONS + simplex)."""
    tg = str(destination)
    ts1 = [str(x).strip() for x in (peer_row.get("TS1_STATIC") or []) if str(x).strip()]
    ts2 = [str(x).strip() for x in (peer_row.get("TS2_STATIC") or []) if str(x).strip()]
    in_ts1 = tg in ts1
    in_ts2 = tg in ts2
    if peer_is_simplex(peer_row) and (in_ts1 or in_ts2):
        return SIMPLEX_VOICE_SLOT
    if in_ts1 and not in_ts2:
        return 1
    if in_ts2 and not in_ts1:
        return 2
    return event_slot
