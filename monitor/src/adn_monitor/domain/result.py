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

"""Result type for functional error handling (Success/Failure)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


@dataclass(frozen=True, slots=True)
class Success(Generic[T]):
    """Successful result wrapping a value."""

    value: T


@dataclass(frozen=True, slots=True)
class Failure(Generic[E]):
    """Failed result wrapping an error."""

    error: E


Result = Success[T] | Failure[E]


def is_ok(r: Result[T, E]) -> bool:
    """Return True if result is Success."""
    return isinstance(r, Success)


def is_fail(r: Result[T, E]) -> bool:
    """Return True if result is Failure."""
    return isinstance(r, Failure)


def unwrap_or(r: Result[T, E], default: T) -> T:
    """Return value if Success, else default."""
    return r.value if isinstance(r, Success) else default
