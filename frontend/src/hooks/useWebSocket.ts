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

import { useEffect, useRef, useState, useCallback } from 'react';

const WS_GROUPS = ['main', 'bridge', 'lnksys', 'opb', 'statictg', 'log', 'lsthrd_log', 'tgcount', 'server_info'] as const;
export type WsGroup = (typeof WS_GROUPS)[number];

const GROUP_OPCODE: Record<WsGroup, string> = {
  main: 'i',
  lnksys: 'c',
  opb: 'o',
  statictg: 's',
  bridge: 'b',
  log: 'l',
  lsthrd_log: 'h',
  tgcount: 't',
  server_info: 'v',
};

const RECONNECT_INITIAL_MS = 2000;
const RECONNECT_MAX_DELAY_MS = 15000;

function getWsUrl(): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${proto}//${host}/ws`;
}

export interface UseWebSocketOptions {
  groups: WsGroup[];
  onMessage?: (opcode: string, payload: string) => void;
}

export function useWebSocket({ groups, onMessage }: UseWebSocketOptions) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<{ opcode: string; payload: string } | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);
  const attemptRef = useRef(0);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const url = getWsUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      attemptRef.current = 0;
      setConnected(true);
      if (groups.length > 0) {
        ws.send('conf,' + groups.join(','));
      }
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;
      if (!mountedRef.current) return;
      const delay = Math.min(
        RECONNECT_INITIAL_MS * Math.pow(1.5, attemptRef.current),
        RECONNECT_MAX_DELAY_MS
      );
      attemptRef.current += 1;
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectTimeoutRef.current = null;
        connect();
      }, delay);
    };

    ws.onerror = () => {
      // Close will follow; no extra handling needed
    };

    ws.onmessage = (event) => {
      const data = String(event.data);
      const opcode = data.slice(0, 1);
      const payload = data.slice(1);
      setLastMessage({ opcode, payload });
      onMessageRef.current?.(opcode, payload);
    };
  }, [groups.join(',')]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [connect]);

  return { connected, lastMessage, reconnect: connect };
}

/** Payload is JSON for opcodes i,c,o,s,b,h,t,v; plain string for q,l */
function parsePayload(opcode: string, payload: string): unknown {
  if (opcode === 'q' || opcode === 'l') return payload;
  try {
    return JSON.parse(payload) as unknown;
  } catch {
    return payload;
  }
}

export function useWebSocketGroup(group: WsGroup) {
  const [data, setData] = useState<unknown>(null);
  const wantOpcode = GROUP_OPCODE[group];

  useWebSocket({
    groups: [group],
    onMessage: (opcode, payload) => {
      if (opcode !== wantOpcode) return;
      setData(parsePayload(opcode, payload));
    },
  });

  return { data };
}
