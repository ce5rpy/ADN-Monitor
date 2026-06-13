/*
 * ADN Monitor - Linked Systems card layout for narrow viewports.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

import type { ReactNode } from 'react';
import { Box, Card, CardContent, Chip, Divider, Stack, Typography } from '@mui/material';
import type { TFunction } from 'i18next';
import QrzLink from './QrzLink';
import { ConnectedTime, masterPeerKey, servicePeerKey } from '../context/LiveConnectedContext';
import { TgChipGroup, type UaTgEntry } from './TgChipGroup';

type TsEntry = { TS?: boolean | string; TRX?: string; SUB?: string; DEST?: string };
type SingleTs = { TGID?: number | string; TO?: string };
export type PeerEntry = Record<string, unknown> & {
  CALLSIGN?: string;
  CONNECTED?: string;
  LOCATION?: string;
  MODE?: string;
  RADIO_ID?: string;
  1?: TsEntry;
  2?: TsEntry;
  STATS?: {
    CONNECTION?: string;
    CONNECTED?: string;
    PINGS_SENT?: number;
    PINGS_ACKD?: number;
  };
  SINGLE_TS1?: SingleTs;
  SINGLE_TS2?: SingleTs;
  UA_MULTI_TS1?: SingleTs[];
  UA_MULTI_TS2?: SingleTs[];
  SINGLE_MODE?: boolean;
  TS1_STATIC?: string[];
  TS2_STATIC?: string[];
};

type Ctable = {
  MASTERS?: Record<string, { PEERS?: Record<string, PeerEntry> }>;
  PEERS?: Record<string, PeerEntry>;
};

function getTs(peer: PeerEntry, ts: 1 | 2): TsEntry {
  const t = peer[ts] ?? (peer as Record<string, unknown>)[String(ts)];
  return (t as TsEntry) ?? {};
}

function activeTgFromDest(dest: string | undefined): string {
  if (!dest) return '';
  const s = String(dest).replace(/&nbsp;/g, ' ').trim();
  const m = s.match(/\d+/);
  return m ? m[0] : '';
}

function trxChipColor(trx: string): 'success' | 'error' | 'default' {
  if (trx === 'TX') return 'success';
  if (trx === 'RX') return 'error';
  return 'default';
}

/** Fixed min height so empty TG/src/dst rows do not reflow the card list. */
const slotValueSx = {
  mt: 0.25,
  minHeight: 24,
  display: 'flex',
  alignItems: 'center',
} as const;

const tgValueSx = {
  ...slotValueSx,
  flexWrap: 'wrap',
  gap: 0.25,
  alignContent: 'flex-start',
} as const;

const srcDstValueSx = slotValueSx;

const srcDstChipSx = {
  maxWidth: '100%',
  '& .MuiChip-label': {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
} as const;

/** Subtle connected-time badge on mobile (secondary info, not status highlight). */
const connectedBadgeSx = {
  px: 1,
  py: 0.5,
  borderRadius: 1,
  textAlign: 'center',
  flexShrink: 0,
  bgcolor: (theme: { palette: { mode: string } }) =>
    theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
  color: 'text.secondary',
} as const;

function hasTgContent(staticTgs: string[], singleTg: string, multiTgs: UaTgEntry[]): boolean {
  if (staticTgs.length > 0) return true;
  if (singleTg.trim()) return true;
  return multiTgs.some((e) => String(e.TGID ?? '').trim());
}

function SrcDstCell({
  label,
  value,
  chipColor,
}: {
  label: string;
  value: string;
  chipColor: 'success' | 'error' | 'default';
}) {
  return (
    <Box sx={{ minWidth: 0 }}>
      <Typography variant="caption" color="text.secondary" display="block">
        {label}
      </Typography>
      <Box sx={srcDstValueSx}>
        {value ? (
          <Chip size="small" label={value} color={chipColor} sx={srcDstChipSx} />
        ) : (
          <Typography variant="body2" sx={{ lineHeight: '24px' }}>
            —
          </Typography>
        )}
      </Box>
    </Box>
  );
}

type SlotProps = {
  slot: 1 | 2;
  peer: PeerEntry;
  showTg: boolean;
  t: TFunction;
};

function SlotBlock({ slot, peer, showTg, t }: SlotProps) {
  const ts = getTs(peer, slot);
  const trx = String(ts.TRX ?? '');
  const sub = String(ts.SUB ?? '').replace(/&nbsp;/g, ' ').trim();
  const dest = String(ts.DEST ?? '').replace(/&nbsp;/g, ' ').trim();
  const chipColor = trxChipColor(trx);
  const singleMode = peer.SINGLE_MODE === true;
  const staticTgs = ((slot === 1 ? peer.TS1_STATIC : peer.TS2_STATIC) ?? []).filter(Boolean) as string[];
  const singleTg = singleMode ? String((slot === 1 ? peer.SINGLE_TS1 : peer.SINGLE_TS2)?.TGID ?? '').trim() : '';
  const singleTo = singleMode ? String((slot === 1 ? peer.SINGLE_TS1 : peer.SINGLE_TS2)?.TO ?? '').trim() : '';
  const multiTgs = (singleMode ? [] : (slot === 1 ? peer.UA_MULTI_TS1 : peer.UA_MULTI_TS2) ?? []) as UaTgEntry[];

  return (
    <Box>
      <Stack direction="row" spacing={0.75} alignItems="center" flexWrap="wrap" useFlexGap>
        <Chip size="small" label={`TS${slot}`} color={chipColor} />
      </Stack>
      {showTg ? (
        <Box sx={{ mt: 0.75 }}>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.25 }}>
            {t('lnksys_static_tg', { defaultValue: 'Static TG' })}
          </Typography>
          <Box sx={tgValueSx}>
            {hasTgContent(staticTgs, singleTg, multiTgs) ? (
              <TgChipGroup
                staticTgs={staticTgs}
                singleTg={singleTg}
                singleTo={singleTo}
                multiTgs={multiTgs}
                trx={trx}
                activeTg={activeTgFromDest(ts.DEST)}
                t={t}
              />
            ) : (
              <Typography variant="body2" sx={{ lineHeight: '24px' }}>
                —
              </Typography>
            )}
          </Box>
        </Box>
      ) : null}
      <Box
        sx={{
          mt: 0.75,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 1,
          alignItems: 'start',
        }}
      >
        <SrcDstCell label={t('lnksys_src', { defaultValue: 'Source' })} value={sub} chipColor={chipColor} />
        <SrcDstCell label={t('lnksys_dst', { defaultValue: 'Destination' })} value={dest} chipColor={chipColor} />
      </Box>
    </Box>
  );
}

type MasterPeerCardsProps = {
  masters: Ctable['MASTERS'];
  filter: (peerId: string, peer: PeerEntry) => boolean;
  tableKey: string;
  showEmptyMasters: boolean;
  showTg: boolean;
  t: TFunction;
};

export function MasterPeerCards({ masters, filter, tableKey, showEmptyMasters, showTg, t }: MasterPeerCardsProps) {
  const cards: ReactNode[] = [];
  for (const [masterName, master] of Object.entries(masters ?? {})) {
    const peerList = master?.PEERS ?? {};
    const list = Object.entries(peerList).filter(([pid, p]) => filter(String(pid), p as PeerEntry));
    if (list.length === 0 && !showEmptyMasters) continue;
    for (const [peerId, peer] of list) {
      const p = peer as PeerEntry;
      cards.push(
        <Card key={`${tableKey}-${masterName}-${peerId}`} variant="outlined" sx={{ mb: 1.5 }}>
          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
              <Box sx={{ minWidth: 0, flex: 1 }}>
                <Typography variant="subtitle2" fontWeight={700} noWrap>
                  <QrzLink callsign={String(p.CALLSIGN ?? peerId)}>{String(p.CALLSIGN ?? peerId)}</QrzLink>
                </Typography>
                <Chip size="small" label={peerId} sx={{ mt: 0.5 }} />
                {p.LOCATION ? (
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                    {String(p.LOCATION)}
                  </Typography>
                ) : null}
              </Box>
              <Box sx={connectedBadgeSx}>
                <Typography variant="caption" display="block">
                  {t('lnksys_connected', { defaultValue: 'Time Connected' })}
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'nowrap' }}>
                  <ConnectedTime
                    cellKey={masterPeerKey(masterName, String(peerId))}
                    fallback={String(p.CONNECTED ?? '—')}
                  />
                </Typography>
              </Box>
            </Stack>
            <Divider sx={{ my: 1 }} />
            <SlotBlock slot={1} peer={p} showTg={showTg} t={t} />
            <Divider sx={{ my: 1 }} />
            <SlotBlock slot={2} peer={p} showTg={showTg} t={t} />
          </CardContent>
        </Card>
      );
    }
  }
  return <>{cards}</>;
}

type ServicePeerCardsProps = {
  peers: Ctable['PEERS'];
  t: TFunction;
};

export function ServicePeerCards({ peers, t }: ServicePeerCardsProps) {
  return (
    <>
      {Object.entries(peers ?? {}).map(([name, peer]) => {
        const p = peer as PeerEntry;
        const st = p.STATS;
        return (
          <Card key={`svc-${name}`} variant="outlined" sx={{ mb: 1.5 }}>
            <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
                <Box sx={{ minWidth: 0, flex: 1 }}>
                  <Typography variant="subtitle2" fontWeight={700} noWrap>
                    {name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    {String(p.MODE ?? '')}
                  </Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ mt: 0.5 }}>
                    <QrzLink callsign={String(p.CALLSIGN ?? '')}>{String(p.CALLSIGN ?? '')}</QrzLink>
                  </Typography>
                  <Chip size="small" label={String(p.RADIO_ID ?? '')} sx={{ mt: 0.5 }} />
                  {p.LOCATION ? (
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                      {String(p.LOCATION)}
                    </Typography>
                  ) : null}
                </Box>
                <Box sx={connectedBadgeSx}>
                  <Typography variant="caption" display="block">
                    {t('lnksys_connected', { defaultValue: 'Connected' })}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'nowrap' }}>
                    <ConnectedTime cellKey={servicePeerKey(name)} fallback={String(st?.CONNECTED ?? '—')} />
                  </Typography>
                  {typeof st?.PINGS_SENT === 'number' ? (
                    <Typography variant="caption" display="block">
                      {st.PINGS_SENT} / {String(st.PINGS_ACKD ?? 0)}
                    </Typography>
                  ) : null}
                </Box>
              </Stack>
              <Divider sx={{ my: 1 }} />
              <SlotBlock slot={1} peer={p} showTg={false} t={t} />
              <Divider sx={{ my: 1 }} />
              <SlotBlock slot={2} peer={p} showTg={false} t={t} />
            </CardContent>
          </Card>
        );
      })}
    </>
  );
}
