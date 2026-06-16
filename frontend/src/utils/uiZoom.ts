/*
 * ADN Monitor - UI zoom on #root (proportional layout: text, rows, padding, images).
 */

export const UI_ZOOM_COOKIE = 'adn_ui_zoom';
export const DEFAULT_UI_ZOOM = 100;
export const MIN_UI_ZOOM = 50;
export const MAX_UI_ZOOM = 125;
export const UI_ZOOM_STEP = 5;

export function clampUiZoom(percent: number): number {
  return Math.min(MAX_UI_ZOOM, Math.max(MIN_UI_ZOOM, Math.round(percent)));
}

function readCookie(name: string): string | null {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const m = document.cookie.match(new RegExp(`(?:^|; )${escaped}=(\\d+)`));
  return m ? m[1] : null;
}

export function getUiZoom(): number {
  const raw = readCookie(UI_ZOOM_COOKIE);
  if (raw != null) {
    const n = parseInt(raw, 10);
    if (!Number.isNaN(n)) {
      return clampUiZoom(n);
    }
  }
  return DEFAULT_UI_ZOOM;
}

function rootElement(): HTMLElement | null {
  return document.getElementById('root');
}

export function applyUiZoom(percent: number): number {
  const p = clampUiZoom(percent);
  const factor = p / 100;
  document.documentElement.style.setProperty('--adn-ui-zoom', String(factor));
  document.documentElement.style.fontSize = '';
  const root = rootElement();
  if (root) {
    root.style.zoom = p === 100 ? '' : String(factor);
  }
  return p;
}

export function saveUiZoom(percent: number): number {
  const p = applyUiZoom(percent);
  const maxAge = 365 * 24 * 60 * 60;
  document.cookie = `${UI_ZOOM_COOKIE}=${p};path=/;max-age=${maxAge};SameSite=Lax`;
  return p;
}

/** Call once before React mount to avoid layout flash. */
export function initUiZoom(): number {
  return applyUiZoom(getUiZoom());
}
