"""單元測試：儲存層。"""

import pytest

from src.news_scraper.models import NewsArticle
from src.news_scraper.storage import JsonLinesStore


@pytest.mark.unit
def test_jsonl_save_and_load(tmp_path) -> None:
    path = tmp_path / "news.jsonl"
    store = JsonLinesStore(path)
    articles = [
        NewsArticle(title="一", url="https://a/1", summary="s1"),
        NewsArticle(title="二", url="https://a/2", summary="s2"),
    ]
    assert store.save(articles) == 2
    loaded = store.load()
    assert len(loaded) == 2
    assert loaded[0].title == "一"
    assert loaded[1].url == "https://a/2"


@pytest.mark.unit
def test_load_missing_file(tmp_path) -> None:
    assert JsonLinesStore(tmp_path / "missing.jsonl").load() == []
