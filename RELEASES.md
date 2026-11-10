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
