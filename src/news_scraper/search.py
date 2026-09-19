"""
搜尋層（Search）
================
對已擷取的 NewsArticle 做關鍵字過濾。

【註解教學】搜尋與爬取分離：
爬蟲負責「取得資料」，搜尋負責「篩選資料」；兩者可獨立測試與重用。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .models import NewsArticle


@dataclass(frozen=True)
class SearchOptions:
    """
    搜尋選項。

    Attributes:
        query: 關鍵字字串；空白分隔多個詞
        fields: 要搜尋的欄位（title / summary / source / url / tags）
        match_all: True 時每個關鍵字都要命中；False 時任一命中即可
        case_sensitive: 是否區分大小寫
    """

    query: str
    fields: tuple[str, ...] = ("title", "summary", "source", "tags")
    match_all: bool = False
    case_sensitive: bool = False


_ALLOWED_FIELDS = frozenset({"title", "summary", "source", "url", "tags"})


def parse_keywords(query: str) -> list[str]:
    """將查詢字串拆成關鍵字列表（依空白分割，忽略空詞）。"""
    return [part for part in query.split() if part.strip()]


def _field_text(article: NewsArticle, field: str) -> str:
    if field == "title":
        return article.title
    if field == "summary":
        return article.summary
    if field == "source":
        return article.source
    if field == "url":
        return article.url
    if field == "tags":
        return " ".join(article.tags)
    raise ValueError(f"不支援的搜尋欄位: {field}")


def _haystack(article: NewsArticle, fields: Sequence[str], *, case_sensitive: bool) -> str:
    unknown = set(fields) - _ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"不支援的搜尋欄位: {sorted(unknown)}")
    text = " ".join(_field_text(article, f) for f in fields)
    return text if case_sensitive else text.casefold()


def article_matches(
    article: NewsArticle,
    keywords: Sequence[str],
    *,
    fields: Sequence[str] = ("title", "summary", "source", "tags"),
    match_all: bool = False,
    case_sensitive: bool = False,
) -> bool:
    """判斷單則新聞是否符合關鍵字條件。"""
    if not keywords:
        return True
    haystack = _haystack(article, fields, case_sensitive=case_sensitive)
    needles = keywords if case_sensitive else [k.casefold() for k in keywords]
    if match_all:
        return all(needle in haystack for needle in needles)
    return any(needle in haystack for needle in needles)


def search_articles(
    articles: Iterable[NewsArticle],
    query: str,
    *,
    fields: Sequence[str] = ("title", "summary", "source", "tags"),
    match_all: bool = False,
    case_sensitive: bool = False,
) -> list[NewsArticle]:
    """
    依關鍵字篩選新聞列表。

    query 為空字串時回傳全部（等同不過濾），方便 CLI 共用流程。
    """
    keywords = parse_keywords(query)
    if not keywords:
        return list(articles)
    return [
        article
        for article in articles
        if article_matches(
            article,
            keywords,
            fields=fields,
            match_all=match_all,
            case_sensitive=case_sensitive,
        )
    ]


def search_with_options(
    articles: Iterable[NewsArticle],
    options: SearchOptions,
) -> list[NewsArticle]:
    """以 SearchOptions 執行搜尋（便於序列化／測試）。"""
    return search_articles(
        articles,
        options.query,
        fields=options.fields,
        match_all=options.match_all,
        case_sensitive=options.case_sensitive,
    )
