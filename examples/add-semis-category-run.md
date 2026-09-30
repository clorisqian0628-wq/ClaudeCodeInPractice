I added a new `semis` category to `sources.yaml` with three sources: EE Times, Semiconductor Engineering and SemiAnalysis. A test run of `fetch.py --category semis` pulled 8 items from all 3 sources with no failures. That run wrote to `data/check.json`, so today's `data/latest.json` is unchanged.

**Added (3)**

| Source | Feed | Check |
|---|---|---|
| EE Times | `https://www.eetimes.com/feed/` | OK, 10 dated entries, newest 5h ago. Sample: "Astera Labs' Leo Controller Update Targets Memory Constraints", "AI Data Centers Make Power, Cooling Critical to Scaling" |
| Semiconductor Engineering | `https://semiengineering.com/feed/` | OK, 10 dated entries, newest 20h ago. Sample: "TSMC OIP: Chip Industry Growth Blows Past Forecast", "Moores Lab AI: Applying Agentic AI Across Chip Design" |
| SemiAnalysis | `https://newsletter.semianalysis.com/feed` | OK, 20 dated entries, newest 31h ago. Sample: "How GLM5.3 Sparse Attention Affects HBM Memory Usage", "Intel Panther Lake Teardown" |

**Not added (2)**

- **CNBC Technology** (`...&id=19854910`): the feed works (30 entries, newest 4h ago), but it covers general tech and politics, not chips. Recent headlines were Cramer segments, Meta's Muse AI and Trump on AI. It would add noise to the semis category and overlap with CNBC Top News in `general`.
- **Tom's Hardware**: the listed feed URL redirects, which is why the check first failed. The new URL (`https://www.tomshardware.com/feeds.xml`) works (50 entries, newest 11h ago), but it's mostly consumer content like Switch 2 deals, power bank reviews and GPU warranty stories. Most of it doesn't matter for SOXX/SMH traders, and at 50 items it would crowd out the other sources.

**Things to watch:**
- 8 items a day is light. Semiconductor Engineering also includes some academic paper roundups.
- SemiAnalysis posts every day or two and puts much of its content behind a paywall. The feed's headline and summary are still enough for the brief.
- If you later want more market-focused chip news, a narrower CNBC semiconductor feed would be worth checking.

