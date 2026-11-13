## Private candidate 1.0.23 (not published)

# BeyondTheField 1.0.23

Changes since public 1.0.7

- Choose separate grade scales for recruiting, rosters and teams, including Off and Blind
- Use optional Athletic Measurables and interest-display choices independently of Recruiting Fog
- Recruit Notes load more reliably and offer shorter, more varied observations, coherent ATH secondary roles and improved new prospect backgrounds
- Previously saved Notes keep their data while technical labels are hidden; compact transfer labels retain year and redshirt status
- Confirmed signing news now follows the actual signing school, including recruits whose interest list still names another leader
- Fans and official accounts have more personality, clearer rivalry references and cleaner grammar; unchanged preseason stories and milestone repetition are reduced
- Social Media reuses unchanged work and handles available historical editions more efficiently without increasing weekly post budgets
- GPI Season matches the weekly grade when a player has only one graded game
- Fog covers additional depth-chart, hub and supported Dynasty Extensions report/drill displays; money formatting and navigation fixes remain
- Settings and history move safely to shared AppData, helping installs in protected folders

Full multi-coach active-school selection and private Notes ownership remain unsupported outside the verified Owner-school perspective. Saved backgrounds are not rerolled. Installed-menu acceptance is still required.

Install or update: close MMC/game, back up the previous DLL and replace it in Plugins. Keep settings and history. Restore that DLL to roll back.

---

# Beyond the Field 1.0.7 — Recruiting feedback and GPI

Changes since the published 1.0.3 release:

- **Choose how recruit interest looks.** Default keeps the normal game display and is the initial choice. Recruit Feedback replaces exact interest bars/rank numbers with broad standings: Favorite, Contender, In the Mix, Outside Looking In and Long Shot. Schools are grouped by standing, then alphabetically within a group; multiple schools can share a tier. Existing movement arrows remain. Rank Only hides the bars but keeps real rankings. Recruiting Fog must be enabled; Blind hides interest altogether.
- **Find prospects you already scouted.** Off-board, uncommitted prospects show their scouting-progress icon in the Target column. It updates after further scouting/removal without needing to flip pages. Names, active-board markers and commitment logos stay intact. This quality-of-life feature is always on.
- **Cleaner recruiting cards.** Full Overview labels align under Influence; Prospect List cards show the same broad standings instead of Interest Unknown. Recruit Feedback and Blind hide the misleading Projected Cutoff divider. Default/Rank Only retain it. Real lockout notices and the game's recruiting rules remain unchanged.
- **GPI branding.** Player Analytics and its fictional Social Media account now use Gridiron Performance Index (GPI), @GPIndex and the G icon. Grade calculations, completed-week restrictions and weekly feed budgets are unchanged. Existing account identities and published history are preserved.
- **More reliable startup.** BTF waits briefly for the exact supported native settings code instead of permanently stopping during early game initialization. Unsupported code/hook owners still fail safely.
- Keeps the Position Changes fix, edited Current NIL formatting, player-card fog/colors, capitalized grades and faster Back navigation. Settings, saves, accounts and published history stay in place. Saved interest choices are preserved; Default applies when no choice has been saved.

**Install/update:** close the game and MMC, then replace only BeyondTheField.dll in the versioned Mod Manager's Plugins folder. Keep all data folders. Use one BTF provider; disable bundled BTF in COT if using this standalone. Matching support files are embedded. To roll back, close MMC/game and restore your saved older DLL; retain settings/history.

**Verification:** Ace installed 1.0.6, restarted MMC/game and reported it working. 1.0.7 adds the Default preference/label change, verified with settings/menu/persistence regressions. Recruiting response, emitted UI, startup, native composition, existing-data and standalone/COT coexistence checks passed; integrity evidence ships beside the ZIP. Successful tests do not certify every game/overhaul combination.

**Known limits:** the full Overview header's stage-progress hiding remains a live-review item. An earlier Windows graphics timeout/game hang has unresolved causality; this release does not claim to fix it. Save/reload, multi-coach and other overhaul combinations need their own acceptance checks. No touchdown replay experiment is included.


---

## Earlier release notes

# Beyond the Field 1.0.3 - Position Changes fix

- Projected overall ratings on the Position Changes preview now follow your player grade style and Roster Fog setting, instead of revealing exact numbers.
- Position calculations, sorting, player counts and the normal selection highlight stay native. This changes the displayed text, not a player's ratings or position.
- The targeted fix retains the working NIL formatting, player-card Ratings fixes, capitalized descriptions and existing Back navigation.
- Your settings, saves, accounts, published posts and history stay in place. The Social Media generator crash fix from 1.0.2 is still included; content and weekly budgets are unchanged.

Close the game and MMC, then replace only `BeyondTheField.dll` in the versioned Mod Manager's Plugins folder. Keep the existing data folders. Matching support files are embedded and prepared automatically. Use one provider of Beyond the Field: disable the same module in COT if you use this standalone DLL.

Validation: the display correction was reproduced and confirmed in the live game on two players using a targeted adapter. The source-built native engine passed the existing menu/NIL/fog regressions, 10,123 focused projected-rating checks, 7,317 analytics-model checks, 2,491 analytics integration checks and native dispatch tests. The actual DLL passed 750 isolated standalone integration checks, including existing-data preservation and coexistence with the other three modules. Offline conversion work was reduced, but a noticeable live Back/reopen speedup was inconclusive. The packaged update still needs its own clean-launch performance check; offline tests do not certify every game or overhaul combination.

Compared with v1.0.2, this release changes the projected-position display adapter and embeds a newly source-built, matched native pair. The managed loader and user-data paths retain the established design. Roll back by closing MMC/game and restoring your saved 1.0.2 `BeyondTheField.dll`; keep all settings/history folders.

Gameday Atmosphere's experimental touchdown replay changes are not included in this release.


---

## Earlier release notes

# Beyond the Field 1.0.2 - first standalone release

This repository was previously named Dynasty-Enhancer. It had **no previous published GitHub release**. This is its first standalone release of the Beyond the Field suite; the old private prototype is not treated as a released version.

- **Dynasty Social Media:** persistent accounts, varied voices, relevant replies, historical editions, and supported results/recruiting/rankings/awards/offseason coverage.
- **Controlled feed size:** National displays up to 300 cards; routine team coverage stays budgeted while important news is protected. New wording choices do not increase the weekly post budget.
- **Player Analytics:** team-only weekly/season mod grades, snaps and player-card access. Only completed weeks contribute. These are mod-calculated PFF-style estimates, not official PFF grades.
- **Separate fog options:** Recruiting, Roster and Team Fog, Recruiting Notes, independent player/team grade styles, optional colors and compact $K/$M displays.
- **Current menu fixes:** native Dynasty scope, player-card buckets/highlight/bars, fitted capitalized descriptive labels, edited NIL/redraw formatting, targeted AIO currency adapters and the current Analytics return path.
- **Generator crash hotfix included:** restoring a saved personal voice with no direct player object no longer stops the entire feed. Published wording/history, identities, save data and settings are preserved.
- **One-DLL installation:** the plugin embeds its verified native engines, generator/content, Node runtime and notices. No separate Node install, helper download or other COT module is required.

New shipped runtime filenames use Beyond the Field branding, including `BeyondTheField.dll` and `beyond-the-field.json`. Old internal data-folder/contract IDs deliberately remain compatibility aliases so existing settings and published history continue to resolve. Existing user data is never renamed/deleted merely for branding.

Remove old `DynastyEnhancer.dll` and `PlayerAnalytics.dll` copies from Plugins, keeping their data folders. If using COT's other modules, disable its Beyond the Field module first. Main-menu and Play Now ratings remain native; this is an offline Dynasty suite.

Validation: 465 generator/content tests, the source-built native Social Media fixture, all-four packaging/coexistence/COT round-trip checks, and the 5,009-check shared practice contract passed. The native Social Media source changes only its configuration filename for this packaging; recruiting and the remaining runtime content/helpers retain COT 1.0.2 bytes. **Ace reported all four standalone releases verified working on November 9, 2026.** Other game/overhaul versions are not certified by offline checks.

Baseline: no previous release; old prototype source commit `32fe13eb04d4e29749455b2e5d06c16d38b08b7e`. Current maintained source is pinned in `source-release.json`. Checked additions/corrections include the Analytics native bridge/models, story renderer/author crash regression, publication/selection budgets, enhancement scope, money-label adapters and card UI programs. See FEATURES.md for the complete user-facing feature list.

Stable promotion: the ZIP and DLL are unchanged from the tested preview. Enclosed preview labels describe the build-time status. Acceptance is user-reported for the tested setup; other game/overhaul combinations are not automatically certified.
