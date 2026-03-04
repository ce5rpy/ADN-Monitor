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
import { Box, Paper, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useWebSocket } from '../hooks/useWebSocket';

export default function Monitor() {
  const { t } = useTranslation();
  const [log, setLog] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useWebSocket({
    groups: ['log'],
    onMessage: (opcode, payload) => {
      if (opcode === 'l') setLog((prev) => [...prev, payload]);
      if (opcode === 'q') setLog((prev) => [...prev, `[Connection] ${payload}`]);
    },
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [log]);

  return (
    <Paper sx={{ p: 2, bgcolor: 'grey.900' }}>
      <Typography variant="h6" sx={{ color: 'primary.light', mb: 1 }}>
        {t('nav_mon')}
      </Typography>
      <Box
        component="pre"
        sx={{
          height: 40 * 16,
          overflow: 'auto',
          fontFamily: 'monospace',
          fontSize: 12,
          color: 'success.light',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
        }}
      >
        {log.length === 0 && t('mon_wait')}
        {log.map((line, i) => (
          <span key={i}>{line}\n</span>
        ))}
        <div ref={bottomRef} />
      </Box>
    </Paper>
  );
}
