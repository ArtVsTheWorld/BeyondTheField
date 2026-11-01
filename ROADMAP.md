# Dynasty Enhancer roadmap

## Current prototype: native Dynasty lifecycle

- Active Dynasty and controlled program read from runtime tables instead of a configured save.
- Stable editions published after regular-season week advancement, with a live Week 8 → Week 9 rollover verified.
- Midweek scholarship offers verified in the native feed; commitments, injuries/recovery, and current-week results share the same publication path.
- Deterministic IDs, scoped history, and fixture coverage for identity changes, earlier-week loading, and replay with different outcomes.
- Native menu/controller behavior retained; simulation access remains read-only.

Before broader release, validate active-Dynasty switching, an actual older-save restore/replay, offseason/year transitions, and cold launch. The runtime observer currently waits for stable state rather than hooking the native advance-completion callback.

## Current content work: new voice foundation

Step 1 now has six voice guides, a native personality policy, and thirty new review drafts. All former tweet wording and the original sample cards are retired on this branch. Drafts are unapproved and excluded from runtime; event detection remains available as structured facts.

Next, revise the voices from user feedback, build the verified condition matrix, and implement the new author/template renderer. Then expand the approved catalog, repetition controls, and curated publication. Depth-chart status, transfer risk, NIL, awards, and broader postseason stories need their data conditions verified before publication. Preserve single publication-week filtering and complete dedicated scopes.

## Planned 1.0 integration

1. Native Social Media with active-Dynasty and week/midweek lifecycle support.
2. Existing player analytics grades mod, integrated as a component.
3. Existing ratings fog-of-war mod, replacing numerical player-rating displays throughout the UI with less granular information.

The analytics and fog-of-war components are planned integrations, not included in this baseline. Version 1.0 follows integration and validation of all three. The product goal is more convincing Dynasty context and presentation without structural changes to Dynasty data or altered simulation outcomes.
