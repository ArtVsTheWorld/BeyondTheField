# Dynasty Enhancer

Dynasty Enhancer improves the offline College Football 27 Dynasty experience through worldbuilding, context, and realism. It uses native game menus and presentation changes without restructuring Dynasty data or changing simulation outcomes.

This is a development prototype, not the planned 1.0 release.

## Editorial reset: Step 1

This branch starts the Social Media writing from scratch. The original three illustrative cards and all prior authored runtime tweet wording have been removed. `Tools/story_events.mjs` retains the verified event facts and conditions. `Tools/feed_engine.mjs` currently publishes zero authored stories with `contentStatus: drafting`; only system status/empty-state rows remain available to the native UI. Draft writing is not a production template pack.

The user selected grounded college-football Twitter, all six account types, fictional media/fan accounts, personality-led player/recruit voices, secondary position influences (usually more restrained QBs), and no numerical ability values or game-system language in posts.

- `Content/Editorial/voice-guide.json`: six voice guides, writing boundaries, native personality mapping, and position guidance.
- `Content/Editorial/review-samples.json`: thirty new independent review scenarios, five per voice, all unapproved for runtime.
- `Tools/render_voice_review.mjs`: creates a readable local review page. Run `node Tools/render_voice_review.mjs`, then open `Build/voice-review.html` and give feedback by post ID.

The native `Player.Personality` field was verified read-only and added to this branch's capture/normalization path: Leader, Intense, Entertainer, TeamPlayer, and Unpredictable. The prose associations are editorial proposals, not measured psychological rules. Position is a secondary influence. Missing/sentinel personalities normalize to null. Personality labels, codes, and internal values never appear in the review posts.

Review 03 uses short, punchy team captions; varied lengths across the other voices; and more natural player, recruit and fan phrasing. PLAYER-04 now celebrates a teammate without a box-score speech. The specific 42-point example has been removed. Analyst examples include a measured red-zone touchdown rate, with additional opportunities documented in `Content/Editorial/analyst-opportunities.json`. Emojis stay disabled pending a native font visual check. Current-coach references, natural position-free handles and personality-led voices remain. The recruiting phone call is authored worldbuilding around a verified commitment and coach identity, not native contact telemetry. Run the renderer and open `Build/voice-review-03.html` or the latest `Build/voice-review.html`.

`Tools/team_analytics.mjs` computes rushing yards per game/rank, weighted third-down percentage, red-zone touchdown rate, turnover margin, and a unique season-largest winning margin derived from actual results. It prefers current-first native season totals corroborated by published scorecard W/L/T or matching team records, with complete validated game caches as an alternative. National ranks and superlatives require full eligible-field coverage.

The read-only Week 9 audit reconciled 138 FBS programs and 511 published finals. Rushing, third-down and red-zone season totals match their game caches for every eligible program; all inspected published quarter-score splits plus overtime sum to the finals. Some CPU games already contain final scores before publication. The new reader captures `HasBeenPublished`, and normalization excludes unpublished results, quarter splits and player performance from public facts. Some separate team record counters lag; published scorecards and current-season totals provide corroboration. No live DLL was replaced for this audit.

The historical live v47 build and its published archives remain available at tag `prototype-active-dynasty-v47`. This isolated content worktree has not replaced the currently loaded DLL. The remaining sections describe that verified native UI/data foundation; story publication on this branch resumes only after the replacement content and renderer are implemented.

## Current component: Social Media

A Social Media button in the CFB tab opens a native vertical feed with opaque tweet cards, account images, adaptive card heights, smooth controller scrolling, and two native dropdowns. LT chooses All Posts, National, Conference, or My Team. RT selects one publication week, oldest to newest; the active week is the default. All Posts uses a curated mix with soft targets of 35% national, 25% conference, and 40% team news. Dedicated views expose all qualifying stories.

Stories include previous-week results and performances plus current-week rankings, Heisman news, matchups, recruiting, injury reports, and calendar items. Publication week governs the edition even when the event occurred the week before. Betting lines are fictional generated game content.

**Active-Dynasty candidate:** the DLL reads the loaded career session and packed runtime tables without invoking native table methods or writing game data. A background observer checks roughly every three seconds, rejects inactive/advancing stages and changing captures, and requires two matching captures before generation. New weeks create editions; midweek offers, commitments, injuries/recovery, and completed games update the current edition. This detects native runtime changes; it does not hook the advance callback. Reopen the page to adopt the latest immutable feed.

The read-only capture has been compared with the save reader: all 122 generated story bodies, categories, and avatar selections matched in the inspected Week 8 snapshot. Automated lifecycle tests cover rollover, unsaved midweek events, deduplication, rollback, and identity isolation. The user verified the live Week 8 feed, USC recap, both dropdowns, and scrolling. The user also verified three midweek scholarship posts after the native `New` status fix, without manually saving. The game did autosave during the recruiting session; the DLL itself reads runtime memory. The subsequent Week 8 → Week 9 advance also passed: Week 9 was selected automatically, all 153 generated story bodies/categories/avatar choices matched the diagnostic save reader, and the three offer posts remained in the Week 8 archive without repeating in Week 9. Unsupported runtime layouts remain unavailable rather than reading a configured save as a silent fallback.

The preserved save-backed UI build is tagged `social-media-v45-baseline`.

## Build

Windows x64, Visual Studio C++ tools, and Windows SDK are required. From the project root:

```powershell
.\Source\build.ps1
```

This builds `Build/DynastyEnhancer.dll`, `Build/LoadDynastyEnhancer.exe`, `Build/LiveCapture.exe`, and runs the native tests. Both native dropdowns and the read-only feed are enabled by default. Generated native UI patch headers are included; no extracted game assets are required to compile. Native bindings are build-specific and reject unsupported code/asset layouts.

Node.js is required for the story generator. Copy `Config/dynasty-enhancer.example.json` to `Build/dynasty-enhancer.json` and set the Node executable path if needed. The active-Dynasty reader needs no save path, parser, or external schema. Generated snapshots, feeds, and publication history live beside the DLL under `Build/` and are not game saves.

The legacy save adapter remains as a diagnostic comparison tool: `Config/social-refresh.example.json` documents its external dependencies. It is not the candidate DLL's data source.

```powershell
node --test Tests/feed_engine.test.mjs Tests/feed_selection.test.mjs Tests/runtime_lifecycle.test.mjs Tests/runtime_recruiting.test.mjs Tests/editorial_content.test.mjs Tests/team_analytics.test.mjs
Build/LiveCapture.exe <PID> Build/runtime-raw.json
node Tools/export_runtime.mjs Build/runtime-raw.json Build/runtime-feed.json
```

For development, load with `Build/LoadDynastyEnhancer.exe <PID> <absolute-DLL-path>`. Stop with the same arguments plus `--stop`, after returning from Social Media to the CFB hub. The stop guard refuses replacement while the Social Media page is open. Use a fresh DLL filename for another candidate in the same process; stopped modules remain pinned. This repository does not install an automatic loader.

## Roadmap and provenance

See [ROADMAP.md](ROADMAP.md) for the planned 1.0 scope. [docs/verified-v45.json](docs/verified-v45.json) records the verified predecessor and the minimal packaging changes made here. Saves, generated feeds, extracted assets, and local runtime configuration are deliberately excluded from version control. See [docs/runtime-lifecycle.md](docs/runtime-lifecycle.md) for capture, publication, and validation details.

Third-party JSON code retains its MIT license; see [Vendor/json.LICENSE.txt](Vendor/json.LICENSE.txt). A license for the original project code has not yet been selected.
