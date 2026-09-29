# Full pipeline with fact-check loop: Monday 2026-09-28 (headless, via run_brief.sh)

Final report from the agent. Resulting brief: [briefs/2026-09-28.md](../briefs/2026-09-28.md)

> Note: the three YouTube 404s were a YouTube-side outage. At the time, the feed endpoint returned 404 for every channel, including Google's own. The pipeline correctly continued with the 3 working sources and disclosed the missing ones.

Today's brief is written to `briefs/2026-09-28.md` and passed the fact-check after one revision.

- **Lookback:** 72 hours (Monday), covering news since Friday's close.
- **Fetch:** all 3 attempts ended with the same errors, so the brief uses what was fetched: 71 items from 3 of 6 sources (CNBC Top News, WSJ Markets, MarketWatch Top Stories).
- **Missing sources:** CNBC Television, Bloomberg Television and Yahoo Finance (YouTube) all returned HTTP 404 on every attempt. The brief lists them in its footer. Since they fail consistently, the feed addresses themselves may be wrong or retired rather than briefly down. `add-news-source` can check them.
- **Fact-check:**
  - **First check failed** with three issues:
    - An unsupported claim that Nvidia is the biggest weight in tech indices.
    - About 253 words, over the ~230 limit.
    - Misleading wording on the crude price: it said oil rose "after" Saudi Arabia reopened a pipeline, when the reopening actually pulled prices down.
  - **Revision:** the unsupported sentence was removed, two minor items were dropped and the crude line was reworded.
  - **Second check passed:** no issues, about 222 words, and all 27 facts match the fetched data.
- **Contents:**
  - Treasury yields at a 19-year high and the Dow down more than 300 points.
  - Stalled U.S.–Iran ceasefire talks and oil.
  - Nvidia's record $150B buyback and its roughly $13B deal for Hugging Face.
  - Anthropic's IPO filing and OpenAI dropping its next model release.
  - Also on the radar: AMD, MongoDB, Australia's rate hike and gold.
- **Late run:** it ran at 22:12, so most items have Tuesday (UTC) timestamps and Monday's session is covered as already closed. As the skill specifies, the brief keeps the local date, 2026-09-28.


