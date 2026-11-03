# Season recap and deferred NIL reports — v81

## Phase transition

The captured game moves from NationalChampionship Week 20 to OffSeason Week 0, with CurrentStage also OffSeason. v80 limited focus fixtures to the current NFLSeason week, gated normal recap detection to NFLSeason, and marked its offseason stories local. The active catalog had 993 stories but zero National IDs. This was a generator/scope gap, not a failure to capture the new week.

v81 recognizes this exact recap edition. A single published, internally consistent current-year national final carries into it as the shared focus. Other years, duplicate finals, unpublished results and invalid teams are rejected. Completed title fixtures never become predictions or appear as new final reactions in later offseason weeks. The archived title edition stays distinct from the new recap publication.

The new pack includes championship context, both finalists’ season records and coaches, verified scoring progression and ball-security comparisons, all five national analyst personalities, nonparticipant fans missing the season, and prestige-aware retrospectives. The snapshot’s player game-performance records are empty, so this replay uses actual team/quarter box scores and a truthful roster-count fallback instead of invented individual final-game statistics. The exact final is Miami 31–22 BYU: Miami trailed 14–9 at halftime and won the second half 22–8.

## Staff and portal reporting

Confirmed same-season hires, dismissals, departures, retirements and contract developments are reconstructed from preserved structured publication events. Pending offers and pending dismissals are excluded. Retrospective wording makes clear these moves occurred during the cycle. In this replay, current carousel tables are empty but 13 supported prior moves remain available in history. Coordinator stories remain local; major head-coach changes can be National.

Portal-watch eligibility requires a roster player with an integer transfer-risk indicator from 50 through 100, excludes the native -1 sentinel, and excludes seniors without verified remaining eligibility. National watches focus on the existing top-60 coverage pool and higher risk (70+); other programs retain beat coverage. Each school has at most two candidates before the shared weekly budget. These posts explicitly describe retention risk, never confirmed portal entry, interest in another school or a destination. Every current player has -1 in this capture, so this edition correctly contains no named transfer-risk posts. No public probability is printed.

## NIL publication timing

The existing verified transaction baseline is retained during Offseason Week 0, including compatibility with v80 histories. No compensation-change posts publish during that week. When Offseason Week 1 is observed, final Week 0 compensation is compared with its opening baseline and net changes become reports in the new edition. Both amounts must be known and nonnegative, the player/team must match, and the observation years must match. Reverted edits, unchanged values, new installs without an observed baseline, and team moves do not create changes. One point remains $2,500.

Reports persist across unchanged Week 1 refreshes, do not repeat in Week 2, and remain archived. Later offseason midweek changes and verified coach renewals can publish normally. If recap week was never observed, the system does not invent its deal history. Actual next-week in-game reporting remains to be checked.

## Verification

263 Node tests pass, covering phase resets, title result integrity, all five analysts, player qualification and text bounds, risk sentinels, staff ledgers, next-week raises/cuts, rollback/net changes, missing baselines, subsequent-week deduplication, later offseason changes and archive/prose stability. Native decoding validates every dynamic scope across the real 23-edition catalog. The preview has 30 For You cards, 22 National cards and 5–20 total posts per program. No saves or simulation outcomes are modified. Installation and controller results are recorded separately in verified-v81.json.

Deployment: v81 is installed and payload-verified. Eight saves and nine history files were checksum-backed up, and history was migrated byte for byte. Live Offseason Week 0 publication is logged with 1,049 stories, 30 For You cards, 22 National cards and 23 editions without saving. The user confirmed recap news, scrolling and Back work. After advance, native logs confirm Offseason Week 1 publication; the feed contains 479 net NIL follow-up stories. Individual deal accuracy remains a separate user check. The native CFB tab disappears at this stage, motivating the persistent access change in v82.
