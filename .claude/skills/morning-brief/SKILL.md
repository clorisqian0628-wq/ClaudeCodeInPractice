---
name: morning-brief
description: Orchestrate the multi-agent morning brief. Fetch news for every category in sources.yaml, have writer and fact-checker subagents work each category in parallel, then have the editor merge them into briefs/YYYY-MM-DD.md. Use when asked to run, generate, or redo the morning brief (this is also what the weekday cron job runs).
---

# Morning brief (orchestrator)

## Purpose

You are the orchestrator. You do not write or check the brief yourself; you
coordinate specialists and handle their failures:

| Agent | Role | Tools |
|---|---|---|
| `fetch.py` (script) | Pull news per category → `data/<category>.json` | n/a |
| `market-analyst` (subagent, 1 per category) | Write a category section | Read, Write |
| `brief-checker` (subagent, 1 per category + 1 final) | Fact-check against the data | Read, Grep |
| `editor` (subagent) | Merge sections into the final brief | Read, Write |

A file must always land in `briefs/TODAY.md`, even when parts fail.

## When to use

- The weekday 7:00 cron job (`run_brief.sh`) runs this headless.
- The user asks to run or redo today's brief.

Not for: adding sources or categories (use `add-news-source`).

## Inputs

- `sources.yaml`: every top-level key is a CATEGORY.
- `date "+%F %a"` → TODAY, WEEKDAY. HOURS = 72 on Mon/Sat/Sun (covers
  Friday's close and the weekend), else 24.
- Category settings (priority order; an unknown category gets focus "news
  about <category> relevant to trading", budget 100, last in priority):

| Category | Title | Focus | Word budget |
|---|---|---|---|
| general | Market | Fed and rates, macro data, trade/geopolitics, oil, mega-cap tech, index moves | 180 |
| semis | Semis | Chip demand and supply, AI accelerators, memory, foundries, export controls: what moves SOXX/SMH | 120 |

Final brief limit: sum of budgets for the categories included (max 300).

## Process

Run from the project root.

**Parallelism is required, not optional.** Categories are independent, so
each stage below is ONE assistant message containing one tool call per
category. Do not wait for one category's result before starting the
next. With categories general and semis, your messages look like:

| Message | Tool calls in that single message |
|---|---|
| Fetch | `Bash` fetch general + `Bash` fetch semis |
| Write | `Agent` market-analyst (general) + `Agent` market-analyst (semis) |
| Check | `Agent` brief-checker (general) + `Agent` brief-checker (semis) |
| Revise / re-check | one call per FAILED category, all in one message |
| Merge, final check | single calls (they need all sections) |

Retries of a single category (fetch attempt 2, etc.) can be single calls.

### 1. Fetch: all categories in parallel, max 3 attempts each

`.venv/bin/python -W ignore fetch.py --category C --hours HOURS --out data/C.json`

| Result | Action |
|---|---|
| Exit 0 | Category ready. |
| Exit 1 + `FAILED SOURCES` | Rerun that category (YouTube feeds often 404/500 briefly). After 3 attempts, use it anyway if `data/C.json` has items; failures are in its `errors`. |
| Traceback / missing module | Fix the environment (e.g. `.venv/bin/pip install -r requirements.txt`), rerun. |
| Still no items after 3 attempts | **Drop the category** and record the reason for the editor. |

If *every* category is dropped, write `briefs/TODAY.md` with
`**Brief not generated.** Fetch failed after 3 attempts.` plus the errors, and stop.

### 2. Write: one `market-analyst` per category, in parallel

Give each: CATEGORY, title, FOCUS, input `data/C.json`, output
`briefs/sections/TODAY-C.md`, WORD BUDGET, lookback ("last HOURS hours").

### 3. Check: one `brief-checker` per section, in parallel

Give each only: the section path, `data/C.json`, WORD LIMIT = budget + 20.
Don't pass your notes or the writer's reasoning; the check is useful because
it is independent.

### 4. Revise failed sections: max 1 round, in parallel

For each FAIL: send the checker's issue list, unchanged, to a
`market-analyst` for that section ("fix exactly these issues in <path>"),
then re-check with `brief-checker` (again in parallel across categories).
Still FAIL → append to that section file:
`> ⚠️ Fact-check failed: <one line per remaining issue>`.
Never loop more than once.

If a writer produced no file at all, retry that writer once; if it fails
again, drop the category ("writer failed").

### 5. Merge: `editor`

Give it: section paths in priority order, TODAY, output `briefs/TODAY.md`,
TOTAL WORD LIMIT, and dropped categories with reasons.

If the editor fails (no file), write `briefs/TODAY.md` yourself by
concatenating the sections under a `# Morning Market Brief - TODAY` header,
with a note `(unedited: editor failed)`.

### 6. Final check: `brief-checker` on the merged brief

Give it `briefs/TODAY.md`, **all** `data/C.json` files used, WORD LIMIT =
total limit + 20. This catches anything the editor changed.
FAIL → one fix by the `editor` with the issue list, re-check once, then
append the ⚠️ line if still failing.

## Output

- `briefs/TODAY.md`: the final brief. `briefs/sections/`: per-category sections.
- A short final report: lookback, per category (fetch attempts, items,
  missing sources, check verdicts and revisions), editor result (duplicates
  removed, words cut), final check verdict.

## Constraints

- Never edit `sources.yaml`, `fetch.py`, or agent files to make an error go away.
- Never overwrite a brief or section for another date. Re-running the same day overwrites that day's files.
- Only the subagents write brief content. You only write the fallback files described above.

## Edge cases and nuances

- **Partial data beats no brief.** A dead source or category never blocks
  the others; it appears in "Missing sources" / "Not included".
- **Cross-category duplicates are expected** (Nvidia news is both macro and
  semis). Writers work independently and can't know; the editor fixes it.
- **Market holidays:** thinner brief is fine; nobody should fill space.
- **Late-evening runs:** the brief keeps the local date; mention it in the report if after 18:00.
