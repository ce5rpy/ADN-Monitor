"""Self-service use case unit tests (no HTTP / DB)."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.application.self_service_use_cases import SelfServiceUseCases
from adn_monitor.domain import is_ok
from adn_monitor.domain.client import Client
from adn_monitor.domain.session import UserSession


def _user(
    *,
    int_ids: list[int] | None = None,
    selected: int | None = 1,
    login_method: str = "password",
) -> UserSession:
    ids = int_ids or [1, 2]
    return UserSession(
        callsign="XX1XX", int_ids=ids, selected_int_id=selected, login_method=login_method
    )


def test_get_device_parses_options():
    repo = MagicMock()
    repo.get_by_id.return_value = Client(
        int_id=1,
        callsign="XX1XX",
        options="TS1=1,2;TIMER=15;",
        modified=False,
        mode=4,
    )
    auth_repo = MagicMock()
    auth_repo.get_logged_in_devices_by_callsign.return_value = [
        {"int_id": 1, "callsign": "XX1XX"}
    ]
    uc = SelfServiceUseCases(repo, auth_repo=auth_repo)
    result = uc.get_device(_user(), None, "192.168.1.1")
    assert is_ok(result)
    body = result.value
    assert body["int_id"] == 1
    assert body["options"]["TS1"] == ["1", "2"]
    assert body["options"]["TIMER"] == "15"


def test_update_options_sets_modified_via_repo():
    repo = MagicMock()
    repo.update_options.return_value = 1
    auth_repo = MagicMock()
    auth_repo.get_logged_in_devices_by_callsign.return_value = [
        {"int_id": 1, "callsign": "XX1XX"}
    ]
    uc = SelfServiceUseCases(repo, auth_repo=auth_repo)
    result = uc.update_options(_user(), None, "TS1=9;", "192.168.1.1")
    assert is_ok(result)
    repo.update_options.assert_called_once_with(1, "TS1=9;")


def test_list_devices_password_uses_callsign():
    auth_repo = MagicMock()
    auth_repo.get_logged_in_devices_by_callsign.return_value = [
        {"int_id": 100, "callsign": "XX1XX"},
        {"int_id": 200, "callsign": "XX1XX"},
    ]
    uc = SelfServiceUseCases(MagicMock(), auth_repo=auth_repo)
    devices = uc.list_devices(_user(login_method="password"), "192.168.1.1")
    assert devices == [
        {"int_id": 100, "callsign": "XX1XX"},
        {"int_id": 200, "callsign": "XX1XX"},
    ]
    auth_repo.get_logged_in_devices_by_callsign.assert_called_once_with("XX1XX")


def test_list_devices_ip_uses_host():
    auth_repo = MagicMock()
    auth_repo.get_logged_in_devices_by_host.return_value = [
        {"int_id": 100, "callsign": "XX1XX"},
        {"int_id": 200, "callsign": "YY2YY"},
    ]
    uc = SelfServiceUseCases(MagicMock(), auth_repo=auth_repo)
    devices = uc.list_devices(_user(login_method="ip"), "192.168.1.1")
    assert devices == [
        {"int_id": 100, "callsign": "XX1XX"},
        {"int_id": 200, "callsign": "YY2YY"},
    ]
    auth_repo.get_logged_in_devices_by_host.assert_called_once_with("192.168.1.1")


def test_list_devices_falls_back_to_session_without_auth_repo():
    uc = SelfServiceUseCases(MagicMock())
    devices = uc.list_devices(_user(int_ids=[5, 10]), "192.168.1.1")
    assert devices == [
        {"int_id": 5, "callsign": "XX1XX"},
        {"int_id": 10, "callsign": "XX1XX"},
    ]
