# Dynasty Enhancer — MMC prototype v64

This package adds MMC startup support to the verified v63 Social Media feature set. It is a development prototype, not Dynasty Enhancer 1.0. Player Analytics and Roster Fog have not yet been merged into it.

## Install and use

1. Close MMC and the game. Copy this package's complete `Plugins` folder into the folder containing the MMC executable, merging folders.
2. Keep both parts: `Plugins/DynastyEnhancer.dll` is the managed MMC adapter; `Plugins/DynastyEnhancer/Runtime-v64/` contains the native game DLL, loader, generator and content.
3. Node.js must be installed. The runtime's `dynasty-enhancer.json` contains its executable path; update that path if Node is installed elsewhere. The exporter path should remain `Tools/export_runtime.mjs`.
4. Open MMC and launch College Football 27 normally. Open or create an offline Dynasty. The adapter loads the runtime once per game process; the runtime waits for the supported active Dynasty and its native UI assets before installing its hooks. Allow roughly 10–20 seconds after the hub appears, then open CFB → Social Media. If needed, switch away from CFB and back once to refresh a cached hub menu.

You do not need to manually run the loader or save your Dynasty to publish news. Reopening Social Media adopts the latest stable weekly/midweek edition. For You shows up to 30 posts, National 100 and each conference 60, sorted by parent likes with replies attached. Team feeds keep their existing capacity.

The old standalone native `DynastyEnhancer.dll` does not belong directly in MMC's `Plugins` folder. Replace it with this package's MMC adapter. Do not enable multiple Social Media/Dynasty Enhancer loaders together. To disable this loader, close MMC/game and rename the top-level adapter to `DynastyEnhancer.dll.disabled`.

## History and diagnostics

Account identities and publication history are stored in `Plugins/DynastyEnhancer/Runtime-v64/RuntimeHistory`. Keep this folder when updating. Existing development history can be copied into it while the game is closed; the installer used for this test preserves the existing v63 history. ZIP packages intentionally contain no user history, Dynasty saves or extracted game assets.

- MMC launch status: `Plugins/DynastyEnhancer-launcher.log`.
- Game startup, UI hooks and feed publication: `Plugins/DynastyEnhancer/Runtime-v64/social-media.jsonl`.
- Generator errors: `Plugins/DynastyEnhancer/Runtime-v64/runtime-generator.log`.

`startup_waiting` at the title screen or during loading is expected. `active` followed by `runtime_feed_published` confirms native readiness and publication. `activation_failed` is a failure and should be reported with its reason. Unsupported game code or owned UI hooks are rejected. The mod reads Dynasty data and changes presentation only; it does not alter simulation outcomes or save structure.

The MMC adapter verifies packaged runtime/content hashes before loading. User configuration and history are editable and excluded from those hashes; changing protected content requires rebuilding its package manifest.
