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

import { Box, Typography, Link } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useDashboardConfig } from '../context/DashboardConfigContext';
import { useWebSocketGroup } from '../hooks/useWebSocket';

const currentYear = new Date().getFullYear();

export default function Footer() {
  const { t } = useTranslation();
  const { title, footer } = useDashboardConfig();
  const brand = title || t('footer_brand', 'ADN Systems');
  const { data } = useWebSocketGroup('server_info');
  const isV2 = (data as { mode?: string } | null)?.mode === 'v2';

  return (
    <Box
      component="footer"
      sx={{
        py: { xs: 1.5, sm: 2 },
        px: { xs: 1.5, sm: 2 },
        mt: 'auto',
        flexShrink: 0,
        borderTop: '1px solid',
        borderColor: 'divider',
        backgroundColor: (theme) =>
          theme.palette.mode === 'dark'
            ? 'rgba(30, 30, 30, 0.75)'
            : 'rgba(255, 255, 255, 0.75)',
        textAlign: 'center',
        '@media (orientation: landscape) and (max-height: 500px)': {
          py: 0.5,
          px: 1,
          '& .MuiTypography-root': { fontSize: '0.75rem' },
        },
      }}
    >
      {footer.length > 0 && (
        <Typography variant="body2" color="text.secondary" component="div" sx={{ mb: 1 }}>
          {footer.map((item, i) => (
            <span key={i}>
              {i > 0 && ' · '}
              <Link
                href={item.url}
                target={item.url.startsWith('http') ? '_blank' : undefined}
                rel={item.url.startsWith('http') ? 'noopener' : undefined}
                color="primary.main"
                underline="hover"
              >
                {item.name}
              </Link>
            </span>
          ))}
        </Typography>
      )}
      <Typography variant="body2" color="text.secondary" component="div">
        {brand}
        <span id="footer-report-sep">{isV2 ? ' ✦  ' : ' · '}</span>
        {t('footer_copyright', { year: currentYear, defaultValue: 'Copyright {{year}} - All rights reserved.' })}{' '}
        <Link href="https://adn.systems" target="_blank" rel="noopener" color="primary.main" underline="hover">
          {t('footer_app', 'ADN Systems Monitor')}
        </Link>
      </Typography>
      <Typography variant="body2" color="text.secondary" component="div" sx={{ mt: 1 }}>
        {t('footer_developed', 'Developed with')} ❤️ {t('footer_by', 'by')}{' '}
        <Link href="https://www.qrz.com/db/CE5RPY" target="_blank" rel="noopener" color="primary.main" underline="hover">
          CE5RPY
        </Link>
      </Typography>
    </Box>
  );
}
