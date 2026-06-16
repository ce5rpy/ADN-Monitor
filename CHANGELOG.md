# Changelog

All notable changes to **adn-monitor** (monitor + dashboard) are documented here.

## [2.0.0-rc.3] - 2026-06-16

Pairs with **adn-server 2.0.0-rc.2**.

### Fixed

- **Static TG + live QSO:** removing a static TG via self-service (OPTIONS / `dashboard_state`) clears active voice chips on the peer row instead of leaving the slot green.
- **Voice END cross-slot:** END clears every timeslot showing the call TG, not only the slot derived from current OPTIONS (fixes stuck chips after static TG removal mid-QSO).
- **`clean_te` timeout:** stale cleanup now resets `TRX` as well as source/destination fields so TS1/TS2 slot chips return to idle after ~3 minutes.

### Compatibility

- **Server:** adn-server **2.0.0-rc.2** or newer (report v2 slim wire).

## [2.0.0-rc.2] - 2026-06-16

Pairs with **adn-server 2.0.0-rc.2**.

### Fixed

- **Linked Systems TS chips:** on GROUP VOICE events, receiving hotspots highlight the timeslot where that TG appears in peer OPTIONS (`TS1_STATIC` / `TS2_STATIC`), not only the wire timeslot from the server. The transmitting peer still uses the wire slot.

### Compatibility

- **Server:** adn-server **2.0.0-rc.2** (cross-slot static TG downlink eligibility).

## [2.0.0-rc.1] - 2026-06-12

First v2 release candidate since **1.0.0** (~13 commits). Pairs with **adn-server 2.0.0-rc.1**.

### Added

- **FastAPI unified stack** — single `monitor/monitor.py`: REST self-service (`Clients` MySQL), WebSocket dashboard (`/ws`), report TCP ingest.
- **Report v2 ingest** — `dashboard_state` slim wire (**D-25**); polyglot fallback for legacy pickle; optional MQTT ingest.
- **Linked Systems (CTABLE)** — rebuild from `dashboard_state`; stable Time Connected via `connected_at`; targeted WS refresh.
- **Inject-only UX** — per-peer static TG chips from server OPTIONS; preserve `SINGLE=0` multi-dynamic bridge chips.
- **Performance** — lastheard row cache; lighter dashboard fingerprints on WS updates.

### Removed

- **`backend/`** — PHP Slim API (self-service and auth now in FastAPI).
- **`proxy/`** — standalone UDP hotspot proxy (use integrated **`PROXY`** in **adn-server**).

### Changed

- Single **`.env`** at project root; React frontend unchanged, served by FastAPI.
- Top TG stats query fix and map UI zoom control.

### Fixed

- Slim-wire realtime dashboard updates after server CONFIG push.
- MySQL reconnect and safe alias cache refresh under load.
- Login-by-IP behind reverse proxy (client IP from `X-Forwarded-For` / `X-Real-IP`).

### Compatibility

- **Server:** adn-server **2.0.0-rc.1** (report v2 slim wire, HELLO JSON).
- **Legacy server:** still connects when HELLO is absent (pickle/CSV ingest path).

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
