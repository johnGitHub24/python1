"""
爬蟲協調器（Scraper）
====================
【註解教學】協調器只做流程編排，不寫死 HTTP / 解析細節。
這讓 loop-verify-debug 時能針對單一層級除錯。
"""

from __future__ import annotations

from .fetcher import HttpFetcher
from .models import NewsArticle
from .parser import dedupe_by_url, detect_and_parse
from .search import search_articles
from .storage import JsonLinesStore

DEFAULT_SEARCH_FIELDS = ("title", "summary", "source", "tags")


class NewsScraper:
    """新聞爬蟲門面：fetch → parse → dedupe → search →（可選）store。"""

    def __init__(self, fetcher: HttpFetcher | None = None) -> None:
        # 【註解教學】依賴注入：測試可傳入 fake fetcher。
        self.fetcher = fetcher or HttpFetcher()

    def scrape_url(
        self,
        url: str,
        *,
        source: str = "",
        query: str = "",
        match_all: bool = False,
        fields: tuple[str, ...] = DEFAULT_SEARCH_FIELDS,
    ) -> list[NewsArticle]:
        """從單一 URL 抓取並解析新聞列表（可選關鍵字篩選）。"""
        result = self.fetcher.get(url)
        articles = detect_and_parse(
            result.text,
            result.content_type,
            source=source,
            base_url=result.url,
        )
        articles = dedupe_by_url(articles)
        return search_articles(
            articles,
            query,
            fields=fields,
            match_all=match_all,
        )

    def scrape_many(
        self,
        urls: list[str],
        *,
        source: str = "",
        query: str = "",
        match_all: bool = False,
        fields: tuple[str, ...] = DEFAULT_SEARCH_FIELDS,
    ) -> list[NewsArticle]:
        """依序抓取多個來源並合併去重（可選關鍵字篩選）。"""
        collected: list[NewsArticle] = []
        for url in urls:
            # 多來源時先合併再搜尋，避免過早過濾
            collected.extend(self.scrape_url(url, source=source))
        articles = dedupe_by_url(collected)
        return search_articles(
            articles,
            query,
            fields=fields,
            match_all=match_all,
        )

    def scrape_and_save(
        self,
        urls: list[str],
        output_path: str,
        *,
        source: str = "",
        append: bool = False,
        query: str = "",
        match_all: bool = False,
        fields: tuple[str, ...] = DEFAULT_SEARCH_FIELDS,
    ) -> list[NewsArticle]:
        """抓取、可選搜尋後寫入 JSONL。"""
        articles = self.scrape_many(
            urls,
            source=source,
            query=query,
            match_all=match_all,
            fields=fields,
        )
        JsonLinesStore(output_path).save(articles, append=append)
        return articles

    def search_stored(
        self,
        path: str,
        query: str,
        *,
        match_all: bool = False,
        fields: tuple[str, ...] = DEFAULT_SEARCH_FIELDS,
    ) -> list[NewsArticle]:
        """對已儲存的 JSONL 做關鍵字搜尋。"""
        articles = JsonLinesStore(path).load()
        return search_articles(
            articles,
            query,
            fields=fields,
            match_all=match_all,
        )
