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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useWebSocketGroup } from '../hooks/useWebSocket';
import QrzLink from '../components/QrzLink';
import ActiveQsoBox, { type Ctable } from '../components/ActiveQsoBox';

type LastHeardRow = {
  date: string;
  qso_time: number | string;
  qso_type: string;
  system: string;
  tg_num: number;
  tg_callsign: string;
  dmr_id: number;
  subscriber: string[];
};

type MainPayload = { ctable?: Ctable };
type LogPayload = { rows?: LastHeardRow[] };

function getCountryCodeFromId(id: number): string {
  const n = String(id).replace(/\D/g, '');
  if (n.length >= 3) return n.slice(0, 3);
  if (n.length >= 2) return n.slice(0, 2);
  return n || '';
}

function getCountryCode(tgNum: number): string {
  return getCountryCodeFromId(tgNum);
}

const PROTOCOL_ICONS = ['allstar', 'dstar', 'echolink', 'm17', 'nxdn', 'tetra', 'xlx', 'yaesu'] as const;

function protocolIconsFromText(text: string): string[] {
  const s = (text || '').toLowerCase();
  return PROTOCOL_ICONS.filter((name) => s.includes(name));
}

function FlagImg({ code, fallback = 'world' }: { code: string; fallback?: string }) {
  const src = code ? `/img/flags/${code}.png` : `/img/flags/${fallback}.png`;
  return (
    <Box
      component="img"
      src={src}
      alt=""
      onError={(e) => { (e.target as HTMLImageElement).src = `/img/flags/world.png`; }}
      sx={{ width: 20, height: 14, objectFit: 'contain', flexShrink: 0 }}
    />
  );
}

function ProtocolIcon({ name }: { name: string }) {
  return (
    <Box
      component="img"
      src={`/img/bridges/${name}.png`}
      alt={name}
      sx={{ width: 18, height: 18, objectFit: 'contain', ml: 0.25 }}
    />
  );
}

const tablePaperSx = {
  mt: 0,
  overflow: 'hidden' as const,
  boxShadow: (theme: { palette: { mode: string } }) => (theme.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)'),
};

export default function LastHeardLog() {
  const { t } = useTranslation();
  const { data: mainData } = useWebSocketGroup('main');
  const { data: logData } = useWebSocketGroup('lsthrd_log');
  const mainPayload = mainData as MainPayload | null;
  const logPayload = logData as LogPayload | null;
  const logRows = logPayload?.rows ?? [];
  const ctable = mainPayload?.ctable;
  const hasAnyData = mainData != null || logData != null;

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} color="text.primary" sx={{ mb: 2 }}>
        {t('nav_lsthrd', { defaultValue: 'Last Heard Log' })}
      </Typography>
      {!hasAnyData && (
        <Typography color="text.secondary" sx={{ py: 2 }}>{t('pre_wait')}</Typography>
      )}
      {mainData != null && <ActiveQsoBox ctable={ctable ?? undefined} />}
      {logRows.length > 0 && (
        <TableContainer component={Paper} sx={tablePaperSx}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow sx={{ bgcolor: 'action.hover' }}>
                <TableCell sx={{ fontWeight: 600, whiteSpace: 'nowrap' }}>{t('lh_date')}</TableCell>
                <TableCell sx={{ fontWeight: 600, whiteSpace: 'nowrap' }}>{t('lh_time')}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_callsignid')}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_name', { defaultValue: 'Name' })}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_tgnum')}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_tgname')}</TableCell>
                <TableCell sx={{ fontWeight: 600, whiteSpace: 'nowrap' }}>{t('lh_duration')}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_system')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logRows.map((r, i) => {
                const dateStr = String(r.date ?? '');
                const [datePart, timePart] = dateStr.includes(' ') ? dateStr.split(' ', 2) : [r.date ?? '', ''];
                const durationSec = r.qso_time != null && r.qso_time !== '' ? Math.round(Number(r.qso_time)) : null;
                const isBridge = r.subscriber?.[0]?.toUpperCase() === 'BRIDGE';
                const callFlagCode = getCountryCodeFromId(r.dmr_id);
                const tgFlagCode = getCountryCode(r.tg_num);
                const protocolIcons = protocolIconsFromText(`${r.tg_callsign} ${r.system}`);
                return (
                <TableRow key={i} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                  <TableCell sx={{ width: 105, minWidth: 105, whiteSpace: 'nowrap' }}>{datePart}</TableCell>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>{timePart}</TableCell>
                  <TableCell sx={{ minWidth: 220 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'nowrap' }}>
                      <FlagImg code={callFlagCode} />
                      {isBridge ? (
                        <Typography component="span" variant="body2" fontWeight={600}>Bridge</Typography>
                      ) : r.subscriber?.length ? (
                        <QrzLink callsign={r.subscriber[0]}>
                          <Typography component="span" fontWeight={600}>{r.subscriber[0]}</Typography>
                        </QrzLink>
                      ) : null}
                      <Chip
                        label={r.dmr_id}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem', fontWeight: 500 }}
                        variant="outlined"
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography component="span" variant="body2" fontWeight={600}>
                      {r.subscriber?.[1] ?? '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography component="span" variant="body2" fontWeight={600}>
                      {r.tg_num}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25, flexWrap: 'wrap' }}>
                      <FlagImg code={tgFlagCode} />
                      <Typography component="span" variant="body2" fontWeight={600}>
                        {r.tg_callsign || '—'}
                      </Typography>
                      {protocolIcons.map((name) => (
                        <ProtocolIcon key={name} name={name} />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell sx={{ width: 60 }}>{durationSec != null ? durationSec : '—'}</TableCell>
                  <TableCell>{r.system ?? '—'}</TableCell>
                </TableRow>
              );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
