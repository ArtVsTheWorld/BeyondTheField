# Dynasty Enhancer roadmap

## Current prototype: native Dynasty lifecycle

- Active Dynasty and controlled program read from runtime tables instead of a configured save.
- Stable editions published after regular-season week advancement, with a live Week 8 → Week 9 rollover verified.
- Midweek scholarship offers verified in the native feed; commitments, injuries/recovery, and current-week results share the same publication path.
- Deterministic IDs, scoped history, and fixture coverage for identity changes, earlier-week loading, and replay with different outcomes.
- Native menu/controller behavior retained; simulation access remains read-only.

Before broader release, validate active-Dynasty switching, an actual older-save restore/replay, offseason/year transitions, and cold launch. The runtime observer currently waits for stable state rather than hooking the native advance-completion callback.

## Six-stage Social Media content plan

1. Voice/tone direction approved from thirty samples and subsequent revisions. Legacy prototype wording is retired.
2. Core event conditions verified; weekly awards, verified records and 50 additional analysis scenarios are implemented; deeper depth-chart, NIL and transfer stories remain.
3. Event detection, persistent authors, editable templates and native avatar routing are separate components.
4. Expanded catalog reaches the initial target with 339 variants, including more player/fan perspectives and replies.
5. Two-week template cooldown preferences, stable same-week selections/admission order, account/voice caps, reply dependencies and complete curated conversation blocks are implemented. Multiweek in-game tuning remains.
6. First pack verified live as v50 with 65 tests. The v63 build passes 95 Node tests plus native checks, and the user verified its 30/100/60 feed sizes, likes order, replies, filters and scrolling. The v64 MMC adapter adds startup waiting and package tests. Longer rollover testing and historical-edition restoration remain.

Publication week remains the single week filter. For You selects up to 30 with soft 35/25/40 scope targets and no filler to hit quotas. National displays up to 100 and each native conference up to 60 after category filtering. Views sort parent threads by likes, with replies attached. The underlying dedicated story catalog remains complete.

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
