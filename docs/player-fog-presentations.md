# Broadcast player-rating audit

The installed broadcast archive was parsed offline: **704 entries**, containing
1,350 definitions including aggregate copies. After deduplication, **41 templates
contain 239 player-rating cells**, using **31 attribute columns**. All those cells
are direct player queries with the default text format. Private extracted assets
and full reports remain under ignored `Evidence/PlayerFog/Presentations`.

| Presentation family | Rating fields found | Verification |
|---|---|---|
| Broadcast kicker graphic | Overall, kick power, kick accuracy | Static definition; visual output pending |
| Kick-returner graphic | Overall, speed, agility | Static definition |
| Pregame/runout/QB trot | Overall and position-specific attributes | Static definitions |
| Freshman debuts and player bios | Overall, speed, ball skills and other position attributes | Static definitions |
| Position/star-player comparisons | QB, RB, WR, TE, DE, MLB and safety attributes | Static definitions |
| Matchups to watch | Receiver/coverage, RB/LB, WR/LB and edge/QB comparisons | Static definitions |
| Legacy spotlight variants | QB overall, throw power/accuracy | Static definitions; presence does not establish use in current Dynasty |

## Separate playcall Kicker Range panel

The later screenshot identifies `art_screen.playcall.panel.KickerRange`, which
is separate from the broadcast definitions above. Its circular ACC/PWR badges
import `art_control.group.RatingValueItem`. p68 adds a dedicated asset bank for
the panel's initialization and range-refresh methods. Only `mcAccStat` and
`mcPowStat` are marked for the existing grade-label renderer; their numeric
`WidgetData.value` stays unchanged. Target line, distance remaining, yard
markers, player identity and range geometry remain native.

The panel's native 13- and 7-register frames are retained. Tests cover grade
boundaries, unknown/absent widgets, grade-color repaint and untouched distances
and geometry. A clean-session visual check remains pending.

## Broadcast implementation boundary

Football SystemMuse's `TextVariable` formatter converts an evaluated expression
into a **separate rendered string**. The candidate changes only that rendered
string, after native formatting. It does not change query results, ratings,
expression evaluation, comparisons or gameplay.

Conversion requires all of these:

- Exact native football `TextVariable` and direct `GameQueryVariable` classes.
- Exact player table `AGLP` and one of the 31 verified attribute columns.
- Default text format and a whole numeric rating in 0–100.
- A valid native rendered string cache and allocator.

Ordinary game/season/career statistics, statistical QB rating, team ratings,
jerseys, unknown values, nonnumeric text and other expressions retain native
formatting. Surrounding text such as “OVERALL RATING - ” is a separate text
variable and stays intact.

Startup validates the complete formatter body, exact vtable ownership, query
loader/evaluator layout and native string helper fingerprints. The callback uses
bounded local reads; it performs no process scans or background discovery.
Temporary strings use the game's constructor, reference-counted assignment and
destructor. The native formatter still receives its original input exactly once.

## Evidence and limits

- Offline tests cover all 31 columns × 101 ratings × three native numeric kinds,
  invalid/unknown values, non-player/statistic fields, foreign expression types,
  disabled forwarding and temporary-string lifetime.
- The live process's formatter body, vtable slots and helper code match the
  verified native fingerprints.
- Scene execution and visual output still require a live check. The static audit
  identifies definitions and supported fields; it does not claim that every
  legacy template can appear, or that arbitrary replacement assets use this path.
- Full p68 package includes the pre-snap substitution and playcall Kicker Range
  fixes. Isolated p67 tests
  only the presentation callback alongside p64; it has no reader, menu hooks or
  copied UI definitions and is not the automatic-loading package.

Repeat the offline audit with `python Tools/audit_player_presentations.py`.

## Playcall info-panel family audit

The current `Presentation_Common` collector was read separately from the older
research index. All **35 playcall panel assets** were extracted read-only and
decoded without errors. In particular, `TeamPositionGroups` has a newer asset
GUID than the historical index; the current collector resolves it correctly.
The private catalog is `Evidence/PlayerFog/PlaycallPanels/audit.json`.

| Panel | Treatment in p69 |
|---|---|
| IndividualPositionStats, including the pictured RB/FB Ratings | Grade the three final labels only when the native panel mode is Ratings (2) |
| PlayerVsPlayer | Grade up to three attribute pairs only in Ratings mode, after native comparisons and arrows are calculated |
| ImpactPlayerDepth | Grade its three explicit attribute labels after native selection and ordering |
| TeamPositionGroups | Grade each fresh row's player OVR display cell |
| TeamPositionGroups key-stat variant | Grade `ConferenceText`, where this layout puts player OVR; preserve `OverallText`, which contains the ordinary key statistic |
| Trench | Grade player OVR display cells in both lists; preserve weight averages |
| ConferenceRankings | Preserve: even the field called `Ovr` contains a season record here |
| SignedRecruits | Preserve: national rank, star rating and interest visualization |
| ImpactPlayerTraits | Preserve ability names, descriptions and tiers |
| ImpactPlayer / PlayerSelfComparison | Preserve generic statistics and comparisons; no confirmed rating-only path |

The new panel adapters keep native fonts and comparison foregrounds. This also
prevents grade colors from leaking into ordinary statistics when a cached panel
changes modes. Numeric input arrays, rating ordering, comparison arrows, player
IDs, jerseys, years, weight and ordinary statistics remain unchanged. Separate
asset banks use the original register frames and the existing attachment path;
no new native hook or background discovery is added.

Pre-snap Subs passed the user's p68 check. Kicker Range and the p69 panel changes
still need visual verification; the 35-asset audit is static evidence, not a claim
that every panel has appeared in the current game.
