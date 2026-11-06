# Dynasty Enhancements settings

## Current candidate: options-p96

One MMC adapter loads the Social Media v103 runtime and the combined recruiting/player/team display runtime. The native payloads must be updated together: **options protocol 4** adds independent player/team scales and Blind. p96 is packaged for testing; these new options have not yet passed live acceptance. The preceding installed p92 build passed By the Numbers, budgets, pregame team selection and NIL spacing. Later recruiting money layout fixes are included in p96.

## Options and placement

The section is inserted immediately after Commissioner Settings. Native settings and other mods' Game Settings, Team Settings and Playoff Customization sections retain their row keys, types, fields and relative ordering. Buffering is limited to settings-page setup; late/out-of-order writes are remapped. If the Commissioner header cannot be recognized, the new section goes at the end.

| Setting | Default | Effect |
|---|---|---|
| Social Media Feed | On | Feed shortcut, entry and background news capture/generation. Off preserves archives. Re-enabling validates the active edition. |
| Recruiting Fog | On | Scouting grades/ranges and Playing Time masking. Notes, résumés and fictional JUCO labels remain when Off. |
| Roster Fog | On | Covered active-player rating displays. Edit Player ratings are intentionally excluded. |
| Team Fog | On | Covered team OVR/OFF/DEF badges, independent of player fog. |
| Player Grade Scale | A+- | A, A+-, S, Descriptive or Blind for recruiting and active players. |
| Team Grade Scale | A+- | The same five choices, independently for team ratings. |
| Rating Colors | On | Scale colors for grades or numerical ratings with fog Off. Native selected/disabled table contrast is preserved. Blind always keeps native colors. |
| Dollar Values | Off | Currency displays at 4,000 dollars per point, with symbol-free K/M text and native currency icons. Underlying points, sorting, budgets and negotiations stay numeric. |

The original private setting keys are preserved. Team Grade Scale uses a new key; its visual row follows Player Grade Scale. No other mod's DLL or setting keys are replaced.

## Scales

- **A:** A 90+, B 80–89, C 70–79, D 60–69, F below 60.
- **A+-:** minus at 0–2, plain at 3–6, plus at 7–9 within each passing decade; A+ is 97–100. F is below 60.
- **S:** the A bands, with S at 95+. S is blue.
- **Descriptive:** Elite 90+ / purple `#BB70EF`; Great 80–89 / blue `#529FF0`; Good 70–79 / green `#66CF75`; Fair 60–69 / amber `#EDB34F`; Poor below 60 / red `#EA6666`.
- **Blind:** en dash `–`, chosen because the native font already renders it in scouting ranges. No custom grade color is applied. Switching from another scale restores a tint previously owned by the mod while preserving a later native focus repaint. With fog Off, ratings remain numeric and use native colors.

Unknown scouting values stay hidden. Partially scouted attributes use only public low/high bounds, with midpoint-band color. Blind does not expose those bounds. Native coach boost/trend arrows remain attached to table grades, including boosts within the same grade band. Sorting/source values are unchanged.

## Persistence and migration

Profiles live under `Runtime-v103/DynastyEnhancementSettings/<LeagueID>.json`, outside game saves. Save filenames are not identity keys.

Format 1 used `gradeScale` (0–3). Its saved value initializes **both** new scales on load; existing choices are not reset to the new-profile default. Format 2 writes `playerGradeScale` and `teamGradeScale` (0–4). Missing legacy Team Fog/Colors/Dollar Values use their compatible defaults. Invalid types, out-of-range scales and mismatched identities are rejected without overwriting the source file.

The two native payloads share a process-local mapping with a versioned, validated bitset. Menu writes and feed entry verify the active LeagueID. Profiles are loaded/flushed by the worker; Draw/focus callbacks do not poll files. Pending edits remain associated with their old Dynasty after a failed write. A Dynasty switch cannot reuse another league's controls or feed.

## Runtime and checks

Script variants use separate player-scale and team-scale literals. Metadata validation rejects literals inside copied native bodies. Variants are created lazily, remain immutable and are reused when options return to a previous combination. Methods without a particular option reuse their existing definition rather than duplicate it. A bounded pointer cache handles stable Draw/focus calls without guarded reads, scans or allocations. Native source/header storage is separate from selected expanded definitions.

Checks cover all 25 player/team scale combinations; fog/colors combinations; numeric boundaries; Blind fog and color-only paths; pregraded/hidden cached labels; native tint/focus restoration; unchanged model values; both scale literals in native definitions; lazy allocation/reuse; format-1 migration; format-2 persistence; per-Dynasty isolation; shared payload agreement; foreign menu sections; all active native/UI suites and MMC package integrity/tamper checks. Callback timing fixtures are not game frame-time measurements.

## Coverage limits

The stock Draft Results menu is retained. The custom Pick/NFL Team/National/conference browsing experiment is disabled; synthetic draft assignments remain Social Media content only. Its legacy research source is not an active runtime dependency.

The separate Rime opening-lineup and Game Changers/Lightning Combination broadcast banners still expose OVRs. The latest bounded pass-through trace stopped cleanly but did not establish which live integer formatter owns those rating connections. p96 does not introduce a Flags-only or blanket-number substitution. See [presentation audit](player-fog-presentations.md). Other menus/presentation scenes retain the verification status in [coverage](player-fog-coverage.json).
