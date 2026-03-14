# Hotspot Proxy for ADN DMR Peer Server.
# Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Protocol and behaviour derived from the hotspot proxy by Simon Adlem, G7RZU
# (Copyright (C) 2020); credits: Jon Lee G4TSN, Norman Williams M6NBP, Christian OA4DOA.
# Original and this derivative are under GPLv3.

"""
UDP proxy protocol (Homebrew / ADN DMR Peer Server).
"""

from __future__ import annotations

import random
import struct
from datetime import datetime
from hashlib import pbkdf2_hmac
from time import time
from typing import Any, Dict, List, Optional

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import DatagramProtocol

from ...domain import (
    DMRD,
    DMRA,
    MSTC,
    MSTCL,
    MSTN,
    MSTP,
    PRBL,
    PRIN,
    RPTA,
    RPTACK,
    RPTCL,
    RPTK,
    RPTL,
    RPTC,
    RPTO,
    RPTP,
)
from ...domain.ports import PrivHelperPort, ProxyDbPort

try:
    from dmr_utils3.utils import int_id
except ImportError:

    def int_id(peer_id: bytes) -> int:
        if len(peer_id) < 4:
            return 0
        return (peer_id[0] << 24) | (peer_id[1] << 16) | (peer_id[2] << 8) | peer_id[3]


class ProxyProtocol(DatagramProtocol):
    """UDP proxy: clients (repeaters) <-> ADN DMR Peer Server (master)."""

    def __init__(
        self,
        master: str,
        listen_port: int,
        conn_track: Dict[int, Any],
        peer_track: Dict[bytes, Dict[str, Any]],
        rptl_track: Dict[str, int],
        black_list: List[int],
        ip_black_list: Dict[str, float],
        timeout_sec: int,
        debug: bool,
        client_info: bool,
        dest_port_start: int,
        dest_port_end: int,
        priv_helper: Optional[PrivHelperPort],
        db_proxy: Optional[ProxyDbPort],
        use_selfservice: bool,
        pbkdf2_salt: str = "ADN",
        pbkdf2_iterations: int = 2000,
        logger: Any = None,
    ) -> None:
        self.master = master
        self.listen_port = listen_port
        self.conn_track = conn_track
        self.peer_track = peer_track
        self.rptl_track = rptl_track
        self.black_list = black_list
        self.ip_black_list = ip_black_list
        self.timeout = timeout_sec
        self.debug = debug
        self.client_info = client_info
        self.dest_port_start = dest_port_start
        self.dest_port_end = dest_port_end
        self.num_ports = dest_port_end - dest_port_start
        self.priv_helper = priv_helper
        self.db_proxy = db_proxy
        self.use_selfservice = use_selfservice
        self._pbkdf2_salt = pbkdf2_salt.encode("utf-8") if isinstance(pbkdf2_salt, str) else pbkdf2_salt
        self._pbkdf2_iterations = pbkdf2_iterations
        self._log = logger

    def _log_info(self, msg: str, *args: Any) -> None:
        if self._log:
            self._log.info(msg, *args)
        else:
            print(msg % args if args else msg, flush=True)

    def _log_debug(self, msg: str, *args: Any) -> None:
        if self.debug:
            if self._log:
                self._log.debug(msg, *args)
            else:
                print(msg % args if args else msg, flush=True)

    def _send(self, data: bytes, addr: tuple) -> None:
        """Send UDP and log when debug is on."""
        if self.debug:
            host, port = addr
            cmd = data[:4] if len(data) >= 4 else b""
            self._log_debug("TX to %s:%s len=%d cmd=%r", host, port, len(data), cmd)
        self.transport.write(data, addr)

    def reaper(self, peer_id: bytes) -> None:
        """On session timeout: notify master, client, free port, optionally DB log_out."""
        if self.debug:
            self._log_debug("dead %s", peer_id)
        if self.client_info and peer_id != b"\xff\xff\xff\xff":
            pe = self.peer_track.get(peer_id)
            if pe:
                self._log_info(
                    "%s Client: ID:%s IP:%s Port:%s Removed.",
                    datetime.now().replace(microsecond=0),
                    str(int_id(peer_id)).rjust(9),
                    pe["shost"].rjust(15),
                    pe["sport"],
                )
        pe = self.peer_track.get(peer_id)
        if not pe:
            return
        self._send(b"RPTCL" + peer_id, (self.master, pe["dport"]))
        for _ in range(3):
            self._send(b"MSTCL", (pe["shost"], pe["sport"]))
        self.conn_track[pe["dport"]] = False
        if self.use_selfservice and self.db_proxy:
            self.db_proxy.updt_tbl("log_out", peer_id)
        del self.peer_track[peer_id]

    def datagramReceived(self, data: bytes, addr: tuple) -> None:
        host, port = addr
        nowtime = time()
        if host in self.ip_black_list:
            return
        command = data[:4] if len(data) >= 4 else b""
        if self.debug:
            direction = "master" if host == self.master else "client"
            self._log_debug(
                "RX from %s:%s [%s] len=%d cmd=%r",
                host, port, direction, len(data), command,
            )

        if host == self.master:
            self._handle_from_master(data, command, port, nowtime)
            return
        self._handle_from_client(data, command, host, port, nowtime)

    def _handle_from_master(
        self,
        data: bytes,
        command: bytes,
        port: int,
        nowtime: float,
    ) -> None:
        peer_id = None
        if command == PRBL:
            if len(data) < 9:
                return
            peer_id = data[4:8]
            try:
                bltime = float(data[8:].decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return
            pe = self.peer_track.get(peer_id)
            if not pe:
                return
            self.ip_black_list[pe["shost"]] = bltime
            if self.client_info:
                self._log_info("Add to blacklist: host %s. Expire time %s", pe["shost"], bltime)
            if self.priv_helper:
                self._log_info("Ask priv_helper to add to iptables: host %s, port %s.", pe["shost"], self.listen_port)
                reactor.callInThread(self.priv_helper.add_blocklist, self.listen_port, pe["shost"])
            return

        if command == DMRD and len(data) >= 15:
            peer_id = data[11:15]
        elif command == RPTA:
            if len(data) >= 10 and data[6:10] in self.peer_track:
                peer_id = data[6:10]
            else:
                peer_id = self.conn_track.get(port)
        elif command == MSTN and len(data) >= 10:
            peer_id = data[6:10]
        elif command == MSTP and len(data) >= 11:
            peer_id = data[7:11]
        elif command == MSTC and len(data) >= 9:
            peer_id = data[5:9]

        if peer_id is None:
            return
        if peer_id not in self.peer_track:
            return
        pe = self.peer_track[peer_id]
        self._send(data, (pe["shost"], pe["sport"]))
        if command in (MSTN, MSTC):
            if pe.get("timer") and pe["timer"].active():
                pe["timer"].reset(15)

    def _handle_from_client(
        self,
        data: bytes,
        command: bytes,
        host: str,
        port: int,
        nowtime: float,
    ) -> None:
        peer_id = None
        if command == DMRD and len(data) >= 15:
            peer_id = data[11:15]
        elif command == DMRA and len(data) >= 8:
            peer_id = data[4:8]
        elif command == RPTL and len(data) >= 8:
            peer_id = data[4:8]
            self.rptl_track[host] = self.rptl_track.get(host, 0) + 1
            if self.rptl_track[host] > 50:
                self._log_info("(RPTL) exceeded max: %s", self.rptl_track[host])
                bltime = nowtime + 600
                self.ip_black_list[host] = bltime
                self.rptl_track.pop(host, None)
                if self.client_info:
                    self._log_info("(RPTL) Add to blacklist: host %s. Expire time %s", host, bltime)
                if self.priv_helper:
                    self._log_info("(RPTL) Ask priv_helper to add to iptables: host %s, port %s.", host, self.listen_port)
                    reactor.callInThread(self.priv_helper.add_blocklist, self.listen_port, host)
                return
        elif command == RPTK and len(data) >= 8:
            peer_id = data[4:8]
        elif command == RPTC:
            if len(data) >= 5 and data[:5] == RPTCL:
                peer_id = data[5:9] if len(data) >= 9 else None
            else:
                peer_id = data[4:8] if len(data) >= 8 else None
                if self.use_selfservice and self.db_proxy and peer_id and peer_id in self.peer_track:
                    mode = data[97:98].decode("utf-8", errors="replace") if len(data) >= 98 else "4"
                    callsign = data[8:16].rstrip().decode("utf-8", errors="replace")
                    self.db_proxy.ins_conf(int_id(peer_id), peer_id, callsign, host, mode)
                    pe = self.peer_track[peer_id]
                    pe["opt_timer"] = reactor.callLater(10, self._login_opt, peer_id)
        elif command == RPTO and len(data) >= 8:
            peer_id = data[4:8]
            if self.use_selfservice and self.db_proxy and peer_id in self.peer_track:
                if data[8:].upper().startswith(b"PASS=") and len(data) >= 13:
                    psswd_raw = data[13:]
                    if len(psswd_raw) >= 6:
                        dk = pbkdf2_hmac(
                            "sha256",
                            psswd_raw,
                            self._pbkdf2_salt,
                            self._pbkdf2_iterations,
                        ).hex()
                        self.db_proxy.updt_tbl("psswd", peer_id, psswd=dk)
                        self._send(RPTACK + peer_id, (host, port))
                        self._log_info("Password stored for: %s", int_id(peer_id))
                        return
                self.db_proxy.updt_tbl("opt_rcvd", peer_id)
                pe = self.peer_track[peer_id]
                if pe.get("opt_timer") and pe["opt_timer"].active():
                    pe["opt_timer"].cancel()
                    self._log_info("Options received from: %s", int_id(peer_id))
        elif command == RPTP and len(data) >= 11:
            peer_id = data[7:11]
        else:
            return

        if peer_id is None:
            return

        if peer_id in self.peer_track:
            pe = self.peer_track[peer_id]
            pe["sport"] = port
            pe["shost"] = host
            self._send(data, (self.master, pe["dport"]))
            if pe.get("timer") and pe["timer"].active():
                pe["timer"].reset(self.timeout)
            return

        if int_id(peer_id) in self.black_list:
            return
        ports_avail = [p for p in self.conn_track if not self.conn_track[p]]
        if not ports_avail:
            return
        dport = random.choice(ports_avail)
        self.conn_track[dport] = peer_id
        self.peer_track[peer_id] = {
            "dport": dport,
            "sport": port,
            "shost": host,
            "timer": reactor.callLater(self.timeout, self.reaper, peer_id),
        }
        self._send(data, (self.master, dport))
        self._send(PRIN + host.encode("utf-8") + b":" + str(port).encode("utf-8"), (self.master, dport))
        if self.client_info and peer_id != b"\xff\xff\xff\xff":
            self._log_info(
                "%s New client: ID:%s IP:%s Port:%s, assigned to port:%s.",
                datetime.now().replace(microsecond=0),
                str(int_id(peer_id)).rjust(9),
                host.rjust(15),
                port,
                dport,
            )

    @inlineCallbacks
    def _login_opt(self, peer_id: bytes) -> None:
        if not self.db_proxy or peer_id not in self.peer_track:
            return
        try:
            res = yield self.db_proxy.slct_opt(peer_id)
            if not res or not res[0]:
                return
            options = res[0][0]
            if not options:
                return
            pe = self.peer_track[peer_id]
            self._send(b"RPTO" + peer_id + options.encode("utf-8"), (self.master, pe["dport"]))
            self._log_info("Options sent at login for: %s, opt: %s", int_id(peer_id), options)
        except Exception as err:
            if self._log:
                self._log.warning("login_opt error: %s", err)
            else:
                print("login_opt error:", err, flush=True)

    def _peer_id_from_db(self, value: Any) -> Optional[bytes]:
        """Normalize DB dmr_id (bytes or int) to 4-byte peer_id for peer_track lookup."""
        if isinstance(value, bytes) and len(value) == 4:
            return value
        if isinstance(value, int) and 0 <= value <= 0xFFFFFFFF:
            return struct.pack(">I", value)
        return None

    @inlineCallbacks
    def send_opts(self) -> None:
        if not self.db_proxy:
            return
        try:
            results = yield self.db_proxy.slct_db()
            for row in results:
                if len(row) < 2:
                    continue
                pid = self._peer_id_from_db(row[0])
                options = row[1]
                if pid is None or pid not in self.peer_track or not options:
                    continue
                self.db_proxy.updt_tbl("rst_mod", pid)
                pe = self.peer_track[pid]
                self._send(b"RPTO" + pid + (options.encode("utf-8") if isinstance(options, str) else options), (self.master, pe["dport"]))
                self._log_info("Options update sent for: %s", int_id(pid))
        except Exception as err:
            if self._log:
                self._log.warning("send_opts error: %s", err)
            else:
                print("send_opts error:", err, flush=True)

    def lst_seen(self) -> None:
        if not self.db_proxy:
            return
        dmrid_list = [(pid,) for pid in self.peer_track]
        if dmrid_list:
            self.db_proxy.updt_lstseen(dmrid_list)
