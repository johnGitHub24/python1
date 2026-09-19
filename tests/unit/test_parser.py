"""單元測試：解析器（純字串，不連網）。"""

import pytest

from src.news_scraper.parser import (
    HtmlListParser,
    RssParser,
    dedupe_by_url,
    detect_and_parse,
)
from src.news_scraper.models import NewsArticle
from tests.fixtures.sample_feeds import SAMPLE_HTML, SAMPLE_RSS


@pytest.mark.unit
def test_rss_parser_skips_empty_title() -> None:
    articles = RssParser().parse(SAMPLE_RSS, source="fixture")
    assert len(articles) == 2
    assert articles[0].title == "第一則"
    assert articles[1].summary == "摘要 B"  # HTML 已剝除
    assert articles[0].source == "fixture"


@pytest.mark.unit
def test_html_parser_resolves_relative_urls() -> None:
    articles = HtmlListParser().parse(
        SAMPLE_HTML,
        source="html-fixture",
        base_url="https://news.example/",
    )
    assert len(articles) == 2
    assert articles[0].url == "https://news.example/stories/1"
    assert articles[0].published_at is not None
    assert articles[1].url == "https://news.example/stories/2"


@pytest.mark.unit
def test_detect_and_parse_chooses_rss() -> None:
    articles = detect_and_parse(SAMPLE_RSS, "application/rss+xml")
    assert len(articles) == 2


@pytest.mark.unit
def test_dedupe_by_url() -> None:
    a = NewsArticle(title="A", url="https://x/1")
    b = NewsArticle(title="B", url="https://x/1")
    c = NewsArticle(title="C", url="https://x/2")
    assert [x.title for x in dedupe_by_url([a, b, c])] == ["A", "C"]
