/*
 * ADN Monitor - elapsed time formatting (parity with monitor time_utils / ElapsedTime).
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

/** Format seconds elapsed as "Xd Xh", "Xh Xm", "Xm Xs", or "Xs". */
export function formatElapsedSeconds(delta: number): string {
  const d = Math.max(0, Math.floor(delta));
  const secs = d % 60;
  const mins = Math.floor(d / 60) % 60;
  const hours = Math.floor(d / 3600) % 24;
  const days = Math.floor(d / 86400);
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${mins}m`;
  if (mins > 0) return `${mins}m ${secs}s`;
  return `${secs}s`;
}

/** Parse monitor CONNECTED label into elapsed seconds (legacy fallback). */
export function parseElapsedLabel(label: string): number | null {
  const s = label.trim();
  if (!s || s.startsWith('--')) return null;
  const day = /^(\d+)d\s+(\d+)h$/.exec(s);
  if (day) return parseInt(day[1], 10) * 86400 + parseInt(day[2], 10) * 3600;
  const hour = /^(\d+)h\s+(\d+)m$/.exec(s);
  if (hour) return parseInt(hour[1], 10) * 3600 + parseInt(hour[2], 10) * 60;
  const min = /^(\d+)m\s+(\d+)s$/.exec(s);
  if (min) return parseInt(min[1], 10) * 60 + parseInt(min[2], 10);
  const sec = /^(\d+)s$/.exec(s);
  if (sec) return parseInt(sec[1], 10);
  return null;
}
