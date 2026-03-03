/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2025  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
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

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Paper, TextField, Button, Typography, Box, Alert } from '@mui/material';
import { useTranslation } from 'react-i18next';

const API_BASE = import.meta.env.VITE_API_BASE || '';

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [callsign, setCallsign] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch(API_BASE + '/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ callsign: callsign.trim(), password }),
        credentials: 'include',
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error || t('sslog_err_failed'));
        return;
      }
      navigate(data.redirect || '/self-service');
    } catch {
      setError(t('sslog_err_network'));
    } finally {
      setLoading(false);
    }
  };

  const tryIpLogin = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await fetch(API_BASE + '/api/auth/login-by-ip', { credentials: 'include' });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error || t('sslog_err_auto'));
        return;
      }
      navigate(data.redirect || '/self-service');
    } catch {
      setError(t('sslog_err_network'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 400, mx: 'auto', py: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box component="img" src="/logo.png" alt="" sx={{ maxWidth: 280, maxHeight: 120, width: 'auto', height: 'auto', objectFit: 'contain', display: 'block', mb: 2 }} />
        <Typography variant="h5" gutterBottom>{t('self_service')}</Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField fullWidth label={t('sslog_call')} value={callsign} onChange={(e) => setCallsign(e.target.value)} required sx={{ mb: 2 }} />
          <TextField fullWidth type="password" label={t('sslog_pass')} value={password} onChange={(e) => setPassword(e.target.value)} required inputProps={{ minLength: 6 }} sx={{ mb: 2 }} />
          <Button type="submit" variant="contained" fullWidth disabled={loading}>{t('sslog_login')}</Button>
        </form>
        <Button fullWidth sx={{ mt: 2 }} onClick={tryIpLogin} disabled={loading}>{t('sslog_login_ip')}</Button>
      </Paper>
    </Box>
  );
}
