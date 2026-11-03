# Dynasty Enhancer - MMC prototype v92

Native Social Media inside the offline Dynasty hub. Open **Team → Social Media**, or its CFB shortcut when available. The dedicated-tab experiment remains inactive after v84/v85 failed live checks. This development prototype includes weekly/midweek news, archives, discovery filters and prewritten conditional stories. Analytics grades and ratings fog are not yet merged; this is not version 1.0.

## Installation

1. Close MMC and CFB. Copy the complete package `Plugins` folder into the folder containing MMC, merging folders.
2. Keep both parts: `Plugins/DynastyEnhancer.dll` is the managed MMC adapter. `Plugins/DynastyEnhancer/Runtime-v92/` contains the native DLL, loader, generator and content.
3. Node.js must be installed. Set its executable path in `Runtime-v92/dynasty-enhancer.json` if necessary. Keep the exporter path `Tools/export_runtime.mjs`.
4. Start CFB through MMC and open an offline Dynasty. No fixed title-screen wait is required. The first feed may briefly show Preparing News while two stable native observations are collected; reopening adopts the latest edition.

Do not enable multiple Dynasty Enhancer/Social Media loaders. The standalone native DLL does not belong directly in MMC's top-level Plugins folder. To disable this loader, close MMC/game and rename the top-level managed adapter to `DynastyEnhancer.dll.disabled`.

## Feed and controls

- LT selects For You, National, a native conference or a native team.
- RT selects one publication edition, with the active week selected initially and older editions listed first.
- LB/RB cycle topic/account categories in both directions. Recruiting includes recruit-written posts; Players remains separate. Injuries is a dedicated category. Official Accounts includes CFP.
- All Types shows up to 30 For You, 100 National, 60 conference and 20 team posts, with team draft announcements retained beyond the ordinary team limit. LB/RB category views show every qualifying published story in one vertical feed. LT selects scope only; RT still selects one publication edition. Replies remain attached and likes remain flavor.
- Saving is not required to publish news. New stable Dynasty/week/midweek observations drive publication.

## v92 changes

- Preserves factual media reports of captured roster departures and conference changes outside the weekly flavor budget. A small school's training reactions can no longer erase those reports from category views.
- Uses native offseason stage IDs rather than a fixed week counter. The final roster/alignment stage can have internal week counter 9; it must preserve the captured training baseline. Unknown offseason stages retain evidence.
- Captures Training Results, conference realignment and Encourage Transfers in the background, independently of native News UI readiness. The Team tab and Social Media page need not be available.
- Keeps a cross-year ledger at `RuntimeHistory/<league>/<user-team>/offseason-ledger.json`. Preserve the complete RuntimeHistory folder when updating the runtime.
- Publishes supported carryover stories in the next preseason: noteworthy development in position-relevant skills, roster-review departures and new conference context. Ratings remain private; no save data or simulation outcomes are changed.
- Filters graduates, known draft departures and recycled player records. Unconfirmed destinations stay unconfirmed. A missing record only at year rollover does not prove a roster-review departure.
- Training needs an earlier snapshot. Leave the game running through the final signing day, Training Results and Encourage Transfers, with a few seconds for stable capture at each stage. Periods skipped entirely cannot be fully reconstructed; prior-year conference history can supply limited alignment context.
- Retains the Team/CFB shortcuts, complete category scrolling, filters, replies and existing UI.

## Previous v88 changes

- Removes the attempted LT pagination: the native game caches the list on first entry, so v87's conditional page rows were missing after a later category change. LT remains purely a scope selector.
- Category views scroll through the complete matching story pool, without a 30-post page limit or pagination header. All Types remains curated/capped, with a team draft exception so every selection is visible.
- Full-list checks preserve replies, original editorial order and all 224 draft picks in ascending order. Actual current candidates: National Recruiting 139, expanded For You Recruiting 205; render/scroll performance still needs a controller check.
- Existing Team shortcut, recruit eligibility/context, analyst/fan discourse and save/history preservation remain.

## Previous v87 changes

- Social Media moves to the top of Team using its existing Roster donor and an unused coordinate. Stock Team entries keep their identities and order. Missing donors/occupied coordinates preserve the stock menu. Dynasty Central is unchanged. No hub-tab-list hook is installed.
- Team/conference first-round leadership, top-ten discussion, fan draft reactions and subjective NFL-haul opinions use the verified/persisted draft class. Actual players/rounds remain native; NFL destinations/picks remain simulated. Select the draft publication edition for all official picks; later recruiting weeks can discuss that recorded class without republishing every selection.
- HS/JUCO/transfer labels, verified former schools, rivalry-transfer reports and fan replies. One-star prospects receive no new recruiting posts; a deterministic 10% of two-stars can receive underdog coverage. Big portal moves get Maddox/Brooks coverage; five-star commitments/signings get ESPNCFB reports.
- Factual commitment/signing reports survive normal flavor budgets. Paged browsing exposes all qualifying published posts. For You retains user-team draft picks; archived view expansion preserves existing prose, likes and publication dates.
- Fixes redundant position prefixes before a trailing position description. 283 content tests plus native pagination, full draft ordering, Team shortcut and existing ABI/ownership checks pass. Live checks are tracked separately.

## Previous v86 changes

- Withdraws the dedicated-tab path after the v85 cold-load crash. Native UI implementation and code gates match v83 exactly; stock MenuPanelsReady is not hooked or modified. Dynasty Central and seasonal CFB entries remain.
- Retains portal/unsigned stories, native draft-class players/rounds, stable simulated picks/NFL destinations, all 224 official draft announcements and Transactions pick order.
- Saves and archived feed history are preserved. Native/content/package checks and controller checks are recorded separately.

## Previous v85 changes (withdrawn)

- Corrects v84's descriptor-number ABI, which could blank the entire hub. Uses the native double-number factory and verifies all native scalar fields and the completed pointer array before sending a replacement. Failed verification forwards the untouched native hub.
- Inserts the descriptor physically after Team, as well as assigning its intermediate priority.
- Native regression checks preserve fractional numbers, negative sentinels, insertion position and rejection of corrupt readback. The v84 portal/draft content and existing controls remain.

## Previous v84 changes

- Dedicated Social Media hub tab after Team, with one Open Feed button. Original tab descriptors stay intact; unsupported layouts retain existing shortcuts.
- Opening-week portal news uses actual transfer-list membership, verified former schools and current recruiting interest. Remaining high-school prospect stories exclude committed/signed recruits.
- NFL Draft (@NFLDraft), using the native draft icon, announces all 224 real draft-class players in their native rounds. Pick order and NFL teams are simulated consistently, with all 32 clubs represented in each round. Projections/placeholder NFL scaffolding are excluded.
- National → Transactions preserves the complete draft in pick order, exceeding the ordinary National 100-post cap for this category only. Other feed caps and normal 5–20-per-team coverage remain; official draft selections are exempt from that weekly flavor budget.
- Portal/unsigned recruiting leads For You rather than flooding it with draft picks. Existing archived editions remain.
- 273 Node tests, native layout/decoder checks and the real 25-edition archive pass. Live controller confirmation is tracked separately.

## Previous v83 changes

- LB/RB and both dropdowns redraw the offseason page through the persistent Dynasty Central source.
- Initial entry, filter refresh and diagnostic preflight use one panel-request helper, eliminating the remaining CFB-only refresh.
- Native regression checks preserve the request's self/parameter pointers and failure result. Existing scoped input and foreign-menu safeguards remain.

## Previous v82 changes

- Permanent Social Media button in Dynasty Central; the seasonal CFB entry remains.
- Card, container and panel data use the persistent native User Settings source, with no Heisman/CFB dependency when those records disappear in the offseason.
- Return-to-hub cleanup covers both entry menus. Missing donors or occupied button coordinates preserve the original menu.
- 263 Node tests, native insertion/typed forwarding/collision/host isolation checks and the actual current archive pass. Controller and first-launch checks remain distinct from unit validation.

## Previous v81 changes

- Offseason Week 0 is the season-recap edition: completed title coverage, both finalists, verified quarter-score analysis, all five national analysts, end-of-season fans, season assessments and confirmed carousel retrospectives.
- National eligibility survives the phase change and week-number reset. Prior title-week stories remain archived; completed finals never become new pregame predictions.
- Portal watch uses valid elevated transfer-risk indicators, never the -1 sentinel, confirmed entry language or invented destinations. Seniors are excluded without verified returning eligibility.
- Net NIL adjustments made in recap week publish in Offseason Week 1. Unchanged/reverted edits, unknown amounts and team changes do not produce deals. Later offseason changes remain observable normally.
- 263 Node tests and native checks pass, including every scope in the real 23-edition archive. Live UI and next-week NIL confirmation are separate checks.

## Previous v80 changes

- Explicit news cycles shift finished programs toward recruiting, roster planning, farewells and prestige-aware expectations instead of stale in-season averages.
- Current playoff/title games dominate national discussion. Five analyst voices, distinct player voices, non-rival spectator fans and conference-prestige-sensitive championship coverage use the actual fixtures.
- Box-score recaps use verified quarter scoring and complete offensive stat lines; missing chronology is never invented.
- Neutral-site wins count in season-end checks, and signed negative-yardage games can corroborate season rushing totals.
- 251 Node tests and native checks pass; all 22 real publication editions validate in every dynamic scope. In-game v80 confirmation remains a separate check.
- The native CFP bracket still showed Loading Playoff Field after v79 hooks were stopped. The captured bracket is complete; cause is unresolved. No bracket or save data is changed.

## Previous v79 changes

- Transactions on LB/RB: reported coaching moves/contracts, signed recruits and their listed NIL offers, and observed compensation changes. Replies stay with their reports.
- Likes are flavor, up to 20K for major events. All views use varied editorial order instead of popularity sorting.
- A shared 5–20-post weekly allowance across all voices discussing each program; replies and both sides of a matchup count. Sparse facts do not receive fictional filler.
- Player references include natural position labels before character/byte validation.
- Diagnostic panel loads no longer run on hover or normal entry. Reopened dropdown assets first reuse a fully verified native allocation pool; large old catalogs are retired on the worker, archive facts are not duplicated in the UI payload, and unchanged captures back off to eight seconds.
- 232 Node tests, native checks and 21 real editions pass. Clean-launch/rollover performance verification remains a live check.

## Previous v77 changes

- Bowl Week 2 capture survives unknown optional historical bowl-art IDs. Unknown identity, enum state and result values remain strict errors.
- More verified team offense/defense, penalties, turnovers, coach career/splits and NIL allocation stories; 1 NIL point equals $2,500.
- Team schemes come from the active Dynasty. Conference-strength discussions use coherent native prestige grades, including custom leagues.
- Heisman context includes meaningful rushing/receiving production, turnovers and the actual latest game; earlier editions cannot consume later games.
- Percentage-based after-contact yardage and all-snap sack-allowed rates, with neutral/positive/negative analysis selected by evidence.
- 215 Node tests, native checks and the real 20-edition catalog pass. UI verification follows deployment.

## Previous v76 changes

- Week 16 awaits official selections; Week 17 confirms native bowls, playoff berths/byes and partial-bracket paths. Missing bye opponents remain conditional.
- Five-plus win teams without assignments learn their season is over at selection week. Fewer-than-five-win teams can finish at CCG week. Partial future assignments protect live seasons.
- Final annual awards, Heisman and national/conference All-American selections use actual issued records. Heisman watch/poll/standings updates stop after CCG week.
- Signed recruits are distinct from verbal commitments, with individual announcements, welcomes and school signing-group summaries.
- Native coaching openings/offers distinguish pending changes, departures, completed hires and retained contracts. Confirmed news uses a publication ledger across phases.
- Stored Week 16 premature confirmations/standings are corrected without reconstructing unavailable historical injuries or recruiting.
- 201 Node tests plus native/MMC checks. Live bracket, awards, signing and coaching page checks remain part of verification.

## Previous v75 changes

- Occasional opposing-unit and receiver/secondary comparisons, with per-game/per-attempt baselines and actual-game recaps. Recaps exclude the game itself from entering averages.
- Independent Barstool fan posts; more personal and volatile After Dark season reactions. Both remain Fans, with clean language across new and archived prose.
- Verified season endings, senior thanks/farewells, staff/QB accountability, native recruiting-class rankings and coach-pressure reports. Bowl-eligible teams awaiting assignment stay pending; an unbeaten regular season is not called a completed perfect season.
- Endings publish once and persist in their edition. Week 15 uses fresh championship-week hype rather than another Week 14 invitation.
- 185 Node tests plus native/MMC checks. Actual postseason progression and current-class/job-security UI comparison remain live checks.

## Previous v74 changes

- Late-season conference races, verified Week 14 title-game invitations, bowl-threshold discussion, actual bowl/playoff assignments and current-opponent CFP stakes.
- Observed team all-time, player-career and head-coach milestone crossings. First observation seeds quietly; existing native totals already include current-season results.
- Historical season comparisons, conference finishes and supported title/bowl/playoff drought references. Missing history never becomes a guessed date.
- Broken tackles per 100 carries, yards after contact, YAC share, OL sacks per 100 offensive snaps, defensive per-game rates, kicking/return breakdowns and single-game dual production. All season rate inputs corroborate published player game records.
- More current-week rivalry promotion and opposing-fan conversation, retaining the stable 33% reply gate.
- 167 Node tests plus native catalog and adapter checks. Actual postseason milestone updates and a fresh MMC cold launch still need live progression checks.

## Previous v73 changes

National analytics focus on the current poll's top 60; school beats retain the smaller-program analysis. Jake Whitmore, Marcus Bennett, Tina Brooks, David Ellison and Chris Maddox all receive regular-season stories, with distinct opinion/humor/evaluation wording. ESPNCFB remains a separate account.

Injury reports use native remaining-week ranges and severity/status. They do not subtract elapsed weeks twice or invent an exact date. Season-ending reports apply to the injury's current season; uncertain/undiagnosed cases retain appropriate uncertainty.

The CFP account (@CFBPlayoff) uses native image `dynas_stickers_CFP`. Its first three ranking posts begin at regular Week 10 when a complete native CFP Top 25 is available. AP remains primary before that point. The initial publication does not compare AP places with CFP places. Later reports cover CFP movement and contender discussion. Native playoff games and championship results drive postseason coverage; rankings alone do not establish a berth.

TeamBuilder fan/beat accounts use the primary logo because the alternate numeric slots displayed placeholders in the live test. Other native on-white, helmet, mascot and secondary bindings remain.

## History, diagnostics and limits

Preserve `Runtime-v83/RuntimeHistory` when updating. The installer supports checksum-verified migration. The ZIP contains no user history, saves or extracted game images. Archived facts/likes are retained; requested presentation migrations can update account artwork/names. Recovered skipped weeks contain only supported historical facts and are labeled. Recruiting gaps use explicit catch-up observations rather than assigning an unknown event week.

- MMC status: `Plugins/DynastyEnhancer-launcher.log`.
- Runtime/UI status: `Runtime-v83/social-media.jsonl`.
- Generator diagnostics: `Runtime-v83/runtime-generator.log`.

`active` and `runtime_feed_published` identify successful readiness/publication; `runtime_feed_resumed` identifies an exact cache match after reload. Unsupported native code, conflicting UI ownership, invalid catalogues and changed protected payloads are rejected. User configuration/history are editable; changing protected runtime/content files requires rebuilding the package manifest.

The mod observes Dynasty data and changes presentation only. It does not write simulation/save records or change save structure. Live postseason/year-rollover and fresh v76 cold-launch checks remain follow-up validation. See the source repository's `docs/postseason-decisions-v76.md` for evidence and coverage details.
