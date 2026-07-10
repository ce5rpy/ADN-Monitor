"""Tests for dynamic TG reload requests (peer_dynamic_tgs.need_reload)."""

from __future__ import annotations

from adn_monitor.application.peer_system_lookup import peer_master_names
from adn_monitor.application.self_service_use_cases import SelfServiceUseCases
from adn_monitor.domain import is_fail, is_ok
from adn_monitor.domain.client import Client
from adn_monitor.domain.session import UserSession


class _FakeDeviceRepo:
    def get_by_id(self, int_id: int) -> Client | None:
        return Client(int_id=int_id, callsign="TEST", options="", modified=False, mode=4)

    def update_options(self, int_id: int, options: str) -> int:
        return 1

    def get_modified(self, int_id: int) -> bool:
        return False


class _FakeDynamicRepo:
    def __init__(self) -> None:
        self.calls: list[tuple[int, list[str] | None]] = []

    def mark_need_reload(
        self,
        int_id: int,
        *,
        fallback_system_names: list[str] | None = None,
    ) -> bool:
        self.calls.append((int_id, fallback_system_names))
        return True


class _FakeAuthRepo:
    def get_logged_in_devices_by_host(self, host: str) -> list[dict[str, object]]:
        return [{"int_id": 7300444, "callsign": "TEST"}]

    def get_logged_in_devices_by_callsign(self, callsign: str) -> list[dict[str, object]]:
        return [{"int_id": 7300444, "callsign": callsign}]


def test_request_dynamic_reload_marks_peer() -> None:
    dynamic = _FakeDynamicRepo()
    uc = SelfServiceUseCases(_FakeDeviceRepo(), auth_repo=_FakeAuthRepo(), dynamic_tg_repo=dynamic)
    user = UserSession(callsign="TEST", int_ids=[7300444], selected_int_id=7300444, login_method="ip")
    result = uc.request_dynamic_reload(
        user,
        7300444,
        "10.0.0.1",
        fallback_system_names=["SYSTEM-2"],
    )
    assert is_ok(result)
    assert dynamic.calls == [(7300444, ["SYSTEM-2"])]


def test_request_dynamic_reload_rejects_foreign_device() -> None:
    dynamic = _FakeDynamicRepo()
    uc = SelfServiceUseCases(_FakeDeviceRepo(), auth_repo=_FakeAuthRepo(), dynamic_tg_repo=dynamic)
    user = UserSession(callsign="TEST", int_ids=[7300444], selected_int_id=7300444, login_method="ip")
    result = uc.request_dynamic_reload(user, 9999999, "10.0.0.1")
    assert is_fail(result)
    assert dynamic.calls == []


def test_request_dynamic_reload_password_allows_callsign_devices() -> None:
    dynamic = _FakeDynamicRepo()

    class _AuthRepo(_FakeAuthRepo):
        def get_logged_in_devices_by_host(self, host: str) -> list[dict[str, object]]:
            return []

        def get_logged_in_devices_by_callsign(self, callsign: str) -> list[dict[str, object]]:
            return [
                {"int_id": 7300444, "callsign": callsign},
                {"int_id": 7300555, "callsign": callsign},
            ]

    uc = SelfServiceUseCases(_FakeDeviceRepo(), auth_repo=_AuthRepo(), dynamic_tg_repo=dynamic)
    user = UserSession(
        callsign="TEST",
        int_ids=[7300444, 7300555],
        selected_int_id=7300555,
        login_method="password",
    )
    result = uc.request_dynamic_reload(user, 7300555, "10.0.0.1")
    assert is_ok(result)
    assert dynamic.calls == [(7300555, None)]


def test_peer_master_names_from_ctable() -> None:
    ctable = {
        "MASTERS": {
            "SYSTEM-2": {"PEERS": {7300444: {"id": 7300444}}},
            "ECHO": {"PEERS": {99: {"id": 99}}},
        }
    }
    assert peer_master_names(ctable, 7300444) == ["SYSTEM-2"]
    assert peer_master_names(ctable, 999) == []
