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

import { useEffect, useRef, useState, useCallback } from 'react';

const WS_GROUPS = ['main', 'bridge', 'lnksys', 'opb', 'statictg', 'log', 'lsthrd_log', 'tgcount'] as const;
export type WsGroup = (typeof WS_GROUPS)[number];

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
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const url = getWsUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      if (groups.length > 0) {
        ws.send('conf,' + groups.join(','));
      }
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;
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
    connect();
    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [connect]);

  return { connected, lastMessage, reconnect: connect };
}

/** Payload is JSON for opcodes i,c,o,s,b,h,t; plain string for q,l */
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
  const groups = [group];

  useWebSocket({
    groups,
    onMessage: (opcode, payload) => {
      setData(parsePayload(opcode, payload));
    },
  });

  return { data };
}
