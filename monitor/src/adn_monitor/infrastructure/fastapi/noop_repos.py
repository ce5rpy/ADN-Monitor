"""In-memory no-op repositories when MySQL is unavailable (ingest still runs)."""

from __future__ import annotations

from ...application.ports import AliasRepository, LastHeardRepository, TgCountRepository
from ...domain.entities import PeerAlias, SubscriberAlias, TalkgroupAlias


class NoOpAliasRepository(AliasRepository):
    def get_subscriber(self, dmr_id: int) -> SubscriberAlias | None:
        return None

    def get_peer(self, peer_id: int) -> PeerAlias | None:
        return None

    def get_talkgroup(self, tgid: int) -> TalkgroupAlias | None:
        return None

    def ensure_subscriber_in_cache(self, dmr_id: int) -> None:
        return None

    def ensure_talkgroup_in_cache(self, tg_id: int) -> None:
        return None


class NoOpLastHeardRepository(LastHeardRepository):
    def insert_last_heard(self, *args, **kwargs) -> None:
        return None

    def insert_lstheard_log(self, *args, **kwargs) -> None:
        return None

    def select_for_render(self, table: str, row_num: int) -> list:
        return []

    def clean_table(self, table: str, keep_rows: int) -> None:
        return None


class NoOpTgCountRepository(TgCountRepository):
    def insert_tgcount(self, *args, **kwargs) -> None:
        return None

    def select_tgcount(self, row_num: int):
        return None

    def clean_tgcount(self) -> None:
        return None
