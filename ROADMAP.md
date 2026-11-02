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
4. Expanded catalog reaches the initial target with 277 variants, including more player/fan perspectives and replies.
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
