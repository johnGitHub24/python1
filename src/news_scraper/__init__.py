"""
新聞資訊爬蟲套件
================
提供 RSS / HTML 新聞擷取、解析與儲存能力。

教學重點：
- 模組化設計：fetch → parse → store
- 可測試性：依賴注入、介面分離
- 禮貌爬蟲：逾時、User-Agent、錯誤處理
"""

from .models import NewsArticle
from .scraper import NewsScraper
from .search import SearchOptions, search_articles

__all__ = ["NewsArticle", "NewsScraper", "SearchOptions", "search_articles"]
__version__ = "1.1.0"
