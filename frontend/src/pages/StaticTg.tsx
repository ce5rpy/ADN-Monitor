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
 */

import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useWebSocketGroup } from '../hooks/useWebSocket';
import QrzLink from '../components/QrzLink';

type TsEntry = { TS?: boolean | string; TRX?: string; SUB?: string; DEST?: string };
type SingleTs = { TGID?: number | string; TO?: string };
type PeerEntry = Record<string, unknown> & {
  CALLSIGN?: string;
  CONNECTED?: string;
  RX_FREQ?: string;
  TX_FREQ?: string;
  LOCATION?: string;
  1?: TsEntry;
  2?: TsEntry;
  SINGLE_TS1?: SingleTs;
  SINGLE_TS2?: SingleTs;
  TS1_STATIC?: string[];
  TS2_STATIC?: string[];
};
type MasterEntry = { REPEAT?: string; PEERS?: Record<string, PeerEntry> };
type Ctable = {
  MASTERS?: Record<string, MasterEntry>;
  PEERS?: Record<string, PeerEntry>;
};

type StatictgPayload = { ctable?: Ctable; emaster?: boolean };

function getTs(peer: PeerEntry, ts: 1 | 2): TsEntry {
  const t = peer[ts] ?? (peer as Record<string, unknown>)[String(ts)];
  return (t as TsEntry) ?? {};
}

/** Extract TG number from DEST string. */
function activeTgFromDest(dest: string | undefined): string {
  if (!dest) return '';
  const s = String(dest).replace(/&nbsp;/g, ' ').trim();
  const m = s.match(/\d+/);
  return m ? m[0] : '';
}

export default function StaticTg() {
  const { t } = useTranslation();
  const { data } = useWebSocketGroup('lnksys');
  const payload = data as StatictgPayload | null;
  const ctable = payload?.ctable;
  const emaster = payload?.emaster ?? false;

  if (data == null) {
    return (
      <Box>
        <Typography color="text.secondary">{t('pre_wait', { defaultValue: 'Waiting for server info...' })}</Typography>
      </Box>
    );
  }

  const masters = ctable?.MASTERS ?? {};
  const hasMasters = Object.keys(masters).length > 0;
  const showEmptyMasters = emaster;

  const rows: React.ReactNode[] = [];
  for (const [masterName, master] of Object.entries(masters)) {
    const peerList = master?.PEERS ?? {};
    const peerEntries = Object.entries(peerList);
    if (peerEntries.length === 0 && !showEmptyMasters) continue;

    for (const [peerId, peer] of peerEntries) {
      const p = peer as PeerEntry;
      const ts1 = getTs(p, 1);
      const ts2 = getTs(p, 2);
      const trx1 = String(ts1.TRX ?? '');
      const trx2 = String(ts2.TRX ?? '');
      const activeTg1 = activeTgFromDest(ts1.DEST);
      const activeTg2 = activeTgFromDest(ts2.DEST);
      const staticTs1 = (p.TS1_STATIC ?? []).filter(Boolean);
      const staticTs2 = (p.TS2_STATIC ?? []).filter(Boolean);
      const single1 = p.SINGLE_TS1 ?? {};
      const single2 = p.SINGLE_TS2 ?? {};
      const singleTg1 = String(single1.TGID ?? '').trim() || '';
      const singleTg2 = String(single2.TGID ?? '').trim() || '';
      const to1 = String(single1.TO ?? '').trim() || '';
      const to2 = String(single2.TO ?? '').trim() || '';

      rows.push(
        <TableRow key={`st-${masterName}-${peerId}-1`} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
          <TableCell rowSpan={2} sx={{ width: 200 }}>
            <Typography variant="body2" fontWeight="bold"><QrzLink callsign={String(p.CALLSIGN ?? peerId)}>{String(p.CALLSIGN ?? peerId)}</QrzLink></Typography>
            <Chip size="small" label={peerId} sx={{ mt: 0.25 }} />
            <Typography variant="caption" display="block" color="text.secondary">{String(p.LOCATION ?? '')}</Typography>
          </TableCell>
          <TableCell rowSpan={2} align="center" sx={{ bgcolor: 'success.light', color: 'success.contrastText', width: 110, minWidth: 110, maxWidth: 110, whiteSpace: 'nowrap' }}>
            {String(p.CONNECTED ?? '')}
          </TableCell>
          <TableCell align="center" sx={{ width: 56, minWidth: 56 }}>
            <Chip size="small" label="TS1" color={trx1 === 'TX' ? 'success' : trx1 === 'RX' ? 'error' : 'default'} />
          </TableCell>
          <TableCell>
            {staticTs1.length > 0 ? staticTs1.map((tg) => {
              const isActive = (trx1 === 'RX' || trx1 === 'TX') && String(tg) === activeTg1;
              return (
                <Chip key={tg} size="small" label={tg} color={isActive ? (trx1 === 'TX' ? 'success' : 'error') : 'default'} sx={{ mr: 0.25, mb: 0.25 }} />
              );
            }) : ''}
          </TableCell>
          <TableCell align="center" sx={{ width: 80, minWidth: 80, whiteSpace: 'nowrap' }}>{singleTg1}</TableCell>
          <TableCell align="center" sx={{ width: 80, minWidth: 80, whiteSpace: 'nowrap' }}>{to1}</TableCell>
        </TableRow>,
        <TableRow key={`st-${masterName}-${peerId}-2`} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
          <TableCell align="center" sx={{ width: 56, minWidth: 56 }}>
            <Chip size="small" label="TS2" color={trx2 === 'TX' ? 'success' : trx2 === 'RX' ? 'error' : 'default'} />
          </TableCell>
          <TableCell>
            {staticTs2.length > 0 ? staticTs2.map((tg) => {
              const isActive = (trx2 === 'RX' || trx2 === 'TX') && String(tg) === activeTg2;
              return (
                <Chip key={tg} size="small" label={tg} color={isActive ? (trx2 === 'TX' ? 'success' : 'error') : 'default'} sx={{ mr: 0.25, mb: 0.25 }} />
              );
            }) : ''}
          </TableCell>
          <TableCell align="center" sx={{ width: 80, minWidth: 80, whiteSpace: 'nowrap' }}>{singleTg2}</TableCell>
          <TableCell align="center" sx={{ width: 80, minWidth: 80, whiteSpace: 'nowrap' }}>{to2}</TableCell>
        </TableRow>
      );
    }
  }

  const tablePaperSx = {
    overflow: 'auto' as const,
    boxShadow: (t: { palette: { mode: string } }) => (t.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)'),
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} color="text.primary" sx={{ mb: 2 }}>
        {t('statictg_title', { defaultValue: 'Static TG' })}
      </Typography>

      {!hasMasters && (
        <Typography color="text.secondary" sx={{ py: 2 }}>
          {t('statictg_no_data', { defaultValue: 'Waiting for server info...' })}
        </Typography>
      )}

      {hasMasters && rows.length > 0 && (
        <Paper sx={tablePaperSx}>
          <TableContainer>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell sx={{ fontWeight: 600, width: 200 }}>{t('lnksys_callsign', { defaultValue: 'Callsign' })} ({t('statictg_dmrid', { defaultValue: 'DMR Id' })})<br />{t('lnksys_loc', { defaultValue: 'Location' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: 110, minWidth: 110, maxWidth: 110 }}>{t('lnksys_connected', { defaultValue: 'Time Connected' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: 56, minWidth: 56, whiteSpace: 'nowrap' }} align="center">{t('lnksys_slot', { defaultValue: 'Slot' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{t('lnksys_static_tg', { defaultValue: 'Static TG' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: 80, minWidth: 80, whiteSpace: 'nowrap' }}>{t('lnksys_single_tg', { defaultValue: 'Single TG' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: 80, minWidth: 80 }}>{t('lnksys_to', { defaultValue: 'T/O' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>{rows}</TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
}
