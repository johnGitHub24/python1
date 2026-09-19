# NewsScraper Lab · 使用指令總表

本文件整理專案開發過程中用過的指令。  
Windows 若 `python` 不在 PATH，請一律改用 `py -3`。

> 工作目錄請先切到專案根目錄：  
> `d:\SouceDemo\Python_Remote\Python1`

---

## 目錄

1. [環境安裝](#1-環境安裝)
2. [爬蟲 CLI（現行版本）](#2-爬蟲-cli現行版本)
3. [單元／整合測試](#3-單元整合測試)
4. [Harness：Loop → Verify → Debug](#4-harnessloop--verify--debug)
5. [測試 HTML 報告（可選／曾使用）](#5-測試-html-報告可選曾使用)
6. [資訊檢索 IR（曾開發，目前版本未包含）](#6-資訊檢索-ir曾開發目前版本未包含)
7. [Git 版本控制](#7-git-版本控制)
8. [文件與教學](#8-文件與教學)

**自然語言對照（人話 → 指令）**：見 [`NATURAL_LANGUAGE.md`](NATURAL_LANGUAGE.md)。

---

## 1. 環境安裝

```bash
# 安裝相依套件
pip install -r requirements.txt

# 或指定 Python 啟動器（Windows 建議）
py -3 -m pip install -r requirements.txt

# 查看版本
py -3 --version
py -3 -m pip --version
```

可選（產生 pytest HTML 報告時需要）：

```bash
py -3 -m pip install pytest-html
```

---

## 2. 爬蟲 CLI（現行版本）

進入點：`python -m src.news_scraper.cli`（或 `py -3 -m ...`）

### 2.1 參數一覽

| 參數 | 說明 |
|------|------|
| `--demo` | 使用內建示範 RSS（不連外網） |
| `--url URL` | 指定 RSS／HTML 網址（可重複多次） |
| `--search-file PATH` | 對既有 JSONL 做關鍵字搜尋 |
| `-o` / `--output PATH` | 輸出 JSONL（預設 `out/news.jsonl`） |
| `-q` / `--query TEXT` | 關鍵字（空白分隔多詞） |
| `--match-all` | 多關鍵字須全部命中 |
| `--fields a,b,c` | 搜尋欄位（預設 `title,summary,source,tags`） |
| `--source NAME` | 來源標籤 |

### 2.2 常用指令

```bash
# 離線示範：抓取內建 2 則新聞
py -3 -m src.news_scraper.cli --demo -o out/demo.jsonl

# 示範 + 關鍵字篩選
py -3 -m src.news_scraper.cli --demo -q "測試" -o out/hits.jsonl
py -3 -m src.news_scraper.cli --demo -q "Loop" -o out/hits.jsonl

# 多關鍵字全部命中
py -3 -m src.news_scraper.cli --demo -q "測試 驅動" --match-all -o out/hits.jsonl

# 指定搜尋欄位
py -3 -m src.news_scraper.cli --demo -q "python" --fields tags -o out/hits.jsonl

# 對已存檔的 JSONL 離線搜尋
py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "Loop" -o out/hits.jsonl

# 從真實 URL 抓取（請遵守 robots.txt 與服務條款）
py -3 -m src.news_scraper.cli --url https://example.com/feed.xml -o out/news.jsonl
py -3 -m src.news_scraper.cli --url https://a/feed.xml --url https://b/feed.xml -o out/news.jsonl

# 查看 CLI 說明
py -3 -m src.news_scraper.cli -h
```

---

## 3. 單元／整合測試

```bash
# 跑全部測試（詳細）
py -3 -m pytest -v

# 安靜模式
py -3 -m pytest -q

# 只跑單元測試（不連外網）
py -3 -m pytest -m unit
py -3 -m pytest -m unit -v

# 只跑整合測試（本機 HTTPServer）
py -3 -m pytest -m integration
py -3 -m pytest -m integration -v

# 覆蓋率（終端機）
py -3 -m pytest --cov=src/news_scraper --cov-report=term-missing

# 覆蓋率（HTML，輸出到資料夾）
py -3 -m pytest --cov=src/news_scraper --cov-report=html:out/reports/coverage

# 失敗時顯示精簡 traceback
py -3 -m pytest --tb=short
py -3 -m pytest --tb=line

# Windows 終端機中文較穩（PowerShell）
$env:PYTHONIOENCODING='utf-8'
py -3 -m pytest -v
```

---

## 4. Harness：Loop → Verify → Debug

腳本：`harness/loop_verify_debug.py`  
報告：`out/harness/last_run.json`

```bash
# 跑一次並附覆蓋率
py -3 harness/loop_verify_debug.py --cov

# 只跑一次（明確）
py -3 harness/loop_verify_debug.py --once

# 最多重試 3 次（失敗才繼續 loop）
py -3 harness/loop_verify_debug.py --max-loops 3

# 只驗證單元／整合
py -3 harness/loop_verify_debug.py --unit-only
py -3 harness/loop_verify_debug.py --integration-only --cov

# 每次 loop 間隔秒數
py -3 harness/loop_verify_debug.py --max-loops 3 --sleep 2

# 通過後仍跑滿次數
py -3 harness/loop_verify_debug.py --max-loops 3 --no-stop-on-pass

# 說明
py -3 harness/loop_verify_debug.py -h
```

---

## 5. 測試 HTML 報告（可選／曾使用）

開發過程曾用 `pytest-html` 產生網頁報告。

```bash
# 先安裝外掛（若尚未安裝）
py -3 -m pip install pytest-html

# 單元測試 HTML（單檔、內嵌資源）
py -3 -m pytest -m unit --html=out/reports/unit.html --self-contained-html -v

# 整合測試 HTML
py -3 -m pytest -m integration --html=out/reports/integration.html --self-contained-html -v

# 覆蓋率網頁
py -3 -m pytest --cov=src/news_scraper --cov-report=html:out/reports/coverage -q
```

瀏覽器開啟：

- `out/reports/unit.html`
- `out/reports/integration.html`
- `out/reports/coverage/index.html`

（若曾產生索引頁）`out/reports/index.html`

PowerShell 開啟索引（若檔案存在）：

```powershell
Start-Process ".\out\reports\index.html"
```

---

## 6. 資訊檢索 IR（曾開發，目前版本未包含）

> 說明：開發過程曾加入 TF-IDF 資訊檢索（`--ir`、`retrieval.py`），  
> 之後曾依要求退回 `e9d5bf5`，**現行程式碼預設沒有這些參數**。  
> 下列指令僅作歷史紀錄；若重新合併 IR 功能後才可使用。

```bash
# （歷史）示範語料後做相關性排序
py -3 -m src.news_scraper.cli --demo -o out/demo.jsonl
py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "TF-IDF 資訊檢索" --ir --top-k 3 -o out/ir.jsonl

# （歷史）直接對 demo 做 IR
py -3 -m src.news_scraper.cli --demo -q "單元測試" --ir -o out/ir.jsonl

# （歷史）最低分數門檻
py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "harness" --ir --min-score 0.1 --top-k 5
```

當時新增參數：`--ir`、`--top-k`、`--min-score`；輸出含 `ir_score`、`matched_terms`。

---

## 7. Git 版本控制

```bash
# 狀態與紀錄
git status
git log --oneline -5
git remote -v

# 初始化（專案首次）
git init -b main
git remote add origin https://github.com/johnGitHub24/python1.git

# 暫存與提交（範例）
git add .
git commit -m "訊息說明為何變更"

# 推送到 GitHub
git push -u origin main

# 退回指定版本（會丟棄該點之後的本機提交／變更，請先確認）
git reset --hard e9d5bf5abab73fbc2a8ace8e6f151c8284b78291
git clean -fd

# 若遠端也要對齊該版（危險：需明確確認後再執行）
# git push --force origin main
```

遠端倉庫：https://github.com/johnGitHub24/python1

---

## 8. 文件與教學

```bash
# 教學頁（瀏覽器開啟）
# docs/tutorial.html

# 本指令總表
# docs/COMMANDS.md

# README
# README.md
```

PowerShell：

```powershell
Start-Process ".\docs\tutorial.html"
Start-Process ".\docs\COMMANDS.md"   # 若關聯到編輯器
```

---

## 快速抄寫區（現行最常用）

```bash
py -3 -m pip install -r requirements.txt
py -3 -m src.news_scraper.cli --demo -o out/demo.jsonl
py -3 -m src.news_scraper.cli --demo -q "Loop" -o out/hits.jsonl
py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "測試" -o out/hits.jsonl
py -3 -m pytest -m unit
py -3 -m pytest -m integration
py -3 -m pytest --cov=src/news_scraper --cov-report=term-missing
py -3 harness/loop_verify_debug.py --cov --once
```

---

## 維護說明

- 新增 CLI 參數或腳本時，請同步更新本檔與 `README.md`。  
- 見專案規則：`.cursor/rules/sync-docs-after-tasks.mdc`。
