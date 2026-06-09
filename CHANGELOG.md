# Changelog

All notable changes to **adn-monitor** (monitor + dashboard) are documented here.

## [Unreleased]

### Removed

- **`backend/`** — PHP Slim API (replaced by FastAPI in `monitor.py`).
- **`proxy/`** — standalone UDP hotspot proxy (use integrated **`PROXY`** in **adn-server**).

### Changed

- Single entrypoint **`monitor/monitor.py`** (FastAPI: REST, WebSocket, report ingest).
- Single **`.env`** at project root.

## [1.0.0] - 2026-06-06

First stable public release of the ADN Systems monitor stack.

### Added

- **Monitor** (`monitor/`): Python/Twisted process — report client, WebSocket dashboard, MySQL persistence, alias sync.
- **Frontend** (`frontend/`): React dashboard (systems, OpenBridge, last heard, self-service UI).
- **Backend** (`backend/`): PHP REST API (auth, config, self-service).
- **Proxy** (`proxy/`): UDP hotspot fan-in with `adn-proxy.yaml` and PORT+GENERATOR pool.
- HELLO-aware report client: auto-detect **legacy** (adn-dmr-server) vs **v2** (new-adn-server JSON HELLO).
- Live refresh on CONFIG push, linked-system table (CTABLE), Time Connected clocks.
- WebSocket payload deduplication and grouped multiplexing on one connection.
- LOGGER.ENABLED toggle; SIGUSR2 log reopen for logrotate.

### Fixed (highlights)

- lnksys CTABLE stability across report reconnect and refresh.
- OpenBridge stream clear on END,RX; RTS per-OBP system.
- Last heard duration merge and timezone display (stored UTC → configured TIMEZONE).

### Compatibility

- **Server:** adn-server **1.0.0** (report HELLO mode v2 + pickle snapshots).
- **Legacy:** still connects to old adn-dmr-server when HELLO is absent (legacy mode).
