# Dynasty Enhancer

Dynasty Enhancer improves the offline College Football 27 Dynasty experience through worldbuilding, context, and realism. It uses native game menus and presentation changes without restructuring Dynasty data or changing simulation outcomes.

This is a development prototype, not the planned 1.0 release.

## Current component: Social Media

A Social Media button in the CFB tab opens a native vertical feed with opaque tweet cards, account images, adaptive card heights, smooth controller scrolling, and two native dropdowns. LT chooses All Posts, National, Conference, or My Team. RT selects one publication week, oldest to newest; the active week is the default. All Posts uses a curated mix with soft targets of 35% national, 25% conference, and 40% team news. Dedicated views expose all qualifying stories.

Stories include previous-week results and performances plus current-week rankings, Heisman news, matchups, recruiting, injury reports, and calendar items. Publication week governs the edition even when the event occurred the week before. Betting lines are fictional generated game content.

**Baseline limitation:** this checkpoint reads a configured save through a local parser and refreshes when that file changes. It does not yet follow the active in-memory Dynasty or generate from week-advance and midweek events. That connection is the next development milestone.

## Build

Windows x64, Visual Studio C++ tools, and Windows SDK are required. From the project root:

```powershell
.\Source\build.ps1
```

This builds `Build/DynastyEnhancer.dll`, `Build/LoadDynastyEnhancer.exe`, and runs the native tests. Both native dropdowns and the read-only feed are enabled by default. Generated native UI patch headers are included; no extracted game assets are required to compile. Native bindings are build-specific and reject unsupported code/asset layouts.

Node.js is required only for the current save-backed feed exporter. Copy `Config/social-refresh.example.json` to `Build/social-refresh.json`, supply your own local save/schema/parser paths and Dynasty identity, and use `Tools/export_feed.mjs` to create `Build/social-feed.json`. The external save parser/schema are not distributed here.

```powershell
node --test Tests/feed_engine.test.mjs Tests/feed_selection.test.mjs
node Tools/export_feed.mjs Build/social-refresh.json Build/social-feed.json
```

For development, load with `Build/LoadDynastyEnhancer.exe <PID> <absolute-DLL-path>`. Stop with the same arguments plus `--stop`, after returning from Social Media to the CFB hub. The stop guard refuses replacement while the Social Media page is open. Use a fresh DLL filename for another candidate in the same process; stopped modules remain pinned. This repository does not install an automatic loader.

## Roadmap and provenance

See [ROADMAP.md](ROADMAP.md) for the planned 1.0 scope. [docs/verified-v45.json](docs/verified-v45.json) records the verified predecessor and the minimal packaging changes made here. Saves, generated feeds, extracted assets, and local runtime configuration are deliberately excluded from version control.

Third-party JSON code retains its MIT license; see [Vendor/json.LICENSE.txt](Vendor/json.LICENSE.txt). A license for the original project code has not yet been selected.
