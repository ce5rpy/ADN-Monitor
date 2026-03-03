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

import { Box, Typography, Link } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useDashboardConfig } from '../context/DashboardConfigContext';

const currentYear = new Date().getFullYear();

export default function Footer() {
  const { t } = useTranslation();
  const { title, footer } = useDashboardConfig();
  const brand = title || t('footer_brand', 'ADN Systems');

  return (
    <Box
      component="footer"
      sx={{
        py: 2,
        px: 2,
        mt: 'auto',
        borderTop: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper',
        textAlign: 'center',
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
        {brand} · {t('footer_copyright', { year: currentYear, defaultValue: 'Copyright {{year}} - All rights reserved.' })}{' '}
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
