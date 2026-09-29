# brief-checker: standalone tests

Each test ran headless: `claude -p "Use the brief-checker subagent to check <brief> against data/latest.json"`.

- **Test 1:** the real brief [briefs/2026-09-27.md](../briefs/2026-09-27.md), written before the checker existed.
- **Test 2:** [bad-brief.md](bad-brief.md), a copy of that brief with 3 planted errors:
  - an invented number ("2-year yields hit 4.92%")
  - trade advice ("Traders should buy Nvidia calls")
  - a missing citation on story 3


## Checker output for `briefs/2026-09-27.md`
VERDICT: FAIL
Word count (body, approx): 290 (about 330 including the citation parentheses)
Issues:
1. [LENGTH] All stories: the body is well over the ~230-word limit. Evidence: Story 1 is about 64 words, Story 2 about 61, Story 3 about 66, Story 4 about 50 and "Also on the radar" about 49, not counting the citation parentheses. Fix: cut about 60 words. For example, drop the analysis sentences ("Oil is adding to the inflation and yield pressure...", "This is a direct headline for Nvidia and chip stocks Monday.") and shorten the radar line.
2. [WEAK] Story 1: "Trump rejected an Iranian offer of a 7-day ceasefire" appears only in the chapter list of "Bloomberg This Weekend 09/27/2026" ("00:04:14 - Trump Rejects Iranian Offer For 7-Day Ceasefire"). No reporting text confirms it. Fix: take the claim from reported text, or attribute it as a Bloomberg TV segment headline.
3. [WEAK] Story 1: "Brent was at $104 and WTI at $92" appears only in the same chapter list ("00:08:57 - Brent Crude at $104/Barrel, WTI at $92/Barrel"). No item title or reporting summary gives these prices. The WSJ items say only that oil "fell but remained at elevated levels" and "Crude futures settled lower." Fix: remove the specific prices, or label them as a Bloomberg TV segment headline.
4. [WEAK] Story 2: "Consumer sentiment also fell on worries about prices" appears only in the chapter list ("01:23:45 - US Consumer Sentiment Falls on Worries About Prices, Economy"). Fix: drop it or attribute it as a segment headline.
5. [WEAK] Story 2: "the September jobs report on Friday" as the week's key event has chapter-list support only ("01:21:42 - Traders Await September Jobs Report on Friday"). The only reporting nearby is CNBC's "Here are the 4 big things we're watching..." ("Both sides of the Fed's dual mandate are in focus"), which does not name the jobs report or the day. Fix: attribute it to the segment headline, or rephrase as "labor/inflation data in focus" to match the CNBC summary.
6. [WEAK] Story 3: "a $30 billion tariff deal" appears only in chapter lines ("00:54:16 - US, China Agree to $30 Billion Tariff Deal" and "01:46:33 - Jamrisko on US, China Agree to $30 Billion Tariff Deal"). The reported summary ("US China Trade Truce Leaves Key Issues Unresolved") supports only "extended the trade truce through Jan. 10." Fix: remove the $30 billion figure or attribute it as a segment headline.

Everything else checks out:
- **Story 1:** The Dow snapping a three-session losing streak and oil dipping on Hormuz hopes are both in WSJ items. Stalled talks come from Bloomberg ("US Iran Talks Hit Familiar Sticking Points"). Indexes near records despite oil and yields comes from MarketWatch ("Look closer...").
- **Story 2:** The 19-year high is in CNBC. "Since 2007" and mortgage rates at 7.03%, the first time above 7% in 20 months, are in the Yahoo summary (not a timestamp line). The Fed bracing for hikes is in MarketWatch.
- **Story 3:** "Through Jan. 10" and the open trade and AI questions are in Bloomberg. The ByteDance, Alibaba and RTX PRO 5500 report is in CNBC.
- **Story 4:** The force majeure notice on the New Mexico data center is in WSJ and Yahoo. Debt-heavy AI builders facing higher costs is in CNBC. Micron reporting this week is in CNBC. Micron as "a market event in and of itself" is in MarketWatch.
- **Radar line:** Every item is in a title or summary.
- **Other checks:** Every cited source has a matching item. There is no advice wording. `errors[]` is empty. The footer count of 113 items from 6 sources matches the JSON.

Checked: 26 facts, 26 found in source data (5 of them only in YouTube chapter lists, flagged WEAK).

Files: briefs/2026-09-27.md, data/latest.json

## Checker output for `examples/bad-brief.md`
VERDICT: FAIL
Word count (body, approx): 325
Issues:
1. [UNSUPPORTED] Story 2: "2-year yields hit 4.92% for the first time in 20 months." Evidence: neither "4.92" nor any 2-year yield figure appears anywhere in the JSON. "First time in 20 months" comes from the Yahoo Finance (YouTube) item "Mortgage rates top 7% for the first time in 20 months..." and refers to mortgage rates. The brief has put it on a yield number that isn't in the data. Fix: remove the 2-year yield claim. Keep "first time in 20 months" only with the mortgage-rate fact.
2. [ADVICE] Story 3: "Traders should buy Nvidia calls into Monday's open." Evidence: this is a direct trade recommendation, and nothing in the JSON supports it. Fix: delete the sentence. If you want context, say why the ByteDance/Alibaba news matters without telling anyone to trade.
3. [CITATION] Story 3: no source is cited. Evidence: the facts are in CNBC Top News "China weighs allowing ByteDance, Alibaba to buy new Nvidia chips, The Information reports" and in Bloomberg Television "US China Trade Truce Leaves Key Issues Unresolved" (truce through Jan. 10, trade and AI questions unresolved). Fix: add *(CNBC Top News, Bloomberg Television)*.
4. [LENGTH] Body: about 325 words, against a limit of about 230. Story 1 is about 72 words, Story 2 about 79, Story 3 about 64, Story 4 about 65, and "Also on the radar" about 45. Fix: cut about 95 words. Shorten each story to 2-3 sentences and trim the radar line.
5. [WEAK] Story 1: "Trump rejected an Iranian offer of a 7-day ceasefire, and Brent was at $104 and WTI at $92." Evidence: these appear only in the chapter list of Bloomberg Television "Bloomberg This Weekend 09/27/2026" ("00:04:14 - Trump Rejects Iranian Offer For 7-Day Ceasefire", "00:08:57 - Brent Crude at $104/Barrel, WTI at $92/Barrel"). No article reports them. Fix: attribute them clearly to the Bloomberg segment, or drop the exact prices. The WSJ item "Asian Bond Yields Rise Despite Oil Decline..." ("oil fell but remained at elevated levels") supports the general point.
6. [WEAK] Story 2: "Consumer sentiment also fell on worries about prices" and "the September jobs report on Friday." Evidence: both come only from the Bloomberg This Weekend chapter list ("01:23:45 - US Consumer Sentiment Falls on Worries About Prices, Economy", "01:21:42 - Traders Await September Jobs Report on Friday"). CNBC "Here are the 4 big things we're watching..." says only "Both sides of the Fed's dual mandate are in focus" and does not name the jobs report. Fix: attribute these to Bloomberg Television, or soften them.
7. [WEAK] Story 3: "with a $30 billion tariff deal." Evidence: this appears only in the Bloomberg This Weekend chapter list ("00:54:16 - US, China Agree to $30 Billion Tariff Deal"). The Bloomberg item "US China Trade Truce Leaves Key Issues Unresolved" confirms the Jan. 10 extension but not the $30 billion figure. Fix: drop the $30 billion figure or attribute it to the Bloomberg segment.

Other checks, no issues:
- Citations in Stories 1, 2 and 4 all match items in the JSON. For example, Story 4's CNBC Top News matches "Debt-hungry AI companies face increased risk as bond yields spike", and its MarketWatch matches "Micron could dethrone Nvidia...".
- `errors[]` is empty, so the footer doesn't need to disclose any failed sources. "113 items from 6 sources" matches the data.
- Format is fine: there are 4 numbered top stories and an "Also on the radar" line.
- All four top stories are market-level.
- Every "Also on the radar" item is in the data: the Apple $5.7B verdict and planned appeal, Meta's best month since 2013, Microsoft's Copilot overhaul, the Eli Lilly obesity pipeline update, RAF Fairford, and the nor'easter causing flight delays.

Checked: 29 facts, 28 found in source data (5 of those found only in a YouTube chapter list and marked WEAK).

Files: examples/bad-brief.md, data/latest.json
