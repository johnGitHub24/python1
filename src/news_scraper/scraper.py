"""
爬蟲協調器（Scraper）
====================
【初學者導讀】本檔核心語法：
- 組合多個模組（import 後呼叫）
- 預設參數與關鍵字參數
- list.extend 合併清單
"""

from __future__ import annotations

from .fetcher import HttpFetcher
from .models import NewsArticle
from .parser import dedupe_by_url, detect_and_parse
from .search import search_articles
from .storage import JsonLinesStore

# 【語法】常數 tuple：當「預設搜尋欄位」共用，避免到處複製貼上。
DEFAULT_SEARCH_FIELDS = ("title", "summary", "source", "tags")


class NewsScraper:
    """新聞爬蟲門面：fetch → parse → dedupe → search →（可選）store。"""

    def __init__(self, fetcher: HttpFetcher | None = None) -> None:
        # 【語法】依賴注入：
        # 正式環境：不傳參數 → 用真正的 HttpFetcher()
        # 測試環境：傳入 FakeFetcher → 不需要上網
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
        # 步驟 1：下載
        result = self.fetcher.get(url)
        # 步驟 2：解析（關鍵字參數把「誰是誰」寫清楚）
        articles = detect_and_parse(
            result.text,
            result.content_type,
            source=source,
            base_url=result.url,
        )
        # 步驟 3：去重
        articles = dedupe_by_url(articles)
        # 步驟 4：搜尋過濾（query 为空字串時，search 會回傳全部）
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
            # 【語法】list.extend(另一個list)：把另一個 list 的元素「展開加進去」。
            # 注意：append(list) 會變成「list 裡又塞一個 list」，通常不是我們要的。
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
        # 【語法】先建立物件再呼叫方法：JsonLinesStore(路徑).save(...)
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
