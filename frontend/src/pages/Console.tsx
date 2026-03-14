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

import { useEffect, useRef, useState } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useWebSocket } from '../hooks/useWebSocket';

/** Max log lines to keep in memory (tail). */
const MAX_LINES = 500;

/** Page that shows GROUP VOICE START/END messages from the monitor WebSocket log group. */
export default function Console() {
  const { t } = useTranslation();
  const [lines, setLines] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { connected } = useWebSocket({
    groups: ['log'],
    onMessage: (opcode, payload) => {
      if (opcode === 'l' && payload) {
        setLines((prev) => {
          const next = [...prev, payload].slice(-MAX_LINES);
          return next;
        });
      }
    },
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [lines]);

  const paperSx = {
    bgcolor: 'background.paper',
    boxShadow: (theme: { palette: { mode: string } }) =>
      theme.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)',
  };

  return (
    <Box>
      <Paper
        variant="outlined"
        sx={{
          ...paperSx,
          p: 2,
          mb: 2,
        }}
      >
        <Typography variant="h5" fontWeight={700} color="text.primary" sx={{ mb: 1 }}>
          {t('nav_console')}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t('console_desc')}
          {!connected && ` — ${t('pre_wait')}`}
        </Typography>
      </Paper>
      <Paper
        variant="outlined"
        sx={{
          ...paperSx,
          p: 1.5,
          fontFamily: 'monospace',
          fontSize: { xs: '0.75rem', sm: '0.8rem' },
          minHeight: 120,
          maxHeight: '60vh',
          overflow: 'auto',
          WebkitOverflowScrolling: 'touch',
        }}
      >
        {lines.length === 0 && (
          <Typography color="text.secondary" component="span">
            {connected ? t('console_empty') : t('pre_wait')}
          </Typography>
        )}
        {lines.map((line, i) => (
          <Box key={i} component="div" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {line}
          </Box>
        ))}
        <div ref={bottomRef} />
      </Paper>
    </Box>
  );
}
