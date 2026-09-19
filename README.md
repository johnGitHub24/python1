# NewsScraper Lab

Python 新聞資訊爬蟲教學專案：單元／整合測試、HTML 教學（Mermaid）、註解規範、以及 **Loop → Verify → Debug** harness。

## 快速開始

```bash
pip install -r requirements.txt
py -3 -m src.news_scraper.cli --demo -o out/demo.jsonl
py -3 -m src.news_scraper.cli --demo -q "測試" -o out/hits.jsonl
py -3 -m pytest
py -3 harness/loop_verify_debug.py --cov
```

## 搜尋

```bash
# 爬取同時篩選
py -3 -m src.news_scraper.cli --demo -q "Loop" -o out/hits.jsonl

# 對既有 JSONL 離線搜尋
py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "測試 驅動" --match-all -o out/hits.jsonl
```
用瀏覽器開啟 `docs/tutorial.html` 閱讀完整教學與流程圖。

## 專案結構

```
src/news_scraper/   # 爬蟲核心（fetch → parse → store）
tests/unit/         # 單元測試（不連外網）
tests/integration/  # 整合測試（本機 HTTPServer）
harness/            # Loop-Verify-Debug 鞍具
docs/tutorial.html  # HTML 指導教學 + Mermaid
```

## 測試

```bash
pytest -m unit
pytest -m integration
pytest --cov=src/news_scraper --cov-report=term-missing
```

## 禮貌提醒

實際爬取公開網站前請遵守 robots.txt 與服務條款，並控制請求頻率。本專案預設以 fixture 與本機 server 完成教學與驗證。
