"""整合測試：本機 HTTP server + 真實 requests/parser/storage 管線。"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest

from src.news_scraper.cli import main as cli_main
from src.news_scraper.scraper import NewsScraper
from src.news_scraper.storage import JsonLinesStore
from tests.fixtures.sample_feeds import SAMPLE_HTML, SAMPLE_RSS


class _Handler(BaseHTTPRequestHandler):
    rss_body = SAMPLE_RSS.encode("utf-8")
    html_body = SAMPLE_HTML.encode("utf-8")

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/rss"):
            body, ctype = self.rss_body, "application/rss+xml; charset=utf-8"
        elif self.path.startswith("/html"):
            body, ctype = self.html_body, "text/html; charset=utf-8"
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


@pytest.fixture(scope="module")
def local_server():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    base = f"http://{host}:{port}"
    yield base
    server.shutdown()


@pytest.mark.integration
def test_end_to_end_rss_to_jsonl(local_server, tmp_path) -> None:
    out = tmp_path / "out.jsonl"
    scraper = NewsScraper()
    articles = scraper.scrape_and_save([f"{local_server}/rss"], str(out), source="local")
    assert len(articles) == 2
    loaded = JsonLinesStore(out).load()
    assert len(loaded) == 2
    assert loaded[0].url.startswith("https://news.example/")


@pytest.mark.integration
def test_end_to_end_html_list(local_server) -> None:
    articles = NewsScraper().scrape_url(f"{local_server}/html", source="html-local")
    assert len(articles) == 2
    assert articles[0].url.endswith("/stories/1")


@pytest.mark.integration
def test_cli_demo_mode(tmp_path) -> None:
    out = tmp_path / "demo.jsonl"
    code = cli_main(["--demo", "-o", str(out)])
    assert code == 0
    assert len(JsonLinesStore(out).load()) == 2


@pytest.mark.integration
def test_scrape_with_query_filter(local_server, tmp_path) -> None:
    out = tmp_path / "filtered.jsonl"
    articles = NewsScraper().scrape_and_save(
        [f"{local_server}/rss"],
        str(out),
        query="第一則",
    )
    assert len(articles) == 1
    assert articles[0].title == "第一則"


@pytest.mark.integration
def test_cli_search_file(tmp_path) -> None:
    src = tmp_path / "all.jsonl"
    out = tmp_path / "hits.jsonl"
    assert cli_main(["--demo", "-o", str(src)]) == 0
    code = cli_main(["--search-file", str(src), "-q", "Loop", "-o", str(out)])
    assert code == 0
    hits = JsonLinesStore(out).load()
    assert len(hits) == 1
    assert "Loop" in hits[0].title


@pytest.mark.integration
def test_cli_demo_with_query(tmp_path) -> None:
    out = tmp_path / "q.jsonl"
    assert cli_main(["--demo", "-q", "測試驅動", "-o", str(out)]) == 0
    assert len(JsonLinesStore(out).load()) == 1
