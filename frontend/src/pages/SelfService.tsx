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

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Box,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useTranslation } from 'react-i18next';
import Calc from './Calc';

const API_BASE = import.meta.env.VITE_API_BASE || '';

interface DeviceOptions {
  TS1: string[];
  TS2: string[];
  DIAL: string;
  VOICE: string;
  LANG: string;
  SINGLE: string;
  TIMER: string;
}

function optionsToStr(d: { options: DeviceOptions }): string {
  const o = d.options;
  const s = [
    o.TS1?.length ? 'TS1=' + o.TS1.join(',') : '',
    o.TS2?.length ? 'TS2=' + o.TS2.join(',') : '',
    o.VOICE !== '-1' ? 'VOICE=' + o.VOICE : '',
    o.LANG !== '0' ? 'LANG=' + o.LANG : '',
    o.SINGLE !== '-1' ? 'SINGLE=' + o.SINGLE : '',
    o.TIMER !== '0' ? 'TIMER=' + o.TIMER : '',
  ]
    .filter(Boolean)
    .join(';');
  return s ? s + ';' : s;
}

export default function SelfService() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [user, setUser] = useState<{ callsign: string; int_ids: number[]; selected_int_id: number | null } | null>(null);
  const [device, setDevice] = useState<{ int_id: number; options: DeviceOptions; mode: number } | null>(null);
  const [optionsStr, setOptionsStr] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [calcOpen, setCalcOpen] = useState(false);

  useEffect(() => {
    fetch(API_BASE + '/api/auth/me', { credentials: 'include' })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setUser)
      .catch(() => navigate('/login'));
  }, [navigate]);

  useEffect(() => {
    if (!user?.selected_int_id) return;
    setError('');
    setSuccess('');
    fetch(API_BASE + '/api/self-service/device?int_id=' + user.selected_int_id, { credentials: 'include' })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setDevice(d);
        setOptionsStr(optionsToStr(d));
      })
      .catch(() => setError(t('ss_err_device')));
  }, [user?.selected_int_id, t]);

  const handleSelectDevice = (intId: number) => {
    fetch(API_BASE + '/api/self-service/device/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ int_id: intId }),
      credentials: 'include',
    }).then(() => setUser((u) => (u ? { ...u, selected_int_id: intId } : null)));
  };

  const handleSave = () => {
    if (!user?.selected_int_id) return;
    setError('');
    setSuccess('');
    setSaving(true);
    fetch(API_BASE + '/api/self-service/device/options', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ int_id: user.selected_int_id, options: optionsStr }),
      credentials: 'include',
    })
      .then(async (r) => {
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data.error || 'Update failed');
        setSuccess(t('calc_saved', { defaultValue: 'Saved.' }));
      })
      .catch((e) => setError(e.message || 'Network error'))
      .finally(() => setSaving(false));
  };

  const handleLogout = () => {
    fetch(API_BASE + '/api/auth/logout', { method: 'POST', credentials: 'include' }).then(() => navigate('/login'));
  };

  if (!user) return null;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          {user.callsign}
          {user.selected_int_id != null && ` (${user.selected_int_id})`}
        </Typography>
        <Button onClick={handleLogout}>{t('calc_lout')}</Button>
      </Box>

      {user.int_ids.length > 1 && (
        <FormControl size="small" sx={{ minWidth: 120, mb: 2 }}>
          <InputLabel>{t('calc_dev')}</InputLabel>
          <Select
            value={user.selected_int_id ?? ''}
            label={t('calc_dev')}
            onChange={(e) => handleSelectDevice(Number(e.target.value))}
          >
            {user.int_ids.map((id) => (
              <MenuItem key={id} value={id}>
                {id}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {device && (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 2 }}>
            {t('ss_calc_hint')}{' '}
            <Button variant="text" size="small" onClick={() => setCalcOpen(true)} sx={{ fontWeight: 600, p: 0, minWidth: 'auto', textTransform: 'none', verticalAlign: 'baseline' }}>
              {t('nav_calc')}
            </Button>
          </Typography>
          <Dialog open={calcOpen} onClose={() => setCalcOpen(false)} maxWidth="lg" fullWidth scroll="paper">
            <DialogTitle sx={{ py: 0.5, px: 1, display: 'flex', justifyContent: 'flex-end' }}>
              <IconButton aria-label="close" onClick={() => setCalcOpen(false)} size="small">
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent sx={{ p: 0, overflow: 'auto' }}>
              <Calc />
            </DialogContent>
          </Dialog>
          <TextField
            fullWidth
            label={t('ss_options')}
            value={optionsStr}
            onChange={(e) => setOptionsStr(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={handleSave} disabled={saving}>
            {saving ? t('calc_saving', { defaultValue: 'Saving...' }) : t('calc_save')}
          </Button>
        </>
      )}
    </Paper>
  );
}
