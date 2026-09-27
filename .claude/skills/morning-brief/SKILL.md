---
name: morning-brief
description: Fetch the last 24h of market news and write today's brief to briefs/YYYY-MM-DD.md. Use when asked to run or generate the morning brief.
---

Run these steps from the project root. TODAY is today's date as YYYY-MM-DD
(get it with `date +%F`).

## 1. Fetch (with retry loop, max 3 attempts)

Run: `.venv/bin/python -W ignore fetch.py`

Check the result after each attempt:

- **Exit 0** -> go to step 2.
- **Exit 1 with "FAILED SOURCES"** -> some sources failed. Read the message.
  YouTube feeds often return 404/500 briefly, so rerun. If the same source
  still fails after 3 attempts, continue to step 2 anyway as long as
  `data/latest.json` has items. The failure is recorded in its `errors`
  field and will appear in the brief.
- **Any other error** (traceback, missing module, missing file) -> read the
  error and fix the cause if it is an environment problem, e.g.
  `ModuleNotFoundError` -> `.venv/bin/pip install -r requirements.txt`.
  Then rerun.

Do NOT edit `sources.yaml` or `fetch.py` to make an error go away. A source
that is permanently broken needs a human decision.

If after 3 attempts there is no usable `data/latest.json` (missing or zero
items), write `briefs/TODAY.md` containing:

    # Morning Market Brief - TODAY
    **Brief not generated.** Fetch failed after 3 attempts.
    Last error: <paste the error>

and stop.

## 2. Write the brief

Use the `market-analyst` subagent. Tell it:
input `data/latest.json`, output `briefs/TODAY.md`, date TODAY.

## 3. Check

Read `briefs/TODAY.md`. Confirm it exists, has a "Top stories" section, and
cites sources. Report the file path and how many attempts the fetch took.
