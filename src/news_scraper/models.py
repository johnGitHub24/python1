"""
資料模型（Data Model）
======================
【初學者導讀】本檔核心語法：
- @dataclass：少寫很多樣板碼
- 型別標註 str | None（可選值）
- @classmethod：用「類別」呼叫的建構方式
- raise ValueError：主動回報錯誤
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class NewsArticle:
    """
    單則新聞文章。

    【語法】class 用來定義「自訂資料型別」。
    這裡的每個欄位，之後都能用 article.title 這種方式讀取。
    """

    # 【語法】必填欄位：沒有「= 預設值」
    title: str
    url: str
    # 【語法】選填欄位：有預設值，建立物件時可以省略
    summary: str = ""
    source: str = ""
    # 【語法】A | B 表示「可以是 A 或 B」；None 代表「沒有值」。
    published_at: datetime | None = None
    # 【語法】field(default_factory=...)：
    # 預設值若是「每次呼叫都要新算」的東西（例如現在時間），
    # 不能直接寫 = datetime.now()，要用 default_factory。
    # lambda: ... 是「匿名小函式」，這裡每次建立物件就取當下 UTC 時間。
    fetched_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    # 【語法】空的 tuple 寫成 () ；tuple[str, ...] 表示元素都是字串。
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """
        【語法】dataclass 在 __init__ 結束後會呼叫 __post_init__。
        適合放驗證邏輯：資料一建立就檢查合不合法。
        """
        # 【語法】or：左邊是假值就看右邊。
        # ""（空字串）是假值；strip() 去掉空白後若變空，也視為無效。
        if not self.title or not self.title.strip():
            raise ValueError("title 不可為空")
        if not self.url or not self.url.strip():
            raise ValueError("url 不可為空")

    def to_dict(self) -> dict[str, Any]:
        """
        轉成字典，方便寫入 JSON。

        【語法】-> dict[str, Any]：鍵是字串，值可以是任意型別。
        """
        # 【語法】asdict(dataclass實例) → 一般 dict。
        data = asdict(self)
        # 【語法】for 變數 in (a, b): 依序處理兩個鍵名。
        for key in ("published_at", "fetched_at"):
            value = data[key]
            # 【語法】isinstance(x, 型別) 檢查 x 是不是該型別。
            if isinstance(value, datetime):
                # ISO 字串例如 "2026-09-19T10:00:00+00:00"，JSON 友好。
                data[key] = value.isoformat()
        # 【語法】list(tuple) 把不可變的 tuple 轉成可變 list（JSON 陣列）。
        data["tags"] = list(self.tags)
        return data

    # 【語法】@classmethod：第一個參數是 cls（類別本身），不是 self（實例）。
    # 呼叫方式：NewsArticle.from_dict({...}) 而不是 article.from_dict(...)。
    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> NewsArticle:
        """從字典還原 NewsArticle（與 to_dict 對稱）。"""
        # 【語法】dict.get(鍵, 預設值)：鍵不存在時回傳預設值，不會 KeyError。
        published = raw.get("published_at")
        fetched = raw.get("fetched_at")
        # 【語法】cls(...) 等同 NewsArticle(...)，但寫 cls 較利於繼承。
        return cls(
            title=str(raw["title"]),  # 【語法】raw["title"] 鍵不存在會拋 KeyError
            url=str(raw["url"]),
            summary=str(raw.get("summary", "")),
            source=str(raw.get("source", "")),
            published_at=_parse_dt(published),
            # 【語法】A or B：A 有值就用 A，否則用 B。
            fetched_at=_parse_dt(fetched) or datetime.now(timezone.utc),
            tags=tuple(raw.get("tags") or ()),
        )


def _parse_dt(value: Any) -> datetime | None:
    """將 ISO 字串或 datetime 轉成「有時區」的 datetime。"""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        # 【語法】三元運算 + 屬性檢查 tzinfo（時區資訊）
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    # 【語法】字串.replace(舊, 新) 做文字替換；Z 是 UTC 的常見寫法。
    text = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(text)
