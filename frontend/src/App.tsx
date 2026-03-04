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

import { useMemo, useState, lazy, Suspense } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Menu,
  MenuItem,
  Select,
  FormControl,
  SelectChangeEvent,
  Box,
  Container,
  CircularProgress,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useTranslation } from 'react-i18next';

import Footer from './components/Footer';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Systems = lazy(() => import('./pages/Systems'));
const StaticTg = lazy(() => import('./pages/StaticTg'));
const OpenBridge = lazy(() => import('./pages/OpenBridge'));
const TopTg = lazy(() => import('./pages/TopTg'));
const LastHeardLog = lazy(() => import('./pages/LastHeardLog'));
const Console = lazy(() => import('./pages/Console'));
const Calc = lazy(() => import('./pages/Calc'));
const TgList = lazy(() => import('./pages/TgList'));
const BridgeList = lazy(() => import('./pages/BridgeList'));
const Login = lazy(() => import('./pages/Login'));
const SelfService = lazy(() => import('./pages/SelfService'));
import { useDashboardConfig } from './context/DashboardConfigContext';

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'es', label: 'Español' },
  { code: 'pt', label: 'Português' },
  { code: 'fr', label: 'Français' },
  { code: 'de', label: 'Deutsch' },
  { code: 'it', label: 'Italiano' },
  { code: 'nl', label: 'Nederlands' },
  { code: 'ca', label: 'Català' },
  { code: 'bg', label: 'Български' },
  { code: 'zh', label: '中文' },
  { code: 'et', label: 'Eesti' },
  { code: 'el', label: 'Ελληνικά' },
  { code: 'pl', label: 'Polski' },
  { code: 'sr', label: 'Српски' },
  { code: 'th', label: 'ไทย' },
  { code: 'tr', label: 'Türkçe' },
  { code: 'uk', label: 'Українська' },
];

function App() {
  const { t, i18n } = useTranslation();
  const dashboard = useDashboardConfig();
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('mode');
    return saved === 'dark' || saved === null;
  });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [infoAnchor, setInfoAnchor] = useState<null | HTMLElement>(null);

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? 'dark' : 'light',
          primary: {
            main: darkMode ? '#2dd4bf' : '#0d9488',
            light: darkMode ? '#5eead4' : '#14b8a6',
            dark: darkMode ? '#14b8a6' : '#0f766e',
          },
          secondary: {
            main: darkMode ? '#a78bfa' : '#7c3aed',
          },
          background: {
            default: darkMode ? '#0f172a' : '#f8fafc',
            paper: darkMode ? '#1e293b' : '#ffffff',
          },
        },
        typography: {
          fontFamily: '"Plus Jakarta Sans", "Source Sans 3", "Roboto", sans-serif',
          fontSize: 14,
          h6: { fontWeight: 600 },
          subtitle1: { fontWeight: 600 },
          subtitle2: { fontWeight: 600 },
        },
        shape: {
          borderRadius: 12,
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
                borderRadius: 10,
                fontWeight: 600,
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                borderRadius: 12,
                backgroundImage: 'none',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 12,
              },
            },
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                borderRadius: 0,
              },
            },
          },
          MuiTableRow: {
            styleOverrides: {
              root: {
                '&:last-child td': { borderBottom: 0 },
              },
            },
          },
          MuiTableCell: {
            styleOverrides: {
              root: {
                borderBottom: '1px solid',
                borderColor: 'divider',
              },
            },
          },
        },
      }),
    [darkMode]
  );

  const toggleTheme = () => {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem('mode', next ? 'dark' : 'light');
  };

  const handleLanguageChange = (e: SelectChangeEvent<string>) => {
    i18n.changeLanguage(e.target.value);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          ...(dashboard.background && {
            backgroundImage: 'url(/img/bk.jpg)',
            backgroundAttachment: 'fixed',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }),
        }}
      >
        <AppBar
          position="sticky"
          color="default"
          elevation={0}
          sx={{
            borderBottom: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <Toolbar sx={{ flexWrap: 'wrap', gap: 0.5, minHeight: { xs: 56, sm: 64 }, py: 0.5 }}>
            <IconButton
              edge="start"
              color="inherit"
              sx={{ mr: 0.5, display: { md: 'none' } }}
              onClick={(e) => setAnchorEl(e.currentTarget)}
              aria-label={t('nav_menu', { defaultValue: 'Open menu' })}
            >
              <MenuIcon />
            </IconButton>
            <Box
              component={Link}
              to="/"
              sx={{
                display: 'flex',
                alignItems: 'center',
                flexGrow: 1,
                textDecoration: 'none',
                color: 'primary.main',
              }}
            >
              <Typography variant="h6" component="span" fontWeight={700} color="inherit">
                {dashboard.title}
              </Typography>
            </Box>

            <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 0.25 }}>
              <Button color="inherit" component={Link} to="/" sx={{ fontWeight: 500 }}>
                {t('nav_dash', { defaultValue: 'Dashboard' })}
              </Button>
              <Button color="inherit" component={Link} to="/systems">
                {t('nav_lnksys', { defaultValue: 'Linked Systems' })}
              </Button>
              <Button color="inherit" component={Link} to="/systemstg">
                {t('nav_statg', { defaultValue: 'Static TG' })}
              </Button>
              <Button color="inherit" component={Link} to="/openbridge">
                {t('nav_opb', { defaultValue: 'OpenBridge' })}
              </Button>
              <Button color="inherit" component={Link} to="/toptg">
                {t('nav_tptg', { defaultValue: "Top TG's" })}
              </Button>
              {dashboard.selfService && (
                <Button color="inherit" component={Link} to="/self-service" onClick={() => navigate('/self-service')}>
                  {t('self_service', { defaultValue: 'Self-service' })}
                </Button>
              )}
              <Button
                color="inherit"
                component="a"
                href="https://selfcare.adn.systems/"
                target="_blank"
                rel="noopener noreferrer"
                sx={{ fontWeight: 500 }}
              >
                {t('selfcare', { defaultValue: 'SelfCare' })}
              </Button>
              <Button color="inherit" onClick={(e) => setInfoAnchor(e.currentTarget)}>
                {t('nav_info', { defaultValue: 'Info' })}
              </Button>
              {(dashboard.navLinks?.items?.length ?? 0) > 0 &&
                dashboard.navLinks.items.map((item, idx) => (
                  <Button
                    key={idx}
                    color="inherit"
                    component="a"
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ fontWeight: 500 }}
                  >
                    {item.name}
                  </Button>
                ))}
            </Box>

            <FormControl size="small" sx={{ minWidth: 120, mx: 0.5 }}>
              <Select
                value={LANGUAGES.find((l) => l.code === i18n.language || l.code === i18n.language?.split(/[-_]/)[0])?.code ?? 'en'}
                onChange={handleLanguageChange}
                variant="outlined"
                sx={{
                  height: 36,
                  fontSize: '0.875rem',
                  borderRadius: 2,
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'divider' },
                }}
              >
                {LANGUAGES.map(({ code, label }) => (
                  <MenuItem key={code} value={code}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <IconButton onClick={toggleTheme} color="inherit" aria-label={darkMode ? 'Light mode' : 'Dark mode'}>
              {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Toolbar>
        </AppBar>

        <Box
          sx={{
            width: '100%',
            display: 'flex',
            justifyContent: 'center',
            py: 2,
            px: 2,
            borderBottom: 1,
            borderColor: 'divider',
            bgcolor: 'background.default',
          }}
        >
          <Container maxWidth="xl" sx={{ display: 'flex', justifyContent: 'center' }}>
            <Box
              component="img"
              src="/img/logo.png"
              alt=""
              sx={{ width: '50%', maxWidth: '50%', height: 'auto', objectFit: 'contain', display: 'block' }}
            />
          </Container>
        </Box>

        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
          <MenuItem component={Link} to="/" onClick={() => setAnchorEl(null)}>
            {t('nav_dash')}
          </MenuItem>
          <MenuItem component={Link} to="/systems" onClick={() => setAnchorEl(null)}>
            {t('nav_lnksys')}
          </MenuItem>
          <MenuItem component={Link} to="/systemstg" onClick={() => setAnchorEl(null)}>
            {t('nav_statg')}
          </MenuItem>
          <MenuItem component={Link} to="/openbridge" onClick={() => setAnchorEl(null)}>
            {t('nav_opb')}
          </MenuItem>
          <MenuItem component={Link} to="/toptg" onClick={() => setAnchorEl(null)}>
            {t('nav_tptg')}
          </MenuItem>
          {dashboard.selfService && (
            <MenuItem component={Link} to="/self-service" onClick={() => setAnchorEl(null)}>
              {t('self_service', { defaultValue: 'Self-service' })}
            </MenuItem>
          )}
          <MenuItem
            component="a"
            href="https://selfcare.adn.systems/"
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => setAnchorEl(null)}
          >
            {t('selfcare', { defaultValue: 'SelfCare' })}
          </MenuItem>
          {dashboard.showConsole && (
            <MenuItem component={Link} to="/console" onClick={() => setAnchorEl(null)}>
              {t('nav_console')}
            </MenuItem>
          )}
          <MenuItem component={Link} to="/lastheard" onClick={() => setAnchorEl(null)}>
            {t('nav_lsthrd')}
          </MenuItem>
          <MenuItem component={Link} to="/calc" onClick={() => setAnchorEl(null)}>
            {t('nav_calc')}
          </MenuItem>
          <MenuItem component={Link} to="/wwtg" onClick={() => setAnchorEl(null)}>
            {t('nav_tglst')}
          </MenuItem>
          <MenuItem component={Link} to="/wwbridges" onClick={() => setAnchorEl(null)}>
            {t('nav_brdglst')}
          </MenuItem>
          {(dashboard.navLinks?.items?.length ?? 0) > 0 &&
            dashboard.navLinks.items.map((item, idx) => (
              <MenuItem
                key={idx}
                component="a"
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setAnchorEl(null)}
              >
                {item.name}
              </MenuItem>
            ))}
        </Menu>

        <Menu anchorEl={infoAnchor} open={Boolean(infoAnchor)} onClose={() => setInfoAnchor(null)}>
          {dashboard.showConsole && (
            <MenuItem component={Link} to="/console" onClick={() => setInfoAnchor(null)}>
              {t('nav_console')}
            </MenuItem>
          )}
          <MenuItem component={Link} to="/calc" onClick={() => setInfoAnchor(null)}>
            {t('nav_calc')}
          </MenuItem>
          <MenuItem component={Link} to="/wwtg" onClick={() => setInfoAnchor(null)}>
            {t('nav_tglst')}
          </MenuItem>
          <MenuItem component={Link} to="/wwbridges" onClick={() => setInfoAnchor(null)}>
            {t('nav_brdglst')}
          </MenuItem>
          <MenuItem component={Link} to="/lastheard" onClick={() => setInfoAnchor(null)}>
            {t('nav_lsthrd')}
          </MenuItem>
        </Menu>

        <Container component="main" sx={{ flex: 1, py: 3, px: { xs: 2, sm: 3 } }} maxWidth="xl">
          <Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress /></Box>}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/systems" element={<Systems />} />
              <Route path="/systemstg" element={<StaticTg />} />
              <Route path="/openbridge" element={<OpenBridge />} />
              <Route path="/toptg" element={<TopTg />} />
              <Route path="/lastheard" element={<LastHeardLog />} />
              <Route path="/console" element={<Console />} />
              <Route path="/calc" element={<Calc />} />
              <Route path="/wwtg" element={<TgList />} />
              <Route path="/wwbridges" element={<BridgeList />} />
              <Route path="/login" element={<Login />} />
              <Route path="/self-service" element={<SelfService />} />
            </Routes>
          </Suspense>
        </Container>

        <Footer />
      </Box>
    </ThemeProvider>
  );
}

export default App;
