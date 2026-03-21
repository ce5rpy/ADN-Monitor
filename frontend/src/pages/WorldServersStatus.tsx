/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Box,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableFooter,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { TableCaptionTitle } from '../components/TableCaptionTitle';
import { useDashboardConfig } from '../context/DashboardConfigContext';

type ServerEntry = {
  name?: string;
  network?: string;
  server?: string;
  port?: number | string;
  password?: string;
  status?: string;
  login_ok?: boolean;
  status_code?: number;
  timestamp?: string;
};

type StatusPayload = {
  servers?: Record<string, ServerEntry>;
  total_checked?: number;
  online_count?: number;
  offline_count?: number;
  start?: string;
  end?: string;
  error?: string;
};

function flagCodeFromNetwork(network: string): string {
  const n = network.trim();
  if (n.length >= 3) return n.slice(0, 3);
  return '';
}

function FlagImg({ code }: { code: string }) {
  const src = code ? `/img/flags/${code}.png` : '/img/flags/world.png';
  return (
    <Box
      component="img"
      src={src}
      alt=""
      sx={{ width: 22, height: 'auto', display: 'block', verticalAlign: 'middle' }}
      onError={(e) => {
        (e.target as HTMLImageElement).src = '/img/flags/world.png';
      }}
    />
  );
}

function statusCodeHint(t: (k: string, o?: Record<string, string>) => string, code: number | undefined): string {
  switch (code) {
    case 1:
      return t('srvrs_err_code_1');
    case 2:
      return t('srvrs_err_code_2');
    case 3:
      return t('srvrs_err_code_3');
    case 4:
      return t('srvrs_err_code_4');
    default:
      return t('srvrs_offline');
  }
}

export default function WorldServersStatus() {
  const { t } = useTranslation();
  const { apiBase } = useDashboardConfig();
  const [data, setData] = useState<StatusPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    const base = (apiBase ?? '').replace(/\/$/, '');
    const url = base ? `${base}/api/servers/status` : '/api/servers/status';
    setError(null);
    fetch(url)
      .then(async (r) => {
        const body = (await r.json().catch(() => ({}))) as StatusPayload & { error?: string };
        if (!r.ok) {
          throw new Error(body?.error || t('srvrs_load_err'));
        }
        if (body?.error) {
          throw new Error(body.error);
        }
        return body;
      })
      .then((payload) => {
        setData(payload);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message || t('srvrs_load_err'));
        setLoading(false);
      });
  }, [apiBase, t]);

  useEffect(() => {
    setLoading(true);
    load();
    const id = window.setInterval(load, 90_000);
    return () => window.clearInterval(id);
  }, [load]);

  const rows = useMemo(() => {
    const srv = data?.servers;
    if (!srv || typeof srv !== 'object') return [];
    return Object.entries(srv)
      .map(([key, entry]) => ({ key, ...entry }))
      .sort((a, b) => {
        const na = String(a.name ?? a.network ?? a.key);
        const nb = String(b.name ?? b.network ?? b.key);
        const c = na.localeCompare(nb);
        if (c !== 0) return c;
        return String(a.network ?? '').localeCompare(String(b.network ?? ''));
      });
  }, [data]);

  const meta = data && !data.error && (data.total_checked != null || data.online_count != null);

  return (
    <Box>
      {loading && !data && (
        <Typography color="text.secondary" sx={{ py: 2 }}>
          {t('srvrs_loading')}
        </Typography>
      )}
      {error && (
        <Typography color="error" sx={{ py: 2 }}>
          {error}
        </Typography>
      )}
      {!error && rows.length > 0 && (
        <Paper sx={{ overflow: 'hidden' }}>
          <TableContainer sx={{ maxWidth: '100%', overflowX: 'auto' }}>
            <Table
              size="small"
              stickyHeader
              sx={{
                width: '100%',
                tableLayout: 'auto',
                '& .MuiTableCell-root': { py: 0.5, px: 0.75, fontSize: '0.8125rem' },
                '& .MuiTableCell-head': { whiteSpace: 'normal', lineHeight: 1.2 },
              }}
            >
              <TableCaptionTitle>{t('srvrs_title')}</TableCaptionTitle>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: 32, maxWidth: 32, p: 0.5 }} aria-label="" />
                  <TableCell sx={{ fontWeight: 600, maxWidth: 100 }}>{t('srvrs_country')}</TableCell>
                  <TableCell sx={{ fontWeight: 600, maxWidth: 88 }}>{t('srvrs_network')}</TableCell>
                  <TableCell sx={{ fontWeight: 600, minWidth: 120 }}>{t('srvrs_host')}</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: 72, maxWidth: 88 }}>{t('srvrs_password')}</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: 52, maxWidth: 56 }}>{t('srvrs_port')}</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 600, width: 76, px: 0.5 }}>{t('srvrs_reachable')}</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 600, width: 72, px: 0.5 }}>{t('srvrs_login')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => {
                  const network = String(row.network ?? row.key ?? '');
                  const host = String(row.server ?? '');
                  const country = String(row.name ?? '');
                  const port = row.port ?? '';
                  const password = String(row.password ?? '');
                  const online = String(row.status ?? '').toLowerCase() === 'online';
                  const loginOk = Boolean(row.login_ok);
                  const code = typeof row.status_code === 'number' ? row.status_code : undefined;
                  const hint = statusCodeHint(t, code);
                  return (
                    <TableRow key={row.key} hover>
                      <TableCell sx={{ p: 0.5, verticalAlign: 'middle' }}>
                        <FlagImg code={flagCodeFromNetwork(network)} />
                      </TableCell>
                      <TableCell
                        sx={{
                          maxWidth: 100,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                        title={country}
                      >
                        {country}
                      </TableCell>
                      <TableCell
                        sx={{
                          maxWidth: 88,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                        title={network}
                      >
                        {network}
                      </TableCell>
                      <TableCell sx={{ wordBreak: 'break-word', overflowWrap: 'anywhere', py: 0.75 }} title={host}>
                        <Typography component="span" variant="body2">
                          {host || '—'}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ maxWidth: 88, overflow: 'hidden' }} title={password}>
                        <Typography
                          component="span"
                          variant="body2"
                          sx={{ fontFamily: 'monospace', fontSize: '0.75rem', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis' }}
                        >
                          {password}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ whiteSpace: 'nowrap' }}>{String(port)}</TableCell>
                      <TableCell align="center" sx={{ px: 0.25 }}>
                        <Chip
                          size="small"
                          label={online ? t('srvrs_online') : t('srvrs_offline')}
                          color={online ? 'success' : 'error'}
                          title={online ? undefined : hint}
                          sx={{ height: 22, '& .MuiChip-label': { px: 0.75, fontSize: '0.7rem' } }}
                        />
                      </TableCell>
                      <TableCell align="center" sx={{ px: 0.25 }}>
                        <Chip
                          size="small"
                          label={loginOk ? t('srvrs_online') : t('srvrs_offline')}
                          color={loginOk ? 'success' : 'error'}
                          title={loginOk ? undefined : hint}
                          sx={{ height: 22, '& .MuiChip-label': { px: 0.75, fontSize: '0.7rem' } }}
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
              {meta && (
                <TableFooter>
                  <TableRow>
                    <TableCell colSpan={8}>
                      <Typography variant="body2" color="text.secondary">
                        {t('srvrs_count', {
                          count: data?.total_checked ?? rows.length,
                          online: data?.online_count ?? '—',
                          offline: data?.offline_count ?? '—',
                        })}
                      </Typography>
                    </TableCell>
                  </TableRow>
                </TableFooter>
              )}
            </Table>
          </TableContainer>
        </Paper>
      )}
      {!loading && !error && rows.length === 0 && data && (
        <Typography color="text.secondary">{t('srvrs_empty')}</Typography>
      )}
    </Box>
  );
}
