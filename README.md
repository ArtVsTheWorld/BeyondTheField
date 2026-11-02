# Dynasty Enhancer

Dynasty Enhancer improves the offline College Football 27 Dynasty experience through worldbuilding, context, and realism. It uses native game menus and presentation changes without restructuring Dynasty data or changing simulation outcomes.

This is a development prototype, not the planned 1.0 release.

## Social Media writing: first generation pack

The user approved the Review 03 writing direction and requested generation. `Content/Runtime/first-pack.json` now contains 180 prewritten variants across the six account types plus the fictional model-line account. `Tools/story_renderer.mjs` applies them to verified event facts; it never calls an online text model. The original three illustrative cards and prior prototype tweet wording remain retired. Editorial samples remain separate from the executable pack.

The first slice covers published results, player/team performances, polls, offers and new commitments, injuries, upcoming matchups, Heisman/CFP rankings, standings, calendar items and fictional model lines. Analysts use corroborated rushing rank, weighted third-down conversions, red-zone touchdown rate, turnover margin and season-largest margins. `Content/Editorial/analyst-opportunities.json` tracks deeper calculations still to implement. Mere ranking updates without analytic evidence use reporter accounts.

Official accounts use compact captions, native nicknames and occasional hashtags. Players normally post positive reactions; native personality leads, with secondary QB restraint. Players, recruits and fans vary punctuation and casual phrasing. Current-coach mentions require a real coach reference. Recruiting phone calls and personal reactions are authored worldbuilding around actual events. A persistent optional faith-language style is assigned independently of native personality/position, not presented as detected belief.

`Tools/story_conversations.mjs` adds bounded player/fan replies to actual parent posts; `Tools/story_templates.mjs` handles cooldowns and frozen selections. `Tools/story_authors.mjs` persists identity and collision resolution in runtime history. Recruiting-to-roster transitions and position, jersey or week changes retain the handle. Deterministic event/week choices keep existing wording stable during unrelated midweek updates. Missing slots suppress the variant. Bodies must fit 280 Unicode code points and the existing native 512-byte budget, without truncating factual values. All Posts caps repeated template forms, account frequency and voice repetition. Complete parent/reply blocks can now appear there while retaining the 20-post limit and scope mix. Dedicated scopes keep qualifying facts and conversations together. Player congratulations require a real recruit post; a scholarship offer never triggers commitment/welcome language. Team posts tag persisted athlete handles. Cross-week template choices prefer phrases that account has not used in the previous two weeks, with a least-recent fallback when all valid wording is cooling down. Same-week bodies and conversation admission order are persisted so unrelated midweek arrivals do not reroll or evict existing replies.

Native emoji testing is complete: the current tweet font showed missing-glyph boxes for every tested symbol/emoji, including football, fire, trophy, hands, flags and combined sequences. Ordinary text, accented Latin and punctuation rendered. Runtime emojis are disabled; decorative arrows use ASCII `->`. See `docs/native-font-check.json`. `Tools/export_emoji_probe.mjs` is an explicit development-only exporter with no history writes and is never the production exporter.

The read-only Week 9 data audit reconciled 138 FBS programs and 511 published finals. Rushing, third-down and red-zone totals matched the game caches for every program; all inspected quarter-score splits plus overtime matched their finals. Cached unpublished CPU scores are excluded from public news and player performances. Every future snapshot still passes validity/coverage checks.

The verified first-pack source is on `content/voice-foundation`, with the conversation expansion on `content/conversations`; generated previews are under Build. The historical live v47 source, DLL and archives remain available at tag `prototype-active-dynasty-v47`. The replacement generator starts its own observed publication history; it does not rewrite the old prototype editions or re-use their wording. Its first observed week is the active week. The candidate compiled and passed local checks. v49 loaded in-game and published 168 Week 9 posts (20 curated); native cards, account logos and vertically scrolled posts were observed. Checking the native Heisman panel exposed zero-based candidate places; the adapter now converts them to displayed ranks, retains the leader and treats -1 as unknown prior place. All 65 tests pass. The corrected v50 generator publishes 169 posts, including the previously omitted leader. The user verified the corrected Heisman rank, fitting text, My Team filter and controller scrolling in-game. The temporary emoji DLL was stopped successfully.

## Conversation and portrait expansion

The new pack supports recruit welcomes from actual roster players, fan replies to players/reporters/analysts, teammate congratulations, and official accounts tagging athletes. All replies require an actual generated parent, inherit its scope and display the native Reply label. Generation limits keep reactions from turning into automatic walls of replies. Two persistent fan accounts per school and additional analyst identities provide room for different voices without changing existing handles.

Portrait routing now uses verified nonblank entries from native library 1 for players and recruits regardless of NIL status. This includes generated face portraits; all 5,040 native generic IDs were found in that library. `Content/Runtime/portrait-ranges.json` contains numeric availability ranges, no images or extracted assets. The reader captures `PortraitForceSilhouette`, and missing/blank/forced-silhouette cases fall back to the team logo. In-game image/layout verification for this candidate is pending.

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
node --test Tests/feed_engine.test.mjs Tests/feed_selection.test.mjs Tests/runtime_lifecycle.test.mjs Tests/runtime_recruiting.test.mjs Tests/editorial_content.test.mjs Tests/team_analytics.test.mjs Tests/story_generation.test.mjs Tests/conversations.test.mjs
Build/LiveCapture.exe <PID> Build/runtime-raw.json
node Tools/export_runtime.mjs Build/runtime-raw.json Build/runtime-feed.json
```

For development, load with `Build/LoadDynastyEnhancer.exe <PID> <absolute-DLL-path>`. Stop with the same arguments plus `--stop`, after returning from Social Media to the CFB hub. The stop guard refuses replacement while the Social Media page is open. Use a fresh DLL filename for another candidate in the same process; stopped modules remain pinned. This repository does not install an automatic loader.

## Roadmap and provenance

See [ROADMAP.md](ROADMAP.md) for the planned 1.0 scope. [docs/verified-v45.json](docs/verified-v45.json) records the verified predecessor and the minimal packaging changes made here. Saves, generated feeds, extracted assets, and local runtime configuration are deliberately excluded from version control. See [docs/runtime-lifecycle.md](docs/runtime-lifecycle.md) for capture, publication, and validation details.

Third-party JSON code retains its MIT license; see [Vendor/json.LICENSE.txt](Vendor/json.LICENSE.txt). A license for the original project code has not yet been selected.
