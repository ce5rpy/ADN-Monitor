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

import { useState, useCallback } from 'react';
import {
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableRow,
  TableCell,
  IconButton,
  Box,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useTranslation } from 'react-i18next';

function buildOptions(p: {
  ts1: number[];
  ts2: number[];
  dial: number;
  voice: string;
  lang: string;
  single: string;
  timer: number;
  mode: string;
}): string {
  const parts: string[] = [];
  // Duplex: TS1 and TS2 always (both slots)
  if (p.mode === 'Duplex' && p.ts1.length > 0) parts.push('TS1=' + p.ts1.join(','));
  if (p.mode === 'Duplex' && p.ts2.length > 0) parts.push('TS2=' + p.ts2.join(','));
  // Simplex: single slot is always TS2 (we use ts2 state for it)
  if (p.mode === 'Simplex' && p.ts2.length > 0) parts.push('TS2=' + p.ts2.join(','));
  parts.push('DIAL=' + (p.dial ? 1 : 0));
  if (p.voice !== '-1') parts.push('VOICE=' + p.voice);
  if (p.voice === '1') parts.push('LANG=' + p.lang);
  if (p.single !== '-1') parts.push('SINGLE=' + p.single);
  if (p.timer > 0) parts.push('TIMER=' + p.timer);
  return parts.join(';');
}

export default function Calc() {
  const { t } = useTranslation();
  const [mode, setMode] = useState<'Duplex' | 'Simplex'>('Duplex');
  const [ts1, setTs1] = useState<number[]>([0]);
  const [ts2, setTs2] = useState<number[]>([0]);
  const [dial, setDial] = useState(0); // 0 or 1
  const [voice, setVoice] = useState('-1');
  const [lang] = useState('en_GB');
  const [single, setSingle] = useState('-1');
  const [timer, setTimer] = useState(0);

  const optionsStr = buildOptions({ ts1, ts2, dial, voice, lang, single, timer, mode });
  const withQuotes = `Options="${optionsStr}"`;

  const addRow = useCallback((slot: 1 | 2) => {
    if (slot === 1) setTs1((p) => [...p, 0]);
    else setTs2((p) => [...p, 0]);
  }, []);
  const removeRow = useCallback((slot: 1 | 2, index: number) => {
    if (slot === 1) setTs1((p) => p.filter((_, i) => i !== index));
    else setTs2((p) => p.filter((_, i) => i !== index));
  }, []);
  const setSlotValue = useCallback((slot: 1 | 2, index: number, value: number) => {
    if (slot === 1) setTs1((p) => p.map((v, i) => (i === index ? value : v)));
    else setTs2((p) => p.map((v, i) => (i === index ? value : v)));
  }, []);

  const copy = (text: string) => navigator.clipboard.writeText(text);

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>{t('clc_title')}</Typography>
      <FormControl size="small" sx={{ minWidth: 120, mb: 2 }}>
        <InputLabel>{t('calc_type')}</InputLabel>
        <Select value={mode} label={t('calc_type')} onChange={(e) => setMode(e.target.value as 'Duplex' | 'Simplex')}>
          <MenuItem value="Duplex">Duplex</MenuItem>
          <MenuItem value="Simplex">Simplex</MenuItem>
        </Select>
      </FormControl>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        {mode === 'Duplex' && (
          <Box>
            <Typography variant="subtitle2">{t('calc_ts1')}</Typography>
            <Table size="small">
              <TableBody>
                {ts1.map((v, i) => (
                  <TableRow key={i}>
                    <TableCell>TG {i + 1}</TableCell>
                    <TableCell>
                      <TextField type="number" size="small" value={v} onChange={(e) => setSlotValue(1, i, Number(e.target.value) || 0)} inputProps={{ min: 0 }} />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => removeRow(1, i)}><DeleteIcon /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Button startIcon={<AddIcon />} onClick={() => addRow(1)} size="small">{t('calc_addts1')}</Button>
          </Box>
        )}
        <Box>
          <Typography variant="subtitle2">{t('calc_ts2')}</Typography>
          <Table size="small">
            <TableBody>
              {ts2.map((v, i) => (
                <TableRow key={i}>
                  <TableCell>TG {i + 1}</TableCell>
                  <TableCell>
                    <TextField type="number" size="small" value={v} onChange={(e) => setSlotValue(2, i, Number(e.target.value) || 0)} inputProps={{ min: 0 }} />
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => removeRow(2, i)}><DeleteIcon /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Button startIcon={<AddIcon />} onClick={() => addRow(2)} size="small">{t('calc_addts2')}</Button>
        </Box>
      </Box>
      <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 2 }}>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>{t('calc_dialtg')}</InputLabel>
          <Select value={String(dial)} label={t('calc_dialtg')} onChange={(e) => setDial(Number(e.target.value))}>
            <MenuItem value="0">{t('calc_voiceoff')}</MenuItem>
            <MenuItem value="1">{t('calc_voiceon')}</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>{t('calc_voice')}</InputLabel>
          <Select value={voice} label={t('calc_voice')} onChange={(e) => setVoice(e.target.value)}>
            <MenuItem value="-1">{t('calc_voicesrv')}</MenuItem>
            <MenuItem value="0">{t('calc_voiceoff')}</MenuItem>
            <MenuItem value="1">{t('calc_voiceon')}</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>{t('calc_smode')}</InputLabel>
          <Select value={single} label={t('calc_smode')} onChange={(e) => setSingle(e.target.value)}>
            <MenuItem value="-1">{t('calc_smodesrv')}</MenuItem>
            <MenuItem value="0">{t('calc_smodeoff')}</MenuItem>
            <MenuItem value="1">{t('calc_smodeon')}</MenuItem>
          </Select>
        </FormControl>
        <TextField label={t('calc_tgto')} type="number" value={timer} onChange={(e) => setTimer(Number(e.target.value) || 0)} size="small" />
      </Box>
      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2">{t('calc_dmrgw')}</Typography>
        <TextField fullWidth multiline value={withQuotes} inputProps={{ readOnly: true }} size="small" sx={{ mt: 0.5 }} />
        <Button sx={{ mt: 1 }} onClick={() => copy(withQuotes)}>{t('calc_copy1')}</Button>
      </Box>
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2">{t('calc_dmropt')}</Typography>
        <TextField fullWidth multiline value={optionsStr} inputProps={{ readOnly: true }} size="small" sx={{ mt: 0.5 }} />
        <Button sx={{ mt: 1 }} onClick={() => copy(optionsStr)}>{t('calc_copy2')}</Button>
      </Box>
    </Paper>
  );
}
