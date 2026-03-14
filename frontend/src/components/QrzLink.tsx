/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
 * HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
 * hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
 * HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
 * Original works and this derivative are under GPLv3.
 */

import { Link } from '@mui/material';

const QRZ_BASE = 'https://www.qrz.com/db/';

/** Extract callsign for QRZ URL: first token (before comma or space), uppercase. */
export function callsignForQrz(text: string | undefined): string {
  if (!text || typeof text !== 'string') return '';
  const part = text.split(',')[0].trim().split(/\s+/)[0]?.toUpperCase() ?? '';
  return part;
}

/** Returns true if the string looks like a callsign (contains at least one letter). */
export function isCallsignLike(s: string): boolean {
  return /[A-Za-z]/.test(s);
}

type QrzLinkProps = {
  callsign: string;
  children?: React.ReactNode;
  sx?: object;
};

/** Link to QRZ.com callsign lookup (opens in new tab). */
export default function QrzLink({ callsign, children, sx }: QrzLinkProps) {
  const call = callsignForQrz(callsign);
  if (!call || !isCallsignLike(call)) return <>{children ?? callsign}</>;
  return (
    <Link
      href={`${QRZ_BASE}${encodeURIComponent(call)}`}
      target="_blank"
      rel="noopener noreferrer"
      underline="hover"
      sx={sx}
    >
      {children ?? callsign}
    </Link>
  );
}
