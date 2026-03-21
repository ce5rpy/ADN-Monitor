/*
 * ADN Monitor - compact table title (caption) to save vertical space vs separate Paper + h5.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';

/** First row of the table (HTML caption): compact title without a separate Paper block. */
export function TableCaptionTitle({ children }: { children: ReactNode }) {
  return (
    <Box
      component="caption"
      sx={{
        // MUI Table sets `& caption { captionSide: bottom }` with higher specificity than this node’s classes.
        captionSide: 'top !important',
        textAlign: 'left !important',
        p: '0 !important',
        m: 0,
        width: '100%',
      }}
    >
      <Typography
        variant="subtitle1"
        fontWeight={700}
        color="text.primary"
        sx={{
          py: 0.75,
          px: 1.5,
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: 'action.hover',
          display: 'block',
        }}
      >
        {children}
      </Typography>
    </Box>
  );
}
