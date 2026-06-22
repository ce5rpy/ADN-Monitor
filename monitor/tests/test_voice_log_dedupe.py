# ADN Monitor - voice log dedupe tests
#
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>

from __future__ import annotations

from adn_monitor.application.rts_update import voice_event_skip_master_downlink_log


def test_skip_master_peer_row_tx_start_log() -> None:
    ctable = {"MASTERS": {"SYSTEM-2": {"PEERS": {}}}, "OPENBRIDGES": {}}
    parts = "GROUP VOICE,START,TX,SYSTEM-2,1,730002,730002,2,71442".split(",")
    assert voice_event_skip_master_downlink_log(parts, ctable)


def test_keep_obp_rx_start_log() -> None:
    ctable = {"MASTERS": {}, "OPENBRIDGES": {"OBP-CL": {}}}
    parts = "GROUP VOICE,START,RX,OBP-CL,1,7140023,7140023,1,71442".split(",")
    assert not voice_event_skip_master_downlink_log(parts, ctable)


def test_keep_master_rx_start_log() -> None:
    ctable = {"MASTERS": {"SYSTEM-2": {"PEERS": {}}}, "OPENBRIDGES": {}}
    parts = "GROUP VOICE,START,RX,SYSTEM-2,1,714002301,714002301,2,7141".split(",")
    assert not voice_event_skip_master_downlink_log(parts, ctable)
