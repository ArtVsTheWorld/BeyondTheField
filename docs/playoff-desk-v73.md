# v73: national desk, injuries and CFP coverage

## User-requested changes

TeamBuilder fan and beat accounts now use the primary logo. The v72 secondary ID/source metadata existed, but the live image was a generic placeholder; metadata availability did not prove renderability. Existing ordinary-school on-white/helmet/mascot/secondary mappings remain. Presentation version 3 applies the primary fallback to stored editions without regenerating their facts or likes.

Recruiting and Recruits are merged into one LB/RB category, matching recruiting subjects or recruit authors. Players remains independent. Injuries is a new category; replies follow their parent irrespective of reply voice/category. Official Accounts now includes team accounts and the CFP account.

## National desk

The current public poll's native ranks 1-60 select national coverage. These full native orderings are selection inputs; ranks beyond the visible Top 25 are never printed as public poll positions. Hidden TeamRank is not used. Analysts' smaller-program metrics are retained as school-beat stories. Major national recruiting news can still receive national talent coverage.

The former hardcoded David assignment is replaced with stable topic-based assignment across all five writers. Jake uses direct reporting, Marcus opinion framing, Tina casual/sarcastic framing, David the underlying analytics, and Chris talent/evaluation framing. Player/recruit reports also give Chris appropriate specialist opportunities. Prewritten voice variants preserve the same verified numbers; negative metrics cannot receive positive celebration wrappers. Same-week refreshes retain the selected writer, underlying text and final voice wording. Normal template cooldowns apply to both underlying and voice variants.

In the real Week 10 preview, all five are represented in National's first 100 stories: Jake 11, Marcus 8, Tina 7, David 7, Chris 8. The full edition contains 105 Jake, 102 Marcus, 86 Tina, 142 David and 75 Chris posts. 590 analytics stories are assigned to beats; no national analytics root has only outside-top-60 teams.

## Injury windows

MinInjuryDuration and MaxInjuryDuration are already remaining weeks. This is verified on the same native injury episodes in real Weeks 4, 6 and 10. For example, Isaac Sohn changes from 22-33 to 20-31 to 16-27, while Lamar Sperling changes from 5-7 to 3-5 to -1-1. No second subtraction of the injury week is performed.

Reports use estimates rather than exact dates: a positive range becomes 'Estimated return: 1-2 weeks'; an elapsed minimum with a positive maximum allows a possible return this week. Undiagnosed, EarlyReturn, missing/invalid ranges and the 63 Returning sentinel receive distinct handling. Native season-ending/career-ending severity is respected. A previous-season SeasonEnding flag does not override a current remaining-week window in a new year.

The live user confirmed Jovesa Damuni's 2-3 week estimate and working category controls in v73.

## CFP account and public poll

The account is CFP, @CFBPlayoff, with native image library 34 / asset 41 (`dynas_stickers_CFP`). The user verified CFP publication begins in regular-season Week 10. The code requires that boundary and a complete native CFP Top 25 before changing the primary poll from AP or publishing ranking posts. Seeded last-CFP values cannot create AP-to-CFP movement in the first edition.

The live Week 10 edition publishes the actual top three: Ole Miss, Miami and SMU. Subsequent regular-season posts cover top-three places plus meaningful movement around the top 16/top-12 picture. Analyst, school-beat and fan stories discuss contending teams using explicit CFP ranks. They do not equate rank with an invitation or guaranteed berth.

Postseason previews/results rely on SeasonGame.BowlGame.IsPlayoffBowl, the actual NationalChampionship phase, or corroborated campus first-round teams with native PlayoffRoundReached and no ordinary bowl label. Ordinary bowls, unknown phases, future games, unpublished finals and score/status conflicts do not become playoff results. The installed game exposes actual `CFP First Round` bowl records with bracket slots 0-3; no seed mapping is invented from those slots.

The latest completed playoff round can carry its recap into the next phase. Championship completion produces the champion report and replaces the earlier-round recap. Postseason game facts can support results even if the ranking table clears. Frozen regular-season CFP rankings are not presented as new postseason weekly polls.

## Validation and remaining checks

149 Node tests pass, including all-five-writer assignment, fact/voice stability, top-60 delegation, negative-stat polarity, injury windows, filter merging/reply dependencies, first CFP publication, movement, ordinary-bowl/future/unpublished suppression, round transitions and championship completion. Native tests cover injury filtering and the CFP official/rankings classifications. The real twelve-edition catalogue validates in every dynamic native scope. MMC registration, payload tamper checks and installed-adapter checks pass.

v73 is installed and active in the existing game process, with Week 10 published from native memory (3,260 stories, 30 For You). History migration and its backup are checksum-verified. User confirmation covers injury estimates and category controls. The remaining live checks are all analyst portraits/voice balance, CFP image/account posts, TeamBuilder primary fallback, actual future poll movement and actual postseason/year-rollover coverage. Fresh v73 MMC cold launch is not claimed as tested in this running session.
