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

import { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
} from '@mui/material';
import PrintIcon from '@mui/icons-material/Print';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGE_CODES } from '../i18n';

/**
 * Resolve the manual path for the current UI language.
 * Falls back to English when the translation is not yet available.
 */
function manualUrl(lang: string | undefined): string {
  const code = (lang || 'en').split(/[-_]/)[0]?.toLowerCase();
  const resolved = (SUPPORTED_LANGUAGE_CODES as readonly string[]).includes(code)
    ? code
    : 'en';
  return `${import.meta.env.BASE_URL}handbook/${resolved}.md`;
}

export default function RadioManual() {
  const { t, i18n } = useTranslation();
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const url = manualUrl(i18n.language);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    fetch(url)
      .then(async (res) => {
        if (!res.ok) throw new Error('not found');
        const text = await res.text();
        if (!cancelled) {
          setContent(text);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          if (url.endsWith('/en.md')) {
            setError(true);
            setLoading(false);
          } else {
            // last-resort: try English
            fetch(`${import.meta.env.BASE_URL}handbook/en.md`)
              .then(async (r) => {
                if (!r.ok) throw new Error();
                setContent(await r.text());
                setLoading(false);
              })
              .catch(() => {
                setError(true);
                setLoading(false);
              });
          }
        }
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  return (
    <Box>
      <Paper
        variant="outlined"
        sx={{
          p: 1.5,
          mb: 1.5,
          bgcolor: 'background.paper',
          boxShadow: (theme) =>
            theme.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 1,
        }}
      >
        <Box>
          <Typography variant="subtitle1" fontWeight={700} color="text.primary">
            {t('manual_title', { defaultValue: 'Radio operator manual' })}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {t('manual_subtitle', {
              defaultValue:
                'A practical guide to using ADN: talk groups, PTT, echo, and hotspot setup.',
            })}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexShrink: 0 }}>
          <Button
            component={Link}
            to="/help"
            variant="outlined"
            size="small"
            startIcon={<ArrowBackIcon />}
          >
            {t('manual_back_help', { defaultValue: 'Back to Help' })}
          </Button>
          <Button
            onClick={() => window.print()}
            variant="contained"
            size="small"
            startIcon={<PrintIcon />}
          >
            {t('manual_print', { defaultValue: 'Print / PDF' })}
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: { xs: 2, sm: 3, md: 4 } }} id="manual-print-area">
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Typography color="error">
            {t('manual_error', {
              defaultValue: 'Could not load the manual. Try again later.',
            })}
          </Typography>
        ) : (
          <Box className="manual-body">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
                a: ({ node: _node, href, children }) => (
                  <Box
                    component="a"
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                  >
                    {children}
                  </Box>
                ),
                blockquote: ({ children }) => (
                  <Box
                    component="blockquote"
                    sx={{
                      borderLeft: 4,
                      borderColor: 'primary.main',
                      pl: 2,
                      my: 2,
                      ml: 0,
                      color: 'text.secondary',
                      fontStyle: 'italic',
                    }}
                  >
                    {children}
                  </Box>
                ),
                table: ({ children }) => (
                  <Box
                    component="table"
                    sx={{
                      width: '100%',
                      borderCollapse: 'collapse',
                      my: 2,
                      '& th, & td': {
                        border: 1,
                        borderColor: 'divider',
                        p: 1,
                        textAlign: 'left',
                        fontSize: '0.875rem',
                        verticalAlign: 'top',
                      },
                      '& th': {
                        bgcolor: 'action.hover',
                        fontWeight: 600,
                      },
                    }}
                  >
                    {children}
                  </Box>
                ),
                code: ({ children }) => (
                  <Box
                    component="code"
                    sx={{
                      fontFamily: 'monospace',
                      fontSize: '0.85em',
                      bgcolor: 'action.hover',
                      px: 0.5,
                      borderRadius: 0.5,
                    }}
                  >
                    {children}
                  </Box>
                ),
                pre: ({ children }) => (
                  <Box
                    component="pre"
                    sx={{
                      p: 1.5,
                      my: 1.5,
                      bgcolor: 'action.hover',
                      borderRadius: 1,
                      fontSize: '0.8rem',
                      overflow: 'auto',
                      border: 1,
                      borderColor: 'divider',
                    }}
                  >
                    {children}
                  </Box>
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
