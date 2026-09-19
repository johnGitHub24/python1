"""
HTTP 擷取層（Fetcher）
======================
【初學者導讀】本檔核心語法：
- class / __init__ / self
- 預設參數
- 第三方套件 requests 的基本用法
"""

from __future__ import annotations

from dataclasses import dataclass

# 【語法】import 套件名：使用時寫 requests.Session、requests.get …
import requests


# 【語法】常數慣例：全大寫 + 底線。這不是強制語法，但是社群習慣。
DEFAULT_USER_AGENT = (
    "NewsScraperTutorial/1.0 (+educational; contact=local-dev)"
)


@dataclass
class FetchResult:
    """
    單次 HTTP 回應的精簡結果。

    【語法】沒有 frozen=True 時，欄位之後 theoretically 可再賦值；
    這裡當「資料袋子」用即可。
    """

    url: str
    status_code: int
    text: str
    # 【語法】有預設值的欄位，建立時可省略：FetchResult(url, 200, "...")
    content_type: str = ""


class HttpFetcher:
    """
    禮貌的 HTTP 客戶端。

    【語法】class 裡的函式第一個參數通常叫 self，代表「這個物件自己」。
    呼叫 obj.get(url) 時，Python 會自動把 obj 傳進 self。
    """

    def __init__(
        self,
        timeout: float = 10.0,
        user_agent: str = DEFAULT_USER_AGENT,
        session: requests.Session | None = None,
    ) -> None:
        """
        建構子：建立物件時自動執行。

        【語法】timeout: float = 10.0
        → 參數是浮點數，呼叫時不傳就用 10.0。
        """
        # 【語法】self.xxx = ... 把資料存到物件上，之後其他方法都能用。
        self.timeout = timeout
        # 【語法】A or B：若 session 是 None（假值），就建立新的 Session。
        self.session = session or requests.Session()
        # 【語法】dict.update({...}) 把多個鍵值寫進字典（這裡是 HTTP 標頭）。
        self.session.headers.update({"User-Agent": user_agent})

    def get(self, url: str) -> FetchResult:
        """
        GET 指定 URL，回傳 FetchResult。

        【語法】Raises 寫在 docstring，告訴讀程式的人「可能噴什麼錯」。
        """
        # 【語法】物件.方法(關鍵字參數=值)
        response = self.session.get(url, timeout=self.timeout)
        # 若狀態碼是 404、500 等，這裡會拋例外（不是靜靜回傳失敗頁）。
        response.raise_for_status()
        # 【語法】dict.get(鍵, 預設)：沒有 Content-Type 時回傳 ""。
        content_type = response.headers.get("Content-Type", "")
        # 【語法】用關鍵字參數建立 dataclass，順序不易搞錯。
        return FetchResult(
            url=str(response.url),
            status_code=response.status_code,
            text=response.text,
            content_type=content_type,
        )
