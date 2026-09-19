# NewsScraper Lab

Python 新聞資訊爬蟲教學專案：單元／整合測試、HTML 教學（Mermaid）、**初學者語法註解**、以及 **Loop → Verify → Debug** harness。

## 快速開始

```bash
pip install -r requirements.txt
# Windows 若 python 不在 PATH，請改用：py -3
py -3 -m src.news_scraper.cli --demo -o out/demo.jsonl
py -3 -m src.news_scraper.cli --demo -q "測試" -o out/hits.jsonl
py -3 -m pytest
py -3 harness/loop_verify_debug.py --cov
```

用瀏覽器開啟 `docs/tutorial.html` 閱讀完整教學與流程圖。  
**指令總表**：[`docs/COMMANDS.md`](docs/COMMANDS.md)　·　**操作人話**：[`docs/NATURAL_LANGUAGE.md`](docs/NATURAL_LANGUAGE.md)　·　**Session 你下的指令紀錄**：[`docs/SESSION_PROMPTS.md`](docs/SESSION_PROMPTS.md)

## 搜尋

```bash
# 爬取同時篩選
py -3 -m src.news_scraper.cli --demo -q "Loop" -o out/hits.jsonl

# 對既有 JSONL 離線搜尋
py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "測試 驅動" --match-all -o out/hits.jsonl
```

## 專案結構

```
src/news_scraper/   # 爬蟲核心（fetch → parse → search → store）
tests/unit/         # 單元測試（不連外網）
tests/integration/  # 整合測試（本機 HTTPServer）
harness/            # Loop-Verify-Debug 鞍具
docs/tutorial.html  # HTML 指導教學 + Mermaid
docs/COMMANDS.md         # 終端機指令總表
docs/NATURAL_LANGUAGE.md # 操作人話 ↔ 指令
docs/REQUIREMENTS_NL.md  # 你輸入的五條需求（自然語言語法）
.cursor/rules/           # Cursor 專案規則
```

## 初學者怎麼讀程式

原始碼內註解標籤：

| 標籤 | 用途 |
|------|------|
| `【初學者導讀】` | 檔案開頭：本檔會用到哪些語法 |
| `【語法】` | 行內：型別標註、推導式、`*` 參數、`with` 等 |
| `【註解教學】` | 設計為什麼這樣拆 |

建議閱讀順序：`models.py` → `search.py` → `fetcher.py` → `parser.py` → `scraper.py` → `cli.py`。

## 測試

```bash
pytest -m unit
pytest -m integration
pytest --cov=src/news_scraper --cov-report=term-missing
```

## 文件同步約定

完成功能／重構後，需同步更新 `README.md`、`docs/tutorial.html`、`docs/COMMANDS.md`（見 `.cursor/rules/sync-docs-after-tasks.mdc`）。

## 禮貌提醒

實際爬取公開網站前請遵守 robots.txt 與服務條款，並控制請求頻率。本專案預設以 fixture 與本機 server 完成教學與驗證。
