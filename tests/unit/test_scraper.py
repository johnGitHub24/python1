"""單元測試：Scraper（mock HTTP，不連外網）。"""

from dataclasses import dataclass

import pytest

from src.news_scraper.scraper import NewsScraper
from tests.fixtures.sample_feeds import SAMPLE_RSS


@dataclass
class FakeFetchResult:
    url: str
    status_code: int
    text: str
    content_type: str = "application/rss+xml"


class FakeFetcher:
    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping
        self.calls: list[str] = []

    def get(self, url: str) -> FakeFetchResult:
        self.calls.append(url)
        return FakeFetchResult(url=url, status_code=200, text=self.mapping[url])


@pytest.mark.unit
def test_scrape_url_with_fake_fetcher() -> None:
    fetcher = FakeFetcher({"https://feed/test": SAMPLE_RSS})
    scraper = NewsScraper(fetcher=fetcher)  # type: ignore[arg-type]
    articles = scraper.scrape_url("https://feed/test", source="unit")
    assert len(articles) == 2
    assert fetcher.calls == ["https://feed/test"]


@pytest.mark.unit
def test_scrape_many_dedupes_across_feeds() -> None:
    fetcher = FakeFetcher(
        {
            "https://feed/a": SAMPLE_RSS,
            "https://feed/b": SAMPLE_RSS,
        }
    )
    scraper = NewsScraper(fetcher=fetcher)  # type: ignore[arg-type]
    articles = scraper.scrape_many(["https://feed/a", "https://feed/b"])
    assert len(articles) == 2


@pytest.mark.unit
def test_scrape_url_with_query() -> None:
    fetcher = FakeFetcher({"https://feed/test": SAMPLE_RSS})
    scraper = NewsScraper(fetcher=fetcher)  # type: ignore[arg-type]
    articles = scraper.scrape_url("https://feed/test", query="第二則")
    assert len(articles) == 1
    assert articles[0].title == "第二則"
