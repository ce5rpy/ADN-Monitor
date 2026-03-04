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

"""Domain and application errors."""


class AdnMonitorError(Exception):
    """Base exception for ADN Systems Monitor domain/application."""

    pass


class AliasError(AdnMonitorError):
    """Error loading or resolving alias data."""

    pass


class AliasTableNotFoundError(AliasError):
    """Unknown alias table name."""

    pass


class ConfigError(AdnMonitorError):
    """Configuration loading or validation error."""

    pass


class RepositoryError(AdnMonitorError):
    """Persistence/database error."""

    pass


class ReportProtocolError(AdnMonitorError):
    """HBlink report protocol error (decode, unknown opcode)."""

    pass
