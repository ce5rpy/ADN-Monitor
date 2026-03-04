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

import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useWebSocketGroup } from '../hooks/useWebSocket';

type TgCountRow = {
  tg_num: number;
  name: string;
  qso_count: number;
  qso_time_str: string;
  top_users: string[];
};

type TgCountPayload = { rows?: TgCountRow[] };

export default function TopTg() {
  const { t } = useTranslation();
  const { data } = useWebSocketGroup('tgcount');
  const payload = data as TgCountPayload | null;
  const rows = payload?.rows ?? [];

  return (
    <Box>
      {data == null && (
        <Typography color="text.secondary">{t('pre_wait', { defaultValue: 'Waiting for server info...' })}</Typography>
      )}
      {data != null && rows.length === 0 && (
        <Typography color="text.secondary" sx={{ mt: 2 }}>
          {t('toptg_no_data', { defaultValue: 'No TG count data yet. Data is saved when voice QSOs end (duration > 5s).' })}
        </Typography>
      )}
      {data != null && rows.length > 0 && (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>{t('lh_tgnum')}</TableCell>
                <TableCell>{t('lh_tgname')}</TableCell>
                <TableCell>{t('toptg_qso_count')}</TableCell>
                <TableCell>{t('toptg_time')}</TableCell>
                <TableCell>{t('toptg_top_users')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((r, i) => (
                <TableRow key={i}>
                  <TableCell>{r.tg_num}</TableCell>
                  <TableCell>{r.name}</TableCell>
                  <TableCell>{r.qso_count}</TableCell>
                  <TableCell>{r.qso_time_str}</TableCell>
                  <TableCell>{(r.top_users ?? []).join(', ')}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
