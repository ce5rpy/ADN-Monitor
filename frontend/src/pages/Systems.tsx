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
  Grid,
  Card,
  CardContent,
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
  STATS?: { CONNECTION?: string; CONNECTED?: string; PINGS_SENT?: number; PINGS_ACKD?: number };
  SINGLE_TS1?: SingleTs;
  SINGLE_TS2?: SingleTs;
  TS1_STATIC?: string[];
  TS2_STATIC?: string[];
};
type Ctable = {
  MASTERS?: Record<string, { REPEAT?: string; PEERS?: Record<string, PeerEntry> }>;
  PEERS?: Record<string, PeerEntry>;
  OPENBRIDGES?: Record<string, Record<string, unknown>>;
};

type LnksysPayload = { ctable?: Ctable; emaster?: boolean };

function getTs(peer: PeerEntry, ts: 1 | 2): TsEntry {
  const t = peer[ts] ?? (peer as Record<string, unknown>)[String(ts)];
  return (t as TsEntry) ?? {};
}

/** Extract TG number from DEST string for highlighting active static TG. */
function activeTgFromDest(dest: string | undefined): string {
  if (!dest) return '';
  const s = String(dest).replace(/&nbsp;/g, ' ').trim();
  const m = s.match(/\d+/);
  return m ? m[0] : '';
}

function isRepeater(peerId: string, peer: PeerEntry): boolean {
  const rx = String(peer.RX_FREQ ?? '');
  const tx = String(peer.TX_FREQ ?? '');
  return peerId.length === 6 && rx !== 'N/A' && tx !== 'N/A';
}
function isHotspot(peerId: string, peer: PeerEntry): boolean {
  const rx = String(peer.RX_FREQ ?? '');
  const tx = String(peer.TX_FREQ ?? '');
  return peerId.length >= 7 && rx !== 'N/A' && tx !== 'N/A';
}
function isBridge(peer: PeerEntry): boolean {
  const rx = String(peer.RX_FREQ ?? '');
  const tx = String(peer.TX_FREQ ?? '');
  return rx === 'N/A' && tx === 'N/A';
}

export default function Systems() {
  const { t } = useTranslation();
  const { data } = useWebSocketGroup('lnksys');
  const payload = data as LnksysPayload | null;
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
  const peers = ctable?.PEERS ?? {};

  let countRepeaters = 0;
  let countHotspots = 0;
  let countBridges = 0;
  for (const master of Object.values(masters)) {
    const peerList = master?.PEERS ?? {};
    for (const [pid, p] of Object.entries(peerList)) {
      const peer = p as PeerEntry;
      if (isRepeater(String(pid), peer)) countRepeaters++;
      else if (isHotspot(String(pid), peer)) countHotspots++;
      else if (isBridge(peer)) countBridges++;
    }
  }

  const hasMasters = Object.keys(masters).length > 0;
  const showEmptyMasters = emaster;

  const renderMasterPeerRows = (
    filter: (peerId: string, peer: PeerEntry) => boolean,
    tableKey: string
  ) => {
    const rows: React.ReactNode[] = [];
    for (const [masterName, master] of Object.entries(masters)) {
      const peerList = master?.PEERS ?? {};
      const list = Object.entries(peerList).filter(([pid, p]) => filter(String(pid), p as PeerEntry));
      if (list.length === 0 && !showEmptyMasters) continue;
      for (const [peerId, peer] of list) {
        const p = peer as PeerEntry;
        const ts1 = getTs(p, 1);
        const ts2 = getTs(p, 2);
        const trx1 = String(ts1.TRX ?? '');
        const trx2 = String(ts2.TRX ?? '');
        const sub1 = String(ts1.SUB ?? '').replace(/&nbsp;/g, ' ').trim() || '';
        const sub2 = String(ts2.SUB ?? '').replace(/&nbsp;/g, ' ').trim() || '';
        const dest1 = String(ts1.DEST ?? '').replace(/&nbsp;/g, ' ').trim() || '';
        const dest2 = String(ts2.DEST ?? '').replace(/&nbsp;/g, ' ').trim() || '';
        const chipColor1 = trx1 === 'TX' ? 'success' : trx1 === 'RX' ? 'error' : 'default';
        const chipColor2 = trx2 === 'TX' ? 'success' : trx2 === 'RX' ? 'error' : 'default';
        const activeTg1 = activeTgFromDest(ts1.DEST);
        const activeTg2 = activeTgFromDest(ts2.DEST);
        const staticTs1 = (p.TS1_STATIC ?? []).filter(Boolean);
        const staticTs2 = (p.TS2_STATIC ?? []).filter(Boolean);
        rows.push(
          <TableRow key={`${tableKey}-${masterName}-${peerId}-1`} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
            <TableCell rowSpan={2} sx={colCallsign}>
              <Typography variant="body2" fontWeight="bold"><QrzLink callsign={String(p.CALLSIGN ?? peerId)}>{String(p.CALLSIGN ?? peerId)}</QrzLink></Typography>
              <Chip size="small" label={peerId} sx={{ mt: 0.25 }} />
              <Typography variant="caption" display="block" color="text.secondary">{String(p.LOCATION ?? '')}</Typography>
            </TableCell>
            <TableCell rowSpan={2} align="center" sx={{ bgcolor: 'success.light', color: 'success.contrastText', whiteSpace: 'nowrap', ...colConnected }}>
              {String(p.CONNECTED ?? '—')}
            </TableCell>
            <TableCell align="center" sx={colSlotCell}>
              <Chip size="small" label="TS1" color={chipColor1} />
            </TableCell>
            <TableCell>
              {staticTs1.length > 0 ? staticTs1.map((tg) => {
                const isActive = (trx1 === 'RX' || trx1 === 'TX') && String(tg) === activeTg1;
                return (
                  <Chip key={tg} size="small" label={tg} color={isActive ? (trx1 === 'TX' ? 'success' : 'error') : 'default'} sx={{ mr: 0.25, mb: 0.25 }} />
                );
              }) : ''}
            </TableCell>
            <TableCell align="center">
              {sub1 ? <Chip size="small" label={sub1} color={chipColor1} /> : ''}
            </TableCell>
            <TableCell align="center">
              {dest1 ? <Chip size="small" label={dest1} color={chipColor1} /> : ''}
            </TableCell>
          </TableRow>,
          <TableRow key={`${tableKey}-${masterName}-${peerId}-2`} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
            <TableCell align="center" sx={colSlotCell}>
              <Chip size="small" label="TS2" color={chipColor2} />
            </TableCell>
            <TableCell>
              {staticTs2.length > 0 ? staticTs2.map((tg) => {
                const isActive = (trx2 === 'RX' || trx2 === 'TX') && String(tg) === activeTg2;
                return (
                  <Chip key={tg} size="small" label={tg} color={isActive ? (trx2 === 'TX' ? 'success' : 'error') : 'default'} sx={{ mr: 0.25, mb: 0.25 }} />
                );
              }) : ''}
            </TableCell>
            <TableCell align="center">
              {sub2 ? <Chip size="small" label={sub2} color={chipColor2} /> : ''}
            </TableCell>
            <TableCell align="center">
              {dest2 ? <Chip size="small" label={dest2} color={chipColor2} /> : ''}
            </TableCell>
          </TableRow>
        );
      }
    }
    return rows;
  };

  const tablePaperSx = {
    overflow: 'auto' as const,
    mb: 2,
    boxShadow: (t: { palette: { mode: string } }) => (t.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)'),
  };

  /** Column widths: fixed so table scrolls horizontally on narrow viewports instead of overlapping. */
  const tableMinWidth = 720;
  const colCallsign = { width: 200, minWidth: 200, maxWidth: 200, boxSizing: 'border-box' as const };
  const colConnected = { width: 150, minWidth: 150, maxWidth: 150, boxSizing: 'border-box' as const };
  const colSlot = { width: 75, minWidth: 75, whiteSpace: 'nowrap' as const };
  const colSlotCell = { width: 75, minWidth: 75 };
  const masterCols = [colCallsign, colConnected, colSlot, undefined, undefined, undefined] as const;
  const colService = { width: 130, minWidth: 100, maxWidth: 160 };
  const peerCols = [colService, colCallsign, colConnected, colSlot, undefined, undefined] as const;

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} color="text.primary" sx={{ mb: 2 }}>
        {t('lnksys_title', { defaultValue: 'Linked systems' })}
      </Typography>

      {!hasMasters && Object.keys(peers).length === 0 && (
        <Typography color="text.secondary">
          {t('lnksys_no_data', { defaultValue: 'Waiting for server info...' })}
        </Typography>
      )}

      {hasMasters && (
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={4}>
            <Card sx={{ bgcolor: 'success.main', color: 'success.contrastText' }}>
              <CardContent>
                <Typography variant="h4">{countRepeaters}</Typography>
                <Typography variant="body2">{t('lnksys_repeaters', { defaultValue: 'Repeaters' })}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card sx={{ bgcolor: 'warning.main', color: 'warning.contrastText' }}>
              <CardContent>
                <Typography variant="h4">{countHotspots}</Typography>
                <Typography variant="body2">{t('lnksys_hotspots', { defaultValue: 'Hotspots' })}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card sx={{ bgcolor: 'error.main', color: 'error.contrastText' }}>
              <CardContent>
                <Typography variant="h4">{countBridges}</Typography>
                <Typography variant="body2">{t('lnksys_bridges', { defaultValue: 'Bridges' })}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {countRepeaters > 0 && (
        <Paper sx={tablePaperSx}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ p: 1.5 }}>
            {t('lnksys_repeaters', { defaultValue: 'Repeaters' })}
          </Typography>
          <TableContainer sx={{ minWidth: 0 }}>
            <Table size="small" stickyHeader sx={{ tableLayout: 'fixed', width: '100%', minWidth: tableMinWidth }}>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell sx={{ fontWeight: 600, ...masterCols[0] }}>{t('lnksys_callsign', { defaultValue: 'Callsign' })} ({t('statictg_dmrid', { defaultValue: 'DMR Id' })})<br />{t('lnksys_loc', { defaultValue: 'Location' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...masterCols[1] }}>{t('lnksys_connected', { defaultValue: 'Time Connected' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...colSlot }} align="center">{t('lnksys_slot', { defaultValue: 'Slot' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{t('lnksys_static_tg', { defaultValue: 'Static TG' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_src', { defaultValue: 'Source' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_dst', { defaultValue: 'Destination' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>{renderMasterPeerRows(isRepeater, 'rpt')}</TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {countHotspots > 0 && (
        <Paper sx={tablePaperSx}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ p: 1.5 }}>
            {t('lnksys_hotspots', { defaultValue: 'Hotspots' })}
          </Typography>
          <TableContainer sx={{ minWidth: 0 }}>
            <Table size="small" stickyHeader sx={{ tableLayout: 'fixed', width: '100%', minWidth: tableMinWidth }}>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell sx={{ fontWeight: 600, ...masterCols[0] }}>{t('lnksys_callsign', { defaultValue: 'Callsign' })} ({t('statictg_dmrid', { defaultValue: 'DMR Id' })})<br />{t('lnksys_loc', { defaultValue: 'Location' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...masterCols[1] }}>{t('lnksys_connected', { defaultValue: 'Time Connected' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...colSlot }} align="center">{t('lnksys_slot', { defaultValue: 'Slot' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{t('lnksys_static_tg', { defaultValue: 'Static TG' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_src', { defaultValue: 'Source' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_dst', { defaultValue: 'Destination' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>{renderMasterPeerRows(isHotspot, 'hts')}</TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {countBridges > 0 && (
        <Paper sx={tablePaperSx}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ p: 1.5 }}>
            {t('lnksys_bridges', { defaultValue: 'Bridges (IP)' })}
          </Typography>
          <TableContainer sx={{ minWidth: 0 }}>
            <Table size="small" stickyHeader sx={{ tableLayout: 'fixed', width: '100%', minWidth: tableMinWidth }}>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell sx={{ fontWeight: 600, ...masterCols[0] }}>{t('lnksys_callsign', { defaultValue: 'Callsign' })} ({t('statictg_dmrid', { defaultValue: 'DMR Id' })})<br />{t('lnksys_loc', { defaultValue: 'Location' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...masterCols[1] }}>{t('lnksys_connected', { defaultValue: 'Time Connected' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...colSlot }} align="center">{t('lnksys_slot', { defaultValue: 'Slot' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{t('lnksys_static_tg', { defaultValue: 'Static TG' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_src', { defaultValue: 'Source' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_dst', { defaultValue: 'Destination' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>{renderMasterPeerRows((_, p) => isBridge(p), 'brg')}</TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {Object.keys(peers).length > 0 && (
        <Paper sx={tablePaperSx}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ p: 1.5 }}>
            {t('lnksys_peers', { defaultValue: 'Services (PEERS)' })}
          </Typography>
          <TableContainer>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell sx={{ fontWeight: 600, ...peerCols[0] }}>{t('lnksys_system', { defaultValue: 'Service' })} / {t('lnksys_mode', { defaultValue: 'Mode' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...peerCols[1] }}>{t('lnksys_callsign', { defaultValue: 'Callsign' })} / ID</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...peerCols[2] }}>{t('lnksys_connected', { defaultValue: 'Connected' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600, ...peerCols[3] }}>{t('lnksys_slot', { defaultValue: 'Slot' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_src', { defaultValue: 'Source' })}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="center">{t('lnksys_dst', { defaultValue: 'Destination' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(peers).flatMap(([name, p]) => {
                  const peer = p as PeerEntry;
                  const st = peer.STATS;
                  const ts1 = getTs(peer, 1);
                  const ts2 = getTs(peer, 2);
                  const trx1 = String(ts1.TRX ?? '');
                  const trx2 = String(ts2.TRX ?? '');
                  const chipColor1 = trx1 === 'TX' ? 'success' : trx1 === 'RX' ? 'error' : 'default';
                  const chipColor2 = trx2 === 'TX' ? 'success' : trx2 === 'RX' ? 'error' : 'default';
                  const sub1 = String(ts1.SUB ?? '').replace(/&nbsp;/g, ' ').trim();
                  const sub2 = String(ts2.SUB ?? '').replace(/&nbsp;/g, ' ').trim();
                  const dest1 = String(ts1.DEST ?? '').replace(/&nbsp;/g, ' ').trim();
                  const dest2 = String(ts2.DEST ?? '').replace(/&nbsp;/g, ' ').trim();
                  return [
                    <TableRow key={`svc-${name}-1`} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                      <TableCell rowSpan={2} sx={colService}><Typography fontWeight="bold" noWrap>{name}</Typography><Typography variant="caption" noWrap>{String(peer.MODE ?? '')}</Typography></TableCell>
                      <TableCell sx={colCallsign}><Typography fontWeight="bold" component="span" noWrap><QrzLink callsign={String(peer.CALLSIGN ?? '')}>{String(peer.CALLSIGN ?? '')}</QrzLink></Typography> <Chip size="small" label={String(peer.RADIO_ID ?? '')} /></TableCell>
                      <TableCell rowSpan={2} align="center" sx={{ bgcolor: st?.CONNECTION === 'YES' ? 'success.light' : 'warning.light', whiteSpace: 'nowrap', ...colConnected }}>
                        {String(st?.CONNECTED ?? '—')}
                        {typeof st?.PINGS_SENT === 'number' && <Typography variant="caption" display="block">{st.PINGS_SENT} / {String(st.PINGS_ACKD ?? 0)}</Typography>}
                      </TableCell>
                      <TableCell><Chip size="small" label="TS1" color={chipColor1} /></TableCell>
                      <TableCell align="center">{sub1 ? <Chip size="small" label={sub1} color={chipColor1} /> : ''}</TableCell>
                      <TableCell align="center">{dest1 ? <Chip size="small" label={dest1} color={chipColor1} /> : ''}</TableCell>
                    </TableRow>,
                    <TableRow key={`svc-${name}-2`} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                      <TableCell sx={colCallsign}><Typography variant="caption" noWrap>{String(peer.LOCATION ?? '')}</Typography></TableCell>
                      <TableCell><Chip size="small" label="TS2" color={chipColor2} /></TableCell>
                      <TableCell align="center">{sub2 ? <Chip size="small" label={sub2} color={chipColor2} /> : ''}</TableCell>
                      <TableCell align="center">{dest2 ? <Chip size="small" label={dest2} color={chipColor2} /> : ''}</TableCell>
                    </TableRow>,
                  ];
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

    </Box>
  );
}
