"""
儲存層（Storage）
=================
【初學者導讀】本檔核心語法：
- pathlib.Path 路徑物件
- with 開啟檔案（自動關閉）
- json.dumps / json.loads
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import NewsArticle


class JsonLinesStore:
    """
    以 JSONL（每行一則新聞）持久化。

    【語法】JSONL = JSON Lines：每一行是一個完整 JSON 物件。
    """

    def __init__(self, path: str | Path) -> None:
        # 【語法】Path(path) 把字串路徑轉成 Path 物件，方便 .exists()、.open()。
        self.path = Path(path)

    def save(self, articles: list[NewsArticle], *, append: bool = False) -> int:
        """寫入文章列表；回傳寫入筆數。"""
        # 【語法】parents=True：中間資料夾不存在就一併建立。
        # exist_ok=True：資料夾已存在也不報錯。
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # 【語法】三元運算決定檔案模式："a" 附加、"w" 覆寫。
        mode = "a" if append else "w"
        # 【語法】with ... as fp: 離開區塊時自動關閉檔案，即使中途出錯也會關。
        with self.path.open(mode, encoding="utf-8") as fp:
            for article in articles:
                # 【語法】json.dumps(dict) → JSON 文字。
                # ensure_ascii=False 才能正確寫出中文（否則會變 \\uXXXX）。
                # +"\\n" 讓下一則新聞換行（JSONL 格式）。
                fp.write(json.dumps(article.to_dict(), ensure_ascii=False) + "\n")
        # 【語法】len(list) 回傳元素個數。
        return len(articles)

    def load(self) -> list[NewsArticle]:
        """讀回全部文章；檔案不存在則回傳空列表。"""
        if not self.path.exists():
            return []
        articles: list[NewsArticle] = []
        with self.path.open(encoding="utf-8") as fp:
            # 【語法】for line in 檔案：一次讀一行（含換行字元）。
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                # 【語法】json.loads(文字) → Python dict / list。
                articles.append(NewsArticle.from_dict(json.loads(line)))
        return articles
