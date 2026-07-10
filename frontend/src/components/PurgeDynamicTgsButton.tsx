/*
 * ADN Monitor - Self-service: queue TG 4000-equivalent dynamic TG purge.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

import { useState } from 'react';
import { Button, Typography } from '@mui/material';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import { useTranslation } from 'react-i18next';

const API_BASE = import.meta.env.VITE_API_BASE || '';

type Props = {
  intId: number;
  disabled?: boolean;
  onSuccess?: (message: string) => void;
  onError?: (message: string) => void;
};

export default function PurgeDynamicTgsButton({ intId, disabled = false, onSuccess, onError }: Props) {
  const { t } = useTranslation();
  const [busy, setBusy] = useState(false);

  const handleClick = async () => {
    const ok = window.confirm(
      t('ss_purge_dynamic_confirm', {
        defaultValue: 'Remove user-activated TGs for this hotspot? (equivalent to keying TG 4000)',
      })
    );
    if (!ok) return;
    setBusy(true);
    try {
      const res = await fetch(
        `${API_BASE}/api/self-service/devices/${encodeURIComponent(String(intId))}/request-dynamic-reload`,
        {
          method: 'POST',
          credentials: 'include',
        }
      );
      const data = (await res.json().catch(() => ({}))) as { error?: string };
      if (!res.ok) {
        onError?.(String(data.error || res.statusText));
        return;
      }
      onSuccess?.(
        t('ss_purge_dynamic_ok', {
          defaultValue: 'Reload in progress — dynamic TGs will clear within about 10 seconds.',
        })
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2, mb: 1 }}>
        {t('ss_purge_dynamic_hint', {
          defaultValue: 'Clears user-activated talkgroups (same as transmitting to TG 4000).',
        })}
      </Typography>
      <Button
        variant="outlined"
        color="warning"
        startIcon={<DeleteSweepIcon />}
        disabled={disabled || busy}
        onClick={handleClick}
      >
        {t('ss_purge_dynamic', { defaultValue: 'Remove dynamic TGs' })}
      </Button>
    </>
  );
}
