# Hotspot Proxy for ADN DMR Peer Server

UDP proxy between DMR repeaters (Homebrew protocol) and the ADN DMR Peer Server. Clean architecture; config and credentials aligned with the monitor.

## License and credits

This project is **GPL v3** and is a derivative of the original hotspot proxy:

- **Original**: Copyright (C) 2020 Simon Adlem, G7RZU &lt;g7rzu@gb7fr.org.uk&gt;
- **Credits**: Jon Lee, G4TSN; Norman Williams, M6NBP; Christian, OA4DOA
- **This rewrite**: Copyright (C) 2026 Rodrigo Pérez, CE5RPY

We have reimplemented it in a clean-architecture layout and integrated config with the ADN monitor YAML. The original and this derivative are free software under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html). You must preserve the license and attribution when distributing or modifying this code.

## Config

Configuration lives in the **monitor YAML** (`adn-mon.yaml`). The proxy reads the same file as the monitor and backend.

- **Env**: In the **project root** there is a **`.env.example`** with the variables (including `ADN_CONFIG_PATH`). Copy it to `.env` and set the path to your `adn-mon.yaml`; `.env` is not committed.
- **ADN_CONFIG_PATH**: Path to `adn-mon.yaml` (used by backend, monitor and proxy).

**PROXY.MASTER** in the YAML can be an **IP address** or a **DNS hostname**; the OS resolves the name when sending UDP to the master.

The YAML must include a **PROXY** section (see `monitor/adn-mon.yaml.example`). Optional env overrides: `ADN_PROXY_DEBUG` (log raw packets), `ADN_PROXY_IPV6`, `ADN_PROXY_STATS`, `ADN_PROXY_CLIENTINFO`, `ADN_PROXY_LISTENPORT`.

### Debug (temporary)

- In YAML: set `PROXY.Debug: true` in `adn-mon.yaml`.
- Or without editing config: set env **ADN_PROXY_DEBUG=1** (e.g. in the systemd unit or `.env`). Then restart the proxy. Debug logs raw UDP packets (hex/bytes) and reaper events.

### Master (DMR Peer Server) must listen on the proxy’s port range

The proxy forwards each client to the **master** at `MASTER:DESTPORT_START` … `MASTER:DEST_PORT_END` (e.g. `127.0.0.1:54000`–`127.0.0.1:54100`), one port per client. The **ADN DMR Peer Server** (or compatible master) must be configured to listen on that same address and port range. If the master only listens on a single port (e.g. 62031), it will never receive the proxy’s traffic and clients will not connect. Configure the peer server to bind to `MASTER` and the range given by `DESTPORT_START`/`DEST_PORT_END` in the YAML.

### When does the proxy notify the server (FreeDMR/ADN) and the hotspot about TG/options?

The proxy **sends RPTO (options) only to the master** (ADN DMR Peer Server), never directly to the hotspot. The server is responsible for pushing new options to the repeater.

| Moment | Proxy action | Recipient |
|--------|--------------|-----------|
| **~10 s after login (RPTC)** | `_login_opt`: reads options from DB, sends **RPTO** | **Master** at `(MASTER, dport)` |
| **Every 10 s (`send_opts`)** | For peers with `modified=1`: sends **RPTO**, then `rst_mod` (modified=0) | **Master** at `(MASTER, dport)` |
| **Hotspot sends RPTO** (e.g. options from device) | Forwards RPTO to master; if self-service, stores PASS= or `opt_rcvd` | **Master** (and DB) |

So when you change options in the self-service web, the proxy sends **RPTO** to the **master** within 10 s. The **master** must then push the new config to the hotspot; the proxy does not send RPTO to the client.

### Why don’t proxy clients show in the monitor?

If the peer server does not send reports to the monitor, or uses a different report port/host than `ADN_CONNECTION` in the YAML, the dashboard will not show proxy clients. Check the ADN DMR Peer Server configuration for “report server” / “report port” and set it to match `ADN_IP` and `ADN_PORT` (or the host where the monitor runs and the port it expects).

## Requirements

- Python 3.10+
- Twisted, PyYAML
- MySQL for self-service (same DB/schema as monitor; uses **SELF_SERVICE** in the same YAML).
- Optional: Pyro5 (priv helper), dmr_utils3, setproctitle

## Run

From the project root (or proxy directory), with `ADN_CONFIG_PATH` set to the monitor YAML (e.g. via `.env`):

```bash
python proxy/proxy.py
# or override config path
python proxy/proxy.py --config /path/to/adn-mon.yaml
```

## Layout

```
proxy/
  proxy.py           # Entry point
  src/adn_proxy/    # Domain, application, infrastructure
```
