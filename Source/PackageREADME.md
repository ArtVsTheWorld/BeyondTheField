# Dynasty Enhancer — MMC prototype v68

This package adds preseason coverage and startup/phase-transition corrections to the verified Social Media feature set. It is a development prototype, not Dynasty Enhancer 1.0. Player Analytics and Roster Fog have not yet been merged into it.

## Install and use

1. Close MMC and the game. Copy this package's complete `Plugins` folder into the folder containing the MMC executable, merging folders.
2. Keep both parts: `Plugins/DynastyEnhancer.dll` is the managed MMC adapter; `Plugins/DynastyEnhancer/Runtime-v68/` contains the native game DLL, loader, generator and content.
3. Node.js must be installed. The runtime's `dynasty-enhancer.json` contains its executable path; update that path if Node is installed elsewhere. The exporter path should remain `Tools/export_runtime.mjs`.
4. Open MMC and launch College Football 27 normally. Open or create an offline Dynasty immediately; there is no fixed title-screen delay. The adapter loads the runtime once per game process and installs verified menu hooks before the first hub is constructed. Native UI readiness is separate from feed generation: the page can display its status card while the first two stable observations are collected. Reopening adopts the newest edition. Before native assets are ready, entry uses the game's inert action rather than leaving a pending navigation transaction.

You do not need to manually run the loader or save your Dynasty to publish news. Reopening Social Media adopts the latest stable weekly/midweek edition. For You shows up to 30 posts, National 100 and each conference 60, sorted by parent likes with replies attached. Team feeds keep their existing capacity.

The old standalone native `DynastyEnhancer.dll` does not belong directly in MMC's `Plugins` folder. Replace it with this package's MMC adapter. Do not enable multiple Social Media/Dynasty Enhancer loaders together. To disable this loader, close MMC/game and rename the top-level adapter to `DynastyEnhancer.dll.disabled`.

## History and diagnostics

Account identities and publication history are stored in `Plugins/DynastyEnhancer/Runtime-v68/RuntimeHistory`. Keep this folder when updating. Existing development history can be copied into it while the game is closed; the installer supports checksum-verified history migration. ZIP packages intentionally contain no user history, Dynasty saves or extracted game assets.

- MMC launch status: `Plugins/DynastyEnhancer-launcher.log`.
- Game startup, UI hooks and feed publication: `Plugins/DynastyEnhancer/Runtime-v68/social-media.jsonl`.
- Generator errors: `Plugins/DynastyEnhancer/Runtime-v68/runtime-generator.log`.

`startup_waiting` at the title screen or during loading is expected. `active` followed by `runtime_feed_published` confirms native readiness and publication. `activation_failed` is a failure and should be reported with its reason. Unsupported game code or owned UI hooks are rejected. The mod reads Dynasty data and changes presentation only; it does not alter simulation outcomes or save structure.

The MMC adapter verifies packaged runtime/content hashes before loading. User configuration and history are editable and excluded from those hashes; changing protected content requires rebuilding its package manifest.

Preseason adds AP rankings, explicit Coaches comparisons, native preseason national/conference honors, season/opening-game outlooks, official hype, player camp posts, fan reactions, top-100 recruit watches, fictional title futures, schedule gauntlets, poll/model debates with replies, and conference talent maps. Real offers still require an observed native scholarship change. No game/system ratings appear in tweets. AP remains the primary public poll until a complete native CFP Top 25 is present; a fixed release week is not assumed. First-CFP movement never compares AP places with CFP places.

The phase-transition correction reacquires replaced native filter-model allocations using exact byte gates before entering News. Failed readiness checks complete through native no-action navigation; a late dropdown failure still supplies native page data so Back is preserved. The live reader uses the front-end service's actual CareerManager/database ownership, not the invalid neighboring-object offset used by the earlier prototype.

The week picker now includes stored earlier phases from the same Dynasty, controlled team and season: Preseason appears above regular-season Week 0, followed by later observed weeks. It always selects one edition and defaults to the active week. Earlier editions keep their exact published stories; changing weeks does not regenerate them. Future phases/weeks and other seasons/Dynasties are excluded. Save filenames are not identity keys.

On reload, a cached active edition can resume after the first internally verified native capture if its full normalized fact hash and content revision match exactly. New weeks, changed facts, rewinds and missing caches still use normal reconciliation and stable observations. Resuming does not rewrite history or reroll wording/likes. Initial native context validation can still briefly show the preparing status; `runtime_feed_resumed` identifies a successful cache restoration in the log.
