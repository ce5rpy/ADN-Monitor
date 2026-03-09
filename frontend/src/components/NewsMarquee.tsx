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

import { Box, Link, Typography, useTheme } from '@mui/material';
import Marquee from 'react-fast-marquee';
import { useDashboardConfig } from '../context/DashboardConfigContext';

export default function NewsMarquee() {
  const theme = useTheme();
  const { news } = useDashboardConfig();

  if (news.length === 0) return null;

  return (
    <Box
      sx={{
        width: '100%',
        minWidth: 0,
        mb: 2,
        borderBottom: 1,
        borderColor: 'divider',
        background: `linear-gradient(90deg, ${theme.palette.primary.main}22 0%, ${theme.palette.primary.dark}18 50%, ${theme.palette.primary.main}22 100%)`,
        py: 0.75,
        overflow: 'hidden',
      }}
    >
      <Marquee speed={40} pauseOnHover gradient={false}>
        {news.map((item, i) => (
          <Box key={i} component="span" sx={{ display: 'inline-flex', alignItems: 'center', mx: 2 }}>
            {i > 0 && (
              <Box component="span" sx={{ color: 'text.secondary', fontSize: '0.75rem', mr: 1.5 }}>
                •
              </Box>
            )}
            {item.url && item.url.trim() !== '' ? (
              <Link
                href={item.url}
                target={item.url.startsWith('http') ? '_blank' : undefined}
                rel={item.url.startsWith('http') ? 'noopener' : undefined}
                color="primary.main"
                underline="hover"
                sx={{ fontWeight: 500 }}
              >
                {item.name}
              </Link>
            ) : (
              <Typography component="span" variant="body2" sx={{ fontWeight: 500, color: 'text.primary' }}>
                {item.name}
              </Typography>
            )}
          </Box>
        ))}
      </Marquee>
    </Box>
  );
}
