"""Self-service use case unit tests (no HTTP / DB)."""

from __future__ import annotations

from unittest.mock import MagicMock

from adn_monitor.application.self_service_use_cases import SelfServiceUseCases
from adn_monitor.domain import is_fail, is_ok
from adn_monitor.domain.client import Client
from adn_monitor.domain.session import UserSession


def _user(*, int_ids: list[int] | None = None, selected: int | None = 1) -> UserSession:
    ids = int_ids or [1, 2]
    return UserSession(callsign="XX1XX", int_ids=ids, selected_int_id=selected)


def test_get_device_parses_options():
    repo = MagicMock()
    repo.get_by_id.return_value = Client(
        int_id=1,
        callsign="XX1XX",
        options="TS1=1,2;TIMER=15;",
        modified=False,
        mode=4,
    )
    uc = SelfServiceUseCases(repo)
    result = uc.get_device(_user(), None)
    assert is_ok(result)
    body = result.value
    assert body["int_id"] == 1
    assert body["options"]["TS1"] == ["1", "2"]
    assert body["options"]["TIMER"] == "15"


def test_update_options_sets_modified_via_repo():
    repo = MagicMock()
    repo.update_options.return_value = 1
    uc = SelfServiceUseCases(repo)
    result = uc.update_options(_user(), None, "TS1=9;")
    assert is_ok(result)
    repo.update_options.assert_called_once_with(1, "TS1=9;")


def test_select_device_rejects_foreign_int_id():
    repo = MagicMock()
    uc = SelfServiceUseCases(repo)
    result = uc.select_device(_user(int_ids=[1]), 99)
    assert is_fail(result)
