/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2025  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
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
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_date')}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_duration', { defaultValue: 'Duration (s)' })}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_callsignid')}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_tgname')}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_tgnum')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logRows.map((r, i) => (
                <TableRow key={i} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                  <TableCell>{r.date}</TableCell>
                  <TableCell>
                    {r.qso_time != null && r.qso_time !== ''
                      ? Math.round(Number(r.qso_time))
                      : '—'}
                  </TableCell>
                  <TableCell>
                    {r.subscriber?.length ? (
                      <QrzLink callsign={r.subscriber[0]}>{r.subscriber[0]} ({r.dmr_id})</QrzLink>
                    ) : (
                      r.dmr_id
                    )}
                  </TableCell>
                  <TableCell>{r.tg_callsign}</TableCell>
                  <TableCell>{r.tg_num}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
