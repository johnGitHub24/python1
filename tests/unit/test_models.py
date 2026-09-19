"""單元測試：資料模型。"""

from datetime import datetime, timezone

import pytest

from src.news_scraper.models import NewsArticle


@pytest.mark.unit
def test_article_requires_title_and_url() -> None:
    with pytest.raises(ValueError):
        NewsArticle(title="", url="https://x")
    with pytest.raises(ValueError):
        NewsArticle(title="t", url="")


@pytest.mark.unit
def test_to_dict_and_from_dict_roundtrip() -> None:
    original = NewsArticle(
        title="標題",
        url="https://example.com/1",
        summary="摘要",
        source="demo",
        published_at=datetime(2026, 9, 19, 10, 0, tzinfo=timezone.utc),
        tags=("tech", "edu"),
    )
    restored = NewsArticle.from_dict(original.to_dict())
    assert restored.title == original.title
    assert restored.url == original.url
    assert restored.summary == original.summary
    assert restored.source == original.source
    assert restored.published_at == original.published_at
    assert restored.tags == original.tags
