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

import { useEffect, useState } from 'react';
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useDashboardConfig } from '../context/DashboardConfigContext';

type BridgeRow = [string, string, string];

export default function BridgeList() {
  const { t } = useTranslation();
  const { apiBase } = useDashboardConfig();
  const [rows, setRows] = useState<BridgeRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    const base = (apiBase ?? '').replace(/\/$/, '');
    const url = base ? `${base}/api/aliases/bridge-list` : '/api/aliases/bridge-list';
    fetch(url)
      .then(async (r) => {
        if (!r.ok) {
          const errBody = await r.text();
          let msg = t('tbl_load_err', { defaultValue: 'Error loading data' });
          try {
            const j = JSON.parse(errBody) as { error?: string };
            if (j?.error) msg = j.error;
          } catch {
            // ignore
          }
          throw new Error(msg);
        }
        return r.text();
      })
      .then((text) => {
        const lines = text.trim().split(/\r?\n/);
        const sep = lines[0]?.includes('\t') ? '\t' : ',';
        lines.shift();
        const data: BridgeRow[] = lines.map((line) => {
          const parts = line.split(sep);
          return [parts[0]?.trim() ?? '', parts[1]?.trim() ?? '', parts[2]?.trim() ?? ''];
        });
        data.sort((a, b) => a[0].localeCompare(b[0]));
        setRows(data);
      })
      .catch((e) => setError(e instanceof Error ? e.message : t('tbl_load_err')));
  }, [apiBase, t]);

  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Paper sx={{ overflow: 'auto' }}>
      <Typography variant="h6" sx={{ p: 2 }}>{t('tbl_bridges')}</Typography>
      <TableContainer>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>{t('lh_tgnum', { defaultValue: 'TG#' })}</TableCell>
              <TableCell>{t('lh_tgname', { defaultValue: 'Name' })}</TableCell>
              <TableCell>{t('lh_system', { defaultValue: 'Country' })}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map(([country, col1, col2], i) => (
              <TableRow key={i}>
                <TableCell>{col1}</TableCell>
                <TableCell>{col2}</TableCell>
                <TableCell>{t(`country.${country}`, { defaultValue: country })}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>{t('tbl_count_bridges')}: {rows.length}</Typography>
    </Paper>
  );
}
