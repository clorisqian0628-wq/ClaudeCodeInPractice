# Morning Market News Brief

Every weekday morning, pull the last 24 hours of market news from RSS feeds
and YouTube channels, and have a Claude Code agent turn it into a ~200-word
brief for a short-term index/ETF trader. Saved as `briefs/YYYY-MM-DD.md`.

Built as a Claude Code learning project: a Python script, a skill, a
subagent, a self-correcting retry loop, and cron scheduling.
Full product/technical spec: [PRD.md](PRD.md) ([.docx](PRD.docx)). Skills (Module 2): [SKILLS.md](SKILLS.md).

**Example output:** [briefs/2026-09-27.md](briefs/2026-09-27.md)

## How it works

```
cron (weekdays 7:00) → run_brief.sh → claude -p → morning-brief skill
   1. fetch.py        sources.yaml → data/latest.json (last 24h, deduped)
   2. retry loop      on failure: read error, retry/fix, max 3 attempts
   3. market-analyst  subagent (Read/Write only) writes the brief
   4. check           briefs/YYYY-MM-DD.md exists and cites sources
```

| File | Role |
|---|---|
| `sources.yaml` | News sources, grouped by category (RSS or YouTube) |
| `fetch.py` | Fetches, filters to last 24h, dedupes. Exits 1 and names any failed source |
| `.claude/skills/morning-brief/SKILL.md` | Orchestrates the steps and the retry loop |
| `.claude/agents/market-analyst.md` | Subagent that picks the top stories and writes the brief |
| `run_brief.sh` | Headless entry point for cron, with a tight `--allowedTools` list |
| `tests/test_fetch.py` | Unit test using a fake local RSS file |

## Setup

Requires Python 3.9+ and [Claude Code](https://claude.com/claude-code).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python fetch.py          # just fetch → data/latest.json
.venv/bin/python -m pytest tests   # unit test
./run_brief.sh                     # full pipeline, same as cron → briefs/ and logs/
```

Or interactively inside Claude Code: *"run the morning brief"*.

## Schedule (macOS)

```bash
(crontab -l 2>/dev/null; echo "0 7 * * 1-5 $PWD/run_brief.sh") | crontab -
```

Give `/usr/sbin/cron` Full Disk Access (System Settings → Privacy & Security)
if the project lives under `~/Desktop` or `~/Documents`.

## Tested

- 24h filter: unit test with a fake RSS feed ✅
- Full headless run: ~1 min, 98 items from 5 sources ✅
- Retry loop: added a broken feed URL. The agent retried 3 times, flaky
  YouTube feeds recovered, and the broken feed was reported as
  "Missing sources" in the brief instead of being silently dropped ✅

## Add a category

Add a new top-level key to `sources.yaml` (e.g. `semis:`) and run
`fetch.py --category semis`. No code changes needed.
