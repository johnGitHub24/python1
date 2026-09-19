# 自然語言 ↔ 指令對照

用「人話」描述你想做的事，對應到可執行的指令。  
（Windows 請用 `py -3`；工作目錄為專案根目錄。）

完整終端機語法另見 [`COMMANDS.md`](COMMANDS.md)。

---

## 怎麼讀這張表

| 欄位 | 意思 |
|------|------|
| 你可能會說 | 自然語言（口語／需求描述） |
| 實際指令 | 複製到終端機執行 |

---

## 一、環境與安裝

| 你可能會說 | 實際指令 |
|------------|----------|
| 幫我裝好這個專案需要的套件 | `py -3 -m pip install -r requirements.txt` |
| 我電腦上的 Python 是哪一版？ | `py -3 --version` |
| 我要產生網頁測試報告，多裝一個外掛 | `py -3 -m pip install pytest-html` |

---

## 二、爬新聞／示範資料

| 你可能會說 | 實際指令 |
|------------|----------|
| 不要連外網，用內建示範新聞跑一次 | `py -3 -m src.news_scraper.cli --demo -o out/demo.jsonl` |
| 把示範結果存到指定檔案 | `py -3 -m src.news_scraper.cli --demo -o out/我的檔名.jsonl` |
| 去抓這個 RSS／網址的新聞 | `py -3 -m src.news_scraper.cli --url https://example.com/feed.xml -o out/news.jsonl` |
| 一次抓好幾個來源 | `py -3 -m src.news_scraper.cli --url https://a/feed.xml --url https://b/feed.xml -o out/news.jsonl` |
| 幫我看這個程式有哪些參數可以下 | `py -3 -m src.news_scraper.cli -h` |

**參數的人話：**

| 參數 | 自然語言意思 |
|------|----------------|
| `--demo` | 用內建練習資料，不上網 |
| `--url …` | 要抓的網址（可說多次＝多個來源） |
| `-o` / `--output …` | 結果存到哪裡 |
| `--source …` | 幫這批新聞標一個來源名稱 |

---

## 三、搜尋新聞（關鍵字）

| 你可能會說 | 實際指令 |
|------------|----------|
| 示範資料裡找出標題或摘要有「Loop」的 | `py -3 -m src.news_scraper.cli --demo -q "Loop" -o out/hits.jsonl` |
| 關鍵字要「測試」和「驅動」都出現才算 | `py -3 -m src.news_scraper.cli --demo -q "測試 驅動" --match-all -o out/hits.jsonl` |
| 只在標籤欄位找 python | `py -3 -m src.news_scraper.cli --demo -q "python" --fields tags -o out/hits.jsonl` |
| 不要重新爬，直接搜之前存好的檔 | `py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "Loop" -o out/hits.jsonl` |
| 空白隔開的多個詞，有一個命中就好 | （預設行為）加 `-q "詞A 詞B"`，不要加 `--match-all` |

**參數的人話：**

| 參數 | 自然語言意思 |
|------|----------------|
| `-q` / `--query "…"` | 我想找的關鍵字 |
| `--match-all` | 每個詞都要出現（比較嚴） |
| `--fields title,summary,…` | 要在哪些欄位裡找 |
| `--search-file …` | 搜已經下載好的檔，不再上網 |

---

## 四、測試有沒有壞掉

| 你可能會說 | 實際指令 |
|------------|----------|
| 全部測試跑一遍，詳細顯示 | `py -3 -m pytest -v` |
| 安靜一點，只看過不過 | `py -3 -m pytest -q` |
| 只測小函式，不要開伺服器 | `py -3 -m pytest -m unit` |
| 測整條管線（本機假網站） | `py -3 -m pytest -m integration` |
| 看看程式碼測到多少比例 | `py -3 -m pytest --cov=src/news_scraper --cov-report=term-missing` |
| 覆蓋率做成網頁給我看 | `py -3 -m pytest --cov=src/news_scraper --cov-report=html:out/reports/coverage` |
| 失敗時不要印太長的錯誤 | `py -3 -m pytest --tb=short` |
| 終端機中文亂碼，先設編碼 | PowerShell：`$env:PYTHONIOENCODING='utf-8'` 再跑測試 |

---

## 五、自動驗證迴圈（Harness）

| 你可能會說 | 實際指令 |
|------------|----------|
| 跑測試，順便看覆蓋率，驗證一次就好 | `py -3 harness/loop_verify_debug.py --cov --once` |
| 失敗的話自動再試最多三次 | `py -3 harness/loop_verify_debug.py --max-loops 3` |
| 這次只檢查單元測試 | `py -3 harness/loop_verify_debug.py --unit-only` |
| 這次只檢查整合測試 | `py -3 harness/loop_verify_debug.py --integration-only --cov` |
| 每次重試中間等兩秒 | `py -3 harness/loop_verify_debug.py --max-loops 3 --sleep 2` |

**人話對應流程：**  
「先跑 → 看過不過 → 失敗給提示再跑」＝ Loop → Verify → Debug。

---

## 六、測試報告網頁（可選）

| 你可能會說 | 實際指令 |
|------------|----------|
| 單元測試結果做成網頁 | `py -3 -m pytest -m unit --html=out/reports/unit.html --self-contained-html -v` |
| 整合測試結果做成網頁 | `py -3 -m pytest -m integration --html=out/reports/integration.html --self-contained-html -v` |
| 用瀏覽器打開報告 | 開啟 `out/reports/unit.html` 等檔案 |

---

## 七、Git（存檔／推送／退回）

| 你可能會說 | 實際指令 |
|------------|----------|
| 現在改了哪些檔？ | `git status` |
| 最近幾個版本訊息 | `git log --oneline -5` |
| 遠端倉庫是哪個？ | `git remote -v` |
| 把變更交出去存一版 | `git add .` 然後 `git commit -m "說明為何改"` |
| 推到 GitHub | `git push -u origin main` |
| 整份專案退回某一個舊版本 | `git reset --hard <SHA>` 再視需要 `git clean -fd` |

遠端範例：https://github.com/johnGitHub24/python1

---

## 八、資訊檢索 IR（歷史功能｜現行預設沒有）

| 你當時可能會說 | 歷史指令（需程式含 `--ir`） |
|----------------|------------------------------|
| 不要只篩有沒有，要依相關性排序 | `… -q "查詢" --ir --top-k 3 -o out/ir.jsonl` |
| 只留分數夠高的 | 再加上 `--min-score 0.1` |

> 目前若退回未含 IR 的版本，上表指令會無法使用。

---

## 九、一句話速查（最常用）

| 一句話 | 指令 |
|--------|------|
| 裝套件 | `py -3 -m pip install -r requirements.txt` |
| 離線示範爬蟲 | `py -3 -m src.news_scraper.cli --demo -o out/demo.jsonl` |
| 找含 Loop 的示範新聞 | `py -3 -m src.news_scraper.cli --demo -q "Loop" -o out/hits.jsonl` |
| 搜舊檔 | `py -3 -m src.news_scraper.cli --search-file out/demo.jsonl -q "測試" -o out/hits.jsonl` |
| 跑單元測試 | `py -3 -m pytest -m unit` |
| 跑整合測試 | `py -3 -m pytest -m integration` |
| 驗證＋覆蓋率 | `py -3 harness/loop_verify_debug.py --cov --once` |

---

## 維護

新增功能或參數時，請同步更新本檔與 [`COMMANDS.md`](COMMANDS.md)。  
規則：`.cursor/rules/sync-docs-after-tasks.mdc`。
