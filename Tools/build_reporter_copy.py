"""Static factual reporting alternatives and measured analytic context."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.reporter.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])

add('beat.team_stats',
    '{school} vs. {opponent}: {passingYards} passing yards, {rushingYards} rushing yards, {firstDowns} first downs, {giveaways} {giveawayLabel}.',
    'The {school} offense against {opponent}: {passingYards} through the air, {rushingYards} on the ground. {firstDowns} first downs, {giveaways} {giveawayLabel}.',
    '{passingYards} passing and {rushingYards} rushing yards for {school} against {opponent}. The rest: {firstDowns} first downs, {giveaways} {giveawayLabel}.',
    '{school} produced {passingYards} passing yards and {rushingYards} rushing yards against {opponent}, with {firstDowns} first downs and {giveaways} {giveawayLabel}.',
    'Against {opponent}, {school} finished at {passingYards} passing, {rushingYards} rushing. First downs: {firstDowns}. Giveaways: {giveaways}.',
    'The offensive line from the box score: {school}, {passingYards} passing yards, {rushingYards} rushing yards, {firstDowns} first downs and {giveaways} {giveawayLabel} vs. {opponent}.',
    '{school}\'s {opponent} game in numbers: {passingYards} passing yards, {rushingYards} rushing yards. {firstDowns} first downs, {giveaways} {giveawayLabel}.',
    '{firstDowns} first downs and {giveaways} {giveawayLabel} for {school} against {opponent}. Yardage split: {passingYards} passing, {rushingYards} rushing.',
    'Box-score snapshot vs. {opponent}: {school} had {passingYards} passing yards, {rushingYards} rushing yards, {firstDowns} first downs and {giveaways} {giveawayLabel}.',
    '{school} through the air: {passingYards}. On the ground: {rushingYards}. Against {opponent}, that came with {firstDowns} first downs and {giveaways} {giveawayLabel}.')
forms('beat.performance','~ {school}\'s {playerName} against {opponent}: {statLine}. {resultLine}',
    'The performance line:','From the box score:','The individual production:','A player line to note:',
    'Looking back at the game:','One performance from the matchup:','The player spotlight:',
    'A look at the production:','The stat line:','From the game review:')
for key,label in [('beat.injury','remains on the injury list'),('beat.new_injury','has been added to the injury list')]:
    forms(key,'~ {school}\'s {playerName} '+label+'.{injuryDetail} {timetable}',
        'Availability update:','Injury update:','The medical report:','The current injury picture:',
        'From the injury report:','A health update:','The availability note:',
        'The injury-list update:','A medical update:','On the injury list:')
forms('injury.report','~ {school}\'s {playerName}.{injuryDetail} {timetable}',
    'Injury report:','Availability update:','The current injury report:','Health update:',
    'The injury-list note:','From the medical report:','The availability picture:',
    'A medical update on','On the current injury list:','The injury update:')
forms('beat.preview','{awayLabel} vs. {homeLabel} ~.{rivalryDetail}',
    'is on the schedule this week','is the matchup this week','is coming up this week','is set for this week',
    'is on this week\'s slate','is a game to follow this week','is up this week',
    'is part of the current week\'s schedule','is a current-week matchup','is ahead this week')
forms('beat.standings','~ {conference}: {leaders}. These teams lead the current standings.',
    'Standings check in the','The latest from the','The current league picture in the',
    'The leading group in the','At the top of the','The standings snapshot for the',
    'The front of the race in the','The league leaders in the','The current standings for the','The standings note from the')
forms('beat.independents','~ {leaders}. These are overall records for independent programs.',
    'Independent-team check:','The independent picture:','Among the independents:',
    'An independent-program snapshot:','The current independent records:','Checking the independent teams:',
    'The independents in view:','The independent-program report:','Records among the independents:',
    'The independent-team standings note:')
forms('analyst.rushing','{school}: {rushingYardsPerGame} rushing yards per game, {rankPhrase} in FBS through {sampleGames} games. ~',
    'The ground game belongs in the discussion.','That is the production behind the national place.',
    'Both the average and the sample matter.','The rushing volume has a national reference point.',
    'That puts the ground game in context.','The national rushing comparison starts there.',
    'A ground-game figure to keep in view.','The average gives the ranking a concrete basis.',
    'The sample is now part of that comparison.','That is the rushing profile entering the next game.')
forms('analyst.rushing_poll','{school} rises from No. {previousPollRank} to No. {pollRank}. Its {rushingYardsPerGame} rushing yards a game rank {rankPhrase} in FBS through {sampleGames} games. ~',
    'The ground game is part of the resume.','That production helps explain the football behind the ranking.',
    'A national rushing profile alongside the poll move.','There is rushing production to go with the ranking.',
    'The rushing numbers belong beside the poll update.','That is one part of the team profile behind the move.',
    'The ground game deserves a place in the discussion.','The rise has a measurable rushing backdrop.',
    'The rushing average adds context to the poll spot.','The next defense has a productive ground game to plan for.')
for key,descriptor,ends in [
 ('third_low','third-down conversion',['Keeping drives alive is a problem.','Early-down success matters even more when third downs stall.', 'That rate leaves possessions ending too often.','A real issue extending drives.','The offense needs more new sets of downs.']),
 ('third_high','third-down conversion',['The offense is earning extra sets of downs.','A lot of chances to end drives have become fresh downs.','That is sustained possession value.','The offense has been difficult to get off the field.','The conversion rate is a strength.'])]:
    pairs('analyst.'+key,[
        '{school}: {percent}% on third down, {conversions} of {attempts} through {sampleGames} games.',
        '{school} has converted {conversions} of {attempts} third downs ({percent}%) in {sampleGames} games.'],ends)
for key,ends in [('red_low',['Touchdowns are getting left behind inside the 20.','Reaching the red zone and finishing for six are different things.','The finishing rate needs improvement.','That is a lot of trips without a touchdown.','The offense needs more six-point finishes.']),('red_high',['The offense is finishing those trips for six.','Getting inside the 20 has often meant a touchdown.','The finishing rate is a strength.','Those visits are producing touchdowns.','The offense is making red-zone opportunities count.'])]:
    pairs('analyst.'+key,[
        '{school}: {touchdowns} red-zone TD on {trips} trips ({percent}%) through {sampleGames} games.',
        '{school} has finished {percent}% of its {trips} red-zone trips with TD: {touchdowns} scores in {sampleGames} games.'],ends)
for key,sign,ends in [('turnover_plus','+',['That is an extra-possession cushion.','The takeaways have helped the possession balance.','The next game still has to earn its own takeaways.','Ball security and takeaways have given this team an advantage.','The margin is one part of the current record.']),('turnover_minus','',['That is a costly possession deficit.','The team is giving opponents extra chances.','The possession balance needs to change.','Ball security has to be part of the evaluation.','That margin makes other parts of the game harder.'])]:
    pairs('analyst.'+key,[
        '{school}: '+sign+'{margin} turnover margin, {takeaways} takeaways against {giveaways} giveaways in {sampleGames} games.',
        '{takeaways} takeaways, {giveaways} giveaways for {school}. Turnover margin: '+sign+'{margin} through {sampleGames} games.'],ends)
forms('analyst.margin','{school}\'s {score} win over {opponent} has a {margin}-point margin, the largest among {comparisonGames} published FBS games this season. ~',
    'That is the full-season comparison.','The comparison goes beyond this week\'s slate.',
    'No other published FBS result this season has a larger gap.','A result at the top of the margin list.',
    'That is a season-wide winning-margin marker.','The number stands out across the whole published schedule.',
    'A season-leading final margin.','The gap is the largest in the current result set.',
    'A full-season margin benchmark.','The result leads the season\'s published winning margins.')
forms('analyst.heisman','{school}\'s {playerName} {rankChange} in the Heisman race after {statLine} vs. {opponent}. ~',
    'The production belongs with the ranking.','That is the latest performance behind the watch-list spot.',
    'A recent game to keep in the evaluation.','The ranking has an on-field reference point.',
    'The stat line adds context to the attention.','One game in a season-long evaluation.',
    'Keep the whole performance in the discussion.','The case still depends on the full season.',
    'That is the recent football behind the race.','The next game will add another piece to the case.')
forms('world.upset','{winnerLabel} ~ {loserLabel}, {score}. A result that changes the week\'s conversation.',
    'upsets','stuns','takes down','knocks off','beats','defeats','gets the better of','comes out on top against','earns an upset win over','wins against')
forms('world.streak','{school} ~ {count} straight wins.',
    'has put together','is up to','has reached','stands at','has recorded','has a run of',
    'has built a run of','is riding a run of','has a winning run of','has extended its run to')
forms('world.award','{school}\'s {playerName} ~ the {award} for Week {awardWeek}.',
    'is named','has been named','is selected as','earns recognition as','receives recognition as',
    'is honored as','takes the honor of','is recognized as','has earned recognition as','has been selected as')
forms('world.record_broken','{school}\'s {playerName} ~ the {recordScope} {period} record for {metric} with {value}.',
    'breaks','has broken','sets','has set','establishes','has established','posts a new mark for','creates a new mark in','raises the mark in','sets a new mark in')
forms('world.record_holder','The {recordScope} {period} record for {metric} ~ {school}\'s {playerName}: {value}.',
    'belongs to','now belongs to','is held by','is now held by','has a holder in','lists',
    'has its current mark from','has its current holder in','has a mark set by','is currently credited to')
forms('world.flip','{playerName} ~ {oldSchool} to {newSchool}.',
    'flips his commitment from','has flipped his commitment from','changes his commitment from','has changed his commitment from',
    'switches his commitment from','has switched his commitment from','makes a commitment change from',
    'moves his commitment from','has moved his commitment from','takes his commitment from')
forms('world.rivalry_flip','{playerName} ~ {oldSchool} to rival {newSchool}.',
    'flips his commitment from','has flipped his commitment from','changes his commitment from','has changed his commitment from',
    'switches his commitment from','has switched his commitment from','makes a commitment change from',
    'moves his commitment from','has moved his commitment from','takes his commitment from')
forms('world.decommit','{playerName} ~ {oldSchool}. The recruitment is open again.',
    'is no longer committed to','has withdrawn his commitment to','has decommitted from','has reopened his recruitment after a commitment to',
    'is reopening his recruitment after committing to','has ended his commitment to','has backed away from his commitment to',
    'has come off the commitment list at','has reopened things after committing to','is back on the board after committing to')
forms('world.undefeated','{away} ({awayWins}-0) faces {home} ({homeWins}-0) this week. ~',
    'Two unbeaten records meet.','The perfect starts get a head-to-head test.','Both teams enter without a loss.',
    'A matchup between undefeated teams.','The unbeaten runs meet on the same field.','Two unblemished records are on the line.',
    'The unbeaten-team discussion gets a direct result.','Neither team has lost coming into this one.',
    'The undefeated starts cannot both survive a decisive result.','The next test comes against another unbeaten team.')
forms('world.bounceback','{school} faces {opponent} after last week\'s upset loss. ~',
    'The response becomes part of the story.','The next result will tell us more than another explanation.',
    'A chance to change the conversation.','The next game is the immediate test.',
    'There is a recent result to answer for.','The follow-up deserves attention.',
    'The week brings a chance to reset the mood.','The previous loss puts more eyes on the response.',
    'The next game offers the quickest answer.','The team gets an on-field chance to respond.')

root.joinpath('Content/Runtime/reporter-variety-pack.json').write_text(json.dumps({'revision':'reporter-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
