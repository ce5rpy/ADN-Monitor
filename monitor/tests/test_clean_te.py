"""Stale timeslot cleanup (clean_te) must reset TRX so TS chips go idle."""

from __future__ import annotations

import time

from adn_monitor.application.hblink_table import clean_te


def test_clean_te_clears_trx_on_stale_voice() -> None:
    stale = time.time() - 200
    ctable = {
        "MASTERS": {
            "SYSTEM-2": {
                "PEERS": {
                    5200386: {
                        1: {"TS": False, "TRX": ""},
                        2: {
                            "TS": False,
                            "TRX": "TX",
                            "SUB": "",
                            "DEST": "",
                            "TIMEOUT": stale,
                        },
                    }
                }
            }
        },
        "PEERS": {},
        "OPENBRIDGES": {},
    }
    clean_te(ctable)
    ts2 = ctable["MASTERS"]["SYSTEM-2"]["PEERS"][5200386][2]
    assert ts2["TRX"] == ""
    assert ts2["TS"] is False
