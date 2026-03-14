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
          minHeight: 120,
          maxHeight: '60vh',
          overflow: 'auto',
          fontFamily: 'monospace',
          fontSize: { xs: 11, sm: 12 },
          color: 'success.light',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
          WebkitOverflowScrolling: 'touch',
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
