"""
儲存層（Storage）
=================
將新聞寫入 JSON Lines，方便 CLI 與整合測試驗證輸出。
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import NewsArticle


class JsonLinesStore:
    """以 JSONL（每行一則新聞）持久化。"""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, articles: list[NewsArticle], *, append: bool = False) -> int:
        """
        寫入文章列表。

        Returns:
            寫入筆數
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with self.path.open(mode, encoding="utf-8") as fp:
            for article in articles:
                fp.write(json.dumps(article.to_dict(), ensure_ascii=False) + "\n")
        return len(articles)

    def load(self) -> list[NewsArticle]:
        """讀回全部文章；檔案不存在則回傳空列表。"""
        if not self.path.exists():
            return []
        articles: list[NewsArticle] = []
        with self.path.open(encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                articles.append(NewsArticle.from_dict(json.loads(line)))
        return articles
