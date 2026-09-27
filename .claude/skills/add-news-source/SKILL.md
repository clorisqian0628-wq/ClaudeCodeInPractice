---
name: add-news-source
description: Find, verify, and add a news website (RSS) or YouTube channel to sources.yaml for the morning brief. Use when asked to add, replace, or check a news source, or to start a new source category (e.g. "add Yahoo Finance's YouTube channel", "add a semiconductors category with these sites").
---

# Add a news source

## Purpose

`sources.yaml` drives what the morning brief reads. A bad entry (wrong
channel, dead feed, off-topic source) either breaks the daily fetch or quietly
makes the brief worse. This skill makes every new source go through the same
checks, so the list stays clean without manual trial and error.

## When to use

- The user names a website or YouTube channel to add to the brief.
- The user wants a new category (e.g. `semis`). A category is just a new
  top-level key in `sources.yaml`, with no code changes.
- A source keeps failing in the brief and the user wants to replace it.

Not for: changing `fetch.py`, scraping sites without a feed, or tracking
individual tickers (out of scope for this project).

## Inputs

| Input | Required | Default |
|---|---|---|
| Source: site name, URL, feed URL, or YouTube @handle/URL | yes | |
| Category | no | `general` |
| Display name | no | the publisher's name, e.g. "Yahoo Finance (YouTube)" |

If the user gives only a publisher name ("add Bloomberg"), ask whether they mean
the website or the YouTube channel only if both exist and it is unclear.
Otherwise pick the one that has a working feed.

## Process

Run commands from the project root. The checker is
`.venv/bin/python -W ignore .claude/skills/add-news-source/check_feed.py`
(called CHECK below).

1. **Check for duplicates.** Read `sources.yaml`. If the same URL or
   `channel_id` is already there (in any category), stop and say where.

2. **Find the feed.**
   - *Website:* look for an official RSS/Atom feed. Try the site's RSS page,
     `<link rel="alternate" type="application/rss+xml">` in the homepage
     HTML, or `/rss`, `/feed`. Prefer a markets/business section feed over
     the site-wide "top news" feed.
   - *YouTube:* get the channel ID with `CHECK youtube-id <channel URL>`.
     Do not grep the page for `"channelId"`. The first match is often a
     *different* related channel (e.g. @CNBCtelevision's page mentions the
     main CNBC channel first).

3. **Verify it.** Run `CHECK rss <url>` or `CHECK youtube <channel_id>`.
   Accept only if ALL of these hold:
   - Prints `OK` with entries that have dates (no dates means the 24h filter
     drops everything).
   - The feed title matches the source you meant (catches wrong channel IDs).
   - Newest item is less than ~48h old (an active source, not an archive).
   - Recent titles are relevant to the category, e.g. for `general`: markets,
     macro, Fed, big tech, not lifestyle or personal finance.

4. **Add it** to `sources.yaml` under the category, matching the existing
   format exactly. Edit the text; do not load and re-dump the YAML (that
   would delete comments and reorder keys).
   ```yaml
     - name: Yahoo Finance (YouTube)
       type: youtube
       channel_id: UCEAZeUIeJs0IjQiqTCdVSIg
   ```
   `rss` sources use `url:` instead of `channel_id:`. For a new category,
   add a new top-level key with a list.

5. **Confirm end to end.** Run
   `.venv/bin/python -W ignore fetch.py --category <category> --out data/check.json`
   (a separate output file so the day's `data/latest.json` is untouched).
   The new source must not appear under FAILED SOURCES. Other sources
   failing with YouTube 404/500 is normal flakiness, not your change.

## Output

A short report:

```
Added: <name> (<type>) to <category>
Feed:  <url or channel_id>
Check: <feed title>, <N> entries, newest <age>h ago
Sample: <2-3 recent titles>
fetch.py: <N> items from <M> sources, new source OK
```

or, if not added: `Not added: <name>`, the reason, and alternatives.

## Constraints

- Only `rss` and `youtube` types exist. Never edit `fetch.py` to support a
  source; if a source needs scraping or an API key, report it and stop.
- Never remove or change existing sources unless the user asked for a
  replacement.
- Use official feeds only. No third-party RSS generators.

## Edge cases and nuances

- **YouTube feeds are flaky.** They randomly return 404/500 for valid
  channels. CHECK retries 4 times; if it still fails, try again once
  after ~30s before rejecting. A valid channel ID with a 404 is almost always
  flakiness.
- **No RSS feed** (e.g. Reuters and Bloomberg websites dropped theirs): do
  not add it. Suggest the publisher's YouTube channel if it has one, or a
  similar site that has a feed.
- **Paywalled sites** (WSJ): feeds give headline + summary, which is enough
  for the brief. Fine to add.
- **Very high-volume feeds** (100+ items/day, e.g. wire "all news" feeds)
  crowd out other sources. Prefer a narrower section feed and mention the
  volume in the report.
- **Same publisher, two formats** (site + YouTube) is fine: they carry
  different content, and `fetch.py` dedupes by link.

## Examples

**"Add Yahoo Finance's YouTube channel"** → `CHECK youtube-id
https://www.youtube.com/@YahooFinance` → `UCEAZeUIeJs0IjQiqTCdVSIg` → CHECK
shows "Yahoo Finance", fresh market videos → added to `general` → fetch OK.

**"Add Reuters"** → no official RSS feed exists any more → not added;
suggest Reuters' YouTube channel or CNBC Economy RSS instead.
