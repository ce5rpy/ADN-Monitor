"""Auth use case unit tests."""

from __future__ import annotations

from hashlib import pbkdf2_hmac
from unittest.mock import MagicMock

from adn_monitor.application.auth_use_cases import AuthUseCases
from adn_monitor.domain import is_fail, is_ok


def test_login_verifies_pbkdf2():
    password = "secret"
    digest = pbkdf2_hmac("sha256", password.encode(), b"ADN", 2000).hex()
    repo = MagicMock()
    repo.find_by_callsign_and_logged_in.return_value = {
        1: {"callsign": "XX1XX", "psswd": digest},
    }
    repo.get_int_ids_for_callsign.return_value = [1]
    uc = AuthUseCases(repo, pbkdf2_salt="ADN", pbkdf2_iterations=2000)
    ok = uc.login("XX1XX", password)
    assert is_ok(ok)
    assert ok.value.callsign == "XX1XX"
    assert ok.value.int_ids == [1]


def test_login_rejects_bad_password():
    repo = MagicMock()
    repo.find_by_callsign_and_logged_in.return_value = {
        1: {"callsign": "XX1XX", "psswd": "deadbeef"},
    }
    uc = AuthUseCases(repo)
    result = uc.login("XX1XX", "wrong")
    assert is_fail(result)
