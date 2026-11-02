# World news expansion

This expands the native Social Media feed with 24 additional team-analysis scenarios and 26 player-analysis scenarios. They supplement the existing rushing rank, third-down conversion, red-zone TD rate, turnover margin and season-margin stories. CPU and user programs use the same event eligibility; For You personalizes selection, not the underlying facts.

## Team analysis: 24 scenarios

| Group | Scenarios | Evidence |
| --- | --- | --- |
| Scoring | High scoring offense; strong/struggling scoring defense; dominant/poor scoring margin; offense carrying a struggling defense | Published finals, corroborated season record, at least three games |
| Offensive efficiency | Yards per rushing/pass attempt combined; passing yards per attempt; rushing yards per carry; pass/run tendency | Native season counters reconciled against published game caches, minimum attempts |
| Passing decisions | Interception rate; passing touchdown rate | Interceptions or TD divided by actual pass attempts |
| Situational offense | Fourth-down conversions; settling for red-zone field goals | Actual conversions/attempts; FG share of red-zone scoring trips |
| Defense | Rush yards allowed; pass yards allowed; takeaways; sacks; red-zone TD rate allowed | Reconciled defensive counters and actual denominators |
| Discipline | Low/high penalty yardage per game | Reconciled penalty yards, game count |
| Game patterns | Second-half scoring margin; halftime comeback wins; losses after leading through three quarters | All quarter and overtime scores must sum to finals; second-half margin excludes overtime |
| Schedule/results | Home-road scoring split; close-game record; opponents' combined record excluding head-to-head games | Verified venue classification; published finals; unique opponents with corroborated records |

The season selector admits up to three of these team analyses per program per edition, rotating among qualifying scenarios. Dedicated scopes retain all selected stories. A threshold is a news trigger, not a claim that a team leads the country.

## Player analysis: 26 scenarios

| Group | Scenarios | Evidence |
| --- | --- | --- |
| National/conference leaders | Passing yards; passing TD; rushing yards; receiving yards; sacks; interceptions | Native current-season totals reconciled with published game records; complete comparison field; ties retained |
| QB efficiency | Completion percentage; passing yards/attempt; TD–INT totals | Minimum pass attempts, actual completions/yards/TD/INT |
| Skill-position efficiency | Rushing yards/carry; receiving yards/catch; yards after catch/catch; receiving TD/catch | Minimum carries/receptions and reconciled totals |
| Production/workload | Scrimmage yards/game; dual-threat QB production; team carry share; team catch share; team rushing/receiving TD share | Player totals, games played and verified team denominators |
| Defense | Tackles/game; tackles for loss; forced fumbles; pass breakups | Native defensive counters; sacks reconcile whole plus half sacks |
| Specialists | Field-goal accuracy; success from 50+ yards; net punting | Made/attempted and actual net punt yards, minimum samples |
| Young players | Freshman offensive or defensive production | Native class year, verified scrimmage yards or tackles |

Up to four additional player analyses per program are selected per edition, with leaders prioritized. Missing native totals or game caches suppress corresponding leader comparisons instead of silently omitting a potential leader. Rate/workload stories generally require three player appearances and their own minimum sample.

## Events and reactions

| Story family | Trigger and guardrails |
| --- | --- |
| Upsets | Published final; captured pregame model favorite loses by an upset threshold, or winner beats a materially higher-ranked opponent using the prior-week/captured poll. Updated polls are not presented as pregame rankings. |
| Winning streaks | Four or more consecutive published wins within the current season; game coverage must match the official record. |
| Weekly awards | Native national/conference offensive/defensive award, with a matching published performance in that award week. |
| Records | Native school, conference or FBS single-game/single-season record table; correct season, player/team and matching production. Runtime observation must establish an increase to say “broke.” Season records need an observed increase. The initial observation seeds the baseline; newly observed records remain in the current edition. |
| Staff/player reactions | Fan replies to verified positive/negative analysis, naming the actual player, head coach, offensive coordinator or defensive coordinator where available. No invented quotations or coach actions. |
| Recruiting pickups | Native commitment, optional star detail, prestige-sensitive fan response; low-star pickups at elite programs can draw beat scrutiny. |
| Major recruiting | Every newly observed five-star commitment and national No. 1 receives a major fan reaction. Four/five-star recruits at low-prestige programs get program-changing excitement. |
| Departures | Observed hard commitment changes to another school, or verified reopened recruiting stage; Signed does not count as a decommitment. Losing-program fans can react negatively. |
| Rivalry recruiting steals | Approved extra: a verified flip to a school listed as a native rival. |
| Undefeated collisions | Approved extra: upcoming game between two verified unbeaten teams, each with at least three wins. |
| Bounce-back watch | Approved extra: next matchup following a verified previous-week upset loss. |

Recruit stars map from the native star enum; school prestige uses the native half-star scale. National No. 1 uses the native recruiting rank. Recruiting changes need an observation baseline and are not fabricated from a single snapshot. Other player/news families remain available outside the user team too.

## Engagement and model lines

Views are removed. Standalone posts use deterministic flavor likes based on native brand exposure, media-poll rank and voice. Ordinary posts cap at 5K; major recruiting, huge upsets and comparable major stories can reach 10K. Replies receive 1–20% of their actual parent's likes, rounded down to whole likes. Small parents can therefore have zero-like replies. Same-week counts remain stable. The footer right-aligns the word “likes” with a 14-pixel native inset: neither tested native heart asset rendered reliably, so no unsupported font symbol is used.

The fictional spread model draws on the Toolkit starter/depth blend and league-relative strength approach. It compares weighted offense/defense/special teams, applies matchup and home-field terms, compresses rivalries, rounds to half-points and caps at 45. Unknown/incomplete rosters produce no line. Internal ability calculations never appear as numerical player ratings in tweet text. This model never invokes force-win or changes simulation results. Attribution and the reference license are in THIRD_PARTY_NOTICES.md and LICENSES/.

## Runtime and evidence limits

All data is read from the active Dynasty. The reader follows current player season stats, published game performances, native awards/records, prestige, staff and recruiting state. It never writes Dynasty tables or game saves. Some inspected team sack-allowed counters were all zero, so this build does not invent pass-protection analysis from them.

An in-session reload can expose the shared database instead of its active child. The reader now checks the exact supported child type and parent relationship, rejects ambiguity, and caches the verified child. Discovery is bounded to small committed private regions, 6 GiB of scan reads and 12 seconds; normal captures retain their separate 512 MiB/eight-second budget. Identity/stage and packed table contents are checked again before publication. Unsupported layouts remain unavailable.

Regenerate aggregate evidence with:

```powershell
node --test Tests/*.test.mjs
Build/LiveCapture.exe <PID> Build/runtime-raw.json
node Tools/export_runtime.mjs Build/runtime-raw.json Build/runtime-feed.json
node Tools/audit_world_news.mjs Build/runtime-raw.json Build/runtime-feed.json Build/world-news-audit.json
```

Actual qualifying counts depend on Dynasty conditions; the 50 scenarios are supported conditions, not a promise that all 50 fire every week. Rare flips, new records and undefeated collisions have deterministic fixture coverage; they are not claimed as live events when absent from the inspected Dynasty.
