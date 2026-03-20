# ADN Systems Monitor

Dashboard for ADN networks: PHP API, React frontend, and a Python process that connects to the ADN/peer report server, writes to the database, and serves live data over WebSocket.

---

## Architecture

| Part        | Folder      | Role |
|-------------|-------------|------|
| **Backend**  | `backend/`  | REST API (PHP/Slim): dashboard config, alias, auth, Self Service. |
| **Frontend** | `frontend/` | Web UI (React). Served as static files after `npm run build`. |
| **Monitor**  | `monitor/`  | Python process: WebSocket, MySQL, connection to ADN report server. Live data (Last Heard, linked systems, etc.). |

- Backend and frontend can run without the monitor (no live data).
- In production you do not need Node running: it is only used to **build** the frontend; then serve `frontend/dist/` with Nginx or Apache.

---

## Requirements

- **PHP** 8.1+ (extensions: json, pdo_mysql, yaml; Composer)
- **Node.js** 18+ (for frontend build only)
- **Python** 3.10+ (monitor: Twisted, PyYAML, MySQLdb, etc.)
- **MySQL** (for Self Service and monitor data if using DB)

---

## Configuration

### 1. Main config: `adn-mon.yaml`

All dashboard and monitor behaviour is defined in a **single YAML** file in the monitor folder:

- **Typical path:** `monitor/adn-mon.yaml`
- Copy and adapt from `monitor/adn-mon.yaml` (or create one). It configures:
  - **GLOBAL**: bridges, lastheard, TG count, optional **TIMEZONE** (IANA name, e.g. `Europe/Madrid`) for display and DB wall times independent of the server TZ, etc.
  - **SELF_SERVICE**: MySQL credentials (backend + monitor).
  - **ADN_CONNECTION**: IP and port of the ADN report server.
  - **ALIASES**: URLs and files for alias (peers, subscribers, talkgroups).
  - **LOGGER**, **WEBSOCKET_SERVER**, **DASHBOARD** (title, language, nav/footer/news marquee links).

Paths inside the YAML (e.g. `LOG_PATH`, `PATH` for alias files) are relative to the **monitor/** directory when you run the monitor from there.

### 2. Environment: `.env`

A single **`.env` in the project root** is used by all components. Create it from the example:

```bash
cp .env.example .env
```

Edit `.env` and set at least:

| Variable | Purpose |
|----------|---------|
| **ADN_CONFIG_PATH** | Absolute path to `adn-mon.yaml` (backend and monitor). e.g. `/opt/adn-monitor/monitor/adn-mon.yaml` |
| **ALIASES_BASE_URL** | Base URL for alias when not set in YAML (backend). |
| **VITE_API_BASE** | API base URL at frontend build time. Empty = same origin. |
| **VITE_ALIASES_BASE_URL** | Base URL for alias lists (build). |
| **VITE_DEFAULT_LANGUAGE** | Default language (build). |

Load order (root first, then fallbacks):

- **Backend (PHP)** loads **root `.env`** first; if missing, loads `backend/.env`.
- **Frontend (Vite)** reads **root `.env`** first (VITE_* at build/dev); if missing, reads `frontend/.env`.
- **Monitor**: `monitor/run.sh` and the systemd example use the root `.env` when present.

You can use only `backend/.env` or only `frontend/.env` when you run a single part and prefer not to have a root `.env`.

---

## Running everything (development)

You need two or three terminals (or one in the background).

### Terminal 1: API (PHP)

```bash
cd /opt/adn-monitor
cd backend && composer install && cd ..
./start.sh
```

API is at **http://localhost:8080**.

### Terminal 2: Web UI (React)

```bash
cd /opt/adn-monitor/frontend
npm install
npm run dev
```

Open the URL Vite shows (e.g. **http://localhost:5173**). The dev server proxies `/api` and `/ws` according to your config.

### Terminal 3 (optional): Monitor (live data)

```bash
cd /opt/adn-monitor/monitor
pip install -r requirements.txt   # PyYAML and project deps
python3 monitor.py
```

Or: `./run.sh`. The monitor uses `monitor/adn-mon.yaml` (or `ADN_CONFIG_PATH`). In dev the frontend connects to the monitor WebSocket; in production Nginx proxies `/ws` to the monitor port (e.g. 9000).

---

## Production deployment (full howto)

### 1. Database (MySQL)

Create a user and database for the monitor/backend (credentials go in `adn-mon.yaml`, **SELF_SERVICE** section). Then create or update tables from the monitor:

```bash
cd /opt/adn-monitor/monitor
python3 db_bootstrap.py --config adn-mon.yaml --create   # create tables
python3 db_bootstrap.py --config adn-mon.yaml --update   # migrations
```

### 2. Configuration

- Place **adn-mon.yaml** in `monitor/` (or your chosen path) and set **ADN_CONFIG_PATH** to that file in `.env` and in Nginx/PHP-FPM if needed.
- In the project root: `cp .env.example .env` and fill **ADN_CONFIG_PATH**, **VITE_API_BASE**, etc. for production.

### 3. Frontend build

```bash
cd /opt/adn-monitor/frontend
npm install
npm run build
```

Output is in `frontend/dist/`. That directory is what Nginx (or Apache) will serve.

### 4. Backend (PHP)

- Install dependencies: `cd backend && composer install` (Composer is in `backend/`).
- In production you typically use **PHP-FPM** with Nginx (or Apache) pointing to `backend/public/index.php` for `/api/*`.

### 5. Monitor as a service (systemd)

An example unit is in the repo:

```bash
sudo cp /opt/adn-monitor/examples/adn-monitor.service /etc/systemd/system/
# Adjust WorkingDirectory and ExecStart if your install is not under /opt/adn-monitor
sudo systemctl daemon-reload
sudo systemctl enable adn-monitor
sudo systemctl start adn-monitor
```

The example uses **system Python** (`/usr/bin/python3`). Ensure the monitor dependencies are installed for that Python (e.g. `pip install -r monitor/requirements.txt` or whatever the project uses).

### 6. Nginx (example)

An example config serves the frontend, proxies `/api` to PHP, and `/ws` to the monitor:

```bash
sudo cp /opt/adn-monitor/examples/nginx-adn-monitor.conf /etc/nginx/sites-enabled/
```

Edit the file and set:

- **server_name** (your domains)
- **root** (path to `frontend/dist`)
- **fastcgi_param ADN_CONFIG_PATH** (path to `adn-mon.yaml`)
- WebSocket **upstream** (monitor port, e.g. 127.0.0.1:9000)
- If using HTTPS: certificate paths and the `listen 443 ssl` block (commented in the example)

Then:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 7. Production checklist

1. MySQL created and `db_bootstrap.py --create` / `--update` run.
2. `adn-mon.yaml` and `.env` configured; **ADN_CONFIG_PATH** pointing to the YAML.
3. `npm run build` in `frontend/` and Nginx serving `frontend/dist/`.
4. PHP-FPM serving `backend/public` for `/api`.
5. Monitor running (systemd) and Nginx proxying `/ws` to the monitor port.

---

## Examples in the repo

| File | Description |
|------|-------------|
| **examples/adn-monitor.service** | Example systemd unit (system Python, no pyenv). |
| **examples/nginx-adn-monitor.conf** | Example Nginx site (default listen, example domains). |

Copy and adapt paths, domains, and certificates to your server.

---

## IPv6 support

To run the whole project over IPv6 (or dual-stack):

| Component | What to do |
|-----------|------------|
| **Monitor – WebSocket** | In `adn-mon.yaml`, under `WEBSOCKET_SERVER`, set `LISTEN_INTERFACE: "::"` so the dashboard WebSocket accepts IPv4 and IPv6. Default `""` binds to IPv4 only. |
| **Monitor – connection to ADN** | Set `ADN_CONNECTION.ADN_IP` to the report server’s IPv6 address (or hostname that resolves to IPv6). No code change. |
| **Proxy** | Set env `ADN_PROXY_IPV6=1` and leave `PROXY.LISTEN_IP` empty so the proxy listens on `::`. Use an IPv6 address or hostname for `PROXY.MASTER` (hostnames are resolved at startup). See `proxy/README.md`. |
| **Backend (PHP)** | No app change. Configure the web server (Nginx/Apache) to listen on `[::]:80` and/or `[::]:443` so the API is reachable over IPv6. |
| **Frontend** | No change; it uses the same API/WebSocket URLs. If the server is reachable via IPv6, the browser will use it when available. |

---

## License and credits

This project is **GPL v3**. The **monitor** (Python), **frontend** (React dashboard), and **backend** (PHP API) are derivatives of the following works:

| Project | Author | Description |
|--------|--------|-------------|
| **FDMR Monitor** | OA4DOA | FDMR Monitor for FreeDMR Server based on HBMonv2 — [github.com/yuvelq/FDMR-Monitor](https://github.com/yuvelq/FDMR-Monitor) |
| **HBMonv2** | SP2ONG | HBMonitor v2 for DMR Server based on HBlink/FreeDMR — [github.com/sp2ong/HBMonv2](https://github.com/sp2ong/HBMonv2) |
| **hbmonitor3** | KC1AWV | Python 3 implementation of N0MJS HBmonitor for HBlink — [github.com/kc1awv/hbmonitor3](https://github.com/kc1awv/hbmonitor3) |
| **HBmonitor** | Cortney T. Buffington, N0MJS | Original HBmonitor (Copyright (C) 2013-2018, n0mjs@me.com) |

The **proxy** (Hotspot Proxy for ADN DMR Peer Server) is a derivative of the hotspot proxy by Simon Adlem, G7RZU; credits: Jon Lee G4TSN, Norman Williams M6NBP, Christian OA4DOA (see `proxy/README.md`).

**This codebase:** Copyright (C) 2026 Rodrigo Pérez, CE5RPY. Original works and these derivatives are free software under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html). Preserve license and attribution when distributing or modifying.

---

## Further reading

- **Monitor (WebSocket, DB, ADN):** see `monitor/README.md`.
- **YAML config:** options and sections in `monitor/adn-mon.yaml` (comments in the file).

---

[Español](README_es.md)
