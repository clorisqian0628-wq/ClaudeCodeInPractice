"""Fetch the last 24h of items from sources.yaml and write data/latest.json.

Usage: python fetch.py [--category general] [--sources sources.yaml] [--out data/latest.json]
Exits 1 if any source fails, printing which one.
"""
import argparse
import calendar
import json
import sys
import time
from datetime import datetime, timedelta, timezone

import feedparser
import yaml

YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id={}"


def feed_url(source):
    if source["type"] == "rss":
        return source["url"]
    if source["type"] == "youtube":
        return YOUTUBE_FEED.format(source["channel_id"])
    raise ValueError(f"unknown type {source['type']!r}")


def fetch_source(source, cutoff, tries=3):
    """Return recent items for one source. Raises on failure."""
    url = feed_url(source)
    for attempt in range(tries):
        feed = feedparser.parse(url)
        status = feed.get("status", 200)  # local files have no status
        if status == 200 and feed.entries:
            break
        time.sleep(2)  # YouTube feeds randomly 404/500; try again
    else:
        raise RuntimeError(f"HTTP {status}, {len(feed.entries)} entries from {url}")

    items = []
    for e in feed.entries:
        t = e.get("published_parsed") or e.get("updated_parsed")
        if not t:
            continue
        published = datetime.fromtimestamp(calendar.timegm(t), timezone.utc)
        if published < cutoff:
            continue
        items.append({
            "source": source["name"],
            "type": source["type"],
            "title": e.get("title", ""),
            "link": e.get("link", ""),
            "published": published.isoformat(),
            "summary": e.get("summary", ""),
        })
    return items


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--category", default="general")
    p.add_argument("--sources", default="sources.yaml")
    p.add_argument("--out", default="data/latest.json")
    p.add_argument("--hours", type=int, default=24)
    args = p.parse_args()

    with open(args.sources) as f:
        sources = yaml.safe_load(f)[args.category]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    items, errors, seen = [], [], set()
    for source in sources:
        try:
            for item in fetch_source(source, cutoff):
                if item["link"] not in seen:
                    seen.add(item["link"])
                    items.append(item)
        except Exception as ex:
            errors.append(f"{source['name']}: {ex}")

    items.sort(key=lambda i: i["published"], reverse=True)
    with open(args.out, "w") as f:
        json.dump({"category": args.category, "items": items, "errors": errors}, f, indent=2)

    print(f"{len(items)} items from {len(sources) - len(errors)}/{len(sources)} sources -> {args.out}")
    if errors:
        print("FAILED SOURCES:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
