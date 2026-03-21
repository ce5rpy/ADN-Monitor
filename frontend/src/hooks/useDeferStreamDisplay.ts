/*
 * ADN Monitor - defer showing OpenBridge stream rows until they persist minMs (avoids BCSQ/loop flash).
 */

import { useCallback, useEffect, useRef, useState } from 'react';

const TICK_MS = 200;

/**
 * Tracks client-side first-seen time per key. Use for rapid START/END pairs (e.g. quench).
 * - During render, call `shouldShow(key)`; it returns true only after `minMs` from first sighting.
 * - After building the current snapshot, call `prune(activeKeys)` with all keys still present.
 */
export function useDeferStreamDisplay(minMs = 1000) {
  const firstSeen = useRef<Map<string, number>>(new Map());
  const [, setTick] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setTick((x) => x + 1), TICK_MS);
    return () => clearInterval(id);
  }, []);

  const shouldShow = useCallback((key: string): boolean => {
    const t = Date.now();
    if (!firstSeen.current.has(key)) {
      firstSeen.current.set(key, t);
    }
    const t0 = firstSeen.current.get(key);
    return t0 != null && t - t0 >= minMs;
  }, [minMs]);

  const prune = useCallback((activeKeys: Set<string>) => {
    for (const k of [...firstSeen.current.keys()]) {
      if (!activeKeys.has(k)) {
        firstSeen.current.delete(k);
      }
    }
  }, []);

  return { shouldShow, prune };
}
