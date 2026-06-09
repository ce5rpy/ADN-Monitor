"""Blocking DB reads for WebSocket last-heard rendering."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger("adn-monitor")

_LAST_HEARD_SQL = """SELECT CONVERT(date_time, CHAR), qso_time, qso_type, system, tg_num,
    (SELECT callsign FROM talkgroup_ids WHERE id = tg_num), dmr_id,
    (SELECT json_array(callsign, name) FROM subscriber_ids WHERE id = dmr_id)
    FROM {table} ORDER BY date_time DESC LIMIT %s"""

_TGCOUNT_SQL = """SELECT tg_num, ifnull(callsign, ''), qso_count, qso_time FROM tg_count
    LEFT JOIN talkgroup_ids ON talkgroup_ids.id = tg_count.tg_num
    WHERE tg_count.date = %s ORDER BY qso_time DESC LIMIT %s"""


def _connect(db: dict[str, Any]):
    import MySQLdb

    return MySQLdb.connect(
        host=db.get("SERVER", "localhost"),
        user=db.get("USER", ""),
        passwd=db.get("PASSWD", ""),
        db=db.get("NAME", "hbmon"),
        port=int(db.get("PORT", 3306)),
        charset="utf8mb4",
    )


def sync_select_for_render(db: dict[str, Any], table: str, row_num: int) -> list[tuple[Any, ...]]:
    if table not in ("last_heard", "lstheard_log"):
        return []
    try:
        conn = _connect(db)
        try:
            cur = conn.cursor()
            cur.execute(_LAST_HEARD_SQL.format(table=table), (row_num,))
            rows = cur.fetchall()
            out: list[tuple[Any, ...]] = []
            for row in rows:
                r = list(row)
                if r[7]:
                    r[7] = json.loads(r[7])
                out.append(tuple(r))
            return out
        finally:
            conn.close()
    except Exception as e:
        logger.debug("sync_select_for_render %s: %s", table, e)
        return []


def sync_select_tgcount(
    db: dict[str, Any],
    row_num: int,
    config_global: dict[str, Any] | None = None,
) -> list[Any] | None:
    from ...application.time_utils import format_tgcount_date

    d_today = format_tgcount_date(config_global)
    try:
        conn = _connect(db)
        try:
            cur = conn.cursor()
            cur.execute(_TGCOUNT_SQL, (d_today, row_num))
            rows = cur.fetchall()
            if not rows:
                return None
            res: list[Any] = []
            from ...persistence.db_pool import sec_time

            for tg_num, name, qso_c, qso_time in rows:
                cur.execute(
                    """SELECT ifnull(callsign, "N0CALL") FROM user_count
                    LEFT JOIN subscriber_ids ON subscriber_ids.id = user_count.dmr_id
                    WHERE tg_num = %s AND user_count.date = %s ORDER BY qso_time DESC LIMIT 4""",
                    (tg_num, d_today),
                )
                top = tuple(r[0] for r in cur.fetchall())
                res.append((tg_num, name, qso_c, sec_time(qso_time), top))
            return res
        finally:
            conn.close()
    except Exception as e:
        logger.debug("sync_select_tgcount: %s", e)
        return None
