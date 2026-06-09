"""Authentication use cases (PBKDF2-SHA256, same salt/iterations as hotspot proxy)."""

from __future__ import annotations

from hashlib import pbkdf2_hmac

from ..domain import Failure, Result, Success
from ..domain.session import UserSession
from .ports import AuthRepository


class AuthUseCases:
    def __init__(
        self,
        repo: AuthRepository,
        *,
        pbkdf2_salt: str = "ADN",
        pbkdf2_iterations: int = 2000,
    ) -> None:
        self._repo = repo
        self._salt = pbkdf2_salt
        self._iterations = pbkdf2_iterations

    def login(self, callsign: str, password: str) -> Result[UserSession, str]:
        callsign = callsign.strip()
        if not callsign or not password:
            return Failure("Missing callsign or password")
        rows = self._repo.find_by_callsign_and_logged_in(callsign)
        if not rows:
            return Failure("Invalid callsign or password")
        for row in rows.values():
            if self._verify_password(password, row["psswd"]):
                cs = row["callsign"]
                int_ids = self._repo.get_int_ids_for_callsign(cs)
                return Success(
                    UserSession(
                        callsign=cs,
                        int_ids=int_ids,
                        selected_int_id=int_ids[0] if int_ids else None,
                    )
                )
        return Failure("Invalid callsign or password")

    def login_by_ip(self, ip: str) -> Result[UserSession, str]:
        if not ip:
            return Failure("Unknown client")
        data = self._repo.find_by_host(ip)
        if not data:
            return Failure("No single user for this IP")
        int_ids = [int(x) for x in data["int_ids"]]  # type: ignore[index]
        return Success(
            UserSession(
                callsign=str(data["callsign"]),
                int_ids=int_ids,
                selected_int_id=int_ids[0] if int_ids else None,
            )
        )

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        if isinstance(stored_hash, bytes):
            stored_hash = stored_hash.decode("utf-8", errors="ignore")
        digest = pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self._salt.encode("utf-8"),
            self._iterations,
        ).hex()
        return digest == stored_hash
