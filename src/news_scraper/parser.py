"""
解析層（Parser）
================
支援 RSS/Atom 與簡易 HTML 列表頁。

【註解教學】解析與擷取分離：
同一份 HTML/XML 可用不同 parser；測試時直接餵 fixture 字串即可。
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
        feed = feedparser.parse(content)
        feed_title = source or getattr(feed.feed, "title", "") or "rss"
        articles: list[NewsArticle] = []

        for entry in feed.entries:
            title = (getattr(entry, "title", None) or "").strip()
            link = (getattr(entry, "link", None) or "").strip()
            if not title or not link:
                continue
            if base_url and not link.startswith(("http://", "https://")):
                link = urljoin(base_url, link)

            summary = (
                getattr(entry, "summary", None)
                or getattr(entry, "description", None)
                or ""
            )
            # 去掉 HTML 標籤，保留純文字摘要
            summary = BeautifulSoup(summary, "lxml").get_text(" ", strip=True)

            published = _entry_published(entry)
            articles.append(
                NewsArticle(
                    title=title,
                    url=link,
                    summary=summary,
                    source=feed_title,
                    published_at=published,
                )
            )
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

        for item in soup.select("article.news-item"):
            anchor = item.select_one("a.title")
            if not anchor:
                continue
            title = anchor.get_text(strip=True)
            href = (anchor.get("href") or "").strip()
            if not title or not href:
                continue
            url = urljoin(base_url, href) if base_url else href

            summary_el = item.select_one(".summary")
            summary = summary_el.get_text(" ", strip=True) if summary_el else ""

            published = None
            time_el = item.select_one("time[datetime]")
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
    """
    依 Content-Type / 內容特徵選擇解析器。

    【註解教學】單一入口方便 scraper 與整合測試共用。
    """
    lowered = (content_type or "").lower()
    head = content.lstrip()[:200].lower()

    is_feed = (
        "xml" in lowered
        or "rss" in lowered
        or "atom" in lowered
        or head.startswith("<?xml")
        or "<rss" in head
        or "<feed" in head
    )
    if is_feed:
        return RssParser().parse(content, source=source, base_url=base_url)
    return HtmlListParser().parse(content, source=source or "html", base_url=base_url)


def dedupe_by_url(articles: Iterable[NewsArticle]) -> list[NewsArticle]:
    """依 URL 去重，保留首次出現。"""
    seen: set[str] = set()
    result: list[NewsArticle] = []
    for article in articles:
        if article.url in seen:
            continue
        seen.add(article.url)
        result.append(article)
    return result


def _entry_published(entry: object) -> datetime | None:
    published = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if not published:
        return None
    try:
        dt = parsedate_to_datetime(published)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError, IndexError):
        return _parse_iso(str(published))


def _parse_iso(value: str) -> datetime | None:
    try:
        text = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None
