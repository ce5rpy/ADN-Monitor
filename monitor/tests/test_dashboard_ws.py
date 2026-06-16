"""WebSocket conf protocol unit tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from adn_monitor.application.dashboard_ws import handle_conf_groups, parse_conf_message
from adn_monitor.application.monitor_controller import MonitorState


def test_parse_conf_all():
    assert parse_conf_message("conf,all") == list(
        (
            "main",
            "lnksys",
            "opb",
            "statictg",
            "lsthrd_log",
            "tgcount",
            "bridge",
            "log",
            "server_info",
        )
    )


def test_parse_conf_single_group():
    assert parse_conf_message("conf,lnksys") == ["lnksys"]


def test_handle_conf_server_info():
    state = MonitorState()
    state.server_info = {"server": "adn-server"}
    sent: list[str] = []

    handle_conf_groups(
        state=state,
        conf_global={},
        groups=["server_info"],
        send=sent.append,
        render_last_heard=MagicMock(),
        render_lstheard_log=MagicMock(),
        render_tgcount=MagicMock(),
    )
    assert len(sent) == 1
    assert sent[0][0] == "v"
    body = json.loads(sent[0][1:])
    assert "mode" in body
