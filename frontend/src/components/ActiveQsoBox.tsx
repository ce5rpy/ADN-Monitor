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

import { Box, Typography, Card, CardContent } from '@mui/material';
import { useTranslation } from 'react-i18next';
import QrzLink, { isCallsignLike } from './QrzLink';

export type TimeslotEntry = {
  TS?: boolean | string;
  TYPE?: string;
  SUB?: string;
  CALL?: string;
  SRC?: string | number;
  DEST?: string;
  TG?: string;
  TRX?: string;
};

export type PeerEntry = {
  1?: TimeslotEntry;
  2?: TimeslotEntry;
  CALLSIGN?: string;
  CONNECTED?: string;
  RX_FREQ?: string;
  TX_FREQ?: string;
};

/** OPENBRIDGES[system].STREAMS[streamId] = [trx, sub_call, tgNumStr, timeout] */
type OpenBridgeStream = [string, string, string, number];
type OpenBridgeEntry = { STREAMS?: Record<string, OpenBridgeStream> };

export type Ctable = {
  MASTERS?: Record<string, { PEERS?: Record<string, PeerEntry> }>;
  PEERS?: Record<string, Record<string, TimeslotEntry>>;
  OPENBRIDGES?: Record<string, OpenBridgeEntry>;
};

type ActiveSlot = {
  kind: 'master';
  system: string;
  peerId: string;
  peer: PeerEntry;
  tsNum: 1 | 2;
};
type ActivePeerSlot = {
  kind: 'peer';
  system: string;
  tsNum: 1 | 2;
  ts: TimeslotEntry;
};
type ActiveObQso = {
  kind: 'openbridge';
  tg: string;
  call: string;
  system?: string;
};

export default function ActiveQsoBox({ ctable }: { ctable: Ctable | null | undefined }) {
  const { t } = useTranslation();

  const masterSlots: ActiveSlot[] = [];
  if (ctable?.MASTERS && Object.keys(ctable.MASTERS).length > 0) {
    for (const [system, master] of Object.entries(ctable.MASTERS)) {
      const peers = master?.PEERS ?? {};
      for (const [peerId, peer] of Object.entries(peers)) {
        for (const tsNum of [1, 2] as const) {
          const ts = peer[tsNum as 1 | 2] ?? (peer as Record<string, TimeslotEntry | undefined>)[String(tsNum)];
          const isTsActive = ts && (ts.TS === true || ts.TS === 'true' || (typeof ts.TS === 'string' && ts.TS.toLowerCase() !== 'false'));
          const isRx = String(ts?.TRX ?? '').toUpperCase() === 'RX';
          if (isTsActive && isRx) masterSlots.push({ kind: 'master', system, peerId, peer, tsNum });
        }
      }
    }
  }

  const peerSlots: ActivePeerSlot[] = [];
  if (ctable?.PEERS) {
    for (const [system, slots] of Object.entries(ctable.PEERS)) {
      for (const tsNum of [1, 2] as const) {
        const ts = (slots as Record<string, TimeslotEntry>)[String(tsNum)];
        const isTsActive = ts && (ts.TS === true || ts.TS === 'true' || (typeof ts.TS === 'string' && ts.TS.toLowerCase() !== 'false'));
        const isRx = String(ts?.TRX ?? '').toUpperCase() === 'RX';
        if (isTsActive && isRx && ts) peerSlots.push({ kind: 'peer', system, tsNum, ts });
      }
    }
  }

  const obByKey = new Map<string, ActiveObQso>();
  if (ctable?.OPENBRIDGES) {
    for (const [system, ob] of Object.entries(ctable.OPENBRIDGES)) {
      const streams = ob?.STREAMS ?? {};
      for (const [, entry] of Object.entries(streams)) {
        const arr = Array.isArray(entry) ? entry : [];
        const trx = String(arr[0] ?? '').toUpperCase();
        if (trx !== 'RX') continue;
        const call = String(arr[1] ?? '');
        const tg = String(arr[2] ?? '');
        const key = `${tg}\t${call}`;
        if (!obByKey.has(key)) obByKey.set(key, { kind: 'openbridge', tg, call, system });
      }
    }
  }
  const openBridgeQsos = Array.from(obByKey.values());

  const totalCount = masterSlots.length + peerSlots.length + openBridgeQsos.length;
  const hasAny = totalCount > 0;

  return (
    <Box sx={{ mb: 1.5, minHeight: 140 }}>
      <Typography variant="subtitle1" fontWeight={600} color="text.primary" sx={{ mb: 1.5 }}>
        {t('active_qso')} {hasAny && `(${totalCount})`}
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
        {!hasAny ? (
          <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
            {t('active_qso_none', 'No active QSO at the moment.')}
          </Typography>
        ) : (
          <>
            {masterSlots.map(({ system, peerId, peer, tsNum }, idx) => {
              const ts = peer[tsNum as 1 | 2] ?? (peer as Record<string, TimeslotEntry | undefined>)[String(tsNum)];
              const sub = ts?.SUB ?? '';
              const call = ts?.CALL ?? '';
              const tg = ts?.TG ?? '';
              const displayText = (call && isCallsignLike(call)) ? call : (sub || call);
              return (
                <Card key={`m-${system}-${peerId}-${tsNum}-${idx}`} variant="outlined" sx={{ width: 120, flexShrink: 0, borderColor: 'divider', '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' } }}>
                  <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 }, textAlign: 'center' }}>
                    {(sub || call) && (
                      <Typography variant="body2" fontWeight={500}>
                        <QrzLink callsign={displayText}>{displayText}</QrzLink>
                      </Typography>
                    )}
                    {tg && <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.25 }}>{tg.replace(/&nbsp;/g, ' ')}</Typography>}
                  </CardContent>
                </Card>
              );
            })}
            {peerSlots.map(({ system, tsNum, ts }, idx) => {
              const sub = ts?.SUB ?? '';
              const call = ts?.CALL ?? '';
              const tg = ts?.TG ?? '';
              const displayText = (call && isCallsignLike(call)) ? call : (sub || call);
              return (
                <Card key={`p-${system}-${tsNum}-${idx}`} variant="outlined" sx={{ width: 120, flexShrink: 0, borderColor: 'divider', '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' } }}>
                  <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 }, textAlign: 'center' }}>
                    {(sub || call) && (
                      <Typography variant="body2" fontWeight={500}>
                        <QrzLink callsign={displayText}>{displayText}</QrzLink>
                      </Typography>
                    )}
                    {tg && <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.25 }}>{tg.replace(/&nbsp;/g, ' ')}</Typography>}
                  </CardContent>
                </Card>
              );
            })}
            {openBridgeQsos.map((q, idx) => {
              const isBridge = String(q.call ?? '').toUpperCase() === 'BRIDGE';
              const nameDisplay = isBridge ? (q.system || '—') : (q.call || '—');
              return (
                <Card key={`ob-${q.tg}-${q.call}-${idx}`} variant="outlined" sx={{ width: 120, flexShrink: 0, borderColor: 'divider', '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' } }}>
                  <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 }, textAlign: 'center' }}>
                    <Typography variant="body2" fontWeight={500}>
                      {isBridge ? nameDisplay : <QrzLink callsign={q.call ?? ''}>{nameDisplay}</QrzLink>}
                    </Typography>
                    <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.25 }}>TG {q.tg}</Typography>
                  </CardContent>
                </Card>
              );
            })}
          </>
        )}
      </Box>
    </Box>
  );
}
