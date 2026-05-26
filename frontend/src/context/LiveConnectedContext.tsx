/*
 * ADN Monitor - live "Time Connected" anchors from CONNECTED_SINCE WebSocket fields.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { formatElapsedSeconds, parseElapsedLabel } from '../utils/elapsedTime';

type CtableSlice = {
  MASTERS?: Record<string, { PEERS?: Record<string, Record<string, unknown>> }>;
  PEERS?: Record<string, Record<string, unknown>>;
};

export function masterPeerKey(masterName: string, peerId: string): string {
  return `m:${masterName}:${peerId}`;
}

export function servicePeerKey(serviceName: string): string {
  return `p:${serviceName}`;
}

function resolveSince(
  sinceRaw: unknown,
  connectedLabel: string | undefined,
  nowSec: number,
): number | null {
  if (typeof sinceRaw === 'number' && Number.isFinite(sinceRaw) && sinceRaw > 0) {
    return Math.floor(sinceRaw);
  }
  if (connectedLabel) {
    const elapsed = parseElapsedLabel(connectedLabel);
    if (elapsed != null) return nowSec - elapsed;
  }
  return null;
}

function anchorsFromCtable(ctable: CtableSlice | undefined): Map<string, number | null> {
  const out = new Map<string, number | null>();
  if (!ctable) return out;
  const nowSec = Math.floor(Date.now() / 1000);

  for (const [masterName, master] of Object.entries(ctable.MASTERS ?? {})) {
    for (const [peerId, peer] of Object.entries(master?.PEERS ?? {})) {
      const key = masterPeerKey(masterName, peerId);
      out.set(
        key,
        resolveSince(peer.CONNECTED_SINCE, String(peer.CONNECTED ?? ''), nowSec),
      );
    }
  }

  for (const [name, peer] of Object.entries(ctable.PEERS ?? {})) {
    const stats = peer.STATS as Record<string, unknown> | undefined;
    const key = servicePeerKey(name);
    out.set(
      key,
      resolveSince(stats?.CONNECTED_SINCE, String(stats?.CONNECTED ?? ''), nowSec),
    );
  }

  return out;
}

type LiveConnectedContextValue = {
  getLabel: (cellKey: string, fallback: string) => string;
};

const LiveConnectedContext = createContext<LiveConnectedContextValue | null>(null);

export function LiveConnectedProvider({
  ctable,
  children,
  live = false,
}: {
  ctable: CtableSlice | undefined;
  children: ReactNode;
  /** v2 only: tick live from CONNECTED_SINCE; legacy uses WebSocket CONNECTED as-is. */
  live?: boolean;
}) {
  const anchorsRef = useRef<Map<string, number | null>>(new Map());
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const incoming = anchorsFromCtable(ctable);
    const cur = anchorsRef.current;
    let dirty = false;

    for (const [key, since] of incoming) {
      if (cur.get(key) !== since) {
        cur.set(key, since);
        dirty = true;
      }
    }
    for (const key of [...cur.keys()]) {
      if (!incoming.has(key)) {
        cur.delete(key);
        dirty = true;
      }
    }
    if (dirty) setTick((t) => t + 1);
  }, [ctable]);

  useEffect(() => {
    if (!live) return;
    const id = window.setInterval(() => setTick((t) => t + 1), 1000);
    return () => window.clearInterval(id);
  }, [live]);

  const getLabel = useCallback(
    (cellKey: string, fallback: string) => {
      if (!live) return fallback || '—';
      void tick;
      const since = anchorsRef.current.get(cellKey);
      if (since == null || since <= 0) {
        return fallback || '—';
      }
      const nowSec = Math.floor(Date.now() / 1000);
      return formatElapsedSeconds(Math.max(0, nowSec - since), { showSecondsAfterHour: true });
    },
    [tick, live],
  );

  return (
    <LiveConnectedContext.Provider value={{ getLabel }}>
      {children}
    </LiveConnectedContext.Provider>
  );
}

export function ConnectedTime({ cellKey, fallback }: { cellKey: string; fallback?: string }) {
  const ctx = useContext(LiveConnectedContext);
  const label = ctx?.getLabel(cellKey, fallback ?? '—') ?? fallback ?? '—';
  return <>{label}</>;
}
