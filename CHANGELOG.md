# Changelog

All notable changes to **adn-monitor** (monitor + dashboard) are documented here.

<!-- version list -->

## v2.0.0-rc.14 (2026-06-19)

### Bug Fixes

- Drop force patch on master stable release
  ([`0c8b94e`](https://github.com/ce5rpy/ADN-Monitor/commit/0c8b94ecd327275d66fdfb432caae794fe7d8951))

- Use explicit stable-release script on master
  ([`00cb588`](https://github.com/ce5rpy/ADN-Monitor/commit/00cb588964e3d8745396b67009648f3b3967099d))

### Chores

- Prepare stable 2.0.0 release and README server pairing
  ([#36](https://github.com/ce5rpy/ADN-Monitor/pull/36),
  [`4f6878f`](https://github.com/ce5rpy/ADN-Monitor/commit/4f6878fb9df88546cb7b0c20d57e06f8fa2302a3))


## v2.0.0-rc.13 (2026-06-19)

### Bug Fixes

- Show monitor version from pyproject at runtime
  ([#35](https://github.com/ce5rpy/ADN-Monitor/pull/35),
  [`3ae1449`](https://github.com/ce5rpy/ADN-Monitor/commit/3ae1449d0cfe41565d40049ea94938fcf19aa900))


## v2.0.0-rc.12 (2026-06-19)

### Bug Fixes

- Correct PSR commit_message and ensure GitHub Release is created
  ([#34](https://github.com/ce5rpy/ADN-Monitor/pull/34),
  [`ca1ddc8`](https://github.com/ce5rpy/ADN-Monitor/commit/ca1ddc84a0a87e37e7088bd2f98e67b907ff64ce))

- Replace custom release script with python-semantic-release
  ([#33](https://github.com/ce5rpy/ADN-Monitor/pull/33),
  [`e1a8730`](https://github.com/ce5rpy/ADN-Monitor/commit/e1a873063585ec9944058a0ad146d1de80de277f))


## [2.0.0-rc.11](https://github.com/ce5rpy/ADN-Monitor/compare/v2.0.0-rc.10...v2.0.0-rc.11) (2026-06-19)


### Fixed

* clear stale autorelease labels and fix Release PR title pattern ([#29](https://github.com/ce5rpy/ADN-Monitor/issues/29)) ([daa6f45](https://github.com/ce5rpy/ADN-Monitor/commit/daa6f45efce625ecfb629656e0ccfcdc0c1f0068))
* set group-pull-request-title-pattern for Release Please ([#27](https://github.com/ce5rpy/ADN-Monitor/issues/27)) ([da065cd](https://github.com/ce5rpy/ADN-Monitor/commit/da065cdcfc2df5935d33d9d03889929a4d59e093))
* update README version and release workflow notes ([#28](https://github.com/ce5rpy/ADN-Monitor/issues/28)) ([9896db3](https://github.com/ce5rpy/ADN-Monitor/commit/9896db32fa9e3e85457d7944d742469bfba3a187))

## [2.0.0-rc.10](https://github.com/ce5rpy/ADN-Monitor/compare/v2.0.0-rc.9...v2.0.0-rc.10) (2026-06-19)


### Fixed

* simplify release flow to develop-only with auto-merge ([#25](https://github.com/ce5rpy/ADN-Monitor/issues/25)) ([c229ffa](https://github.com/ce5rpy/ADN-Monitor/commit/c229ffa9cae62236c7c1da630823d8d4e2fcce63))

## [2.0.0-rc.9](https://github.com/ce5rpy/ADN-Monitor/compare/v2.0.0-rc.8...v2.0.0-rc.9) (2026-06-19)

### Fixed

* **ci:** always publish GitHub releases from release-please; hard-sync develop after release

## [2.0.0-rc.8](https://github.com/ce5rpy/ADN-Monitor/compare/v2.0.0-rc.7...v2.0.0-rc.8) (2026-06-19)


### Added

* add configurable news marquee below logo ([109adb9](https://github.com/ce5rpy/ADN-Monitor/commit/109adb93dc24bf2bf887914f47b11ad87e79bdf1))
* add Hotspot Proxy for ADN DMR Peer Server ([b706d6c](https://github.com/ce5rpy/ADN-Monitor/commit/b706d6c6cf1ac867d26119be3321bfed0fe66eb7))
* add LOGGER.ENABLED toggle to monitor and proxy ([4880e53](https://github.com/ce5rpy/ADN-Monitor/commit/4880e530d4f9c52b79a23020abf53f9642b4a31b))
* **assets:** img/flags, img/bridges, ADN icon 100.png ([f54c0f5](https://github.com/ce5rpy/ADN-Monitor/commit/f54c0f552da55172ca2b4034ac828930e9433dcd))
* **calc:** TS2 always in Duplex, Simplex uses TS2 only; consistent ts2 state across mode ([c834bf5](https://github.com/ce5rpy/ADN-Monitor/commit/c834bf5c18ae2d27600d2e4171e71d0d4d1bc7c9))
* **dashboard:** server status page, API proxy, OpenBridge dedupe ([556f354](https://github.com/ce5rpy/ADN-Monitor/commit/556f354053e894d636963441b1b0d07dc29b5b62))
* **frontend:** add Active QSO box to Last Heard, single log table only ([cc3b68d](https://github.com/ce5rpy/ADN-Monitor/commit/cc3b68d71e070ba75ad02900ae64ef83b70a495f))
* **frontend:** add Console page with configurable visibility ([ee8807a](https://github.com/ce5rpy/ADN-Monitor/commit/ee8807a28010f7a7d3ae8fde5c123db3d59c9f8c))
* **frontend:** defer OpenBridge stream rows until 1s visible ([692cba6](https://github.com/ce5rpy/ADN-Monitor/commit/692cba6a74c48ba5e1ce9ec4a888639c5a78b9ab))
* **frontend:** improve Linked Systems mobile layout and table polish ([74b8146](https://github.com/ce5rpy/ADN-Monitor/commit/74b8146503c2d86767f7877d822897d3e7c48f2b))
* **frontend:** isolate WebSocket groups and refine connected time display ([a964382](https://github.com/ce5rpy/ADN-Monitor/commit/a96438273d300e9210f8591cb201480a2da9bbc4))
* **frontend:** options calculator voice language selector with i18n ([22121e6](https://github.com/ce5rpy/ADN-Monitor/commit/22121e66fbd12df00f13f13e3e65ac5917db3be9))
* **frontend:** remove DIAL from options calculator and add trailing semicolon ([862cc57](https://github.com/ce5rpy/ADN-Monitor/commit/862cc57d3318dd8682ef8b4725903b3ad7aedaf7))
* **frontend:** show Monitor/Server versions in footer ([afd6a72](https://github.com/ce5rpy/ADN-Monitor/commit/afd6a72d8cb9ff2a1958ab7bb772cbe3db31efa3))
* **frontend:** use cookie for language preference, fallback config → browser → en ([9c43f66](https://github.com/ce5rpy/ADN-Monitor/commit/9c43f66679de5fa8b9b52b0df68cdf5e8afc4138))
* **i18n:** sync locales, remove unused keys, add missing keys ([67ff8e9](https://github.com/ce5rpy/ADN-Monitor/commit/67ff8e938dc52dc37ebcdbdd3f3ec927dda89b65))
* Last Heard tables (Dashboard and LastHeardLog) ([515844a](https://github.com/ce5rpy/ADN-Monitor/commit/515844a312577a30a3eb203a1d33caa1a20040fc))
* live monitor refresh on CONFIG push and lnksys open ([c4b71ab](https://github.com/ce5rpy/ADN-Monitor/commit/c4b71abb7e92ff0253e47fcd61e5c1538f15b94d))
* live Time Connected clocks via CONNECTED_SINCE ([c23378d](https://github.com/ce5rpy/ADN-Monitor/commit/c23378d7411779959bf5674abe3bb63e5c631b3d))
* **login:** add usage text for managing Options and static TGs in Self Service ([332dfe8](https://github.com/ce5rpy/ADN-Monitor/commit/332dfe8b1fec02facf0300e77970067890196533))
* **monitor:** alias download with BLAKE2b checksum, STALE_HOURS and REVIEW_INTERVAL_MINUTES ([b6762e6](https://github.com/ce5rpy/ADN-Monitor/commit/b6762e611d10906adefe7c7efbbdd3bd51451bdc))
* **monitor:** configurable min duration for dashboard table ([17135d0](https://github.com/ce5rpy/ADN-Monitor/commit/17135d0a275455394d1074b2d614ca08c8ac835c))
* **monitor:** legacy adn-dmr-server compatibility via HELLO and ServerMode ([cb62209](https://github.com/ce5rpy/ADN-Monitor/commit/cb622099b2d06257258bb6f15e4539598f864d10))
* **monitor:** merge Clients.options into PEER_OPTIONS and Static TG display ([4ced127](https://github.com/ce5rpy/ADN-Monitor/commit/4ced127285e33d542a36baca7db013a98398a8ef))
* **monitor:** MySQL reconnect and safe alias cache refresh ([99191eb](https://github.com/ce5rpy/ADN-Monitor/commit/99191eb368467259a49ec49bdbf633cd2a6623e2))
* **monitor:** slim WebSocket ctable, dedup, and safety sync ([e6e22bc](https://github.com/ce5rpy/ADN-Monitor/commit/e6e22bc077d56a377e0020f9330947e599d4654e))
* **monitor:** timezone display, IPv6 WebSocket bind, and hardening ([8b4384f](https://github.com/ce5rpy/ADN-Monitor/commit/8b4384fb39642b798d2b07e82cb02e363410acb4))
* **monitor:** unify dashboard on FastAPI monitor.py ([8214a95](https://github.com/ce5rpy/ADN-Monitor/commit/8214a95597f5c128bef4a9c247c59169e141a8d7))
* **proxy:** add dedicated adn-proxy.yaml with legacy fallback ([14b7cf7](https://github.com/ce5rpy/ADN-Monitor/commit/14b7cf717626c768dc0a3ce90084a281241f6887))
* **proxy:** PORT+GENERATOR pool; drop DEST_PORT_END from config ([8dfd888](https://github.com/ce5rpy/ADN-Monitor/commit/8dfd888bcb0734bd337ac9bc98eec18682659208))
* reopen log files on SIGUSR2 for logrotate ([23e2b40](https://github.com/ce5rpy/ADN-Monitor/commit/23e2b40bb47390765712634ce9795746c1eed6e8))
* **report:** consume v2 topology, routing, voice events and deltas ([dd4ea0c](https://github.com/ce5rpy/ADN-Monitor/commit/dd4ea0cbe87b83e56d4eb0f7e458cf0b2cdf910a))
* **report:** ignore INGRESS for CTABLE; log full ingress for debug ([ac76230](https://github.com/ce5rpy/ADN-Monitor/commit/ac7623029dad23963e13110c74718b62c06f4fcf))
* **self-service:** add Options calculator dialog and hint link ([efddb9f](https://github.com/ce5rpy/ADN-Monitor/commit/efddb9faee75d06a00fa5f44d08d5b2269ef0047))
* **TgList:** Country column with flag and name ([43665ad](https://github.com/ce5rpy/ADN-Monitor/commit/43665ad68e85e943eb0c5a4f05ede86fd167bdc5))
* **ui:** favicon, background image, nav_links as submenu, i18n ([54f89a4](https://github.com/ce5rpy/ADN-Monitor/commit/54f89a483ae4158f46ffcfad7e5339027c7298df))
* **ui:** improve layout and responsiveness ([bbcb352](https://github.com/ce5rpy/ADN-Monitor/commit/bbcb3527d18090afc6505d29ef70d43565c884e2))
* **ws:** auto-reconnect with exponential backoff when WebSocket closes ([1ee1eba](https://github.com/ce5rpy/ADN-Monitor/commit/1ee1eba2671efdf87e16897e78a65e5f62f4bdf7))


### Fixed

* **auth:** resolve client IP behind reverse proxy for login-by-ip ([2e47e4f](https://github.com/ce5rpy/ADN-Monitor/commit/2e47e4fc6da399099a68373b4ec4c3cffbcc18ab))
* **backend:** set modified=1 when updating device options so proxy pushes RPTO ([93ec9b0](https://github.com/ce5rpy/ADN-Monitor/commit/93ec9b0e7434c8efc14e9477132b58cdee985e22))
* clear stale voice TS chips when static TG is removed ([6cb0bd9](https://github.com/ce5rpy/ADN-Monitor/commit/6cb0bd95fa8fa5e5b44d140810e775b7104aa2d2))
* clear stale voice TS chips when static TG is removed ([d36d7d2](https://github.com/ce5rpy/ADN-Monitor/commit/d36d7d26c9e4bef81480c2b9b76fb54c15eae101))
* echo TG 9990 live chips and UA session exclusions ([#10](https://github.com/ce5rpy/ADN-Monitor/issues/10)) ([0b17e78](https://github.com/ce5rpy/ADN-Monitor/commit/0b17e786c92a450d6a06916106fda00388982441))
* **frontend:** Active QSO cards always show red (our server) or green (OpenBridge) border ([92333cb](https://github.com/ce5rpy/ADN-Monitor/commit/92333cbb1ecabd44faa77e606f784b939184d8db))
* **frontend:** dashboard chips RX/TX contrast, light mode Paper border, PEERS Source/Dest chips, dark default theme ([c802640](https://github.com/ce5rpy/ADN-Monitor/commit/c80264039e1da0bf67c35fb151cf2ae63e5a8918))
* **frontend:** keep date, time and duration headers on one row; align Systems table columns ([1d54bde](https://github.com/ce5rpy/ADN-Monitor/commit/1d54bde4a8582ab7ca01b0474e16c4125027b310))
* **frontend:** make logo scroll with content on all viewports including mobile portrait ([854ff81](https://github.com/ce5rpy/ADN-Monitor/commit/854ff814e3b6d235f0aacffba6d1c309cff76b25))
* **frontend:** multiplex dashboard WebSocket groups on one connection ([5c64e3b](https://github.com/ce5rpy/ADN-Monitor/commit/5c64e3b38db3d6dd0bd6c1210ccfc20f00e270b0))
* **frontend:** options fields single-line to prevent Enter adding newlines ([8482674](https://github.com/ce5rpy/ADN-Monitor/commit/8482674ee624a3a08f6b49f8f2138c0adae6768c))
* **help:** correct SelfCare tutorial URL to how-to-selfcare ([54c88e9](https://github.com/ce5rpy/ADN-Monitor/commit/54c88e99fb7a0aaa444b72da7777e3301a58f258))
* **monitor:** add mysqlclient to requirements.txt ([a54fa1a](https://github.com/ce5rpy/ADN-Monitor/commit/a54fa1a64d577981081f77d7bcfdd03de4e55041))
* **monitor:** clear OpenBridge stream on END,RX for all OBP systems ([4783b43](https://github.com/ce5rpy/ADN-Monitor/commit/4783b43204c1bcece2f9684d5948e98eef18ab84))
* **monitor:** color peer TS chip from OPTIONS static TG slot ([512facc](https://github.com/ce5rpy/ADN-Monitor/commit/512facc1cbc4dd6a2b51b5830c299848408d943f))
* **monitor:** correct checksum docstring (blake2b not sha512) ([0b332c6](https://github.com/ce5rpy/ADN-Monitor/commit/0b332c617dd5fc1eb9aaa79486fbef3502db7bc2))
* **monitor:** handle PRIVATE VOICE like GROUP VOICE for BRDG_EVENT ([1ca6f2e](https://github.com/ce5rpy/ADN-Monitor/commit/1ca6f2eb202b38bb209dca3147ec46a93437fba9))
* **monitor:** honor EMPTY_MASTERS when building lnksys ctable ([efa7976](https://github.com/ce5rpy/ADN-Monitor/commit/efa797601995195feb3b046ab0cb5cf3904eaf1a))
* **monitor:** last heard duration merge and sys_dict retention ([f78015c](https://github.com/ce5rpy/ADN-Monitor/commit/f78015c21b8677f7058f6543e17ad90a4611036b))
* **monitor:** OpenBridge RTS per-OBP; VOICE log RX/TX; skip QRZ for BRIDGE ([6fed611](https://github.com/ce5rpy/ADN-Monitor/commit/6fed61161c1abf4132c0e1f3b88ba0107cedd4ab))
* **monitor:** per-peer static TG chips from server OPTIONS only ([97a232b](https://github.com/ce5rpy/ADN-Monitor/commit/97a232b270ee19704f3e5ff58dd39aba02bd2050))
* **monitor:** preserve SINGLE=0 multi-dynamic chips across dashboard_state ([71f9aa1](https://github.com/ce5rpy/ADN-Monitor/commit/71f9aa1d9f5cd0af48821bf5c9eec36ba0298817))
* **monitor:** rebuild CTABLE from dashboard_state snapshots (D-25) ([fb10ee2](https://github.com/ce5rpy/ADN-Monitor/commit/fb10ee2d6c1ff7d3d2504048106f1e737a681ac1))
* **monitor:** restore slim-wire dashboard realtime updates ([65836f4](https://github.com/ce5rpy/ADN-Monitor/commit/65836f46f3949c4ea93974c3ca4e4bf8d0145ba2))
* **monitor:** send empty main WebSocket payload when DB has no rows ([a17698d](https://github.com/ce5rpy/ADN-Monitor/commit/a17698d2a2a03dcb733e4e2a105e27ecab476689))
* **monitor:** stabilize lnksys CTABLE across report reconnect and refresh ([6ccbe5d](https://github.com/ce5rpy/ADN-Monitor/commit/6ccbe5d2b839f33b9e0eec2bccef86f6c2a3a067))
* **monitor:** Top TG query and add UI zoom control ([c8eb999](https://github.com/ce5rpy/ADN-Monitor/commit/c8eb9995d499fedebc940b14a4ae0b18025fa22d))
* **monitor:** UTC persistence, lastheard display, tgcount UTC day ([f50e448](https://github.com/ce5rpy/ADN-Monitor/commit/f50e448136c0922e735fdf0e9a4d865fd85e1a02))
* **proxy:** resolve PROXY.MASTER hostname to IP at startup ([e7e50a0](https://github.com/ce5rpy/ADN-Monitor/commit/e7e50a0c39c32a3ecf5b243bc6882567a20aab28))
* read dashboard version from pyproject.toml ([#19](https://github.com/ce5rpy/ADN-Monitor/issues/19)) ([d3bf164](https://github.com/ce5rpy/ADN-Monitor/commit/d3bf16422448e8ac9147feb0fcebf7e068395ea4))
* reduce spacing between Active QSO and table on Dashboard ([4740509](https://github.com/ce5rpy/ADN-Monitor/commit/4740509ea70fee96d2a5f772d294997f4a7d83d6))
* **report:** static TG from v2 topology and targeted WS refresh ([a319639](https://github.com/ce5rpy/ADN-Monitor/commit/a31963965bf9e39d78f70aa136c7f321738ce532))
* **report:** use topology connected_at for stable link timers ([42cb0b5](https://github.com/ce5rpy/ADN-Monitor/commit/42cb0b5529394d0544297271a8228175b826aabc))
* **self-service:** ensure options always stored and displayed with trailing semicolon ([07c776b](https://github.com/ce5rpy/ADN-Monitor/commit/07c776be56bda302f5c7425dfb2b19e9881eb56d))
* show Linked Systems summary cards when ctable is empty ([#12](https://github.com/ce5rpy/ADN-Monitor/issues/12)) ([6ca1507](https://github.com/ce5rpy/ADN-Monitor/commit/6ca15076c71c3f92522c234604e5c97168d67267))
* solid background for marquee and active QSO with background image ([3069e78](https://github.com/ce5rpy/ADN-Monitor/commit/3069e782eaf309d65b58bee5dab21a784cf5bede))
* **Systems:** show TX/RX green/red on PEERS table slot chips ([f974516](https://github.com/ce5rpy/ADN-Monitor/commit/f9745161949e695289f4105b06793d55f3ceedba))
* TG 4000 must not appear as dynamic UA on monitor ([#7](https://github.com/ce5rpy/ADN-Monitor/issues/7)) ([083956e](https://github.com/ce5rpy/ADN-Monitor/commit/083956e8ac26bfb4d4e08a274f4d5d8917ad3a8d))
* transparent logo area, rounded logo, semi-transparent footer ([8d717b3](https://github.com/ce5rpy/ADN-Monitor/commit/8d717b356bd9ad8c095c6a740b3a909118a6e82b))
* **ui:** center and enlarge landscape logo on mobile ([0f853ac](https://github.com/ce5rpy/ADN-Monitor/commit/0f853ac43535a2b7506c549baa85cac86cb6c38e))
* **ui:** center summary card text on Systems page ([c909aac](https://github.com/ce5rpy/ADN-Monitor/commit/c909aacb591d91fb0d1a8b4b0ec32b2f9ef2e615))
* **ui:** OpenBridge row height and Server Status table ([1dd5bb3](https://github.com/ce5rpy/ADN-Monitor/commit/1dd5bb3b0d8e74f6a5b23c2fcdca915bf37d3237))
* **ui:** remove duplicate Info menu ([395554a](https://github.com/ce5rpy/ADN-Monitor/commit/395554a0688a0983653ab69d924c04c342de8509))


### Performance

* **monitor:** cache lastheard and lighten dashboard fingerprints ([317f685](https://github.com/ce5rpy/ADN-Monitor/commit/317f685f7ed9a1521c6137143942d0f6ab2a3b49))

## [2.0.0-rc.7](https://github.com/ce5rpy/ADN-Monitor/compare/v2.0.0-rc.6...v2.0.0-rc.7) (2026-06-19)


### Fixed

* read dashboard version from pyproject.toml ([#19](https://github.com/ce5rpy/ADN-Monitor/issues/19)) ([d3bf164](https://github.com/ce5rpy/ADN-Monitor/commit/d3bf16422448e8ac9147feb0fcebf7e068395ea4))
* use Release Please `prerelease` versioning so RC bumps increment `rc.N` (not `2.0.0-rc.6` → `2.0.1-rc.6`)

## [2.0.0-rc.6] - 2026-06-19

Pairs with **adn-server 2.0.0-rc.4**.

### Fixed

- **Linked Systems** — show repeater/hotspot/bridge summary cards with zero counts when the lnksys WebSocket delivers an empty CTABLE instead of "Waiting for server info...".

### Changed

- **Dependencies** — declare `itsdangerous>=2.1` in `monitor/requirements.txt` for FastAPI `SessionMiddleware` (self-service auth cookies).

### Compatibility

- **Server:** adn-server **2.0.0-rc.4** or newer.

## [2.0.0-rc.5] - 2026-06-18

Pairs with **adn-server 2.0.0-rc.4**.

### Added

- **Help page** — expanded FAQ and synced i18n strings across all dashboard locales.

### Fixed

- **Echo TG 9990** — no dynamic UA chip; live RX/TX chips preserved during `build_tgstats` prune; ECHO master bridge TX activity uses wire timeslot for slot chips.

### Compatibility

- **Server:** adn-server **2.0.0-rc.4** or newer (echo monitor events + inject-only remap).

## [2.0.0-rc.4] - 2026-06-17

Pairs with **adn-server 2.0.0-rc.3**.

### Added

- **Schema migration `004_peer_dynamic_tgs`** — MariaDB table for server-side dynamic TG persistence (shared with adn-server).

### Fixed

- **TG 4000** — never shown as a dynamic UA chip; `START,RX` dest 4000 clears peer UA state without re-registering 4000 (pairs with server `INGRESS` BRDG_EVENT).

### Compatibility

- **Server:** adn-server **2.0.0-rc.3** or newer (dynamic TG persistence + TG 4000 monitor events).

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
