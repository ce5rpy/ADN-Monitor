"""Alias file sync use case tests."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock

from adn_monitor.application.alias_files_sync import AliasFilesSyncUseCases
from adn_monitor.application.ports import AliasFileDownloaderPort


class _FakeDownloader(AliasFileDownloaderPort):
    def __init__(self) -> None:
        self.downloads: list[str] = []

    def fetch_checksums(self, checksum_url: str) -> dict[str, str] | None:
        return None

    def download_and_verify(
        self,
        dest_dir: str,
        file_name: str,
        url: str,
        checksums: dict[str, str],
    ) -> str:
        return "successfully"

    def download_file(self, url: str, dest_dir: str, file_name: str) -> bool:
        self.downloads.append(file_name)
        Path(dest_dir, file_name).write_text(
            '{"talkgroups": [{"id": 730, "callsign": "ADN"}]}',
            encoding="utf-8",
        )
        return True


def test_refresh_downloads_stale_file(tmp_path: Path):
    alias_dir = tmp_path / "json"
    alias_dir.mkdir()
    stale_file = alias_dir / "talkgroup_ids.json"
    stale_file.write_text("{}", encoding="utf-8")
    old = time.time() - 100000
    import os

    os.utime(stale_file, (old, old))
    table_repo = MagicMock()
    alias_repo = MagicMock()
    uc = AliasFilesSyncUseCases(
        files_config={
            "PATH": str(alias_dir),
            "RELOAD_TIME": 3600,
            "PEER": "peer_ids.json",
            "SUBS": "subscriber_ids.json",
            "TGID": "talkgroup_ids.json",
            "PEER_URL": "https://example/peer.json",
            "SUBSCRIBER_URL": "https://example/subs.json",
            "TGID_URL": "https://example/tg.json",
        },
        monitor_root=tmp_path,
        downloader=_FakeDownloader(),
        table_repo=table_repo,
        alias_repo=alias_repo,
        table_count=lambda t: 0,
    )
    uc.refresh_remote_files()
    assert table_repo.populate_from_file.called
    alias_repo.invalidate_cache.assert_called()
    dl = uc._downloader
    assert isinstance(dl, _FakeDownloader)
    assert "talkgroup_ids.json" in dl.downloads


def test_skips_fresh_file(tmp_path: Path):
    alias_dir = tmp_path / "json"
    alias_dir.mkdir()
    (alias_dir / "peer_ids.json").write_text("{}", encoding="utf-8")
    downloader = _FakeDownloader()
    table_repo = MagicMock()
    uc = AliasFilesSyncUseCases(
        files_config={
            "PATH": str(alias_dir),
            "RELOAD_TIME": 999999,
            "PEER": "peer_ids.json",
            "PEER_URL": "https://example/peer.json",
            "SUBS": "",
            "TGID": "",
        },
        monitor_root=tmp_path,
        downloader=downloader,
        table_repo=table_repo,
        table_count=lambda t: 10,
    )
    uc.refresh_remote_files()
    assert downloader.downloads == []
    table_repo.populate_from_file.assert_not_called()


def test_invalid_download_does_not_invalidate_cache(tmp_path: Path):
    alias_dir = tmp_path / "json"
    alias_dir.mkdir()
    stale_file = alias_dir / "talkgroup_ids.json"
    stale_file.write_text("{}", encoding="utf-8")
    old = time.time() - 100000
    import os

    os.utime(stale_file, (old, old))

    class _BadDownloader(_FakeDownloader):
        def download_file(self, url: str, dest_dir: str, file_name: str) -> bool:
            self.downloads.append(file_name)
            Path(dest_dir, file_name).write_text("<html>error</html>", encoding="utf-8")
            return True

    table_repo = MagicMock()
    alias_repo = MagicMock()
    uc = AliasFilesSyncUseCases(
        files_config={
            "PATH": str(alias_dir),
            "RELOAD_TIME": 3600,
            "PEER": "",
            "SUBS": "",
            "TGID": "talkgroup_ids.json",
            "TGID_URL": "https://example/tg.json",
        },
        monitor_root=tmp_path,
        downloader=_BadDownloader(),
        table_repo=table_repo,
        alias_repo=alias_repo,
        table_count=lambda t: 0,
    )
    uc.refresh_remote_files()
    table_repo.populate_from_file.assert_not_called()
    alias_repo.invalidate_cache.assert_not_called()
