/*
 * ADN Monitor - Static + dynamic (UA) TG chips for Linked Systems.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

import { Box, Chip } from '@mui/material';
import type { Theme } from '@mui/material/styles';
import type { TFunction } from 'i18next';
import type { ReactNode } from 'react';

/** Keep TG digits on one line; wrap whole chips, not labels inside a chip. */
const tgChipSx = {
  flexShrink: 0,
  maxWidth: 'none',
  width: 'auto',
  '& .MuiChip-label': {
    whiteSpace: 'nowrap',
    overflow: 'visible',
    textOverflow: 'clip',
    lineHeight: 1.25,
    px: 0.75,
  },
} as const;

function mergeTgChipSx(...parts: Record<string, unknown>[]) {
  return parts.reduce((acc, part) => ({ ...acc, ...part }), { ...tgChipSx });
}

function highlightRingSx(theme: Theme, isActive: boolean, trx: string, base: Record<string, unknown>) {
  if (!isActive || (trx !== 'TX' && trx !== 'RX')) {
    return base;
  }
  const accent = trx === 'TX' ? theme.palette.success.main : theme.palette.error.main;
  return { ...base, boxShadow: `0 0 0 2px ${accent}` };
}

/** UA / dial-pad TG (not in static list); shows timeout until bridge expires. */
function dynamicTgChipSx(theme: Theme, isActive: boolean, trx: string) {
  const isDark = theme.palette.mode === 'dark';
  const base = {
    mr: 0.25,
    mb: 0.25,
    fontWeight: 500,
    bgcolor: isDark ? 'rgba(129, 140, 248, 0.24)' : 'rgba(99, 102, 241, 0.14)',
    color: isDark ? '#c7d2fe' : '#4338ca',
    border: '1px solid',
    borderColor: isDark ? 'rgba(129, 140, 248, 0.45)' : 'rgba(99, 102, 241, 0.35)',
  };
  return highlightRingSx(theme, isActive, trx, base);
}

export type UaTgEntry = { TGID?: string | number; TO?: string };

export type TgChipGroupProps = {
  staticTgs: string[];
  /** SINGLE=1: one active UA TG (static amber or dynamic indigo). */
  singleTg?: string;
  singleTo?: string;
  /** SINGLE=0: multiple dynamic indigo chips until TG 4000. */
  multiTgs?: UaTgEntry[];
  trx: string;
  activeTg: string;
  t: TFunction;
};

/** Static TG chips plus UA highlights (SINGLE vs multi-dynamic). */
export function TgChipGroup({
  staticTgs,
  singleTg = '',
  singleTo,
  multiTgs = [],
  trx,
  activeTg,
  t,
}: TgChipGroupProps): ReactNode {
  const nodes: ReactNode[] = [];
  const single = singleTg.trim();
  const multi = multiTgs.filter((e) => String(e.TGID ?? '').trim());

  staticTgs.forEach((tg) => {
    const tgStr = String(tg);
    const isLive = trx === 'RX' || trx === 'TX';
    const isActive = isLive && tgStr === activeTg;
    const isUaOnStatic = single === tgStr;
    if (isUaOnStatic) {
      const title = singleTo?.trim()
        ? t('lnksys_active_tg_to', {
            tg: tgStr,
            to: singleTo.trim(),
            defaultValue: `Active TG ${tgStr} · timeout ${singleTo.trim()}`,
          })
        : t('lnksys_active_tg', {
            tg: tgStr,
            defaultValue: `Active TG ${tgStr}`,
          });
      nodes.push(
        <Chip
          key={`s-${tg}`}
          size="small"
          label={tg}
          title={title}
          sx={(theme) => mergeTgChipSx(dynamicTgChipSx(theme, isActive, trx))}
        />
      );
      return;
    }
    nodes.push(
      <Chip
        key={`s-${tg}`}
        size="small"
        label={tg}
        color={isActive ? (trx === 'TX' ? 'success' : 'error') : 'default'}
        sx={mergeTgChipSx({ mr: 0.25, mb: 0.25 })}
      />
    );
  });

  if (single && !staticTgs.includes(single)) {
    const isActive = (trx === 'RX' || trx === 'TX') && single === activeTg;
    const title = singleTo?.trim()
      ? t('lnksys_dynamic_tg_to', {
          tg: single,
          to: singleTo.trim(),
          defaultValue: `Dynamic TG ${single} · timeout ${singleTo}`,
        })
      : t('lnksys_dynamic_tg', { tg: single, defaultValue: `Dynamic TG ${single}` });
    nodes.push(
      <Chip
        key={`d-${single}`}
        size="small"
        label={single}
        title={title}
        sx={(theme) => mergeTgChipSx(dynamicTgChipSx(theme, isActive, trx))}
      />
    );
  }

  multi.forEach((ent) => {
    const tg = String(ent.TGID ?? '').trim();
    if (!tg || staticTgs.includes(tg)) {
      return;
    }
    const isActive = (trx === 'RX' || trx === 'TX') && tg === activeTg;
    const to = String(ent.TO ?? '').trim();
    const title = to
      ? t('lnksys_dynamic_tg_to', { tg, to, defaultValue: `Dynamic TG ${tg} · timeout ${to}` })
      : t('lnksys_dynamic_tg', { tg, defaultValue: `Dynamic TG ${tg}` });
    nodes.push(
      <Chip
        key={`m-${tg}`}
        size="small"
        label={tg}
        title={title}
        sx={(theme) => mergeTgChipSx(dynamicTgChipSx(theme, isActive, trx))}
      />
    );
  });

  if (nodes.length === 0) {
    return null;
  }
  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 0.25 }}>
      {nodes}
    </Box>
  );
}
