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
