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

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import es from './locales/es.json';
import pt from './locales/pt.json';
import fr from './locales/fr.json';
import de from './locales/de.json';
import it from './locales/it.json';
import nl from './locales/nl.json';
import ca from './locales/ca.json';
import bg from './locales/bg.json';
import zh from './locales/zh.json';
import et from './locales/et.json';
import el from './locales/el.json';
import pl from './locales/pl.json';
import sr from './locales/sr.json';
import th from './locales/th.json';
import tr from './locales/tr.json';
import uk from './locales/uk.json';

const resources = {
  en: { translation: en },
  es: { translation: es },
  pt: { translation: pt },
  fr: { translation: fr },
  de: { translation: de },
  it: { translation: it },
  nl: { translation: nl },
  ca: { translation: ca },
  bg: { translation: bg },
  zh: { translation: zh },
  et: { translation: et },
  el: { translation: el },
  pl: { translation: pl },
  sr: { translation: sr },
  th: { translation: th },
  tr: { translation: tr },
  uk: { translation: uk },
};

const DEFAULT_LANG = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_DEFAULT_LANGUAGE) || 'en';
const browserLang = typeof navigator !== 'undefined' ? navigator.language?.split(/[-_]/)[0]?.toLowerCase() : '';
const supported = ['en', 'es', 'pt', 'fr', 'de', 'it', 'nl', 'ca', 'bg', 'zh', 'et', 'el', 'pl', 'sr', 'th', 'tr', 'uk'];
const initialLng = localStorage.getItem('language') || (supported.includes(browserLang) ? browserLang : DEFAULT_LANG);

i18n.use(initReactI18next).init({
  resources,
  lng: initialLng,
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
  react: { useSuspense: false },
});

i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
});

export default i18n;
