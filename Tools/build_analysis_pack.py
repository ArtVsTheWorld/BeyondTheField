"""Author the conditional analysis/world-news expansion; contains no Dynasty data."""
import json
from pathlib import Path
families={}
def add(key,*bodies):families[key]=[{'id':key+'.'+str(i+1),'body':b+('{recruitRankDetail}' if key in ['beat.recruit_pickup','beat.recruit_questioned'] and i%2==0 else '')} for i,b in enumerate(bodies)]
team={
'scoring-offense':('{school} is averaging {value} points through {games} games. That is a lot to ask the next defense to keep up with.','{games} games in, {school} is putting up {value} points a game. The scoreboard pressure is real.'),
'scoring-defense':('{school} is allowing {value} points per game through {games} games. That number puts the rest of the team’s work in context.',),
'scoring-margin':('{school} has an average scoring margin of {value} through {games} games. The record is one part of the story; that gap is another.',),
'yards-per-attempt':('{school}: {value} yards per recorded pass/rush attempt across {attempts} attempts. A useful efficiency check alongside the raw yardage.',),
'passing-efficiency':('{school} is getting {value} yards per pass attempt on {attempts} throws. That says more about the passing game than yardage alone.',),
'rushing-efficiency':('{school} is averaging {value} yards per carry across {attempts} carries. Volume and efficiency are different questions. This is the efficiency part.',),
'offensive-balance':('{value}% of {school}’s recorded pass/rush attempts have been {approach}. The offensive identity is pretty clear through {games} games.',),
'interception-rate':('{school} has thrown {interceptions} interceptions on {attempts} attempts: a {value}% interception rate. That is a meaningful part of the passing-game picture.',),
'passing-td-rate':('{school} has {touchdowns} passing TD on {attempts} attempts. That is a touchdown on {value}% of throws through {games} games.',),
'fourth-down':('{school} is {conversions}-for-{attempts} on fourth down ({value}%). Small samples can swing, but those are real possessions extended or given up.',),
'run-defense':('{school} is allowing {value} rushing yards per game through {games} games. Start there when sizing up its next matchup.',),
'pass-defense':('{school} has allowed {value} passing yards per game through {games} games. That is the yardage picture; it does not tell us how often opponents choose to throw.',),
'takeaways':('{takeaways} takeaways in {games} games for {school}, an average of {value}. Opposing offenses have had very little room for careless possessions.',),
'sack-pressure':('{school} has {sacks} sacks through {games} games, or {value} a game. That is tangible disruption, even without a full pressure chart.',),
'red-zone-field-goals':('{school} has {fieldGoals} field goals among {scoringTrips} red-zone TD/FG scoring trips. That is {value}% ending in three rather than six.',),
'penalty-discipline':('{school} is averaging {value} penalty yards through {games} games. Hidden yardage still shows up in the final accounting.',),
'second-half':('{school} has a {value} average second-half scoring margin through {games} games, excluding overtime. The halftime score has not been the whole story.',),
'halftime-comebacks':('{school} has won {count} games after trailing at halftime this season. Worth remembering the next time the first half gets ugly.',),
'fourth-quarter-losses':('{school} has lost {count} games it led after three quarters. Finishing is becoming a fair question for this staff.',),
'home-road-split':('{school}’s average scoring margin: {homeMargin} at home ({homeGames} games), {roadMargin} away ({roadGames}). That is a noticeable venue split.',),
'close-games':('{school} has already played {count} games decided by seven or fewer: {wins} wins and {losses} losses. This season has left very little room to coast.',),
'opponent-records':('{school}’s opponents have a combined {wins}–{losses} record excluding their games against {school}. Some useful context beyond the headline record.',),
'offense-defense-contrast':('{school} is scoring {pointsFor} points a game and allowing {pointsAgainst}. The offense is producing, but the defense is leaving a lot on its plate.',),
'red-zone-defense':('{school} has allowed {touchdowns} TD on {trips} opponent red-zone trips ({value}%). Getting inside the 20 and finishing the drive are different things.',)
}
for k,b in team.items():add('analysis.team.'+k,*b)
for key in ['passing-yards-leader','passing-td-leader','rushing-yards-leader','receiving-yards-leader','sacks-leader','interceptions-leader']:
 add('analysis.player.'+key,'{school}’s {playerName} {lead} {field} with {value} {metricLabel}. That is a name to know before the next kickoff.','{value} {metricLabel} for {playerName} of {school}. He {lead} {field} right now.')
player={
'completion-rate':('{school} QB {playerName} is completing {value}% of passes on {attempts} attempts. Enough throws now to take that rate seriously.',),
'passing-yards-per-attempt':('{school}’s {playerName}: {value} yards per pass attempt across {attempts} throws. A better lens on efficiency than simply counting passing yards.',),
'td-int-ratio':('{playerName} has {touchdowns} passing TD against {interceptions} interceptions for {school}. Those two numbers deserve to be read together.',),
'rushing-yards-per-carry':('{school}’s {playerName} has {yards} rushing yards on {carries} carries, {value} per attempt. That is the workload and the efficiency in one line.',),
'yards-per-catch':('{playerName} of {school} is averaging {value} yards per catch on {catches} receptions. Those catches are moving the ball a long way.',),
'yards-after-catch':('{school}’s {playerName} averages {value} yards after the catch across {catches} receptions. The work is continuing after the ball arrives.',),
'receiving-td-rate':('{touchdowns} of {playerName}’s {catches} catches for {school} have gone for TD ({value}%). A real finishing threat in this passing game.',),
'scrimmage-yards':('{school}’s {playerName} is averaging {value} yards from scrimmage through {games} games: {yards} combined rushing and receiving yards.',),
'dual-threat':('{playerName} of {school} is averaging {passing} passing yards and {rushing} rushing yards a game. Defenses have two different jobs when he is out there.',),
'carry-share':('{playerName} has taken {value}% of {school}’s team carries, {carries} in total. That is a substantial share of the rushing workload.',),
'catch-share':('{playerName} accounts for {value}% of {school}’s completed passes with {catches} catches. That is a central role in the passing offense.',),
'touchdown-share':('{school}’s {playerName} has scored {touchdowns} rushing/receiving TD, {value}% of the team’s passing-plus-rushing TD total. A big piece of the scoring offense.',),
'tackles':('{playerName} has {tackles} tackles for {school}, averaging {value} through {games} games. That includes solo and assisted tackles.',),
'tackles-for-loss':('{school}’s {playerName} has {value} tackles for loss. Plays behind the line add up, even when they do not make the biggest highlight.',),
'forced-fumbles':('{playerName} of {school} has forced {value} fumbles. Creating the loose ball is his contribution; recovering it is a separate question.',),
'pass-breakups':('{school}’s {playerName} has {value} pass breakups. Interceptions get the attention, but those incompletions matter too.',),
'field-goals':('{playerName} is {made}-for-{attempts} on field goals for {school} ({value}%). That is a dependable return so far this season.',),
'long-field-goals':('{school} kicker {playerName} is {made}-for-{attempts} from 50 yards or more. That is a useful range of options for the staff.',),
'net-punting':('{playerName} of {school} is averaging {value} net yards on {punts} punts. Field position work that can disappear in a quick box-score glance.',),
'freshman-production':('Freshman {playerName} already has {production} for {school}. An early contribution worth a little more attention.',)
}
for k,b in player.items():add('analysis.player.'+k,*b)
world={
'world.upset':('{winnerLabel} beats {loserLabel}, {score}. That is a result that will get attention well beyond this matchup.','Final: {winnerLabel} {score} over {loserLabel}. A major change to the expected script.'),
'world.streak':('{school} has won {count} straight. This is turning into a sustained run, not just one good Saturday.',),
'world.award':('{school}’s {playerName} is the {award} for Week {awardWeek}. Recognition for an actual week of production.',),
'world.record_broken':('{playerName} of {school} broke the {recordScope} {period} record for {metric}: {value}. A new line in the record book.',),
'world.record_holder':('The {recordScope} record book now lists {school}’s {playerName} at {value} {metric} for a {period}. A performance with a place in the program’s history.',),
'world.flip':('{playerName} has flipped his commitment from {oldSchool} to {newSchool}. A verified change on the recruiting board.',),
'world.rivalry_flip':('{playerName} has flipped from {oldSchool} to rival {newSchool}. That recruiting change comes with an extra layer of bragging rights.',),
'world.decommit':('{playerName} is no longer committed to {oldSchool}. His recruitment has reopened.',),
'world.undefeated':('{away} ({awayWins}–0) visits {home} ({homeWins}–0) this week. Two unbeaten records, one matchup. Something has to give.',),
'world.bounceback':('{school} faces {opponent} after last week’s upset loss. The next response will get plenty of attention.',),
'beat.recruit_pickup':('{school} adds {starDescription}{position} {playerName}. Another piece of the class coming into focus.','{starDescription}{position} {playerName} is headed to {school}. A new commitment for this recruiting class.'),
'beat.recruit_questioned':('{school} adds {starDescription}{position} {playerName}. This is a lower-profile pickup than this program usually targets. Fair to ask what the staff sees here.',),
'reply.fan.recruit_number_one':('{parentHandle} THE NUMBER ONE RECRUIT IN THE COUNTRY. {nickname} actually got him. somebody tell me to calm down','{parentHandle} {playerName} is No. 1 nationally and he picked US. yeah i’m not being normal about this'),
'reply.fan.recruit_program_changer':('{parentHandle} a {stars}-star picked {school}??? this is the kind of signing we used to just watch other teams make','{parentHandle} {stars}-star {playerName} to the {nickname}. this is massive for us. absolutely massive'),
'reply.fan.recruit_five_star':('{parentHandle} FIVE STAR {playerName}. {nickname} keep adding serious talent','{parentHandle} a 5-star is always worth celebrating. welcome to the {nickname}, {playerName}'),
'reply.fan.recruit_questioned':('{parentHandle} a {stars}-star signing for {school}? i hope this staff sees something the rest of us don’t','{parentHandle} not writing {playerName} off, but this is a strange pickup for a program recruiting at our level'),
'reply.fan.flip':('{parentHandle} {playerName} really flipped from {oldSchool} to {newSchool}. man that’s annoying','{parentHandle} cool cool cool. all that recruiting just for {newSchool} to get {playerName}. i’m sick'),
'reply.fan.decommit':('{parentHandle} losing {playerName} from this class hurts. staff has some work to do','{parentHandle} {playerName} reopened it? yeah i don’t love that at all'),
'reply.fan.coach_good':('{parentHandle} give {coachName} some credit. {school} is getting real production here','{parentHandle} {coachName} deserves flowers for this. keep it going'),
'reply.fan.coach_bad':('{parentHandle} {coachName} has to answer for this at some point. these numbers are rough','{parentHandle} how much longer are we pretending this part of {school} is fine? looking at you, {coachName}'),
'reply.fan.player_good':('{parentHandle} {playerName} deserves way more attention for what he’s doing at {school}','{parentHandle} been trying to tell people about {playerName}. let him work'),
'reply.fan.player_bad':('{parentHandle} i want {playerName} to turn it around but we can’t act like this is working','{parentHandle} those {playerName} numbers for {school} are not it. something has to improve'),
'reply.fan.upset':('{parentHandle} {winner} just did THAT to {loser}. this sport is ridiculous','{parentHandle} {winner} over {loser}. if you need me i’ll be acting completely unreasonable about this'),
'reply.fan.award':('{parentHandle} {playerName} earned that. {nickname} getting some recognition','{parentHandle} say {playerName}’s name a little louder. well deserved'),
'reply.player.award':('{parentHandle} appreciate the love. couldn’t do it without my guys','{parentHandle} thankful for this one. love this team')
}
for k,b in world.items():add(k,*b)
Path('Content/Runtime/analysis-pack.json').write_text(json.dumps({'format':1,'revision':'voices-4-analysis','families':families},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({'newFamilies':len(families),'newVariants':sum(len(v) for v in families.values())})
