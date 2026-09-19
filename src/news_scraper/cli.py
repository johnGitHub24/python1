"""
命令列入口（CLI）
================
【初學者導讀】本檔核心語法：
- argparse：把「終端機參數」變成 Python 變數
- if / elif / else 流程分支
- if __name__ == "__main__": 腳本直接執行的入口
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .scraper import NewsScraper
from .search import search_articles
from .storage import JsonLinesStore


# 【語法】三引號 """...""" 可寫跨很多行的字串（這裡放示範用 RSS XML）。
DEMO_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Demo News</title>
    <item>
      <title>示範新聞：測試驅動開發</title>
      <link>https://example.com/news/tdd</link>
      <description>以單元測試與整合測試打造可靠爬蟲。</description>
      <pubDate>Sat, 19 Sep 2026 09:00:00 GMT</pubDate>
    </item>
    <item>
      <title>示範新聞：Loop Verify Debug</title>
      <link>https://example.com/news/loop</link>
      <description>Harness 工程：迴圈執行、驗證、除錯。</description>
      <pubDate>Sat, 19 Sep 2026 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


def build_parser() -> argparse.ArgumentParser:
    """建立命令列參數解析器。"""
    parser = argparse.ArgumentParser(description="新聞資訊爬蟲（教學版）")
    # 【語法】action="append"：同樣參數可出現多次，結果會是 list。
    # 例：--url a --url b → args.url == ["a", "b"]
    parser.add_argument("--url", action="append", default=[], help="RSS 或 HTML 列表 URL，可重複")
    # 【語法】action="store_true"：有帶這個旗標就是 True，沒帶就是 False。
    parser.add_argument("--demo", action="store_true", help="使用內建示範 RSS（不連外網）")
    parser.add_argument(
        "--search-file",
        default="",
        help="對既有 JSONL 搜尋（不重新爬取）",
    )
    parser.add_argument("-o", "--output", default="out/news.jsonl", help="輸出 JSONL 路徑")
    parser.add_argument("--source", default="", help="來源標籤")
    parser.add_argument(
        "-q",
        "--query",
        default="",
        help="關鍵字搜尋（空白分隔多詞；預設任一命中）",
    )
    parser.add_argument(
        "--match-all",
        action="store_true",
        help="多關鍵字時需全部命中",
    )
    parser.add_argument(
        "--fields",
        default="title,summary,source,tags",
        help="搜尋欄位，逗號分隔（title,summary,source,url,tags）",
    )
    return parser


def _parse_fields(raw: str) -> tuple[str, ...]:
    # 【語法】tuple(... for ...) 建立 tuple；or 用來提供後備預設值。
    fields = tuple(part.strip() for part in raw.split(",") if part.strip())
    return fields or ("title", "summary", "source", "tags")


def _print_articles(articles: list, *, label: str, output: Path | None = None) -> None:
    # 【語法】f-string 裡可以放運算式，例如 len(articles)。
    suffix = f" → {output}" if output is not None else ""
    print(f"{label} {len(articles)} 則新聞{suffix}")
    # 【語法】切片 articles[:5] 最多取前 5 筆（不足 5 筆就全拿）。
    for article in articles[:5]:
        print(f"  - {article.title}")
    if len(articles) > 5:
        print(f"  ... 另有 {len(articles) - 5} 則")


def main(argv: list[str] | None = None) -> int:
    """
    程式主流程；回傳「結束代碼」。

    【語法】慣例：return 0 代表成功；非 0 代表失敗（給終端機／腳本判斷）。
    """
    # 【語法】parse_args(argv) 解析參數；argv 為 None 時自動讀 sys.argv。
    args = build_parser().parse_args(argv)
    output = Path(args.output)
    fields = _parse_fields(args.fields)
    scraper = NewsScraper()

    if args.search_file:
        path = Path(args.search_file)
        if not path.exists():
            # 【語法】file=sys.stderr：錯誤訊息印到「標準錯誤」，不跟一般輸出混在一起。
            print(f"找不到檔案: {path}", file=sys.stderr)
            return 2
        if not args.query.strip():
            print("使用 --search-file 時請提供 -q/--query", file=sys.stderr)
            return 2
        articles = scraper.search_stored(
            str(path),
            args.query,
            match_all=args.match_all,
            fields=fields,
        )
        JsonLinesStore(output).save(articles)
        _print_articles(articles, label="搜尋命中", output=output)
        return 0

    if args.demo:
        # 【語法】函式內部 import：只有走到這個分支才載入，可稍微加快啟動。
        from .parser import RssParser

        articles = RssParser().parse(DEMO_RSS, source=args.source or "demo")
        articles = search_articles(
            articles,
            args.query,
            fields=fields,
            match_all=args.match_all,
        )
        JsonLinesStore(output).save(articles)
    elif args.url:
        articles = scraper.scrape_and_save(
            args.url,
            str(output),
            source=args.source,
            query=args.query,
            match_all=args.match_all,
            fields=fields,
        )
    else:
        print("請指定 --url、--demo 或 --search-file", file=sys.stderr)
        return 2

    label = "搜尋命中" if args.query.strip() else "已擷取"
    _print_articles(articles, label=label, output=output)
    return 0


# 【語法】這一段非常常見：
# 直接執行本檔（python -m src.news_scraper.cli）時 __name__ 會是 "__main__"；
# 被別人 import 時則不會是 "__main__"，就不會自動跑 main()。
if __name__ == "__main__":
    # 【語法】SystemExit(數字) 讓行程以該結束碼結束。
    raise SystemExit(main())
