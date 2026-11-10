# Beyond the Field by Ace

A standalone suite for **offline Dynasty**. No other COT module is required.

## Social Media

- A feed follows captured results, rankings, recruiting, awards, transfers, coaching, conference changes, draft results and other supported Dynasty developments.
- Reporters, analysts, official teams, fans, players and recruits have persistent accounts and different voices. Replies engage with the parent story; stories do not all need replies.
- Browse For You, National, conference, team and topic categories. Choose a past weekly edition to revisit published posts.
- For You favors user programs and selected major national news. National displays up to 300 cards. Routine team coverage has a 15-root-post budget, with important-news protections; replies and recruit statlines have separate treatment. More wording choices do not mean more weekly posts.
- Recruiting posts can include persistent mod-generated high-school game/film records. These are scouting clues, not native game records or reliable development-trait reveals. The mod does not overwrite native player ratings or development traits with those results.
- Casual chatter, rival reactions, seasonal posts and guarded pre-2026 references add variety when their facts/date context qualify. Sparse data uses factual fallbacks.
- GPI (@GPIndex) posts can cover verified mod grades, positional leaders and qualifying weekly individual/team performances. Gridiron Performance Index is a fictional account using mod-calculated grades from tracked Dynasty statistics.
- Accounts and published wording/history survive updates. Refreshing the same edition does not reroll the feed. The 1.0.2 generator hotfix prevents a missing personal-account identity from stopping the rest of the feed.

## Scouting and recruiting

- Separate Recruiting Fog, Roster Fog and Team Fog choices control how much exact rating information is shown inside Dynasty.
- Recruiting Fog includes Default (initial choice), Recruit Feedback and Rank Only interest displays. Feedback uses relative standing words, allows tied tiers, groups schools without exact ranks and preserves movement arrows. Blind hides interest; switching fog off restores the native view.
- Recruit Feedback and Blind remove the misleading Projected Cutoff divider. Default and Rank Only retain it. Actual lockout notices and the game's cut/advancement rules are preserved.
- A scouting-progress icon appears in the Target column for previously scouted prospects who are off your board and uncommitted. It uses tracked scouting progress, refreshes after scouting/removal and preserves prospect names and protected native icons. This quality-of-life feature has no toggle.
- Recruiting Notes collect a recruit's developing evaluation in the supported native UI.
- Roster fog extends to supported small and full player-card rating displays. Main-menu and Play Now displays keep native ratings.
- No native ratings, simulation outcomes or development traits are changed by the presentation fog.

## Rating and money displays

- Choose ordinary letter grades, A+/A/A- grades, S-tier grades or descriptive words such as GOOD and ELITE. The supported Blind option hides exact grades further. Player and team style choices are independent.
- Optional rating colors help distinguish grades. Colors off retains native display colors. Descriptive words are capitalized and fitted to supported rating circles.
- Supported player-card Ratings buckets keep their selection highlight, formatted attributes and matching rating bars without exposing the underlying numbers between bucket changes.
- Projected overalls in Position Changes follow the player grade and Roster Fog choices. Position-change calculations, sorting and player counts remain native.
- Optional compact dollar labels show readable $K/$M values in supported recruiting, offers, NIL, budgets and player-card displays, including edited/redrawn values. Numeric editing values and sorting data remain numeric.
- Defaults: Social Media and the three fog options On; A+/- grades; colors and dollar formatting Off. Choices are saved by Dynasty rather than copied globally to every save.

## Player Analytics

- Browse a selected team's weekly and season performance grades, snaps and player cards in the native UI. The National Analytics list and nonworking Player Stats shortcut are intentionally omitted.
- Only completed weeks appear: Week 0 becomes available in Week 1. Season combines the completed weeks, excluding the current unfinished week.
- Position-appropriate mod grades use the statistics the captured Dynasty actually provides. Available evidence, sampling and program prestige affect uncertainty; these are estimates rather than official film grades.
- Open a player's full card and return to Analytics. Supported card attributes/abilities respect roster fog. No underlying native player rating is replaced by an analytics grade.

## Limits and compatibility

- Offline Dynasty only. This does not add online Dynasty support or change Play Now gameplay ratings.
- Targeted AIO 1.4.1/TeamBuilder adapters are included, but other game/overhaul versions still need their own live checks. Unknown hook owners/layouts are not overwritten.
- Use one Beyond the Field provider. Remove the older standalone Analytics/Enhancer DLLs, or use COT's copy instead. Keep all data folders.
- Current Extra Settings, Expanded Practice and Gameday Atmosphere retain their existing native compatibility contracts. Mixed older versions can fail those checks.
- The standalone embeds its generator, native engines and required Node/notices. It prepares verified files outside the recursive Plugins DLL scan; no separate dependency download is required.
- The 1.0.2 standalone was reported working on November 9, 2026. The 1.0.3 Position Changes correction was confirmed with a targeted live adapter; the packaged update still needs its own clean-launch performance check. Other game/overhaul combinations need their own live checks.

## Release verification and limits

- Startup now waits for verified native settings code instead of permanently stopping if injected while the game is initializing. It requires two stable preflight checks, rejects unknown hook owners and times out after a bounded wait. Ace installed 1.0.6, restarted MMC/game and reported it working; this release retains that startup adapter.
- The user confirmed left-aligned full Overview standings, immediate off-board 100% scouting-icon refresh and the small Prospect List card interest display with temporary live adapters.
- The cutoff adapter now targets the verified native Top Schools list population method and removes only its Projected Cutoff item in Feedback/Blind. Isolated tests cover all four modes, repeated redraw, school-row identity, retained lockout notices and malformed provider counts. Ace reported the clean-installed 1.0.6 build working.
- 1.0.7 changes only the initial interest preference and its Default label after that 1.0.6 test. Saved preferences retain their numeric IDs and values. Save/reload, another Dynasty and other overhaul versions still need their own live checks. Full Overview header progress hiding remains a live-review item.
- Windows recorded a graphics timeout and game hang in an earlier test session. This does not establish whether the mod contributed; stability acceptance remains open.
