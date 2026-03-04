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

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} color="text.primary" sx={{ mb: 2 }}>
        {t('nav_console')}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {t('console_desc')}
        {!connected && ` — ${t('pre_wait')}`}
      </Typography>
      <Paper
        variant="outlined"
        sx={{
          p: 1.5,
          fontFamily: 'monospace',
          fontSize: '0.8rem',
          maxHeight: '70vh',
          overflow: 'auto',
          bgcolor: 'action.hover',
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
