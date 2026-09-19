"""
HTTP 擷取層（Fetcher）
======================
【註解教學】為何獨立 Fetcher？
單元測試可 mock 此層，不必真的連網；整合測試再驗證真實 HTTP 行為。
"""

from __future__ import annotations

from dataclasses import dataclass

import requests


DEFAULT_USER_AGENT = (
    "NewsScraperTutorial/1.0 (+educational; contact=local-dev)"
)


@dataclass
class FetchResult:
    """單次 HTTP 回應的精簡結果。"""

    url: str
    status_code: int
    text: str
    content_type: str = ""


class HttpFetcher:
    """
    禮貌的 HTTP 客戶端。

    設計原則：
    - 明確逾時，避免卡住 harness loop
    - 自訂 User-Agent，方便對方辨識
    - 失敗時拋出清楚例外，利於 debug
    """

    def __init__(
        self,
        timeout: float = 10.0,
        user_agent: str = DEFAULT_USER_AGENT,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get(self, url: str) -> FetchResult:
        """
        GET 指定 URL，回傳 FetchResult。

        Raises:
            requests.RequestException: 網路或 HTTP 錯誤
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        return FetchResult(
            url=str(response.url),
            status_code=response.status_code,
            text=response.text,
            content_type=content_type,
        )
