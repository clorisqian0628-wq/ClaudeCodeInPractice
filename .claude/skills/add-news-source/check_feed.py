"""Check that an RSS feed or YouTube channel works before adding it to sources.yaml.

Usage:
  python check_feed.py rss <url>
  python check_feed.py youtube <channel_id>
  python check_feed.py youtube-id <https://www.youtube.com/@handle>   # look up channel_id

Prints OK/FAIL, the feed title, entry count, and newest item date.
"""
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
import calendar

import feedparser

YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id={}"


def youtube_id(page_url):
    req = urllib.request.Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    # The canonical link is the page owner. A bare "channelId" in the page can
    # belong to a different (related) channel, so don't use that.
    m = re.search(r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[\w-]{22})"', html)
    if not m:
        sys.exit(f"FAIL: no canonical channel id found on {page_url}")
    print(f"channel_id: {m.group(1)}")


def check(url, tries=4):
    for attempt in range(1, tries + 1):
        feed = feedparser.parse(url)
        status = feed.get("status", 200)
        if status == 200 and feed.entries:
            break
        print(f"  attempt {attempt}: HTTP {status}, {len(feed.entries)} entries")
        time.sleep(3)
    else:
        sys.exit(f"FAIL: {url} did not return entries after {tries} attempts")

    dates = [e.get("published_parsed") or e.get("updated_parsed") for e in feed.entries]
    dates = [datetime.fromtimestamp(calendar.timegm(d), timezone.utc) for d in dates if d]
    newest = max(dates) if dates else None
    age_h = (datetime.now(timezone.utc) - newest).total_seconds() / 3600 if newest else None
    print(f"OK: {feed.feed.get('title', '?')!r}")
    print(f"  entries: {len(feed.entries)}, with dates: {len(dates)}")
    print(f"  newest: {newest.isoformat() if newest else 'none'}" + (f" ({age_h:.0f}h ago)" if age_h is not None else ""))
    for e in feed.entries[:5]:
        print(f"  - {e.get('title', '')[:100]}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    kind, arg = sys.argv[1], sys.argv[2]
    if kind == "youtube-id":
        youtube_id(arg)
    elif kind == "youtube":
        check(YOUTUBE_FEED.format(arg))
    elif kind == "rss":
        check(arg)
    else:
        sys.exit(__doc__)
