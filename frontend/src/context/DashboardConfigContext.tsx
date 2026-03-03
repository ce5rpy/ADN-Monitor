/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2025  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
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

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

const getAliasesBase = (): string =>
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_ALIASES_BASE_URL) || 'https://adn.systems/files';

const getDefaultLanguage = (): string =>
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_DEFAULT_LANGUAGE) || 'en';

export type AliasesConfig = {
  peerUrl: string;
  subscriberUrl: string;
  tgidUrl: string;
  serverIdUrl: string;
  checksumUrl: string;
  tgListUrl: string;
  bridgeListUrl: string;
};

function buildDefaultAliases(): AliasesConfig {
  const base = getAliasesBase().replace(/\/$/, '');
  return {
    peerUrl: `${base}/peer_ids.json`,
    subscriberUrl: `${base}/subscriber_ids.json`,
    tgidUrl: `${base}/talkgroup_ids.json`,
    serverIdUrl: `${base}/server_ids.tsv`,
    checksumUrl: `${base}/file_checksums.json`,
    tgListUrl: `${base}/talkgroup_ids.json`,
    bridgeListUrl: `${base}/server_ids.tsv`,
  };
}

const defaultAliases = buildDefaultAliases();

export type NavLinkItem = { name: string; url: string };

type DashboardConfig = {
  title: string;
  language: string;
  background: boolean;
  /** Show/hide local Self-service nav item only. SelfCare link is always in header (hardcoded). */
  selfService: boolean;
  /** Footer links: same structure as nav_links items (name + url) */
  footer: NavLinkItem[];
  navLinks: { name?: string; items: NavLinkItem[] };
  aliases: AliasesConfig;
  apiBase: string;
};

const defaultConfig: DashboardConfig = {
  title: 'ADN Systems Dashboard',
  language: getDefaultLanguage(),
  background: false,
  selfService: false,
  footer: [],
  navLinks: { items: [] },
  aliases: defaultAliases,
  apiBase: '',
};

const DashboardConfigContext = createContext<DashboardConfig>(defaultConfig);

const SUPPORTED_LANGS = ['en', 'es', 'pt', 'fr', 'de', 'it', 'nl'];

function normalizeLanguage(lang: string): string {
  const code = lang.split(/[-_]/)[0]?.toLowerCase() || 'en';
  return SUPPORTED_LANGS.includes(code) ? code : 'en';
}

const getApiBase = (): string =>
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE) || '';

/**
 * Dashboard config flow:
 * 1. Frontend requests GET {apiBase}/api/config/dashboard
 * 2. Backend (PHP) reads monitor/adn-mon.yaml (path from ADN_CONFIG_PATH env or .env)
 * 3. Backend returns JSON with title (DASHTITLE), language, footer1, footer2, etc.
 * 4. If the request fails (no backend, CORS, wrong VITE_API_BASE), defaultConfig is used.
 * Build: set VITE_API_BASE to '' for same-origin (nginx must proxy /api to PHP).
 */
export function DashboardConfigProvider({ children }: { children: React.ReactNode }) {
  const { i18n } = useTranslation();
  const [config, setConfig] = useState<DashboardConfig>(() => ({ ...defaultConfig, apiBase: getApiBase() }));

  const apiBase = getApiBase();

  useEffect(() => {
    const url = `${apiBase}/api/config/dashboard`;
    fetch(url)
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          return Promise.reject({ status: res.status, body: data });
        }
        return data;
      })
      .then((data: {
          title?: string;
          language?: string;
          background?: boolean;
          selfService?: boolean;
          footer?: NavLinkItem[];
          navLinks?: { name?: string; items?: NavLinkItem[] };
        }) => {
        const lang = normalizeLanguage(data.language ?? getDefaultLanguage());
        const nav = data.navLinks ?? {};
        const footer = Array.isArray(data.footer)
          ? data.footer.filter((e): e is NavLinkItem => e && typeof e === 'object' && 'name' in e && 'url' in e)
          : [];
        const title = data.title ?? defaultConfig.title;
        setConfig({
          title,
          language: lang,
          background: Boolean(data.background),
          selfService: Boolean(data.selfService),
          footer,
          navLinks: { name: nav.name ?? '', items: Array.isArray(nav.items) ? nav.items : [] },
          apiBase,
          aliases: defaultAliases,
        });
        if (i18n.language !== lang) {
          i18n.changeLanguage(lang);
        }
      })
      .catch(() => {
        setConfig({
          ...defaultConfig,
          apiBase,
          title: defaultConfig.title,
        });
      });
  }, [i18n, apiBase]);

  return (
    <DashboardConfigContext.Provider value={config}>
      {children}
    </DashboardConfigContext.Provider>
  );
}

export function useDashboardConfig() {
  return useContext(DashboardConfigContext);
}
