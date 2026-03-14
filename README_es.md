# ADN Systems Monitor

Dashboard para redes ADN: API en PHP, interfaz en React y proceso Python que conecta al servidor de reportes (ADN/peer), escribe en base de datos y sirve datos en vivo por WebSocket.

---

## Arquitectura

| Parte       | Carpeta     | Rol |
|------------|-------------|-----|
| **Backend**  | `backend/`  | API REST (PHP/Slim): config del dashboard, alias, auth, Self Service. |
| **Frontend** | `frontend/` | Interfaz web (React). Se sirve como estático tras `npm run build`. |
| **Monitor**  | `monitor/`  | Proceso Python: WebSocket, MySQL, conexión al ADN report server. Datos en vivo (Last Heard, sistemas enlazados, etc.). |

- Backend y frontend pueden usarse sin el monitor (sin datos en vivo).
- En producción no hace falta Node en ejecución: solo se usa para **construir** el frontend; luego se sirve `frontend/dist/` con Nginx o Apache.

---

## Requisitos

- **PHP** 8.1+ (extensiones: json, pdo_mysql, yaml; Composer)
- **Node.js** 18+ (solo para build del frontend)
- **Python** 3.10+ (monitor: Twisted, PyYAML, MySQLdb, etc.)
- **MySQL** (para Self Service y datos del monitor si usas DB)

---

## Configuración

### 1. Config principal: `adn-mon.yaml`

Todo el comportamiento del dashboard y del monitor se define en **un solo YAML** en la carpeta del monitor:

- **Ruta típica:** `monitor/adn-mon.yaml`
- Copia y adapta desde `monitor/adn-mon.yaml` (o crea uno desde cero). Ahí se configuran:
  - **GLOBAL**: bridges, lastheard, TG count, etc.
  - **SELF_SERVICE**: credenciales MySQL (backend + monitor).
  - **ADN_CONNECTION**: IP y puerto del servidor de reportes ADN.
  - **ALIASES**: URLs y archivos de alias (peers, subscribers, talkgroups).
  - **LOGGER**, **WEBSOCKET_SERVER**, **DASHBOARD** (título, idioma, enlaces nav/footer y marquesina de noticias).

Las rutas dentro del YAML (p. ej. `LOG_PATH`, `PATH` para archivos de alias) son relativas al directorio **monitor/** cuando ejecutas el monitor desde ahí.

### 2. Variables de entorno: `.env`

Un único **`.env` en la raíz del proyecto** lo usan todos los componentes. Créalo a partir del ejemplo:

```bash
cp .env.example .env
```

Edita `.env` y ajusta al menos:

| Variable | Uso |
|----------|-----|
| **ADN_CONFIG_PATH** | Ruta absoluta a `adn-mon.yaml` (backend y monitor). Ej: `/opt/adn-monitor/monitor/adn-mon.yaml` |
| **ALIASES_BASE_URL** | Base URL para alias si no la defines en el YAML (backend). |
| **VITE_API_BASE** | URL base de la API en el build del frontend. Vacío = mismo origen. |
| **VITE_ALIASES_BASE_URL** | URL base para listas/alias (build). |
| **VITE_DEFAULT_LANGUAGE** | Idioma por defecto (build). |

Orden de carga (primero raíz, luego fallbacks):

- **Backend (PHP)** carga primero el **`.env` de la raíz**; si no existe, carga `backend/.env`.
- **Frontend (Vite)** lee primero el **`.env` de la raíz** (VITE_* en build/dev); si no existe, lee `frontend/.env`.
- **Monitor**: `monitor/run.sh` y el ejemplo systemd usan el `.env` de la raíz cuando existe.

Puedes usar solo `backend/.env` o solo `frontend/.env` si ejecutas una sola parte y prefieres no tener `.env` en la raíz.

---

## Cómo arrancar todo (desarrollo)

Necesitas dos o tres terminales (o uno en segundo plano).

### Terminal 1: API (PHP)

```bash
cd /opt/adn-monitor
cd backend && composer install && cd ..
./start.sh
```

La API queda en **http://localhost:8080**.

### Terminal 2: Interfaz web (React)

```bash
cd /opt/adn-monitor/frontend
npm install
npm run dev
```

Abre la URL que indique Vite (p. ej. **http://localhost:5173**). El dev server hace proxy de `/api` y `/ws` según tu configuración.

### Terminal 3 (opcional): Monitor (datos en vivo)

```bash
cd /opt/adn-monitor/monitor
pip install -r requirements.txt   # PyYAML y dependencias del proyecto
python3 monitor.py
```

O: `./run.sh`. El monitor usa `monitor/adn-mon.yaml` (o `ADN_CONFIG_PATH`). En dev, el frontend suele conectar al WebSocket del monitor; en producción Nginx hace proxy de `/ws` al puerto del monitor (p. ej. 9000).

---

## Cómo desplegar en producción (howto completo)

### 1. Base de datos (MySQL)

Crea un usuario y una base para el monitor/backend (las credenciales van en `adn-mon.yaml`, sección **SELF_SERVICE**). Luego crea o actualiza las tablas desde el monitor:

```bash
cd /opt/adn-monitor/monitor
python3 db_bootstrap.py --config adn-mon.yaml --create   # crear tablas
python3 db_bootstrap.py --config adn-mon.yaml --update   # migraciones
```

### 2. Configuración

- Deja **adn-mon.yaml** en `monitor/` (o donde prefieras) y apunta **ADN_CONFIG_PATH** a ese archivo en `.env` y en Nginx/PHP-FPM si hace falta.
- En la raíz del proyecto: `cp .env.example .env` y rellena **ADN_CONFIG_PATH**, **VITE_API_BASE**, etc. para producción.

### 3. Build del frontend

```bash
cd /opt/adn-monitor/frontend
npm install
npm run build
```

El resultado está en `frontend/dist/`. Ese directorio es el que servirá Nginx (o Apache).

### 4. Backend (PHP)

- Instala dependencias: `cd backend && composer install` (Composer está en `backend/`).
- En producción se suele usar **PHP-FPM** y Nginx (o Apache) apuntando a `backend/public/index.php` para las rutas `/api/*`.

### 5. Monitor como servicio (systemd)

Hay un ejemplo de unit en el repo:

```bash
sudo cp /opt/adn-monitor/examples/adn-monitor.service /etc/systemd/system/
# Ajusta WorkingDirectory y ExecStart si tu instalación no está en /opt/adn-monitor
sudo systemctl daemon-reload
sudo systemctl enable adn-monitor
sudo systemctl start adn-monitor
```

El ejemplo usa **Python del sistema** (`/usr/bin/python3`). Asegúrate de tener instaladas las dependencias del monitor para ese Python (p. ej. `pip install -r monitor/requirements.txt` u otras que use el proyecto).

### 6. Nginx (ejemplo)

Incluye un ejemplo que sirve el frontend, hace proxy de `/api` a PHP y de `/ws` al monitor:

```bash
sudo cp /opt/adn-monitor/examples/nginx-adn-monitor.conf /etc/nginx/sites-enabled/
```

Edita el archivo y ajusta:

- **server_name** (dominios)
- **root** (ruta a `frontend/dist`)
- **fastcgi_param ADN_CONFIG_PATH** (ruta a `adn-mon.yaml`)
- **upstream** del WebSocket (puerto del monitor, p. ej. 127.0.0.1:9000)
- Si usas HTTPS: certificados y bloque `listen 443 ssl` (en el ejemplo está comentado)

Luego:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 7. Resumen producción

1. MySQL creado y `db_bootstrap.py --create` / `--update` ejecutado.
2. `adn-mon.yaml` y `.env` configurados; **ADN_CONFIG_PATH** apuntando al YAML.
3. `npm run build` en `frontend/` y Nginx sirviendo `frontend/dist/`.
4. PHP-FPM sirviendo `backend/public` para `/api`.
5. Monitor en ejecución (systemd) y Nginx haciendo proxy de `/ws` al puerto del monitor.

---

## Ejemplos en el repo

| Archivo | Descripción |
|---------|-------------|
| **examples/adn-monitor.service** | Unit systemd de ejemplo (Python del sistema, sin pyenv). |
| **examples/nginx-adn-monitor.conf** | Sitio Nginx de ejemplo (listen por defecto, dominios de ejemplo). |

Copia y adapta rutas, dominios y certificados a tu servidor.

---

## Soporte IPv6

Para que todo el proyecto funcione por IPv6 (o dual-stack):

| Componente | Qué hacer |
|-------------|-----------|
| **Monitor – WebSocket** | En `adn-mon.yaml`, dentro de `WEBSOCKET_SERVER`, pon `LISTEN_INTERFACE: "::"` para que el WebSocket del dashboard acepte IPv4 e IPv6. Por defecto `""` enlaza solo a IPv4. |
| **Monitor – conexión al ADN** | Pon en `ADN_CONNECTION.ADN_IP` la IPv6 del servidor de reportes (o un hostname que resuelva a IPv6). No hace falta cambiar código. |
| **Proxy** | Define la variable de entorno `ADN_PROXY_IPV6=1` y deja `PROXY.LISTEN_IP` vacío para que el proxy escuche en `::`. Usa una IPv6 o un hostname en `PROXY.MASTER` (los hostnames se resuelven al arranque). Ver `proxy/README.md`. |
| **Backend (PHP)** | No hay que tocar la app. Configura el servidor web (Nginx/Apache) para escuchar en `[::]:80` y/o `[::]:443` y que la API sea accesible por IPv6. |
| **Frontend** | Sin cambios; usa las mismas URLs de API/WebSocket. Si el servidor es accesible por IPv6, el navegador la usará cuando corresponda. |

---

## Licencia y créditos

Este proyecto es **GPL v3**. El **monitor** (Python), el **frontend** (dashboard React) y el **backend** (API PHP) son derivados de los siguientes trabajos:

| Proyecto | Autor | Descripción |
|----------|-------|-------------|
| **FDMR Monitor** | OA4DOA | FDMR Monitor para FreeDMR Server basado en HBMonv2 — [github.com/yuvelq/FDMR-Monitor](https://github.com/yuvelq/FDMR-Monitor) |
| **HBMonv2** | SP2ONG | HBMonitor v2 para DMR Server basado en HBlink/FreeDMR — [github.com/sp2ong/HBMonv2](https://github.com/sp2ong/HBMonv2) |
| **hbmonitor3** | KC1AWV | Implementación en Python 3 del HBmonitor de N0MJS para HBlink — [github.com/kc1awv/hbmonitor3](https://github.com/kc1awv/hbmonitor3) |
| **HBmonitor** | Cortney T. Buffington, N0MJS | HBmonitor original (Copyright (C) 2013-2018, n0mjs@me.com) |

El **proxy** (Hotspot Proxy para ADN DMR Peer Server) es derivado del hotspot proxy de Simon Adlem, G7RZU; créditos: Jon Lee G4TSN, Norman Williams M6NBP, Christian OA4DOA (ver `proxy/README.md`).

**Este código:** Copyright (C) 2026 Rodrigo Pérez, CE5RPY. Las obras originales y estos derivados son software libre bajo la [Licencia Pública General de GNU v3](https://www.gnu.org/licenses/gpl-3.0.html). Conserva la licencia y la atribución al distribuir o modificar.

---

## Más información

- **Monitor (WebSocket, DB, ADN):** ver `monitor/README.md`.
- **Config en YAML:** opciones y secciones en `monitor/adn-mon.yaml` (comentarios en el propio archivo).

---

[English](README.md)
