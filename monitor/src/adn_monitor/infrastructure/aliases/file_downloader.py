"""HTTP download + BLAKE2b verification for alias files."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import urllib.request
from pathlib import Path

from ...application.ports import AliasFileDownloaderPort

logger = logging.getLogger("adn-monitor")

_USER_AGENT = "ADN-Monitor/2.0"


class UrllibAliasFileDownloader(AliasFileDownloaderPort):
    def fetch_checksums(self, checksum_url: str, timeout: int = 15) -> dict[str, str] | None:
        try:
            req = urllib.request.Request(checksum_url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return {k: v for k, v in data.items() if k != "timestamp" and isinstance(v, str)}
        except Exception as e:
            logger.debug("fetch_checksums failed: %s", e)
            return None

    def download_file(self, url: str, dest_dir: str, file_name: str, timeout: int = 30) -> bool:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            Path(dest_dir).mkdir(parents=True, exist_ok=True)
            (Path(dest_dir) / file_name).write_bytes(data)
            return True
        except Exception as e:
            logger.debug("download_file failed: %s", e)
            return False

    def download_and_verify(
        self,
        dest_dir: str,
        file_name: str,
        url: str,
        checksums: dict[str, str],
    ) -> str:
        if not url:
            return "no url"
        temp_name = file_name + ".tmp"
        if not self.download_file(url, dest_dir, temp_name):
            return "download failed"
        temp_path = Path(dest_dir) / temp_name
        if not temp_path.exists():
            return "download failed (file missing)"
        key = Path(file_name).stem
        expected = checksums.get(key)
        if not expected:
            temp_path.unlink(missing_ok=True)
            return "checksum key missing for " + key
        if not self._verify_blake2b(temp_path, expected):
            temp_path.unlink(missing_ok=True)
            return "checksum verification failed for " + file_name
        final_path = Path(dest_dir) / file_name
        os.replace(temp_path, final_path)
        return "successfully"

    @staticmethod
    def _verify_blake2b(filepath: Path, expected_hex: str) -> bool:
        try:
            h = hashlib.blake2b()
            with filepath.open("rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    h.update(chunk)
            return h.hexdigest() == expected_hex.lower()
        except Exception:
            return False
