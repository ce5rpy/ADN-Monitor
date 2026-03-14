# Hotspot Proxy for ADN DMR Peer Server.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Protocol command constants (Homebrew / ADN DMR Peer Server)."""

# Homebrew protocol commands
DMRD = b"DMRD"
DMRA = b"DMRA"
MSTCL = b"MSTCL"
MSTNAK = b"MSTNAK"
MSTPONG = b"MSTPONG"
MSTN = b"MSTN"
MSTP = b"MSTP"
MSTC = b"MSTC"
RPTL = b"RPTL"
RPTPING = b"RPTPING"
RPTCL = b"RPTCL"
RPTACK = b"RPTACK"
RPTK = b"RPTK"
RPTC = b"RPTC"
RPTP = b"RPTP"
RPTA = b"RPTA"
RPTO = b"RPTO"
# Proxy control / info
PRBL = b"PRBL"
PRIN = b"PRIN"
