"""Sync alias JSON/CSV from remote URLs and local override files into MySQL."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .alias_file_parser import alias_file_is_valid, parse_alias_file
from .alias_paths import resolve_alias_files_dir
from .ports import (
    AliasBulkImportPort,
    AliasFileDownloaderPort,
    AliasRepository,
    AliasTableRepository,
)

logger = logging.getLogger("adn-monitor")

_TABLES = frozenset({"peer_ids", "subscriber_ids", "talkgroup_ids"})


class AliasFilesSyncUseCases:
    def __init__(
        self,
        *,
        files_config: dict[str, Any],
        monitor_root: Path,
        downloader: AliasFileDownloaderPort,
        table_repo: AliasTableRepository | None = None,
        bulk_importer: AliasBulkImportPort | None = None,
        alias_repo: AliasRepository | None = None,
        table_count: Callable[[str], int | None] | None = None,
        local_mtime: dict[str, float] | None = None,
    ) -> None:
        self._files = files_config
        self._monitor_root = monitor_root
        self._downloader = downloader
        self._table_repo = table_repo
        self._bulk = bulk_importer
        self._alias_repo = alias_repo
        self._table_count = table_count
        self._local_mtime = local_mtime if local_mtime is not None else {}

    @property
    def review_interval_sec(self) -> float:
        return float(self._files.get("REVIEW_INTERVAL", 5 * 60))

    def alias_dir(self) -> str:
        return resolve_alias_files_dir(self._files, self._monitor_root)

    def refresh_remote_files(self) -> None:
        path = self.alias_dir()
        stale = int(self._files.get("RELOAD_TIME", 24 * 3600))
        checksum_url = str(self._files.get("CHECKSUM_URL", "")).strip() or None
        for file_name, url_key, table in (
            (self._files.get("PEER", "peer_ids.json"), "PEER_URL", "peer_ids"),
            (self._files.get("SUBS", "subscriber_ids.json"), "SUBSCRIBER_URL", "subscriber_ids"),
            (self._files.get("TGID", "talkgroup_ids.json"), "TGID_URL", "talkgroup_ids"),
        ):
            url = str(self._files.get(url_key, "")).strip()
            if file_name and url:
                self._update_remote_table(path, str(file_name), url, stale, table, checksum_url)

    def refresh_local_files(self, table: str | None = None) -> None:
        if self._bulk is None and self._table_repo is None:
            return
        path = self.alias_dir()
        pairs: list[tuple[str, str]] = []
        if table == "peer_ids" or (not table and self._files.get("LCL_PEER")):
            pairs.append((str(self._files.get("LCL_PEER", "")), "peer_ids"))
        if table == "subscriber_ids" or (not table and self._files.get("LCL_SUBS")):
            pairs.append((str(self._files.get("LCL_SUBS", "")), "subscriber_ids"))
        if table == "talkgroup_ids" or (not table and self._files.get("LCL_TGID")):
            pairs.append((str(self._files.get("LCL_TGID", "")), "talkgroup_ids"))
        for file_name, tbl in pairs:
            if not file_name or tbl not in _TABLES:
                continue
            p2f = Path(path) / file_name
            if not p2f.exists():
                continue
            mtime = p2f.stat().st_mtime
            if self._local_mtime.get(tbl) == mtime:
                continue
            imported = self._import_table(path, file_name, tbl, replace=False)
            if imported:
                self._invalidate_alias_cache(tbl)
                self._local_mtime[tbl] = mtime
            else:
                logger.warning("(alias) %s: local import skipped (invalid file or DB error)", tbl)

    def log_table_counts(self) -> None:
        if self._table_count is None:
            return
        for tbl in _TABLES:
            try:
                n = self._table_count(tbl)
                if n is not None:
                    logger.info("%s entries: %s", tbl, n)
            except Exception as err:
                logger.error("alias table count %s: %s", tbl, err)

    def _invalidate_alias_cache(self, table: str) -> None:
        if self._alias_repo is None:
            return
        invalidate = getattr(self._alias_repo, "invalidate_cache", None)
        if callable(invalidate):
            invalidate(table)

    def _import_table(
        self,
        path: str,
        file_name: str,
        table: str,
        *,
        replace: bool,
    ) -> int:
        """Import alias rows when the on-disk file validates; return rows imported (0 = skip)."""
        if not alias_file_is_valid(path, file_name, table):
            logger.warning(
                "(alias) %s: file %s missing, empty, or unparseable — skip import",
                table,
                file_name,
            )
            return 0
        try:
            if self._bulk is not None:
                imported = self._bulk.import_from_file(path, file_name, table, replace=replace)
            elif self._table_repo is not None:
                self._table_repo.populate_from_file(path, file_name, table, wipe=replace)
                imported = len(parse_alias_file(path, file_name, table))
            else:
                return 0
        except Exception as err:
            logger.warning("(alias) %s: import failed: %s", table, err)
            return 0
        if imported <= 0:
            logger.warning("(alias) %s: import produced no rows", table)
            return 0
        return imported

    def _update_remote_table(
        self,
        path: str,
        file_name: str,
        url: str,
        stale: int,
        table: str,
        checksum_url: str | None,
    ) -> None:
        if table not in _TABLES:
            return
        file_path = Path(path) / file_name
        need_download = not file_path.exists() or (time.time() - file_path.stat().st_mtime) >= stale
        result: str | None = None
        if not need_download:
            logger.info("(alias) %s: using existing file (fresh)", table)
        if need_download:
            reason = "missing" if not file_path.exists() else "stale"
            short_url = url[:60] + "..." if len(url) > 60 else url
            logger.info("(alias) %s: %s, downloading from %s", table, reason, short_url)
            if checksum_url:
                checksums = self._downloader.fetch_checksums(checksum_url)
                if checksums is None:
                    result = "checksum fetch failed"
                else:
                    result = self._downloader.download_and_verify(path, file_name, url, checksums)
            else:
                ok = self._downloader.download_file(url, path, file_name)
                result = "successfully" if ok else "download failed"
            if result and "successfully" in result:
                if not alias_file_is_valid(path, file_name, table):
                    logger.warning(
                        "(alias) %s: download finished but file failed validation",
                        table,
                    )
                    result = "downloaded file failed validation"
                elif checksum_url:
                    logger.info("(alias) %s: downloaded and checksum verified", table)
                else:
                    logger.info("(alias) %s: downloaded", table)
        count: int | None = None
        if self._table_count is not None:
            try:
                count = self._table_count(table)
            except Exception:
                count = None
        downloaded_ok = bool(result and "successfully" in result)
        bootstrap_import = not need_download and count is not None and count <= 2
        if not downloaded_ok and not bootstrap_import:
            if result and "successfully" not in result:
                logger.warning("(alias) %s: %s", table, result)
            return
        if not alias_file_is_valid(path, file_name, table):
            logger.warning(
                "(alias) %s: skip import — on-disk file missing, empty, or unparseable",
                table,
            )
            return
        imported = self._import_table(path, file_name, table, replace=True)
        if imported:
            self._invalidate_alias_cache(table)
        else:
            logger.warning("(alias) %s: import failed — cache unchanged", table)
