# Module 3: Subagents

The project has two subagents with opposite jobs:

| | `market-analyst` (writer) | `brief-checker` (new, Module 3) |
|---|---|---|
| File | [.claude/agents/market-analyst.md](.claude/agents/market-analyst.md) | [.claude/agents/brief-checker.md](.claude/agents/brief-checker.md) |
| Job | Turn ~100 news items into a ~200-word brief | Independently verify the brief before it's final |
| Tools | Read, Write | Read, Grep (read-only) |

## brief-checker

**Purpose.** A trader acts on the brief within minutes of reading it, so an
invented number or disguised trade advice is the worst failure this project
can have. `brief-checker` catches those before the brief is final.

**Responsibilities.** Check every fact and number in the brief against
`data/latest.json`, verify the citations, flag advice or predictions, confirm
failed sources are disclosed, and enforce format and length. Return PASS or
FAIL with a specific issue list: what's wrong, the evidence, and the fix.

| | |
|---|---|
| **Inputs** | Two file paths: the brief and `data/latest.json` |
| **Context** | Only those two files plus its own instructions. It does *not* see the writer's reasoning, the orchestrator's notes, or the conversation |
| **Tools** | `Read`, `Grep` (Grep finds a number like `5.116` among ~100 items quickly). No Write, no Bash |
| **Output** | `VERDICT: PASS/FAIL`, approx. word count, issues tagged `UNSUPPORTED / WEAK / CITATION / ADVICE / DISCLOSURE / FORMAT / LENGTH / RELEVANCE`, facts checked |
| **Constraints** | Judge only against the data (no outside knowledge); never edits the brief; no style opinions |
| **Called when** | Step 3 of the `morning-brief` skill, after `market-analyst` writes the brief. Also usable standalone ("use brief-checker on briefs/X.md") |

**Where it fits in the pipeline** ([morning-brief skill](.claude/skills/morning-brief/SKILL.md)):

```
fetch.py → market-analyst writes → brief-checker
                                      ├─ PASS → done
                                      └─ FAIL → issues → market-analyst fixes → brief-checker again
                                                                   └─ still FAIL → brief kept, ⚠️ warning appended
```
At most one revision, so the writer and checker can't loop forever.

## Why a subagent, not a prompt or a skill

- **Independent reasoning.** A writer checking its own work tends to confirm
  it, because it remembers what it *meant* to say. The checker starts with a fresh
  context and sees only the finished text and the raw data. That separation is
  the point, and a skill can't provide it: a skill runs inside the same
  agent's context, with everything that agent already believes.
- **Dedicated context.** Checking means searching ~100 items for each of ~25
  facts. Doing that in the main agent would fill its context with
  search results. The subagent does the work and returns only a short verdict.
- **Least privilege.** Read + Grep only. A checker that can't edit can't
  quietly "fix" facts to make itself pass.
- **Reusable on its own.** It can check any brief, including old ones or
  hand-written ones, without running the pipeline.

## Tests and results ([examples/](examples/))

| Test | Result |
|---|---|
| Planted errors ([bad-brief.md](examples/bad-brief.md)): invented "2-year yields hit 4.92%", "Traders should buy Nvidia calls", missing citation | **FAIL, all 3 caught**, each with evidence and the exact fix ([output](examples/brief-checker-tests.md)) |
| Yesterday's real brief (written before the checker existed) | **FAIL**: 290 words vs ~230, plus 5 facts (oil $104/$92, "$30B tariff deal") sourced only from a YouTube video's chapter list, not reporting. Neither problem had been noticed |
| Full pipeline, Monday 2026-09-28 | 1st check **FAIL** (unsupported Nvidia claim, 253 words, misleading oil wording) → analyst revised → 2nd check **PASS**, 27/27 facts found ([report](examples/morning-brief-with-factcheck.md), [brief](briefs/2026-09-28.md)) |

## Next

The checker keeps flagging the same two things: length, and facts taken from
YouTube chapter lists. The next improvement is to feed that back into
`market-analyst`'s instructions so first drafts pass more often.
