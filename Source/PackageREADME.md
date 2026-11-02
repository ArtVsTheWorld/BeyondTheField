# Dynasty Enhancer - MMC prototype v73

Native Social Media inside the offline Dynasty CFB hub. This development prototype includes weekly/midweek news, archives, discovery filters and prewritten conditional stories. Analytics grades and ratings fog are not yet merged; this is not version 1.0.

## Installation

1. Close MMC and CFB. Copy the complete package `Plugins` folder into the folder containing MMC, merging folders.
2. Keep both parts: `Plugins/DynastyEnhancer.dll` is the managed MMC adapter. `Plugins/DynastyEnhancer/Runtime-v73/` contains the native DLL, loader, generator and content.
3. Node.js must be installed. Set its executable path in `Runtime-v73/dynasty-enhancer.json` if necessary. Keep the exporter path `Tools/export_runtime.mjs`.
4. Start CFB through MMC and open an offline Dynasty. No fixed title-screen wait is required. The first feed may briefly show Preparing News while two stable native observations are collected; reopening adopts the latest edition.

Do not enable multiple Dynasty Enhancer/Social Media loaders. The standalone native DLL does not belong directly in MMC's top-level Plugins folder. To disable this loader, close MMC/game and rename the top-level managed adapter to `DynastyEnhancer.dll.disabled`.

## Feed and controls

- LT selects For You, National, a native conference or a native team.
- RT selects one publication edition, with the active week selected initially and older editions listed first.
- LB/RB cycle topic/account categories in both directions. Recruiting includes recruit-written posts; Players remains separate. Injuries is a dedicated category. Official Accounts includes CFP.
- For You shows up to 30 posts, National 100 and a conference 60. Likes order parent threads; replies remain attached. Missing real candidates are not replaced with sample tweets.
- Saving is not required to publish news. New stable Dynasty/week/midweek observations drive publication.

## v73 changes

National analytics focus on the current poll's top 60; school beats retain the smaller-program analysis. Jake Whitmore, Marcus Bennett, Tina Brooks, David Ellison and Chris Maddox all receive regular-season stories, with distinct opinion/humor/evaluation wording. ESPNCFB remains a separate account.

Injury reports use native remaining-week ranges and severity/status. They do not subtract elapsed weeks twice or invent an exact date. Season-ending reports apply to the injury's current season; uncertain/undiagnosed cases retain appropriate uncertainty.

The CFP account (@CFBPlayoff) uses native image `dynas_stickers_CFP`. Its first three ranking posts begin at regular Week 10 when a complete native CFP Top 25 is available. AP remains primary before that point. The initial publication does not compare AP places with CFP places. Later reports cover CFP movement and contender discussion. Native playoff games and championship results drive postseason coverage; rankings alone do not establish a berth.

TeamBuilder fan/beat accounts use the primary logo because the alternate numeric slots displayed placeholders in the live test. Other native on-white, helmet, mascot and secondary bindings remain.

## History, diagnostics and limits

Preserve `Runtime-v73/RuntimeHistory` when updating. The installer supports checksum-verified migration. The ZIP contains no user history, saves or extracted game images. Archived facts/likes are retained; requested presentation migrations can update account artwork/names. Recovered skipped weeks contain only supported historical facts and are labeled. Recruiting gaps use explicit catch-up observations rather than assigning an unknown event week.

- MMC status: `Plugins/DynastyEnhancer-launcher.log`.
- Runtime/UI status: `Runtime-v73/social-media.jsonl`.
- Generator diagnostics: `Runtime-v73/runtime-generator.log`.

`active` and `runtime_feed_published` identify successful readiness/publication; `runtime_feed_resumed` identifies an exact cache match after reload. Unsupported native code, conflicting UI ownership, invalid catalogues and changed protected payloads are rejected. User configuration/history are editable; changing protected runtime/content files requires rebuilding the package manifest.

The mod observes Dynasty data and changes presentation only. It does not write simulation/save records or change save structure. Live postseason/year-rollover and fresh v73 cold-launch checks remain follow-up validation. See the source repository's `docs/playoff-desk-v73.md` for evidence and coverage details.
