"""
搜尋層（Search）
================
對已擷取的 NewsArticle 做關鍵字過濾。

【初學者導讀】本檔會用到這些語法：
- def 函式、型別標註（: str、-> list）
- @dataclass 自動產生資料類別
- 列表推導式 [x for x in ...]
- 關鍵字專用參數（* 後面的參數只能用名稱傳入）
- all() / any() 判斷「全部／任一」成立
"""

# 【語法】from __future__ import annotations
# 讓型別標註可以用「尚未定義完」的名稱，也讓 str | None 這類寫法更穩。
from __future__ import annotations

# 【語法】from ... import ...
# 只匯入需要的名稱，使用時寫 dataclass，不必寫 dataclasses.dataclass。
from dataclasses import dataclass
from typing import Iterable, Sequence

# 【語法】相對匯入：同一套件內用「.模組名」
# 意思是：從同一個資料夾的 models.py 匯入 NewsArticle。
from .models import NewsArticle


# 【語法】@dataclass 是「裝飾器」：加在 class 上面，自動產生 __init__ 等樣板碼。
# frozen=True 表示建立後不能改欄位（類似不可變物件，較安全）。
@dataclass(frozen=True)
class SearchOptions:
    """
    搜尋選項（把一堆參數打包成一個物件，比較好傳）。

    【語法】類別裡的屬性寫法：名稱: 型別 = 預設值
    """

    # 【語法】沒有預設值的欄位要寫在「有預設值」的欄位前面。
    query: str
    # 【語法】tuple[str, ...] 表示「元素都是 str 的 tuple，長度不固定」。
    fields: tuple[str, ...] = ("title", "summary", "source", "tags")
    # 【語法】bool 布林值：只有 True / False。
    match_all: bool = False
    case_sensitive: bool = False


# 【語法】frozenset 是「不可變的集合」；用來檢查欄位名稱是否合法。
# 變數名前加底線 _ 是慣例：表示「模組內部用」，外部最好別直接依賴。
_ALLOWED_FIELDS = frozenset({"title", "summary", "source", "url", "tags"})


def parse_keywords(query: str) -> list[str]:
    """
    將查詢字串拆成關鍵字列表。

    【語法】函式簽名解讀：
    - query: str     → 參數名叫 query，型別是字串
    - -> list[str]   → 回傳值是「字串組成的 list」
    """
    # 【語法】列表推導式：
    # [表達式 for 變數 in 可迭代物件 if 條件]
    # split() 預設依空白切開；strip() 去掉頭尾空白。
    return [part for part in query.split() if part.strip()]


def _field_text(article: NewsArticle, field: str) -> str:
    """依欄位名稱取出文章對應文字。"""
    # 【語法】if / elif 鏈：依條件走不同分支。
    # 物件.屬性 → 例如 article.title 讀取 NewsArticle 的 title。
    if field == "title":
        return article.title
    if field == "summary":
        return article.summary
    if field == "source":
        return article.source
    if field == "url":
        return article.url
    if field == "tags":
        # 【語法】" ".join(可迭代) 把多段文字用空白接成一句。
        return " ".join(article.tags)
    # 【語法】f-string：f"...{變數}..." 把變數嵌進字串。
    # raise 拋出例外，呼叫端可用 try/except 處理（或讓程式中止並顯示錯誤）。
    raise ValueError(f"不支援的搜尋欄位: {field}")


def _haystack(
    article: NewsArticle,
    fields: Sequence[str],
    *,
    case_sensitive: bool,
) -> str:
    """
    把多個欄位拼成一大段「可搜尋文字」。

    【語法】參數列表中的單獨 * ：
    * 後面的參數「只能用關鍵字傳入」，例如：
      _haystack(article, fields, case_sensitive=True)  # 正確
      _haystack(article, fields, True)                 # 錯誤
    好處：呼叫時看得到參數意義，不易傳錯位置。
    """
    # 【語法】set 差集：A - B 得到「在 A 裡但不在 B 裡」的元素。
    unknown = set(fields) - _ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"不支援的搜尋欄位: {sorted(unknown)}")

    # 【語法】產生器表達式在 join 裡：
    # (_field_text(...) for f in fields) 不會先建完整 list，較省記憶體。
    text = " ".join(_field_text(article, f) for f in fields)

    # 【語法】三元運算：A if 條件 else B
    # casefold() 比 lower() 更適合「不分大小寫」比較（含特殊字母）。
    return text if case_sensitive else text.casefold()


def article_matches(
    article: NewsArticle,
    keywords: Sequence[str],
    *,
    fields: Sequence[str] = ("title", "summary", "source", "tags"),
    match_all: bool = False,
    case_sensitive: bool = False,
) -> bool:
    """
    判斷單則新聞是否符合關鍵字條件。

    【語法】-> bool 表示回傳 True（符合）或 False（不符合）。
    Sequence[str] 是較廣義的「字串序列」（list、tuple 都可以）。
    """
    # 【語法】空容器在 if 裡視為 False：[]、""、() 都是「假值」。
    if not keywords:
        return True

    haystack = _haystack(article, fields, case_sensitive=case_sensitive)

    # 【語法】條件運算式 + 列表推導：依 case_sensitive 決定要不要轉小寫。
    needles = keywords if case_sensitive else [k.casefold() for k in keywords]

    if match_all:
        # 【語法】all(條件 for x in 集合) → 每一個都要成立才是 True。
        # 【語法】in：子字串是否出現在字串裡，例如 "py" in "pytest" → True。
        return all(needle in haystack for needle in needles)

    # 【語法】any(...) → 只要有一個成立就是 True。
    return any(needle in haystack for needle in needles)


def search_articles(
    articles: Iterable[NewsArticle],
    query: str,
    *,
    fields: Sequence[str] = ("title", "summary", "source", "tags"),
    match_all: bool = False,
    case_sensitive: bool = False,
) -> list[NewsArticle]:
    """
    依關鍵字篩選新聞列表。

    【語法】Iterable[NewsArticle]：任何「可以 for 迴圈走一遍」的東西
    （list、tuple、產生器…）都可以當 articles 傳進來。
    """
    keywords = parse_keywords(query)
    if not keywords:
        # 【語法】list(可迭代) 把內容複製成真正的 list（避免回傳還是產生器）。
        return list(articles)

    # 【語法】列表推導式過濾版：
    # 只保留「if 後面條件為 True」的 article。
    return [
        article
        for article in articles
        if article_matches(
            article,
            keywords,
            fields=fields,
            match_all=match_all,
            case_sensitive=case_sensitive,
        )
    ]


def search_with_options(
    articles: Iterable[NewsArticle],
    options: SearchOptions,
) -> list[NewsArticle]:
    """
    用 SearchOptions 物件呼叫搜尋。

    【語法】物件.屬性：options.query 讀取 dataclass 的欄位。
    """
    return search_articles(
        articles,
        options.query,
        fields=options.fields,
        match_all=options.match_all,
        case_sensitive=options.case_sensitive,
    )
