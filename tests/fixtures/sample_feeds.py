"""共用測試 fixtures。"""

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Fixture News</title>
    <item>
      <title>第一則</title>
      <link>https://news.example/a1</link>
      <description>摘要 A</description>
      <pubDate>Sat, 19 Sep 2026 08:00:00 GMT</pubDate>
    </item>
    <item>
      <title>第二則</title>
      <link>https://news.example/a2</link>
      <description>&lt;b&gt;摘要 B&lt;/b&gt;</description>
      <pubDate>Sat, 19 Sep 2026 09:00:00 GMT</pubDate>
    </item>
    <item>
      <title></title>
      <link>https://news.example/skip</link>
      <description>應被略過</description>
    </item>
  </channel>
</rss>
"""

SAMPLE_HTML = """<!DOCTYPE html>
<html>
<body>
  <article class="news-item">
    <a class="title" href="/stories/1">HTML 新聞一</a>
    <p class="summary">這是摘要一</p>
    <time datetime="2026-09-19T08:30:00+00:00">09/19</time>
  </article>
  <article class="news-item">
    <a class="title" href="https://news.example/stories/2">HTML 新聞二</a>
    <p class="summary">這是摘要二</p>
  </article>
  <div class="ad">不是新聞</div>
</body>
</html>
"""
