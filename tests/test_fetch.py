from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

from fetch import fetch_source


def fake_rss(tmp_path, items):
    entries = "".join(
        f"<item><title>{t}</title><link>{l}</link><pubDate>{format_datetime(d)}</pubDate></item>"
        for t, l, d in items
    )
    path = tmp_path / "feed.xml"
    path.write_text(f'<?xml version="1.0"?><rss version="2.0"><channel><title>Fake</title>{entries}</channel></rss>')
    return str(path)


def test_keeps_only_last_24h(tmp_path):
    now = datetime.now(timezone.utc)
    url = fake_rss(tmp_path, [
        ("Fresh story", "https://x.com/1", now - timedelta(hours=2)),
        ("Old story", "https://x.com/2", now - timedelta(hours=30)),
    ])
    items = fetch_source({"name": "Fake", "type": "rss", "url": url}, now - timedelta(hours=24))
    assert [i["title"] for i in items] == ["Fresh story"]
    assert items[0]["source"] == "Fake"
