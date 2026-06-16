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

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getLanguageCookie, setLanguageCookie, SUPPORTED_LANGUAGE_CODES } from '../i18n';

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
  /** Show Console page in Info menu (call start/end messages). Set show_console in adn-monitor.yaml DASHBOARD. */
  showConsole: boolean;
  /** Footer links: same structure as nav_links items (name + url) */
  footer: NavLinkItem[];
  /** News/events for the marquee below the logo (name + optional url). Same structure as footer. */
  news: NavLinkItem[];
  navLinks: { name?: string; items: NavLinkItem[] };
  aliases: AliasesConfig;
  apiBase: string;
};

const defaultConfig: DashboardConfig = {
  title: 'ADN Systems Dashboard',
  language: getDefaultLanguage(),
  background: false,
  selfService: false,
  showConsole: false,
  footer: [],
  news: [],
  navLinks: { items: [] },
  aliases: defaultAliases,
  apiBase: '',
};

const DashboardConfigContext = createContext<DashboardConfig>(defaultConfig);

/** When no cookie: config default language → browser language → English. */
function resolveDefaultLanguage(configLang: string): string {
  const code = configLang.split(/[-_]/)[0]?.toLowerCase() || 'en';
  const supported = new Set<string>(SUPPORTED_LANGUAGE_CODES);
  if (supported.has(code)) return code;
  const browser = typeof navigator !== 'undefined' ? navigator.language?.split(/[-_]/)[0]?.toLowerCase() ?? '' : '';
  if (supported.has(browser)) return browser;
  return 'en';
}

const getApiBase = (): string =>
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE) || '';

/**
 * Dashboard config flow:
 * 1. Frontend requests GET {apiBase}/api/config/dashboard
 * 2. monitor.py reads adn-monitor.yaml (ADN_CONFIG_PATH or repo root .env)
 * 3. API returns JSON with title (DASHTITLE), language, footer, nav_links, etc.
 * 4. If the request fails (monitor down, CORS, wrong VITE_API_BASE), defaultConfig is used.
 * Build: set VITE_API_BASE to '' for same-origin (nginx proxies /api to monitor.py).
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
          showConsole?: boolean;
          footer?: NavLinkItem[];
          news?: NavLinkItem[];
          navLinks?: { name?: string; items?: NavLinkItem[] };
        }) => {
        const rawConfigLang = (data.language ?? getDefaultLanguage()).split(/[-_]/)[0]?.toLowerCase() || 'en';
        const resolvedLang = resolveDefaultLanguage(rawConfigLang);
        const nav = data.navLinks ?? {};
        const footer = Array.isArray(data.footer)
          ? data.footer.filter((e): e is NavLinkItem => e && typeof e === 'object' && 'name' in e && 'url' in e)
          : [];
        const news = Array.isArray(data.news)
          ? data.news.filter((e): e is NavLinkItem => e && typeof e === 'object' && 'name' in e)
          : [];
        const title = data.title ?? defaultConfig.title;
        setConfig({
          title,
          language: resolvedLang,
          background: Boolean(data.background),
          selfService: Boolean(data.selfService),
          showConsole: Boolean(data.showConsole),
          footer,
          news,
          navLinks: { name: nav.name ?? '', items: Array.isArray(nav.items) ? nav.items : [] },
          apiBase,
          aliases: defaultAliases,
        });
        const cookieLang = getLanguageCookie();
        if (cookieLang && SUPPORTED_LANGUAGE_CODES.includes(cookieLang as (typeof SUPPORTED_LANGUAGE_CODES)[number])) {
          if (i18n.language !== cookieLang) {
            i18n.changeLanguage(cookieLang);
          }
        } else {
          setLanguageCookie(resolvedLang);
          if (i18n.language !== resolvedLang) {
            i18n.changeLanguage(resolvedLang);
          }
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
