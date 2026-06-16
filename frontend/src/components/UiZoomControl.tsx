/*
 * ADN Monitor - Compact zoom: icon opens +/- and level (cookie-persisted).
 */

import { useState } from 'react';
import { Box, IconButton, Popover, Typography } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomInOutlinedIcon from '@mui/icons-material/ZoomInOutlined';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import { useTranslation } from 'react-i18next';
import {
  MAX_UI_ZOOM,
  MIN_UI_ZOOM,
  UI_ZOOM_STEP,
  saveUiZoom,
} from '../utils/uiZoom';

type Props = {
  zoom: number;
  onZoomChange: (next: number) => void;
};

export default function UiZoomControl({ zoom, onZoomChange }: Props) {
  const { t } = useTranslation();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const open = Boolean(anchor);

  const bump = (delta: number) => {
    const next = saveUiZoom(zoom + delta);
    onZoomChange(next);
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={(e) => setAnchor(e.currentTarget)}
        aria-label={t('ui_zoom_group', { defaultValue: 'Page zoom' })}
        aria-expanded={open}
        aria-haspopup="true"
      >
        <ZoomInOutlinedIcon />
      </IconButton>
      <Popover
        open={open}
        anchorEl={anchor}
        onClose={() => setAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{ paper: { sx: { mt: 0.5 } } }}
      >
        <Box
          role="group"
          aria-label={t('ui_zoom_group', { defaultValue: 'Page zoom' })}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.25,
            px: 0.5,
            py: 0.25,
          }}
        >
          <IconButton
            size="small"
            color="inherit"
            disabled={zoom <= MIN_UI_ZOOM}
            onClick={() => bump(-UI_ZOOM_STEP)}
            aria-label={t('ui_zoom_out', { defaultValue: 'Zoom out' })}
          >
            <ZoomOutIcon fontSize="small" />
          </IconButton>
          <Typography
            variant="body2"
            component="span"
            sx={{ minWidth: 40, textAlign: 'center', fontWeight: 600, userSelect: 'none' }}
            aria-live="polite"
          >
            {zoom}%
          </Typography>
          <IconButton
            size="small"
            color="inherit"
            disabled={zoom >= MAX_UI_ZOOM}
            onClick={() => bump(UI_ZOOM_STEP)}
            aria-label={t('ui_zoom_in', { defaultValue: 'Zoom in' })}
          >
            <ZoomInIcon fontSize="small" />
          </IconButton>
        </Box>
      </Popover>
    </>
  );
}
