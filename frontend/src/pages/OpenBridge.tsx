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

import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useWebSocketGroup } from '../hooks/useWebSocket';
import QrzLink from '../components/QrzLink';

type StreamEntry = [string, string, string, number]; // TRX, sub_call, tg_str, timeout
type OpenBridgeEntry = {
  NETWORK_ID?: number | string;
  TARGET_IP?: string;
  TARGET_PORT?: string;
  STREAMS?: Record<string, StreamEntry>;
};
type Ctable = {
  MASTERS?: Record<string, unknown>;
  PEERS?: Record<string, unknown>;
  OPENBRIDGES?: Record<string, OpenBridgeEntry>;
};

type OpbPayload = { ctable?: Ctable; dbridges?: boolean };

export default function OpenBridge() {
  const { t } = useTranslation();
  const { data } = useWebSocketGroup('opb');
  const payload = data as OpbPayload | null;
  const ctable = payload?.ctable;
  const openbridges = ctable?.OPENBRIDGES ?? {};

  if (data == null) {
    return (
      <Box>
        <Typography color="text.secondary">{t('pre_wait', { defaultValue: 'Waiting for server info...' })}</Typography>
      </Box>
    );
  }

  const hasAny = Object.keys(openbridges).length > 0;

  return (
    <Box>
      <Paper
        variant="outlined"
        sx={{
          p: 2,
          mb: 2,
          bgcolor: 'background.paper',
          boxShadow: (theme) => theme.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)',
        }}
      >
        <Typography variant="h6" fontWeight={600}>
          {t('opb_title', { defaultValue: 'OpenBridge' })}
        </Typography>
      </Paper>

      {!hasAny && (
        <Typography color="text.secondary">
          {t('opb_no_data', { defaultValue: 'No OpenBridge entries from server.' })}
        </Typography>
      )}

      {hasAny && (
        <Paper sx={{ overflow: 'auto' }}>
          <TableContainer sx={{ minWidth: 0 }}>
            <Table size="small" stickyHeader sx={{ tableLayout: 'fixed', width: '100%', minWidth: 480 }}>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: '18%', minWidth: 88, maxWidth: 140, whiteSpace: 'nowrap' }}>{t('lnksys_system', { defaultValue: 'OpenBridge' })}</TableCell>
                  <TableCell sx={{ width: '12%', minWidth: 72, maxWidth: 88, whiteSpace: 'nowrap' }}>{t('lnksys_network_id', { defaultValue: 'Network ID' })}</TableCell>
                  <TableCell sx={{ width: '70%', minWidth: 120 }}>{t('opb_activity', { defaultValue: 'Active streams' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(openbridges).map(([name, ob]) => {
                  const streams = ob?.STREAMS ?? {};
                  const streamList = Object.entries(streams).map(([id, entry]) => {
                    const [dir, subCall, tgStr] = Array.isArray(entry) ? entry : [ '', '', '' ];
                    return { id, dir: String(dir), subCall: String(subCall), tg: String(tgStr) };
                  });
                  return (
                    <TableRow key={name}>
                      <TableCell sx={{ width: '18%', minWidth: 88, maxWidth: 140, whiteSpace: 'nowrap' }}>
                        <Typography fontWeight="bold" component="span" noWrap>{name}</Typography>
                      </TableCell>
                      <TableCell sx={{ width: '12%', minWidth: 72, maxWidth: 88, whiteSpace: 'nowrap' }}>
                        <Typography fontWeight="bold" component="span" noWrap>{String(ob?.NETWORK_ID ?? '')}</Typography>
                      </TableCell>
                      <TableCell sx={{ width: '70%', overflow: 'auto', minWidth: 120 }}>
                        <Box component="span" sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {streamList.length === 0 ? (
                            <Typography variant="body2" color="text.secondary">—</Typography>
                          ) : (
                            streamList.map(({ id, dir, subCall, tg }) => (
                              <Box key={id} component="span" sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap', mb: 0.5 }}>
                                <Chip size="small" label={dir} color={dir === 'RX' ? 'success' : dir === 'TX' ? 'error' : 'default'} />
                                <QrzLink callsign={subCall}>{subCall}</QrzLink>
                                <Typography component="span" variant="body2" color="text.secondary"> &gt;&gt; TG {tg}</Typography>
                              </Box>
                            ))
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
}
