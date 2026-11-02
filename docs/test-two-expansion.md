# Second preseason / TeamBuilder test expansion (v71)

The native DLL and managed MMC adapter remain Dynasty Enhancer. No simulation or save records are written.

## Skipped publication weeks

When a previously observed regular-season edition is followed by a later week, missing editions are reconstructed from published games and game-stat caches still available in the active Dynasty. Week 3 therefore contains recaps and performances from Week 2. The picker marks the edition **(recovered)**. Existing observed editions are retained exactly.

Recovered editions contain only results, team game totals, and player game stat lines. They do not claim historical polls, injuries, commitments/offers, awards, betting lines, coaching changes or fictional contemporaneous player/fan reactions. They are never used as recruiting/injury observation baselines. First observation of an older Dynasty does not invent an entire unseen season. Missing/unpublished game caches cannot become zero-valued stats.

Real BYU/TeamBuilder test: Week 2 to Week 4 recovered 520 stories for Week 3. The catalogue contains Preseason and regular Weeks 0, 1, 2, 3 and 4. All previously observed earlier editions remained unchanged. The native decoder validates all six editions and all dynamic scopes.

## Accounts and artwork

- ESPN bets are not implied: ESPNCFB is the general national account; FanDuel Sports posts explicitly described **model projections**, not real bookmaker prices.
- Jake Whitmore (@JakeWhitmoreCFB): rankings, staff and national reporting.
- Marcus Bennett (@MBennettSports): predictions, contenders and debate.
- Tina Brooks (@TinaBrooksCFB): opening overreactions and casual commentary.
- David Ellison (@DavidEllisonFB): evidence-based team/player analytics.
- Chris Maddox (@ChrisMaddoxCFB): recruiting, newcomers and breakout candidates.
- The former school Sideline fan identity is now Barstool <School>. The other local fan identity remains <School> After Dark.
- Beat identities use expanded first/surname pools. Personal handles persist through position, class, school and publication-week changes. Recruit display names add ` | POSITION`; active player names remain plain.
- Ordinary official accounts use the installed on-white bank (Library 64); Barstool uses the secondary bank (Library 89). Mapping joins exact canonical asset names against the primary bank, rather than assuming all IDs align.
- TeamBuilder accounts retain their registered custom primary logo. Player portraits/uniforms remain unchanged. FanDuel receives the native full-colour coin icon (Library 79, Asset 1053), pending visual confirmation.

The attached ESPN PNG is not wired into this DLL. The verified native widget uses an ImageLibrary/AssetId pair; the existing asset reader can inspect EBX libraries but cannot register a PNG as a new native texture. The TeamBuilder repair path is specialized to saved team logos, not a general social-account image importer. A dedicated texture/image-library asset import remains a separate optional task. No shared school logo is replaced with ESPN.

## Publication and For You

- A deterministic 33% gate decides whether an eligible parent thread can receive replies; reply candidates still need a real parent and satisfy account/topic limits. Refreshing or adding another post cannot reroll this gate.
- Scholarship offers retain their independent deterministic 20% gate, equal for CPU and user schools.
- For You prefers actual user-team stories before nearby/pipeline recruit stories. Soft targets are approximately 55% personalized, 20% conference and 25% national. Context can overlap; these are selection preferences, not promises that every week has that exact distribution.
- A second selection pass relaxes soft variety rules to fill 30 when suitable real candidates exist. The one-offer limit, account limits, parent dependencies and a three-item thread bound remain. No invented filler is added.
- National 100/conference 60 caps, likes sorting, reply adjacency, LB/RB types and both dropdowns are retained.
- Personal variants mix capitalization and punctuation rather than making every player write in lowercase.

## New conditional coverage

37 additional story families and 84 variants bring the active catalogue to 231 families / 423 variants.

| Coverage | Required evidence |
| --- | --- |
| Previous season / rebuild | Explicit previous-season win/loss record; suppress all-zero initialization |
| Championship defense / playoff return | Native positive last-season playoff round |
| Conference defense / bowl return | Previous TeamStats slot corroborates the explicit prior record; later Dynasty year |
| New/veteran head coach | Native SeasonsWithTeam and resolved current coach |
| Recruiting/development approach | Native dominant coaching archetype, expressed in ordinary football language |
| Coordinator approach | Resolved coordinator and scheme-focused native archetype |
| Camp position competition | First two genuine depth-chart entries within three internal rating points; single-starter positions only |
| True freshman / young breakout | SchoolYear plus redshirt status; internal evaluation never printed |
| Senior final season | Healthy roster senior; player perspective |
| NIL support | Positive native NIL compensation; no invented dollar amount or brand contract |
| Player spotlight | Current-year preseason national honor |
| Heisman possibility | Returning QB/HB/WR with strong internal evaluation; phrased as a forecast |
| Unranked dark horse / conference favorite | Explicitly described roster-based model and native conference membership |
| Favorable schedule | At least ten scheduled games; zero opponents in current preseason AP Top 25; no claim they are harmless |
| Experienced transfer addition | Prior-year production at a different resolved school; years-with-team alone is insufficient |
| Season kickoff / countdown | Regular Week 0 plus the actual first scheduled opponent/week |
| Opening venue | Actual stadium Name, home opener, verified non-neutral venue |
| New-coach debut | Native zero seasons with school and scheduled Week 0 opener |
| First QB order | Genuine current depth-chart entry and class/redshirt status |
| Player opening excitement | Healthy active roster player, restrained QB alternatives |
| Recruit school watch / player tag | Uncommitted recruit, native top-three schools and their Week 0 game; real persisted athlete handle |
| High-school season excitement | Uncommitted nationally ranked recruit |
| Opening visit | Native ActiveVisitInfo matches current regular Week 0 |
| Dominant / close debut / overreaction | Published Week 0 final; margin >=28 or <=3; available in publication Weeks 0/1 |

## Data limits

The first-year BYU test has zero-initialized previous-season record fields, so it will not produce invented previous-year outcomes. Years-with-team is also zero for many established players; transfer stories require previous-year statistical evidence instead. Stadium Name is the venue (LaVell Edwards Stadium); STADIUM_DISPLAYNAME can be merely the school name (BYU).

Existing archived editions keep their stored prose and images. New content applies when the corresponding phase/week is generated or reconciled as the active edition. Reviewing a preseason conversion of current data is an editorial audit only; it is never published as an actual preseason observation.

## Validation

129 Node tests pass, including 33%/20% stable sampling, genuine depth order, transfer/history guards, native normalization, UTF-8 integrity, archived-week isolation and rewind behavior. Native UI checks, six-edition real catalogue decoding, MMC registration/payload tamper checks and installed-adapter checks pass. The live worker published Week 4 from active Dynasty memory without saving. In-game recovered Week 3 entry and scrolled recap cards are visually observed; final new-logo/coin/controller confirmation remains pending.
