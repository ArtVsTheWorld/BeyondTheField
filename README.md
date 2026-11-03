# Dynasty Enhancer

Dynasty Enhancer improves the offline College Football 27 Dynasty experience through worldbuilding, context, and realism. It uses native game menus and presentation changes without restructuring Dynasty data or changing simulation outcomes.

This is a development prototype, not the planned 1.0 release.

## Hub layout recovery (v85)

The current package is `Build/DynastyEnhancer-v85-MMC.zip`. v84's first in-game hub refresh went blank: its new descriptor used an unsigned-integer native setter with a floating-point ABI. v85 uses the verified double-number factory, reads back the complete native descriptor and array before publication, and preserves the original hub if either fails. The tab is also physically inserted after Team. See [v85 recovery and verification](docs/hub-layout-v85.md). The portal/draft content from v84 remains.

## Previous dedicated hub tab, portal and draft (v84)

The current package is `Build/DynastyEnhancer-v84-MMC.zip`. A year-round **Social Media** hub tab after Team contains **Open Feed**, with the existing native feed and controls. Dynasty Central/CFB shortcuts remain a fallback if the native tab layout cannot be verified.

Offseason Recruiting Week 1 prioritizes confirmed portal entrants and leading unsigned high-school prospects. The official **NFL Draft (@NFLDraft)** account announces all 224 native draft-class players in their actual rounds. Exact picks and NFL destinations are stable simulated worldbuilding, not native draft results. **National → Transactions** presents the complete board in pick order, with top-ten and final-pick coverage. See [v84 implementation and verification](docs/portal-draft-v84.md).

## Previous offseason filter refresh (v83)

The current package is `Build/DynastyEnhancer-v83-MMC.zip`. LB/RB category changes and both dropdown selections now redraw through the persistent Dynasty Central source. v82 accepted the selections but still used a CFB-only redraw path, leaving the visible page stale during the offseason. Entry and all filter refreshes now share one native panel request. See [v83 verification](docs/offseason-filters-v83.md).

## Previous year-round Social Media access (v82)

The current package is `Build/DynastyEnhancer-v82-MMC.zip`. Social Media now has a permanent shortcut in **Dynasty Central**, alongside its existing CFB shortcut. The page no longer borrows CFB/Heisman records, which the native game removes during Players Leaving and the rest of the offseason. See [v82 access and verification](docs/year-round-access-v82.md).

## Previous season recap and NIL timing (v81)

The current package is `Build/DynastyEnhancer-v81-MMC.zip`. Offseason Week 0 now covers the completed national championship, both finalists, season retrospectives, confirmed staff moves and the wait for next season. National no longer empties when the game resets the week counter. Elevated native transfer risk can produce retention-watch stories without claiming a portal entry. NIL adjustments observed during the season-review week publish in the following week. See [v81 behavior and verification](docs/season-review-v81.md).

## Previous intentional news cycles (v80)

The current package is `Build/DynastyEnhancer-v80-MMC.zip`, with the MMC adapter and versioned native runtime. Preseason, opening weeks, midseason, late-season races, postseason and offseason each have explicit editorial rules. Finished teams pivot to their next roster and recruiting class; the national feed emphasizes the actual championship and playoff fixtures. Expectations use native program prestige, including custom teams.

Quarter-score recaps describe verified comebacks, second-half swings and defensive finishes. National championship coverage includes five analyst voices, predictions, matchup evidence, team/player reactions and non-rival fans choosing a contender. Likes remain flavor; shared weekly budgets remain 5–20 posts per team. See [v80 implementation and verification](docs/news-cycles-v80.md).

## Previous transactions and editorial feeds (v79)

Transactions joins the LB/RB filters, supported signings/contract changes receive reported coverage, and player references include positions. Likes can reach 20K for major events. Editorial ordering rotates topics and accounts while keeping replies attached. Normal hover/entry avoids synthetic diagnostic panels; retired catalogs are released on the worker. See [v79 implementation and verification](docs/transactions-editorial-v79.md).

## Previous context and postseason recovery (v77)

The current package is `Build/DynastyEnhancer-v77-MMC.zip`, with managed `Plugins/DynastyEnhancer.dll` and native `Plugins/DynastyEnhancer/Runtime-v77/DynastyEnhancerNative-v77.dll`. Keep the complete versioned runtime beside the adapter.

v77 fixes Bowl Week 2 capture when historical bowl artwork contains an unrecognized optional presentation ID. It adds verified offense/defense efficiency, discipline, ball security, NIL position-group allocation, coaching context, native schemes and prestige-driven conference discussions. Heisman stories include meaningful dual-threat production and distinguish rank, latest performance and season totals. See [calculation and recovery details](docs/context-recovery-v77.md) and [verification](docs/verified-v77.json).

## Preseason and lifecycle prototype (v69)

The current candidate adds 62 prewritten variants across 24 new families (339 variants total): native preseason AP and All-America/All-Conference honors, season outlooks, opening games, team hype, player camp posts, fans, top-100 recruiting watches, fictional title futures, clustered ranked-opponent gauntlets, AP/model debates with fan replies, explicit AP/Coaches comparisons, and conference talent maps. All teams, including TeamBuilder programs, use the same eligibility. See [preseason coverage and lifecycle details](docs/preseason-lifecycle.md).

Public rankings use AP by default and CFP once a complete native CFP Top 25 is present. Coaches is an explicitly labeled alternative. Hidden team Rank is never a public poll. Historical upset ranks keep their captured pregame poll, and AP-to-CFP differences never become weekly movement.

## MMC loader (v69)

The package includes a managed **DynastyEnhancer.dll** adapter for MMC and a separate **DynastyEnhancerNative-v69.dll** game runtime. Use the complete `Build/DynastyEnhancer-v69-MMC.zip` package. The adapter belongs directly in MMC's `Plugins` folder; its native runtime, generator and content belong under `Plugins/DynastyEnhancer/Runtime-v69`. A raw native DLL placed directly in Plugins is not an MMC plugin. See [the package guide](Source/PackageREADME.md).

The adapter has no fixed 20-second title-screen delay. Verified menu hooks install before waiting for Dynasty assets, capturing the first hub construction. Native UI readiness is independent of news generation; a native status card can display while the first edition is prepared. Entry before asset readiness completes through the native inert action, rather than silently returning with navigation pending. On a phase transition, the filter model is reacquired using exact native byte gates rather than reusing a stale allocation. A late dropdown failure retains native page data and Back behavior. The v66 first-hub button passed, but an invalid reader ownership path and a silent navigation guard caused the preseason entry failure. v67 replaces both, expands the reserved Award[] capacity gate, and captures all 600 honors from the live preseason save read only. The user verified preseason posts, the Preseason 2026 choice and normal Back navigation. The same-session advance to regular-season Week 0, its posts and Back navigation also passed. Same-process main-menu reload also passed. The verified v68 managed adapter is installed for the next MMC startup; a fresh v68 cold launch remains a follow-up check.

Configured Node.js must be available. No save path is required. Existing RuntimeHistory is retained by the development installer. Startup diagnostics distinguish `menu_hooks_active`, `startup_waiting`, `active`, and `runtime_feed_published`. v64 automatic loading was verified in-game; [its validation record](docs/verified-v64.json) remains the historical baseline.

Build and stage the prototype package with:

```powershell
.\Source\build.ps1
.\Source\Package.ps1 -MmcRoot 'C:/path/to/MMC'
```

`Source/Install-Mmc.ps1` installs that staged package while MMC/game are closed, backs up the previous top-level DLL and preserves existing configuration/history. It accepts `-HistoryFrom` for the first migration from a development build. Package and adapter smoke tests do not launch or inject the game.

## Week 1 publication and offer frequency (v69)

The first full recruiting week produced 9,029 stories from legitimate CPU/user events, exceeding the old native catalogue validator's 4,096-story limit. v69 raises the validated stored candidate budget to 32,768 per edition/reference pool, retaining the 128 MiB file bound and identity/text/reference checks. Display limits stay 30 For You, 100 National, 60 per conference and the existing team cap after category filtering. A native regression covers 9,300 candidates and rejection beyond the new bound.

Each newly observed scholarship offer now has a deterministic 20% publication chance for both CPU and user programs. Its choice is fixed by Dynasty/year/publication phase/week/offer ID, independent of save filename, user-team selection and unrelated midweek changes. Offers remain observed even if no post is admitted; replies require a published parent. Commitments are unaffected. The separate publication-policy version reconciles the active old offer feed once without changing template revisions or rewriting earlier editions.

The real Week 1 replay selected 857 of 4,089 offer events (20.96%), yielding 2,413 total posts and 30 For You. Preseason and Week 0 archives remained byte-equivalent in the displayed catalogue. Both the original 9,029-story catalogue and the revised catalogue pass native decoding for every scope. 116 Node tests and native/package checks pass. v69 has now published Week 1 in-game, and the user verified its feed, earlier editions, scrolling and Back. Its payload-verified managed adapter is installed for the next MMC launch.

## Publication archives and reloads (v68)

RT now lists earlier observed phases in the same Dynasty/team/season: Preseason, then Week 0 and later regular-season weeks. The active edition is the default and the picker still selects one edition only. Existing preseason wording, author identities, likes and feed order are read from history, not regenerated. Future phases/weeks and other Dynasties/teams/seasons are excluded. History files remain separated by phase for event reconciliation.

An unchanged edition can resume after the first verified native capture when its normalized fact hash and content revision match its stored snapshot. New or changed facts still require stable observations; a rewind follows normal reconciliation. Save filenames are not identity keys. A brief preparing card can still appear while the active native context is first validated.

The before/after reload comparison found all 62 Week 0 posts and For You order identical. The real-data archive test also preserved all 2,382 preseason posts. The user verified both editions in chronological order and all controls in v68. 113 Node tests and native/package tests pass. See [v68 verification](docs/verified-v68.json).

## Feed sizing and ordering (v63)

For You shows up to 30 posts, National up to 100, and each native conference up to 60. Individual team feeds keep their existing capacity. The dedicated caps apply after the LB/RB category filter, so each category can draw from its full qualifying pool. Replies count toward the displayed limits.

Every view, including archived weeks, sorts parent threads by likes descending. Replies remain directly below their own parent and are sorted by likes within that thread; ties use stable story IDs. A limit can end partway through the final thread but never expose a reply without its parent. For You preserves relevance/variety selection and its soft national/conference/team mix before sorting the selected posts. Category/voice allowances scale to 30 posts, while the account, repeated-thread and single-scholarship-offer safeguards remain.

## World news expansion (v62)

The latest build adds 24 advanced team-analysis scenarios and 26 player-analysis scenarios, native national/conference weekly awards, upset and streak stories, observed school/conference/FBS records, and fan reactions involving actual players and staff. Recruiting coverage adds native stars, prestige-sensitive reactions, flips/decommitments, and guaranteed major reactions to newly observed five-stars or the national No. 1. Rivalry recruiting steals, unbeaten collisions and upset bounce-back previews are included. CPU and user programs share eligibility; For You remains a personalized 30-post selection.

The two content packs now provide 277 prewritten variants across 170 families. See [the coverage table](docs/world-news-coverage.md) for all 50 additional analysis scenarios, native data requirements, observation limits, engagement and the fictional spread model. Likes cap at 5K for ordinary standalone posts and 10K for major news; replies receive 1–20% of the parent’s likes. Views are removed. The native heart probes did not render, so the footer uses “likes.” Analysts use the native newspaper icon. Player jersey portraits, native dropdowns and smooth vertical scrolling remain.

The reader also supports the active child-table context exposed after an in-session Dynasty reload. It still reads runtime memory, never a save-file fallback. New native capture fields cover current player season totals, weekly awards, record books, prestige, coordinators and venue identity. The read-only model-line approach references Ace’s Toolkit Smart Force Win and Balla’s starter/depth calculations; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Social Media writing: first generation pack

The user approved the Review 03 writing direction and requested generation. `Content/Runtime/first-pack.json` now contains 180 prewritten variants across the six account types plus the fictional model-line account. `Tools/story_renderer.mjs` applies them to verified event facts; it never calls an online text model. The original three illustrative cards and prior prototype tweet wording remain retired. Editorial samples remain separate from the executable pack.

The first slice covers published results, player/team performances, polls, offers and new commitments, injuries, upcoming matchups, Heisman/CFP rankings, standings, calendar items and fictional model lines. Analysts use corroborated rushing rank, weighted third-down conversions, red-zone touchdown rate, turnover margin and season-largest margins. `Content/Editorial/analyst-opportunities.json` tracks deeper calculations still to implement. Mere ranking updates without analytic evidence use reporter accounts.

Official accounts use compact captions, native nicknames and occasional hashtags. Players normally post positive reactions; native personality leads, with secondary QB restraint. Players, recruits and fans vary punctuation and casual phrasing. Current-coach mentions require a real coach reference. Recruiting phone calls and personal reactions are authored worldbuilding around actual events. A persistent optional faith-language style is assigned independently of native personality/position, not presented as detected belief.

`Tools/story_conversations.mjs` adds bounded player/fan replies to actual parent posts; `Tools/story_templates.mjs` handles cooldowns and frozen selections. `Tools/story_authors.mjs` persists identity and collision resolution in runtime history. Recruiting-to-roster transitions and position, jersey or week changes retain the handle. Deterministic event/week choices keep existing wording stable during unrelated midweek updates. Missing slots suppress the variant. Bodies must fit 280 Unicode code points and the existing native 512-byte budget, without truncating factual values. All Posts caps repeated template forms, account frequency and voice repetition. Complete parent/reply blocks can now appear there while retaining the current post limit and scope mix. Dedicated scopes keep qualifying facts and conversations together. Player congratulations require a real recruit post; a scholarship offer never triggers commitment/welcome language. Team posts tag persisted athlete handles. Cross-week template choices prefer phrases that account has not used in the previous two weeks, with a least-recent fallback when all valid wording is cooling down. Same-week bodies and conversation admission order are persisted so unrelated midweek arrivals do not reroll or evict existing replies.

Native emoji testing is complete: the current tweet font showed missing-glyph boxes for every tested symbol/emoji, including football, fire, trophy, hands, flags and combined sequences. Ordinary text, accented Latin and punctuation rendered. Runtime emojis are disabled; decorative arrows use ASCII `->`. See `docs/native-font-check.json`. `Tools/export_emoji_probe.mjs` is an explicit development-only exporter with no history writes and is never the production exporter.

The read-only Week 9 data audit reconciled 138 FBS programs and 511 published finals. Rushing, third-down and red-zone totals matched the game caches for every program; all inspected quarter-score splits plus overtime matched their finals. Cached unpublished CPU scores are excluded from public news and player performances. Every future snapshot still passes validity/coverage checks.

The verified first-pack source is on `content/voice-foundation`, with the conversation expansion on `content/conversations`; generated previews are under Build. The historical live v47 source, DLL and archives remain available at tag `prototype-active-dynasty-v47`. The replacement generator starts its own observed publication history; it does not rewrite the old prototype editions or re-use their wording. Its first observed week is the active week. The candidate compiled and passed local checks. v49 loaded in-game and published 168 Week 9 posts (20 curated); native cards, account logos and vertically scrolled posts were observed. Checking the native Heisman panel exposed zero-based candidate places; the adapter now converts them to displayed ranks, retains the leader and treats -1 as unknown prior place. All 65 tests pass. The corrected v50 generator publishes 169 posts, including the previously omitted leader. The user verified the corrected Heisman rank, fitting text, My Team filter and controller scrolling in-game. The temporary emoji DLL was stopped successfully.

## Conversation and portrait expansion

The new pack supports recruit welcomes from actual roster players, fan replies to players/reporters/analysts, teammate congratulations, and official accounts tagging athletes. All replies require an actual generated parent, inherit its scope and display the native Reply label. Generation limits keep reactions from turning into automatic walls of replies. Two persistent fan accounts per school and additional analyst identities provide room for different voices without changing existing handles.

Portrait routing now uses verified nonblank entries from native library 1 for players and recruits regardless of NIL status. This includes generated face portraits; all 5,040 native generic IDs were found in that library. `Content/Runtime/portrait-ranges.json` contains numeric availability ranges, no images or extracted assets. The reader captures `PortraitForceSilhouette`, and missing/blank/forced-silhouette cases fall back to the team logo. The user verified native portraits, parent/reply grouping, Reply labels, scrolling and LT in-game. The current isolated history contains Week 9; future editions accumulate as weeks advance. Older v47 prototype archives remain separately preserved.

## Current component: Social Media

A Social Media button in the CFB tab opens a native vertical feed with opaque tweet cards, account images, audience-scaled flavor likes, adaptive card heights, smooth controller scrolling, and two native dropdowns. LT chooses For You, National, each native conference in alphabetical order, then every active team in alphabetical order. Conference identities and memberships come from the loaded Dynasty, including realignments. LB cycles forward and RB cycles backward through All Types, Recruiting, Recaps, Upcoming, Rankings & Awards, Analysts, Beat Reporters, Team Accounts, Players & Recruits, and Fans; the header identifies the active type. Replies always follow their selected parent, regardless of their own author or category. RT selects one publication week, oldest to newest; the active week is the default. For You uses a curated mix with soft targets of 35% national, 25% conference, and 40% team news. The personalized pool includes the user team, native conference peers, important national news, and observed recruiting events involving the user recruiting board, home state, or native school pipelines. Dedicated views expose all qualifying stories, including unranked programs outside the user conference.

Stories include previous-week results and performances plus current-week rankings, Heisman news, matchups, recruiting, injury reports, and calendar items. Publication week governs the edition even when the event occurred the week before. Betting lines are fictional generated game content.

**Active-Dynasty candidate:** the DLL reads the loaded career session and packed runtime tables without invoking native table methods or writing game data. A background observer checks roughly every three seconds, rejects inactive/advancing stages and changing captures, and requires two matching captures before generation. New weeks create editions; midweek offers, commitments, injuries/recovery, and completed games update the current edition. This detects native runtime changes; it does not hook the advance callback. Reopen the page to adopt the latest immutable feed.

The read-only capture has been compared with the save reader: all 122 generated story bodies, categories, and avatar selections matched in the inspected Week 8 snapshot. Automated lifecycle tests cover rollover, unsaved midweek events, deduplication, rollback, and identity isolation. The user verified the live Week 8 feed, USC recap, both dropdowns, and scrolling. The user also verified three midweek scholarship posts after the native `New` status fix, without manually saving. The game did autosave during the recruiting session; the DLL itself reads runtime memory. The subsequent Week 8 → Week 9 advance also passed: Week 9 was selected automatically, all 153 generated story bodies/categories/avatar choices matched the diagnostic save reader, and the three offer posts remained in the Week 8 archive without repeating in Week 9. Unsupported runtime layouts remain unavailable rather than reading a configured save as a silent fallback.

The preserved save-backed UI build is tagged `social-media-v45-baseline`.

## Build

Windows x64, Visual Studio C++ tools, and Windows SDK are required. From the project root:

```powershell
.\Source\build.ps1
```

This builds `Build/DynastyEnhancerNative-v69.dll`, `Build/LoadDynastyEnhancer.exe`, `Build/LiveCapture.exe`, and runs the native tests. Both native dropdowns and the read-only feed are enabled by default. Generated native UI patch headers are included; no extracted game assets are required to compile. Native bindings are build-specific and reject unsupported code/asset layouts.

Node.js is required for the story generator. Copy `Config/dynasty-enhancer.example.json` to `Build/dynasty-enhancer.json` and set the Node executable path if needed. The active-Dynasty reader needs no save path, parser, or external schema. Generated snapshots, feeds, and publication history live beside the DLL under `Build/` and are not game saves.

The legacy save adapter remains as a diagnostic comparison tool: `Config/social-refresh.example.json` documents its external dependencies. It is not the candidate DLL's data source.

```powershell
node --test Tests/*.test.mjs
Build/LiveCapture.exe <PID> Build/runtime-raw.json
node Tools/export_runtime.mjs Build/runtime-raw.json Build/runtime-feed.json
```

For development, load with `Build/LoadDynastyEnhancer.exe <PID> <absolute-DLL-path>`. Stop with the same arguments plus `--stop`, after returning from Social Media to the CFB hub. The stop guard refuses replacement while the Social Media page is open. Use a fresh DLL filename for another candidate in the same process; stopped modules remain pinned. Manual loading is for development; the v64 MMC package provides the automatic loader.

## Roadmap and provenance

See [ROADMAP.md](ROADMAP.md) for the planned 1.0 scope. [docs/verified-v45.json](docs/verified-v45.json) records the verified predecessor and the minimal packaging changes made here. Saves, generated feeds, extracted assets, and local runtime configuration are deliberately excluded from version control. See [docs/runtime-lifecycle.md](docs/runtime-lifecycle.md) for capture, publication, and validation details.

Third-party JSON code retains its MIT license; see [Vendor/json.LICENSE.txt](Vendor/json.LICENSE.txt). A license for the original project code has not yet been selected.

## Social discovery candidate (v56)

The scope list is native Dynasty data, not a fixed conference/team list. The inspected DGA2027 Week 9 catalog contains 11 conference groups and 138 individually indexed programs. The native shared-index generic FCS placeholders are not offered as separate team identities. Historic editions retain their own published stories; a newly introduced scope can be empty in an older edition that never recorded that scope.

Only official team accounts use school logos. Beat reporters use the native microphone icon, analysts now use the newspaper icon, and fans use the social icon. Valid player/recruit portraits remain native. Active player jerseys use the same PlayerPortraits + TeamJerseys library pairing as the roster compositor; recruits retain neutral shirts. Counts are fictional engagement, seeded by publication/story identity and scaled by verified native brand-exposure grade, poll rank, voice, and national relevance. An existing same-week count is preserved across refreshes. Counts do not change simulation data or expose player ability. Coverage volume is not yet scaled by audience.

The two existing dropdowns, native viewport mask, smooth scrolling and category/index metadata remain. Cards have a reserved engagement footer so long bodies do not overlap likes. The file-size guard is 128 MiB for multiweek catalogs, with separate 48-edition, 4,096-story and 512-scope bounds.


## Second-test expansion (v71)

The current package adds supported skipped-week recovery, native on-white/secondary logos, revised account identities, a stable 33% reply gate, more personalized 30-post selection, and 84 preseason/opening variants. The native DLL is `Build/DynastyEnhancerNative-v71.dll`; the MMC package is `Build/DynastyEnhancer-v71-MMC.zip`. See [coverage and data limits](docs/test-two-expansion.md). Automated validation now includes 129 Node tests plus native and MMC adapter checks. The optional supplied ESPN PNG still needs a separate native texture import.


## Account and recruiting continuity update (v72)

v72 adds CanDuel Sports, separate Players/Recruits types, requested native analyst/helmet/mascot images, TeamBuilder secondary images, given-name teammate references and native state/position recruiting ranks. It repairs the observed skipped-week recruiting gap using explicit catch-up reporting and a retained historical observation. [Implementation, artwork IDs and test status](docs/account-refresh-v72.md). Current artifacts: `Build/DynastyEnhancerNative-v72.dll` and `Build/DynastyEnhancer-v72-MMC.zip`.


## National desk, injury windows and CFP (v73)

v73 distributes regular-season national analysis across all five named writers, focuses it on the current poll's top 60 and retains smaller-program metrics with school beats. It adds native injury return estimates and an Injuries category, merges Recruiting/Recruits, restores TeamBuilder primary logos, and adds CFP (@CFBPlayoff) ranking/playoff coverage from Week 10. [Evidence, conditions and remaining live checks](docs/playoff-desk-v73.md). Current DLL/package are `Build/DynastyEnhancerNative-v73.dll` and `Build/DynastyEnhancer-v73-MMC.zip`. 149 Node tests plus native/MMC checks pass; the user verified the live injury estimate and category controls.


## Late season, history and deeper analysis (v74)

v74 adds verified conference championship invitations from Week 14, late-season title and bowl races, assigned postseason matchups, career/all-time milestone crossings, season-history comparisons and current-week rivalry/fan discussion. New advanced rates include broken tackles, contact yardage, YAC share, offensive-line sacks per snap, defensive per-game production, distance-based kicking and returns. [Conditions, evidence and live checks](docs/history-analysis-v74.md). Current native DLL/package: `Build/DynastyEnhancerNative-v74.dll` and `Build/DynastyEnhancer-v74-MMC.zip`. 167 Node tests pass; the actual sixteen-edition catalog validates in every native scope.


## Matchups, fan voices and season endings (v75)

v75 adds occasional opponent-unit/player comparisons with entering-game baselines and actual recaps; independent Barstool fan posts; clean language in new and archived prose; supported season wrapups, senior thanks/farewells and undefeated/winless reactions. Week 15 gets fresh championship-week hype instead of another Week 14 invitation. [Conditions and live checks](docs/matchup-season-v75.md). Current DLL/package: `Build/DynastyEnhancerNative-v75.dll` and `Build/DynastyEnhancer-v75-MMC.zip`. 185 Node tests and the actual seventeen-edition native catalog checks pass.


## Postseason decisions (v76)

v76 treats Week 16 as a waiting week and Week 17 as selection/award/signing time. Native partial bracket slots preserve bye-team paths without inventing opponents; explicit awards/signatures/coaching records drive confirmations. Conference standings stop after CCG week, nonselected five-plus-win teams can close their seasons, and confirmed stories retain their publication edition. [Conditions and evidence](docs/postseason-decisions-v76.md). Current DLL/package: `Build/DynastyEnhancerNative-v76.dll` and `Build/DynastyEnhancer-v76-MMC.zip`. 201 Node tests pass; the real nineteen-edition catalog validates in every native scope.
