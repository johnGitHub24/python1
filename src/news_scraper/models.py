"""
資料模型（Data Model）
======================
【註解教學】為何需要模型？
將「新聞」抽象成結構化物件，方便單元測試斷言、序列化儲存，
並讓 scrape / parse / store 各層用同一契約溝通。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class NewsArticle:
    """
    單則新聞文章。

    Attributes:
        title: 標題（必填）
        url: 原文連結（必填，作為去重鍵）
        summary: 摘要或內文片段
        source: 來源名稱（例如 BBC、本地 fixture）
        published_at: 發布時間（UTC）；未知時為 None
        fetched_at: 爬蟲抓取時間（UTC）
        tags: 可選標籤列表
    """

    title: str
    url: str
    summary: str = ""
    source: str = ""
    published_at: datetime | None = None
    fetched_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # 【註解教學】資料驗證放在模型內，避免髒資料進入下游。
        if not self.title or not self.title.strip():
            raise ValueError("title 不可為空")
        if not self.url or not self.url.strip():
            raise ValueError("url 不可為空")

    def to_dict(self) -> dict[str, Any]:
        """轉成可 JSON 序列化的字典（datetime → ISO 字串）。"""
        data = asdict(self)
        for key in ("published_at", "fetched_at"):
            value = data[key]
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        data["tags"] = list(self.tags)
        return data

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> NewsArticle:
        """從字典還原 NewsArticle（與 to_dict 對稱）。"""
        published = raw.get("published_at")
        fetched = raw.get("fetched_at")
        return cls(
            title=str(raw["title"]),
            url=str(raw["url"]),
            summary=str(raw.get("summary", "")),
            source=str(raw.get("source", "")),
            published_at=_parse_dt(published),
            fetched_at=_parse_dt(fetched) or datetime.now(timezone.utc),
            tags=tuple(raw.get("tags") or ()),
        )


def _parse_dt(value: Any) -> datetime | None:
    """將 ISO 字串或 datetime 轉成 aware datetime。"""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(text)
