# PRD: Morning Market News Brief

**Status:** Prototype (v0.1) working · **Owner:** Jiaying Qian · **Updated:** 2026-09-23

---

## 1. Problem definition

**Problem.** Before the US open, a short-term trader needs to know what
happened in the last 24 hours that could move the broad market. That news is
spread across many sites and YouTube channels, arrives overnight, and is
mostly noise (personal finance, lifestyle, small caps). Reading it all takes
30-60 minutes every morning, and it is easy to miss the one story that matters.

**User.** One person: a short-term trader of US indices, leveraged index ETFs
(e.g. TQQQ, SPXL) and large-cap tech. Reads the brief once, before the open,
on a laptop. Does not want individual ticker tracking or trade calls.

**Why it's worth solving.** The morning window is short and the cost of
missing a macro driver (Fed repricing, a yield spike, an oil shock) is a bad
open. A 2-minute read that replaces 30+ minutes of scanning saves time every
trading day and makes the review more consistent.

**Why AI is useful here.** Fetching and filtering by date is plain code. The
hard part is judgment: from ~100 overlapping headlines, which 3-5 stories
matter *for the index market today*, how do they connect (yields → tech,
oil → inflation → Fed), and how to say that in a few sentences. An LLM
does this well. It can also handle the messy operations step (reading an
error, deciding whether to retry, fix, or give up) that would otherwise
need hand-written rules for every failure mode.

## 2. The agent

| | |
|---|---|
| **Receives** | A trigger (cron, weekdays 7:00) and the skill instructions. Tools: run the fetcher, read/write files, call the analyst subagent. |
| **Decides** | (a) After each fetch: proceed, retry, fix the environment, or give up. (b) In the analyst: which stories matter, which items describe the same story, how to rank them. |
| **Does** | Runs `fetch.py`, reads its exit code and error output, retries up to 3 times, then delegates writing to the `market-analyst` subagent and checks the output. |
| **Produces** | `briefs/YYYY-MM-DD.md` (about 200 words, cited sources, missing sources listed) and a run log in `logs/`. |

**Autonomy vs. human intervention**

| Fully autonomous | Needs a human |
|---|---|
| Retrying transient failures (YouTube feeds randomly return 404/500) | Adding, removing, or replacing a source in `sources.yaml` |
| Fixing environment problems (e.g. reinstalling missing packages) | Changing `fetch.py` code |
| Continuing with partial data and **reporting** missing sources | Changing brief format/length, or adding a category |
| Writing a "brief not generated" file with the error when all attempts fail | Acting on the brief. It is information, never advice |

The agent is told explicitly not to edit `sources.yaml` or `fetch.py` to
make an error go away. That would hide a problem rather than fix it. The
safety net is visibility: every failure ends up in the brief itself.

The agent's permissions in `run_brief.sh` are limited to exactly these commands
(`--allowedTools`). It can run only the fetcher, the pip install, and `date`,
so it cannot run any other shell command.

## 3. System map

```
┌──────────────┐   weekdays 7:00   ┌─────────────────────────────────────────────┐
│  cron (Mac)  │ ────────────────▶ │ run_brief.sh → claude -p (headless)          │
└──────────────┘                   │   allowedTools: Skill, Agent, Read, Write,   │
                                   │   Bash(fetch.py | pip install | date)        │
                                   └───────────────────┬─────────────────────────┘
                                                       ▼
                         ┌──────────── morning-brief skill (orchestrator) ─────────────┐
                         │ 1. run fetch.py ──fail──▶ read error → retry/fix (≤3)        │
                         │        │                     └─ still failing → error brief  │
                         │        ▼ ok / partial                                        │
                         │ 2. market-analyst subagent (Read, Write only)                │
                         │ 3. verify briefs/YYYY-MM-DD.md                               │
                         └──────────────────────────────────────────────────────────────┘
   sources.yaml ──▶ fetch.py ──HTTP──▶ RSS feeds (CNBC, MarketWatch, WSJ)
                        │     ──HTTP──▶ YouTube channel feeds (CNBC TV, Bloomberg TV)
                        ▼
                 data/latest.json ──▶ market-analyst ──▶ briefs/YYYY-MM-DD.md
```

| Layer | v0.1 (prototype) | Notes / later |
|---|---|---|
| **Frontend** | None. Brief is a markdown file opened in any editor or previewer | Later: email/Slack/phone push |
| **Backend / API** | `fetch.py` (Python 3.9, venv, `feedparser`, `pyyaml`). Exit 0 = all ok, 1 = some sources failed (named on stderr) | No server; a script is enough for one user |
| **AI / model layer** | Claude Code headless (`claude -p`). Skill = orchestration and retry logic. Subagent = analysis and writing, with only Read/Write tools | Separate subagent keeps the writer's context clean (only the JSON) and its permissions minimal |
| **Data / context** | `sources.yaml` (sources grouped by category); `data/latest.json` (`items[]`: source, type, title, link, published, summary; `errors[]`); `briefs/` archive; `logs/` | Categories are config-only: add a `semis:` key and run `fetch.py --category semis` |
| **Infrastructure** | User's Mac, crontab, local venv, Claude subscription auth | Mac must be awake at 7:00; cloud schedule could remove that later |
| **External services** | RSS: CNBC Top News, MarketWatch Top Stories, WSJ Markets. YouTube feeds: CNBC Television, Bloomberg Television | YouTube feeds are unreliable, so there are retries at two levels (inside `fetch.py` and in the skill) |

## 4. Product & technical specifications

### Functional requirements

| ID | Requirement | v0.1 |
|---|---|---|
| F1 | Every weekday at 7:00 local, generate a brief without user action | Script ready; cron not yet installed |
| F2 | Pull only items published in the last 24 h from every source in the chosen category | ✅ |
| F3 | Dedupe items by link | ✅ |
| F4 | Support RSS and YouTube sources; new sources/categories by editing YAML only | ✅ |
| F5 | A failing source is never silently dropped: named in stderr, in `latest.json.errors`, and in the brief footer | ✅ tested |
| F6 | Retry loop: max 3 fetch attempts; fix environment errors; continue on partial data; on total failure write an error brief and stop | ✅ tested |
| F7 | Brief: 3-5 top stories, each with what happened, why it matters today, and cited sources. About 200 words | ✅ (runs slightly long, ~250) |
| F8 | No predictions, price targets, or buy/sell language | ✅ in subagent rules |
| F9 | YouTube transcripts when available, fall back to title + description | ⏳ Later (titles/descriptions only now) |

### Non-functional

- **Runtime:** under 3 min end to end (measured: ~1 min).
- **Cost:** one headless Claude session per weekday.
- **Least privilege:** headless run limited to specific tools and commands; the subagent cannot run shell commands.
- **Traceability:** every run is logged in `logs/YYYY-MM-DD.log`; every story cites its source.

### Brief format

```markdown
# Morning Market Brief - YYYY-MM-DD
**Top stories**
1. **Headline.** What happened. Why it matters today. *(Source A, Source B)*
**Also on the radar:** smaller items, one line.
---
Sources: N items from M sources.
Missing sources: name (reason).     ← only if any failed
```

### Testing

| Test | How | Result |
|---|---|---|
| 24 h filter | `pytest`: fake local RSS file with a 2 h-old and a 30 h-old item | ✅ pass |
| Real fetch | `python fetch.py` against live sources | ✅ 83-98 items; flaky YouTube caught and reported |
| Full pipeline | `./run_brief.sh` (headless, same as cron) | ✅ brief written in ~64 s |
| Retry loop | Added a broken feed URL | ✅ 3 attempts; YouTube recovered on retry; broken feed listed as missing in brief; `sources.yaml` untouched by agent |

### Success metrics (after 2 weeks of use)

- Brief present on ≥95% of weekdays by 7:10.
- Takes ≤2 min to read; user rarely needs to open the source sites to understand the top stories.
- Zero invented facts found on spot checks against the source links.

### Risks & open items

- **Date labeling:** news runs to ~midnight UTC; a 7 AM run labels it with the correct trading day, but a late-evening manual run will label it with the prior day.
- **Mac asleep at 7:00** → cron skips the run. Mitigation: `pmset` wake schedule, or move to a cloud schedule.
- **Paywalled sources (WSJ):** RSS gives headline + summary only; enough for a brief.
- **Brief length:** trending ~250 words; tune the prompt after the first week.
- **Source list:** starter set; to be revised by the user.

### Roadmap

1. **v0.1 (this week):** fetcher, skill with retry loop, analyst subagent, run script ✅
2. **v0.2:** install cron, YouTube transcripts, tune length
3. **v0.3:** second category (semiconductors) + editor/merge step across categories
