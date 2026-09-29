---
name: morning-brief
description: Fetch recent market news and write today's brief to briefs/YYYY-MM-DD.md, retrying failed fetches. Use when asked to run, generate, or redo the morning brief (this is also what the weekday cron job runs).
---

# Morning brief

## Purpose

Produce the same kind of brief every trading day, reliably and unattended:
fetch the news, recover from fetch failures on its own, have the
`market-analyst` subagent write the brief, and make sure a file always lands
in `briefs/`, even if the run fails, so a missing brief is never a mystery.

## When to use

- The weekday 7:00 cron job (`run_brief.sh`) runs this headless.
- The user asks to run or redo today's brief.

Not for: adding sources (use `add-news-source`), or analysing a single ticker.

## Inputs

- `sources.yaml`: sources for the `general` category.
- Today's date and weekday: `date "+%F %a"` → TODAY, WEEKDAY.
- Lookback window (HOURS):
  - **Mon, Sat, Sun → 72.** Covers Friday's close, the weekend, and Asia/
    Europe on Monday morning. With 24 hours a Monday brief would miss
    Friday's session and most weekend news.
  - **Tue–Fri → 24.**

## Process

Run from the project root.

### 1. Fetch (retry loop, max 3 attempts)

`.venv/bin/python -W ignore fetch.py --hours HOURS`

After each attempt:

| Result | Action |
|---|---|
| Exit 0 | Go to step 2. |
| Exit 1 + `FAILED SOURCES` | Some sources failed. YouTube feeds often return 404/500 briefly, so rerun. After 3 attempts, if `data/latest.json` has items, go to step 2 anyway; failures are in its `errors` field and the brief will list them. |
| Traceback / missing module / missing file | Environment problem. Read the error and fix it if possible, e.g. `ModuleNotFoundError` → `.venv/bin/pip install -r requirements.txt`. Then rerun. |

If after 3 attempts there is no usable `data/latest.json` (missing or 0
items), write `briefs/TODAY.md`:

    # Morning Market Brief - TODAY
    **Brief not generated.** Fetch failed after 3 attempts.
    Last error: <the error>

and stop.

### 2. Write

Use the `market-analyst` subagent. Tell it: input `data/latest.json`,
output `briefs/TODAY.md`, date TODAY, and the lookback window (e.g. "news
since Friday's close, 72h") so it frames the brief correctly.

### 3. Fact-check (max 1 revision)

Use the `brief-checker` subagent. Give it only the two paths:
`briefs/TODAY.md` and `data/latest.json`. Don't pass along your own notes or
the analyst's reasoning; the check is useful because it is independent.

- **PASS** → done. Keep any warnings for the report.
- **FAIL** → send the checker's issue list, unchanged, to `market-analyst`
  and ask it to fix exactly those issues in `briefs/TODAY.md` (remove
  unsupported facts rather than rewording them). Then run `brief-checker`
  once more.
- **Still FAIL after the revision** → keep the brief, but append at the end:
  `> ⚠️ Fact-check failed: <one line per remaining issue>`
  so the reader knows. Never loop more than once; an unbounded
  writer↔checker loop can run forever.

## Output

- `briefs/TODAY.md` (format defined in `.claude/agents/market-analyst.md`).
- A short final report: file path, lookback hours, fetch attempts, items and
  sources used, missing sources, and the fact-check result (first verdict,
  whether a revision happened, final verdict, issues).

## Constraints

- Never edit `sources.yaml` or `fetch.py` to make an error go away. A
  permanently broken source needs a human (see `add-news-source`).
- Never delete or overwrite an existing brief for another date.
- Re-running on the same day overwrites today's brief; that is intended.

## Edge cases and nuances

- **Partial data is better than no brief.** One dead source should never
  block the brief; it shows up in "Missing sources".
- **Market holidays:** the run still happens; the brief will simply be
  thinner. The analyst should not invent news to fill space.
- **Late-evening manual runs:** most items are timestamped the next day in
  UTC. The brief is still labeled with the local date; mention this in the
  report if the run is after 18:00.
