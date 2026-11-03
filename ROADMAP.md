# Dynasty Enhancer roadmap

## Current priorities after v89

v89's preseason feed and controller regression are user-verified. Training Results, Encourage Transfers and realignment capture are implemented, with 308 passing tests and a copied-data year transition. The full hidden-stage sequence still needs live progression validation.

1. Validate final signing day → Training Results → Encourage Transfers/realignment → next preseason on a backed-up test branch. Check actual development/departure/movement facts, reload persistence, duplicate suppression and no numerical ratings in prose.
2. Finish release lifecycle checks: fresh MMC launch, switching active Dynasties, older-save restore/replay, repeated year changes and long-session capture reliability.
3. Measure native page performance with the complete category lists, large archives and TeamBuilder/custom-conference data. Tune capture and rendering only where measurements show a problem.
4. Review a multiweek sample for repetition, factual context, news-cycle balance and For You relevance. Current ordering is editorial, with likes as flavor; category views retain all qualifying published stories. Default All Types limits remain For You 30/National 100/conference 60/team 20, with the existing draft exception.
5. Integrate the player analytics grades component, then the ratings fog-of-war component; validate both against Social Media and native game menus.
6. Finish release packaging, upgrade/history preservation, documentation and compatibility checks before 1.0.

The dedicated hub tab and arbitrary custom-image registration remain deferred improvements. The Team shortcut is the working entry point; background offseason capture covers the weeks when Team is absent. Historical checkpoints below retain the behavior and test status at their respective versions.

## Current prototype: native Dynasty lifecycle

- Active Dynasty and controlled program read from runtime tables instead of a configured save.
- Stable editions published after regular-season week advancement, with a live Week 8 → Week 9 rollover verified.
- Midweek scholarship offers verified in the native feed; commitments, injuries/recovery, and current-week results share the same publication path.
- Deterministic IDs, scoped history, and fixture coverage for identity changes, earlier-week loading, and replay with different outcomes.
- Native menu/controller behavior retained; simulation access remains read-only.

Before broader release, validate active-Dynasty switching, an actual older-save restore/replay, offseason/year transitions, and cold launch. The runtime observer currently waits for stable state rather than hooking the native advance-completion callback.

## Six-stage Social Media content plan

1. Voice/tone direction approved from thirty samples and subsequent revisions. Legacy prototype wording is retired.
2. Core event conditions verified; weekly awards, verified records and 50 additional analysis scenarios are implemented; native depth-chart, NIL support and evidence-backed transfer stories are now included.
3. Event detection, persistent authors, editable templates and native avatar routing are separate components.
4. Expanded catalog reaches the initial target with 423 variants, including more player/fan perspectives and replies.
5. Two-week template cooldown preferences, stable same-week selections/admission order, account/voice caps, reply dependencies and complete curated conversation blocks are implemented. Multiweek in-game tuning remains.
6. First pack verified live as v50 with 65 tests. The v63 build passes 95 Node tests plus native checks, and the user verified its 30/100/60 feed sizes, likes order, replies, filters and scrolling. The v64 MMC adapter adds startup waiting and package tests. Longer rollover testing and historical-edition restoration remain.

Publication week remains the single week filter. For You selects up to 30 with soft 55/20/25 personalized/conference/national scope targets and no filler to hit quotas. National displays up to 100 and each native conference up to 60 after category filtering. Views sort parent threads by likes, with replies attached. The underlying dedicated story catalog remains complete.

## Planned 1.0 integration

1. Native Social Media with active-Dynasty and week/midweek lifecycle support.
2. Existing player analytics grades mod, integrated as a component.
3. Existing ratings fog-of-war mod, replacing numerical player-rating displays throughout the UI with less granular information.

The analytics and fog-of-war components are planned integrations, not included in this baseline. Version 1.0 follows integration and validation of all three. The product goal is more convincing Dynasty context and presentation without structural changes to Dynasty data or altered simulation outcomes.

## MMC prototype integration

The managed adapter, native runtime package, payload/configuration checks, startup readiness wait and history migration are implemented in v64. A full MMC cold launch now automatically loads the runtime, waits through title/loading, activates in a fresh preseason Dynasty and publishes Week 0. The user verified the Social Media button after one native menu refresh. Immediate automatic refresh of a cached first hub remains startup polish. Final distribution polish, updates and integration of the other two mods remain later work.

## Preseason / startup correction (v67 candidate)

Preseason coverage includes actual AP/Coaches polls, native national/conference honors, outlooks, camp/hype/recruiting voices, fictional title futures, schedule gauntlets, poll-model debates with replies and conference talent maps. AP/CFP selection uses native public poll data and preserves the historical pregame basis. Local tests cover missing data, current-year awards, TeamBuilder identity, phase isolation and unsaved offers.

The fixed startup delay is removed; early menu hooks capture the first hub. Phase-specific filter-model reacquisition and safe navigation fallback address the blank/stuck regular-season Week 0 page. Native and automated story tests pass; live BYU/TeamBuilder recovery and first-hub/phase transition checks are pending. Preseason archives remain phase-isolated; a cross-phase week-picker presentation remains later work.

The v66 entry attempt failed before page activation. Recovery stopped the hooks, disabled automatic loading, and verified all four save hashes unchanged. v67 now follows the front-end service to the actual CareerManager/database and reads 600 live preseason honors; it completes cancelled native navigation and separates UI readiness from feed generation. Live retesting remains pending.

The user verified v67 preseason posts and Back, then advanced in the same process to regular-season Week 0 and verified that feed and Back as well. The runtime published automatically across the phase change. The verified managed adapter is restored for the next MMC startup. Same-process main-menu reload and v67 cold launch remain the next lifecycle checks.

## Archived publication phases and persistence (v68)

Preseason is now selectable above regular-season Week 0, using frozen stored editions from the same Dynasty/team/year. The active edition remains the default; future phases/weeks and other identities are excluded. Matching native facts resume cached wording and likes after the first verified capture instead of regenerating an unchanged edition. Save renaming does not change identity. The user verified both editions and all controls. Source, native DLL, complete MMC package and installed adapter are preserved; v68 cold launch remains a follow-up validation case.

## Week 1 catalogue recovery and scholarship frequency (v69)

v68 cold MMC startup is observed in the launcher/native logs. Its Week 1 generator produced 9,029 stories, but native validation still limited a complete edition to 4,096. v69 raises the stored candidate bound to 32,768 while keeping all visible scope/category caps unchanged. Scholarship posts now use a stable 20% chance per newly observed offer; CPU/user eligibility is identical and commitments remain fully eligible. Real-data replay selects 857 of 4,089 offers and preserves earlier editions. 116 Node tests, large-catalogue native regressions and real-data catalogue decoding pass; v69 published Week 1 in-game and the user verified its feed, earlier editions, scrolling and Back. The installed managed adapter passes payload checks; fresh v69 cold-launch verification remains a follow-up.


## v71 second-test expansion

Supported skipped regular-season editions are recovered and labeled; the real 2-to-4 sim now includes Week 3. Earlier observed archives remain exact. Account/brand/portrait routing, reply sampling, For You relevance and new season-launch conditions are implemented. Details and remaining data limits are in [the test-two coverage note](docs/test-two-expansion.md).

Remaining checks: fresh MMC cold launch of v71, a genuine new preseason-to-opening run for the new conditional content, new-logo/coin visual confirmation, season/postseason/year rollover and older-save replay. The supplied ESPN PNG needs general native texture registration; existing registered image banks are used for now. Analytics grades and ratings fog remain the two later 1.0 integrations.


## v72 continuation

The account artwork and granular writer filters are wired, with native state/position recruit ranks and gap-aware recruiting catch-up. The BYU Week 4 archive repair preserves its original stories and later observations. 137 Node tests plus native/MMC checks pass. Remaining live checks and the season-to-offseason validation sequence are in [the v72 note](docs/account-refresh-v72.md). First complete that lifecycle test, then expand recruiting systems and proceed toward the two other 1.0 components.


## v73 CFP / national desk checkpoint

All five national writers now receive regular-season coverage; outside-top-60 metrics pass to beats. Native injury estimates and the merged Recruiting/new Injuries categories are implemented and live-tested for estimates/controls. CFP coverage begins at the verified Week 10 release with complete native rankings; native playoff fixtures cover later movement, bowl discrimination, round transitions and title results. The next live checkpoints remain actual Week 11+ movement, playoff rounds/championship, offseason/year reset and a cold launch. Then continue recruiting depth/content tuning and the two later 1.0 integrations.


## v74 history / late-season checkpoint

- Implemented: exact configured championship-week schedule matching with Week 14 invitation publication; standings discussion without invented tiebreakers; six-win bowl thresholds versus actual assigned invites; late CFP matchup stakes.
- Implemented: native all-time team totals/career player and head-coach milestones, edition-stable baselines, cross-phase continuity, rollback suppression; historical season records and conference finish comparisons; complete-history gates for since-year claims.
- Implemented: 22 additional advanced player/rate scenarios, rotating team caps, published-game corroboration, derived returner/OL stats, dual-production games; more current-week rivalry and cross-fan dialogue.
- Validation: 167 Node tests and actual 16-edition native catalog checks. Live title-game/postseason counter updates, coach milestones, year reset and fresh v74 MMC launch remain progression checks.


## v75 matchups / season endings checkpoint

- Implemented: occasional matchup/recap comparisons across opposing units, per-attempt efficiency and receiver/secondary production without invented coverage assignments.
- Implemented: clean generated/archived prose, more independent Barstool fan roots and distinct After Dark emotional season reactions.
- Implemented: verified end-of-season publication ledger, team/player/senior/fan/media wrapups, native class/job-security fields, staff/QB accountability, appropriate perfect/winless tone and conservative pending bowls. Exact bowl-selection week is still under user testing.
- Fixed: Week 15 title-week hype replaces duplicated Week 14 invitations.
- Validation: 185 Node tests, native tests and all dynamic scopes across 17 real editions. Live v75 activation requires a clean session after the long-running game's guarded standalone lookup failed; postseason transitions and native class/job-security comparisons remain live checks.


## v76 selection / awards / signing / carousel checkpoint

- Implemented: configured CCG-week boundary, waiting week and Week 17 selection publication; no stale standings/race posts after CCG; targeted waiting-week archive correction.
- Implemented: partial postseason assignments, native first-round/quarterfinal bracket paths, actual byes, final awards/All-Americans, Signed cohort and signing-group summaries.
- Implemented: current coaching openings/offers with pending/confirmed distinctions; cross-phase publication ledgers; selection-week closure for nonselected five-plus-win teams.
- Validation: 201 Node tests, native tests and nineteen real editions/all scopes. Live UI/actual subsequent-round confirmations remain checks; no simulation/save writes.
