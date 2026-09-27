# Module 2: Skills

## Which tasks became skills, and which didn't

| Task | Skill? | Why |
|---|---|---|
| Adding / replacing a news source | ✅ `add-news-source` | Repeats every time the source list grows or a category is added. Same steps each time, and full of traps that are easy to forget |
| Running the daily brief | ✅ `morning-brief` (upgraded) | Runs every weekday, unattended. Needs a fixed process, a retry policy, and clear rules on what the agent may and may not fix |
| Writing the brief itself | ❌ subagent instead | Needs its own clean context and Read/Write-only tools. `market-analyst` is a subagent, called *by* the skill |
| Running tests, installing cron | ❌ | One command each. A skill would add nothing |

## Skills

- [`.claude/skills/add-news-source/SKILL.md`](.claude/skills/add-news-source/SKILL.md)
  with a bundled checker script [`check_feed.py`](.claude/skills/add-news-source/check_feed.py)
- [`.claude/skills/morning-brief/SKILL.md`](.claude/skills/morning-brief/SKILL.md)

## Example results

- [examples/add-news-source-runs.md](examples/add-news-source-runs.md): "Add Yahoo Finance's
  YouTube channel" → found, verified, added, fetch confirmed. "Add Reuters" → correctly
  **rejected** (no official RSS; YouTube channel is off-topic world news) with alternatives,
  `sources.yaml` untouched.
- [examples/morning-brief-run.md](examples/morning-brief-run.md) →
  [briefs/2026-09-27.md](briefs/2026-09-27.md): Sunday run automatically used a 72h lookback
  (Friday's session + weekend), 113 items from 6 sources including the newly added one.

## What the skills improved

**add-news-source: before vs. after**

| Before (Module 1, by hand) | After (skill) |
|---|---|
| Ran curl commands one by one, guessed feed URLs | One request: "add X" |
| Looked up the YouTube channel ID by searching the page's HTML, which gave the **wrong channel** (CNBC instead of CNBC Television) | `check_feed.py youtube-id` reads the page's canonical link and gets the correct ID |
| YouTube 404s looked like dead channels | Flakiness is documented; checker retries 4× before rejecting |
| No quality bar: any working feed could be added | Same 4 checks every time: has dates, title matches, active (<48h), on-topic |
| Risk of breaking the daily fetch or overwriting today's data | Confirms with a real fetch to a separate file |

**morning-brief:** the process is now fully specified (inputs, retry table,
output checks, constraints). Writing it out exposed a real bug: a Monday
brief with a 24h window would miss Friday's close and the whole weekend. The
skill now uses 72h on Sat/Sun/Mon, so every brief covers everything since the
last one.

**Overall:** consistency. Every source passes the same checks, and every
brief follows the same process. Each skill also records what the agent must
*not* do (edit `fetch.py`, silently drop sources, use unofficial feeds),
so unattended runs stay safe.
