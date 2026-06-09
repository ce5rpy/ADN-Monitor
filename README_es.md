# ADN Systems Monitor

**Versión 1.0.0** — compatible con **adn-server 1.0.0**.

Dashboard para redes ADN: proceso **FastAPI** unificado (REST + WebSocket + ingest de informes), frontend React y MySQL opcional (self-service / Last Heard).

El **proxy hotspot UDP** vive en **adn-server** (`PROXY` en `adn-server.yaml`), no en este repositorio.

---

## Arquitectura

| Parte | Carpeta | Rol |
|-------|---------|-----|
| **Monitor** | `monitor/monitor.py` | FastAPI: `/api/*`, `/ws`, ingest TCP o MQTT. |
| **Frontend** | `frontend/` | UI React; estático tras `npm run build`. |

---

## Requisitos

- **Node.js** 18+ (solo build del frontend)
- **Python** 3.10+ (`monitor/requirements.txt`)
- **MySQL** (self-service y Last Heard, si aplica)

---

## Configuración

### 1. `adn-monitor.yaml`

Ruta típica: `monitor/adn-monitor.yaml` (plantilla: `adn-monitor.yaml.example`).

- **GLOBAL**, **SELF_SERVICE**, **MONITOR_APP**, **ADN_CONNECTION**, **ALIASES**, **DASHBOARD**, **LOGGER**

### 2. `.env` (raíz del repo)

```bash
cp .env.example .env
```

| Variable | Uso |
|----------|-----|
| **ADN_CONFIG_PATH** | Ruta a `adn-monitor.yaml` |
| **VITE_API_BASE** | Vacío = mismo origen (Nginx → `monitor.py`) |
| **VITE_DEFAULT_LANGUAGE** | Idioma por defecto del build |

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
2. `npm run build` en `frontend/`
3. systemd: `examples/systemd/adn-monitor.service` → `monitor.py`
4. Nginx: `examples/nginx-adn-monitor.conf` → `/api` + `/ws` a `LISTEN_PORT`

---

## Licencia

**GPL v3**. Derivado de FDMR Monitor, HBMonv2, hbmonitor3 y HBmonitor (ver README en inglés para créditos).

Copyright (C) 2026 Rodrigo Pérez, CE5RPY.

---

[English](README.md)
