# ADN Systems Monitor

**Versión 2.0.0-rc.2** — emparejado con **adn-server 2.0.0-rc.2** (report v2 slim wire + HELLO JSON).

Dashboard para redes ADN: proceso **FastAPI** unificado (REST + WebSocket + ingest de informes), frontend React y MySQL opcional (self-service / Last Heard).

**Novedades v2:** se eliminaron **`backend/`** (PHP) y **`proxy/`** (proxy UDP standalone) de este repo. Self-service, auth y API del dashboard viven en **`monitor/monitor.py`**. El fan-in UDP de hotspots usa **`PROXY`** integrado en **adn-server**. El monitor ingiere **report v2** (`dashboard_state`) desde new-adn-server; **adn-dmr-server** legacy sigue funcionando si no hay HELLO (fallback pickle/CSV).

---

## Arquitectura

| Parte | Carpeta | Rol |
|-------|---------|-----|
| **Monitor** | `monitor/monitor.py` | FastAPI: `/api/*`, `/ws`, ingest TCP o MQTT. |
| **Frontend** | `frontend/` | UI React; estático tras `npm run build`. |

En producción no hace falta Node en runtime: solo para **`npm run build`**; Nginx (o Apache) sirve `frontend/dist/`.

---

## Requisitos

- **Node.js** 18+ (solo build del frontend)
- **Python** 3.10+ (`monitor/requirements.txt`)
- **MySQL** (self-service y Last Heard, si aplica)

---

## Configuración

### 1. `adn-monitor.yaml`

Ruta típica: `monitor/adn-monitor.yaml` (plantilla: `monitor/adn-monitor.yaml.example`).

- **GLOBAL** — bridges, lastheard, TG count, **TIMEZONE**
- **SELF_SERVICE** — MySQL (misma BD que self-service de adn-server, si aplica)
- **MONITOR_APP** — `LISTEN_PORT`, `INGEST` (`tcp` / `mqtt`), `FREQUENCY`
- **ADN_CONNECTION** — IP/puerto del report server; **HELLO_TIMEOUT_MS** para detectar **v2** (adn-server) vs **legacy** (adn-dmr-server). En v2 el footer muestra versiones **Monitor** y **Server** desde HELLO.
- **ALIASES**, **DASHBOARD**, **LOGGER**

### 2. `.env` (raíz del repo)

```bash
cp .env.example .env
```

| Variable | Uso |
|----------|-----|
| **ADN_CONFIG_PATH** | Ruta absoluta a `adn-monitor.yaml` |
| **VITE_API_BASE** | Vacío = mismo origen (Nginx → `monitor.py`) |
| **VITE_DEFAULT_LANGUAGE** | Idioma por defecto del build |

El resto (BD, aliases, ingest) va en **`adn-monitor.yaml`**, no en `.env`.

---

## Desarrollo

```bash
# Terminal 1 — monitor
cd /opt/adn-monitor/monitor
pip install -r requirements.txt
./run.sh

# Terminal 2 — frontend
cd /opt/adn-monitor/frontend
npm install && npm run dev
```

Vite hace proxy de `/api` y `/ws` a **:8080**.

---

## Producción (resumen)

1. MySQL + `db_bootstrap.py --create` / `--update`
2. `adn-monitor.yaml` y `.env` (`ADN_CONFIG_PATH`)
3. `npm run build` en `frontend/`
4. systemd: `examples/systemd/adn-monitor.service` → `monitor.py`
5. Nginx: `examples/nginx-adn-monitor.conf` → `/api` + `/ws` a `LISTEN_PORT`
6. **adn-server** ≥ **2.0.0-rc.2** para report v2 (reinstalar/reiniciar si el footer muestra una versión antigua del servidor)

---

## Soporte IPv6

| Componente | Acción |
|------------|--------|
| **Monitor API** | `MONITOR_APP.LISTEN_HOST`: `::` (dual-stack) |
| **Conexión al report** | `ADN_CONNECTION.ADN_IP` con IPv6 o hostname |
| **Proxy hotspot** | **`PROXY`** en `adn-server.yaml` |

---

## Licencia

**GPL v3**. Derivado de FDMR Monitor, HBMonv2, hbmonitor3 y HBmonitor (ver README en inglés para créditos).

Copyright (C) 2026 Rodrigo Pérez, CE5RPY.

---

## Más información

- [CHANGELOG.md](CHANGELOG.md)
- [adn-server](https://github.com/ce5rpy/ADN-DMR-Peer-Server) — report v2 y monitorización

---

[English](README.md)
