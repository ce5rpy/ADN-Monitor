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

import { useEffect, useState, useMemo } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  TextField,
  InputAdornment,
  Box,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useTranslation } from 'react-i18next';
import { useDashboardConfig } from '../context/DashboardConfigContext';
import { TableCaptionTitle } from '../components/TableCaptionTitle';

type TgEntry = { id: string; name: string; countryCode: string };

/** DMR country code from TG id (e.g. 21472 -> 214, 91 -> 91). */
function getCountryCode(tgId: string): string {
  const n = String(tgId).replace(/\D/g, '');
  if (n.length >= 3) return n.slice(0, 3);
  if (n.length >= 2) return n.slice(0, 2);
  return n || '91';
}

function normalizeRows(data: unknown): TgEntry[] {
  if (Array.isArray(data)) {
    return data.map((item: { id?: number; tgid?: number; callsign?: string; name?: string }) => {
      const id = String(item.id ?? item.tgid ?? '');
      const name = String(item.callsign ?? item.name ?? '').trim();
      return { id, name, countryCode: getCountryCode(id) };
    });
  }
  if (data && typeof data === 'object' && 'results' in data && Array.isArray((data as { results: unknown[] }).results)) {
    const arr = (data as { results: { id?: number; tgid?: number; callsign?: string; name?: string }[] }).results;
    return arr.map((item) => {
      const id = String(item.id ?? item.tgid ?? '');
      const name = String(item.callsign ?? item.name ?? '').trim();
      return { id, name, countryCode: getCountryCode(id) };
    });
  }
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    return Object.entries(data as Record<string, string>).map(([id, name]) => ({
      id,
      name: String(name ?? '').trim(),
      countryCode: getCountryCode(id),
    }));
  }
  const text = String(data);
  const lines = text.trim().split(/\r?\n/);
  lines.shift();
  return lines.map((line) => {
    const parts = line.split(/,|\t/);
    const id = (parts[0]?.trim() ?? '').replace(/^"|"$/g, '');
    const name = (parts[1]?.trim() ?? '').replace(/^"|"$/g, '');
    return { id, name, countryCode: getCountryCode(id) };
  });
}

function FlagImg({ countryCode }: { countryCode: string }) {
  const [err, setErr] = useState(false);
  const src = err || !countryCode ? '/img/flags/world.png' : `/img/flags/${countryCode}.png`;
  return (
    <img
      src={src}
      alt=""
      onError={() => setErr(true)}
      style={{ width: 24, height: 16, objectFit: 'contain', verticalAlign: 'middle' }}
      loading="lazy"
    />
  );
}

export default function TgList() {
  const { t } = useTranslation();
  const { apiBase } = useDashboardConfig();
  const [rows, setRows] = useState<TgEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchTg, setSearchTg] = useState('');
  const [searchName, setSearchName] = useState('');

  useEffect(() => {
    setError(null);
    const base = (apiBase ?? '').replace(/\/$/, '');
    const url = base ? `${base}/api/aliases/tg-list` : '/api/aliases/tg-list';
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
        const ct = r.headers.get('content-type') ?? '';
        if (ct.includes('application/json')) return r.json() as Promise<unknown>;
        return r.text();
      })
      .then((data: unknown) => {
        const out = normalizeRows(data);
        out.sort((a, b) => {
          const cc = a.countryCode.localeCompare(b.countryCode);
          if (cc !== 0) return cc;
          return Number(a.id) - Number(b.id) || a.id.localeCompare(b.id);
        });
        setRows(out);
      })
      .catch((e) => setError(e instanceof Error ? e.message : t('tbl_load_err')));
  }, [apiBase, t]);

  const filtered = useMemo(() => {
    const tgQ = searchTg.trim();
    const nameQ = searchName.trim().toLowerCase();
    if (!tgQ && !nameQ) return rows;
    return rows.filter((r) => {
      if (tgQ && !r.id.includes(tgQ)) return false;
      if (nameQ && !r.name.toLowerCase().includes(nameQ)) return false;
      return true;
    });
  }, [rows, searchTg, searchName]);

  const byCountry = useMemo(() => {
    const map = new Map<string, TgEntry[]>();
    for (const r of filtered) {
      const list = map.get(r.countryCode) ?? [];
      list.push(r);
      map.set(r.countryCode, list);
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }));
  }, [filtered]);

  if (error) return <Typography color="error">{error}</Typography>;

  const tablePaperSx = {
    overflow: 'auto' as const,
    boxShadow: (t: { palette: { mode: string } }) => (t.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)'),
  };

  return (
    <Box>
      <Paper
        variant="outlined"
        sx={{
          p: 2,
          mb: 2,
          bgcolor: 'background.paper',
          boxShadow: (t: { palette: { mode: string } }) => (t.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)'),
        }}
      >
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          <TextField
            size="small"
            label={t('tbl_filter_tg', { defaultValue: 'Filter by TG' })}
          placeholder={t('tbl_placeholder_tg', { defaultValue: 'e.g. 730' })}
          value={searchTg}
          onChange={(e) => setSearchTg(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 180 }}
          helperText={t('tbl_filter_tg_hint', { defaultValue: 'Shows all TGs whose number contains this (e.g. 730 = Chile)' })}
        />
        <TextField
          size="small"
          label={t('tbl_filter_name', { defaultValue: 'Filter by name' })}
          placeholder={t('tbl_placeholder_name', { defaultValue: 'e.g. Chile' })}
          value={searchName}
          onChange={(e) => setSearchName(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 180 }}
          helperText={t('tbl_filter_name_hint', { defaultValue: 'Shows TGs whose name contains this text' })}
        />
        </Box>
      </Paper>

      <Paper sx={tablePaperSx}>
        <TableContainer>
          <Table size="small" stickyHeader>
            <TableCaptionTitle>{t('tbl_tgs', { defaultValue: 'World Wide Talk Groups' })}</TableCaptionTitle>
            <TableHead>
              <TableRow sx={{ bgcolor: 'action.hover' }}>
                <TableCell sx={{ minWidth: 140, fontWeight: 600 }}>{t('tbl_country', { defaultValue: 'Country' })}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_tgnum', { defaultValue: 'TG#' })}</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>{t('lh_tgname', { defaultValue: 'Name' })}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {byCountry.flatMap(([countryCode, list]) =>
                list.map((r) => (
                  <TableRow key={`${r.countryCode}-${r.id}`} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                    <TableCell sx={{ minWidth: 140, py: 0.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <FlagImg countryCode={countryCode} />
                        <Typography component="span" variant="body2">
                          {list[0]?.name ?? countryCode}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{r.id}</TableCell>
                    <TableCell>{r.name}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <Typography variant="body2" color="text.secondary" sx={{ p: 1.5 }}>
          {t('tbl_count_tg', { defaultValue: 'Number of TalkGroups' })}: {filtered.length}
          {(searchTg.trim() || searchName.trim()) && filtered.length !== rows.length && ` (${rows.length} ${t('tbl_total', { defaultValue: 'total' })})`}
        </Typography>
      </Paper>
    </Box>
  );
}
