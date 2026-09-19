"""
解析層（Parser）
================
【初學者導讀】本檔核心語法：
- for 迴圈、continue（跳過本圈）
- getattr / or 串接預設值
- try / except 錯誤處理
- 函式回傳 list
"""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable
from urllib.parse import urljoin

import feedparser
from bs4 import BeautifulSoup

from .models import NewsArticle


class RssParser:
    """使用 feedparser 解析 RSS / Atom。"""

    def parse(
        self,
        content: str,
        *,
        source: str = "",
        base_url: str = "",
    ) -> list[NewsArticle]:
        """
        【語法】* 後面只能用關鍵字傳參數，例如：
        parser.parse(xml, source="demo")
        """
        feed = feedparser.parse(content)
        # 【語法】A or B or C：由左到右，取第一個「真值」。
        # getattr(物件, "屬性名", 預設) 在屬性不存在時回傳預設，避免 AttributeError。
        feed_title = source or getattr(feed.feed, "title", "") or "rss"
        # 【語法】空 list，稍後用 append 一筆筆加進去。
        articles: list[NewsArticle] = []

        # 【語法】for 元素 in 可迭代: 逐一處理。
        for entry in feed.entries:
            # 【語法】(x or "") 確保後面能呼叫字串方法 .strip()。
            title = (getattr(entry, "title", None) or "").strip()
            link = (getattr(entry, "link", None) or "").strip()
            # 【語法】continue：結束「這一圈」，立刻進入下一筆 entry。
            if not title or not link:
                continue
            # 【語法】startswith 可傳 tuple，任一前綴符合即可。
            if base_url and not link.startswith(("http://", "https://")):
                link = urljoin(base_url, link)

            summary = (
                getattr(entry, "summary", None)
                or getattr(entry, "description", None)
                or ""
            )
            # 第三方：BeautifulSoup 解析 HTML，get_text 取出純文字。
            summary = BeautifulSoup(summary, "lxml").get_text(" ", strip=True)

            published = _entry_published(entry)
            # 【語法】list.append(元素) 把新物件加到清單尾端。
            articles.append(
                NewsArticle(
                    title=title,
                    url=link,
                    summary=summary,
                    source=feed_title,
                    published_at=published,
                )
            )
        # 【語法】return 把結果交給呼叫端；函式到此結束。
        return articles


class HtmlListParser:
    """
    解析簡易 HTML 新聞列表。

    約定（教學用 fixture）：
    <article class="news-item">
      <a class="title" href="...">標題</a>
      <p class="summary">摘要</p>
      <time datetime="ISO">...</time>
    </article>
    """

    def parse(
        self,
        content: str,
        *,
        source: str = "html",
        base_url: str = "",
    ) -> list[NewsArticle]:
        soup = BeautifulSoup(content, "lxml")
        articles: list[NewsArticle] = []

        # 【語法】CSS 選擇器字串：找所有 class 含 news-item 的 article。
        for item in soup.select("article.news-item"):
            anchor = item.select_one("a.title")
            if not anchor:
                continue
            title = anchor.get_text(strip=True)
            href = (anchor.get("href") or "").strip()
            if not title or not href:
                continue
            # 【語法】三元：有 base_url 就拼成絕對網址，否則用原 href。
            url = urljoin(base_url, href) if base_url else href

            summary_el = item.select_one(".summary")
            summary = summary_el.get_text(" ", strip=True) if summary_el else ""

            published = None
            time_el = item.select_one("time[datetime]")
            # 【語法】and：兩邊都真才繼續；短路求值可避免 time_el 是 None 還去取值。
            if time_el and time_el.get("datetime"):
                published = _parse_iso(time_el["datetime"])

            articles.append(
                NewsArticle(
                    title=title,
                    url=url,
                    summary=summary,
                    source=source,
                    published_at=published,
                )
            )
        return articles


def detect_and_parse(
    content: str,
    content_type: str = "",
    *,
    source: str = "",
    base_url: str = "",
) -> list[NewsArticle]:
    """依 Content-Type / 內容特徵選擇解析器。"""
    # 【語法】(x or "") 避免 content_type 是 None 時呼叫 .lower() 失敗。
    lowered = (content_type or "").lower()
    # 【語法】切片 s[:200] 取前 200 字；lstrip() 去掉左邊空白。
    head = content.lstrip()[:200].lower()

    # 【語法】多行布林可用括號包起來，or 串接多個條件。
    is_feed = (
        "xml" in lowered
        or "rss" in lowered
        or "atom" in lowered
        or head.startswith("<?xml")
        or "<rss" in head
        or "<feed" in head
    )
    if is_feed:
        # 【語法】RssParser() 先建立物件，再呼叫 .parse(...)
        return RssParser().parse(content, source=source, base_url=base_url)
    return HtmlListParser().parse(content, source=source or "html", base_url=base_url)


def dedupe_by_url(articles: Iterable[NewsArticle]) -> list[NewsArticle]:
    """依 URL 去重，保留首次出現。"""
    # 【語法】set 查「有沒有看過」很快（平均 O(1)）。
    seen: set[str] = set()
    result: list[NewsArticle] = []
    for article in articles:
        if article.url in seen:
            continue
        # 【語法】set.add(元素) 記下來；下次 in 就會是 True。
        seen.add(article.url)
        result.append(article)
    return result


def _entry_published(entry: object) -> datetime | None:
    published = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if not published:
        return None
    # 【語法】try/except：可能失敗的程式放 try；失敗時跑 except。
    try:
        dt = parsedate_to_datetime(published)
        if dt.tzinfo is None:
            # 【語法】replace(...) 回傳「改過欄位的新 datetime」，原物件不改。
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError, IndexError):
        # 【語法】except (A, B, C) 可一次捕捉多種例外型別。
        return _parse_iso(str(published))


def _parse_iso(value: str) -> datetime | None:
    try:
        text = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        # 解析失敗就回傳 None，表示「沒有可信的時間」。
        return None
