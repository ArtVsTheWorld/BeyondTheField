# **November 17 Update**

## **Update 2 Hotfix 5**

**Recruiting Cards**
- Corrected Recruit Feedback labels on full recruit cards to use the full interest values, including the darker bar segment.
- Added the total scholarship-offer count beside the Offer heading. Blind keeps that count hidden.
- Corrected the Locked Out divider and row shading to follow your school's actual lockout flag, even when its interest rank falls outside the stage cutoff. Feedback sorting keeps the other schools' original cutoff membership. Recruiting rules and actions stay unchanged.

**In-Game Ratings**
- Fixed Attributes card ratings that stayed numeric for WRs, linemen and other positions with shortened or different attribute names. Roster Fog now follows the verified rating fields when you change players or flip card pages; the statistics table stays numeric.

**Testing**
- Automated regressions passed for the display fixes, existing Notes, grades, currency and menu discovery. The new lockout-divider behavior still needs an installed-game visual check.

**Install**
- Close MMC and the game, then update to **1.0.46** in Dynasty COT or replace **BeyondTheField.dll** in your usual MMC **Plugins** folder. Settings, saved Notes, accounts and published history carry forward.

---

# **November 17 Update**

## **Update 2 Hotfix 4**

**Game Update Compatibility**
- Restored Beyond the Field on the November 17 game update, including Social Media, recruiting, roster grades and GPI.

**Recruit Notes**
- Moved Notes higher on the card and split the write-up into bulleted Background and Scouting Notes sections. Previous-season stats and position history stay on the card.
- A fully scouted high school or JUCO recruit gets one background note. The note stays the same when you reopen the card. Transfers skip this section.
- Athletic Measurables now appear in their own section as plain estimates. Added the 10-yard split and made room for all seven measurements at 100% scouting when the ratings needed to calculate them can be verified. Partial scouting and Blind rules still apply.

**Ratings & Social Media**
- Fixed numeric ratings in the Attributes panel of the in-game Player Stats card. The stats table still shows its original numbers.
- Improved GPI roster navigation matching for supported menu layouts and input variants.
- Uncommitted recruits now use the default jersey in new Social Media portraits. Previously published posts and saved scouting reports stay intact.

**Install**
- Close MMC and the game, then update to **1.0.43** in Dynasty COT or replace **BeyondTheField.dll** in your usual MMC **Plugins** folder.

---

# **Update 2 Hotfix 3**

**Ratings & Menu Compatibility**
- Improved matching across supported UI overhauls, including menus whose methods have moved
- Fixed missing Recruit Notes on the first visit and rating leaks in player cards, NIL rows and Weekly Practice Plan team banners
- Keeps each UI mod's native layout, money formatting, sorting and player data
- Unsupported modified menus remain protected by compatibility checks

**Menu Responsiveness**
- Reduced repeated adapter work when opening, closing and navigating roster screens, player cards and other Dynasty menus
- Offline callback tests show substantially lower overhead; whole-menu input delays still need confirmation on each setup

**Recruiting & Saved Data**
- Fixed precise interest labels and progress bars showing through Recruit Feedback on supported modified menus
- Keeps manual Recruiting Board position numbers and native visibility for special recruit states
- Preserves settings, Notes, accounts and published history, including the earlier startup and long-path fixes

**Install**
- Close MMC and the game, then replace **BeyondTheField.dll** in your usual **Plugins** folder, or select **1.0.32** in the COT installer after its version check
- Keep existing data folders. No reset or history clearing is needed


---

# **Update 2 Hotfix 2**

**Startup & Saved Data**
- Fixed the confirmed missing-path error caused by deeply nested MMC and legacy history folders
- Improved preparation of runtime files, settings and logs when folder paths are long
- Improved startup checks for runtimes loaded from long folder paths
- Keeps saved settings, Recruit Notes, accounts and published Social Media history

**Install**
- Close MMC and the game, then replace **BeyondTheField.dll** in your usual **Plugins** folder, or select **1.0.26** in the COT installer
- Keep your existing data folders. This fixes the reproduced long-path failure; genuinely missing, unavailable or blocked files still need their own diagnosis


---

# **Update 2 Hotfix**

**More Reliable Startup**
- Fixed a startup issue that could leave Social Media or recruiting/fog inactive when Windows was still updating the game's loaded-file list.
- Fixed the same check reporting a startup failure even when the runtime had already loaded successfully.
- Retries are brief and limited to checking that list. The plugin does not repeat an uncertain runtime load.

**Clearer Error Details**
- Startup logs now name the affected BTF component, the step that failed and the Windows error code.
- Settings, Recruit Notes, accounts and published Social Media history are kept.

**Install**
- Close MMC and the game, then replace **BeyondTheField.dll** in your usual **Plugins** folder. COT users can explicitly check for updates and choose **1.0.25** for BTF only.
- The private build completed a clean live startup with both runtimes verified and Social Media ready. Broader intermittent-startup testing remains ongoing.
- The separate **"Could not find part of the path"** reports are still under investigation pending logs; this hotfix does not claim to resolve them.


---

# Aceâ€™s Beyond the Field 1.0.24

Changes since public release 1.0.7.

- Set separate rating styles for recruits, roster players and teams. Use workout estimates or change how a recruit's interest looks even when Recruiting Fog is off.
- Recruit Notes now give shorter, position-specific scouting observations. New backgrounds better fit each player's workload and can give two-way athletes a second role. Existing Notes keep what you learned.
- Signing stories follow the school the recruit joined. Fans and school accounts respond to the matchup, repeated preseason stories show up less often, and spring exhibitions stay separate from fall coverage.
- Season GPI now matches the weekly grade for a player with one graded game. More depth charts, hub comparisons and supported Dynasty Extensions reports and drills follow your fog choices.
- Settings, Notes, accounts and published editions share one folder across MMC copies on the same Windows account. In a league with several coaches, the verified view is still the owner's school.

Download the standalone ZIP, close MMC and the game, and copy **BeyondTheField.dll** into MMCâ€™s **Plugins** folder. The ZIP includes a full feature list and an illustrated player guide.


---

# Beyond the Field 1.0.7 â€” Recruiting feedback and GPI

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
