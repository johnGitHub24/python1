"""單元測試：搜尋功能。"""

import pytest

from src.news_scraper.models import NewsArticle
from src.news_scraper.search import (
    SearchOptions,
    article_matches,
    parse_keywords,
    search_articles,
    search_with_options,
)


def _sample() -> list[NewsArticle]:
    return [
        NewsArticle(
            title="測試驅動開發入門",
            url="https://a/1",
            summary="用 pytest 寫單元測試",
            source="TechDaily",
            tags=("tdd", "python"),
        ),
        NewsArticle(
            title="Loop Verify Debug 實戰",
            url="https://a/2",
            summary="Harness 工程迴圈",
            source="DevLab",
            tags=("harness",),
        ),
        NewsArticle(
            title="股市收盤整理",
            url="https://a/3",
            summary="指數小漲",
            source="Finance",
        ),
    ]


@pytest.mark.unit
def test_parse_keywords() -> None:
    assert parse_keywords("  pytest   TDD ") == ["pytest", "TDD"]
    assert parse_keywords("") == []


@pytest.mark.unit
def test_search_any_keyword_in_title_or_summary() -> None:
    hits = search_articles(_sample(), "pytest")
    assert len(hits) == 1
    assert hits[0].title.startswith("測試驅動")


@pytest.mark.unit
def test_search_match_all_requires_every_keyword() -> None:
    hits = search_articles(_sample(), "Loop Debug", match_all=True)
    assert len(hits) == 1
    assert "Loop" in hits[0].title

    none = search_articles(_sample(), "Loop 股市", match_all=True)
    assert none == []


@pytest.mark.unit
def test_search_case_insensitive_by_default() -> None:
    hits = search_articles(_sample(), "HARNESS")
    assert len(hits) == 1


@pytest.mark.unit
def test_search_tags_and_source_fields() -> None:
    hits = search_articles(_sample(), "python", fields=("tags",))
    assert len(hits) == 1

    hits = search_articles(_sample(), "Finance", fields=("source",))
    assert len(hits) == 1


@pytest.mark.unit
def test_empty_query_returns_all() -> None:
    articles = _sample()
    assert search_articles(articles, "") == articles


@pytest.mark.unit
def test_search_with_options_and_article_matches() -> None:
    opts = SearchOptions(query="tdd", fields=("tags",), match_all=True)
    hits = search_with_options(_sample(), opts)
    assert len(hits) == 1
    assert article_matches(hits[0], ["tdd"], fields=("tags",))


@pytest.mark.unit
def test_invalid_field_raises() -> None:
    with pytest.raises(ValueError):
        search_articles(_sample(), "x", fields=("body",))
