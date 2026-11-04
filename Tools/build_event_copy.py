"""Offline copy for confirmed news, rankings and historical milestones.

Short factual accounts use alternative football verbs and sentence structures.
No generic inspirational endings or invented consequences are appended.
"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
families={}
def add(key,*bodies):
    families[key]=[{'id':key+'.eventcopy.'+str(i+1),'body':b} for i,b in enumerate(dict.fromkeys(bodies))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])

forms('beat.result','{winner} ~ {loser}, {score}.',
    'beats','defeats','gets past','takes down','wins against','prevails over','earns a win over','gets the better of','finishes on top against','comes away with a win over')
forms('beat.result_close','{winner} ~ {loser}, {score}. A {margin}-point game.',
    'edges','gets past','holds the final advantage over','comes out ahead of','wins a close one against','earns a narrow win over','prevails against','takes a tight one against','finishes ahead of','beats')
forms('beat.result_wide','{winner} ~ {loser}, {score}. The final margin is {margin}.',
    'beats','defeats','gets the better of','finishes ahead of','wins against','prevails over','takes down','comes out on top against','earns a win over','comes away with a win over')
add('beat.tie','{home} and {away} finish tied, {homeScore}-{awayScore}.',
    'A tie on the final scoreboard: {home} {homeScore}, {away} {awayScore}.',
    'No winner in this one. {home} {homeScore}, {away} {awayScore}.',
    'Final: {home} {homeScore}, {away} {awayScore}. The result is a tie.',
    '{homeScore}-{awayScore}: {home} and {away} end level.',
    'The final leaves nothing between them: {home} {homeScore}, {away} {awayScore}.',
    'A level finish for {home} and {away}, {homeScore}-{awayScore}.',
    '{home} {homeScore}, {away} {awayScore}. Neither team gets a win from this result.',
    'Tied at the finish: {home} {homeScore}, {away} {awayScore}.',
    'The {home}-{away} result is a tie, {homeScore}-{awayScore}.')
for key,change,phrases in [
    ('up','climbs', ['moves up','climbs','rises','goes up','advances','moves higher','makes a move up','takes a step up','is up','has risen']),
    ('down','slips',['moves down','slips','falls','drops','slides','moves lower','takes a step down','is down','has dropped','has fallen'])]:
    forms('beat.poll_'+key,'{school} ~ from No. {previousRank} to No. {rank} in the {pollName}.',*phrases)
forms('beat.poll_entry','{school} ~ at No. {rank} in this week\'s {pollName} Top 25.',
    'enters','joins the rankings','makes an appearance','checks in','arrives','is newly ranked','is a new entry','joins the list','appears for the first time in this edition','makes the list')
forms('beat.poll_same','{school} ~ No. {rank} in the {pollName}.',
    'holds at','stays at','remains at','keeps its place at','is still','continues at','retains the spot at','checks in again at','has not moved from','sits unchanged at')
forms('beat.recovery','{school}\'s {playerName} ~. Game participation remains a separate question.',
    'is no longer listed as injured','has come off the injury list','is off the current injury list','no longer has an injured designation','has cleared the listed injury status','has seen the injury designation removed','is not listed as injured now','has had the injured listing cleared','has a cleared injury listing','is no longer carrying the injured designation')
forms('beat.watch','{school}\'s {playerName} ~ against {opponent}.{watchDetail}',
    'is a name to watch','belongs on the watch list','gets a closer look','is one to follow','has a spot on the watch list','is a player to keep in view','is worth following','is on the radar','will be a name to track','is part of the players-to-watch discussion')
forms('beat.cfp','{school} ~ No. {rank} in the CFP rankings. That is a ranking, not a confirmed berth.',
    'sits at','checks in at','is ranked','stands at','holds','occupies','is listed at','has the spot at','appears at','finds itself at')
forms('beat.heisman','{school}\'s {playerName} ~ in the Heisman race.',
    '{rankChange}','{rankChange} on the current watch list','{rankChange} in the latest update','{rankChange} on the latest list','{rankChange} at this point','{rankChange} in the current picture','{rankChange} on this edition\'s list','{rankChange} in this week\'s update','{rankChange} in the latest watch','{rankChange} as the current list stands')

forms('playoff.first_rank','The first CFP rankings ~ {school} at No. {rank}.',
    'place','have','list','put','rank','show','introduce','position','feature','bring in')
forms('playoff.rank','The latest CFP rankings ~ {school} at No. {rank}.',
    'place','have','list','put','rank','show','position','feature','keep track of','include')
add('playoff.rank_move','{school}: No. {previousRank} to No. {rank} in the CFP rankings.',
    '{school} moves {movement} to CFP No. {rank}, from No. {previousRank}.',
    'CFP update: {school} is now No. {rank}. Previous ranking: No. {previousRank}.',
    'The CFP ranking changes for {school}: No. {rank}, after No. {previousRank}.',
    'A move {movement} for {school}. No. {previousRank} becomes No. {rank} in the CFP rankings.',
    '{school} checks in at CFP No. {rank}; the previous list had it No. {previousRank}.',
    'Updated playoff rankings: {school}, No. {rank}. That is {movement} from No. {previousRank}.',
    'The new CFP list has {school} No. {rank}, previously No. {previousRank}.',
    'CFP No. {rank} for {school}. Last edition: No. {previousRank}.',
    '{school} moves from CFP No. {previousRank} to No. {rank}. Direction: {movement}.')
forms('playoff.preview','The College Football Playoff ~: {away} vs. {home}.',
    'matchup is set','stage is set','pairing is confirmed','game is on the board','matchup is confirmed','field brings this pairing','schedule has this matchup','spotlight turns to this game','pairing is on the schedule','matchup to follow is this')
forms('playoff.title_preview','For the national championship, ~: {away} vs. {home}.',
    'the matchup is set','the last pairing is confirmed','the stage is set','the finalists are ready','the final game is on the board','the last two teams meet','the title matchup is confirmed','the season comes down to this','the final pairing is in place','one game remains')
forms('playoff.result','{school} ~ {opponent}, {score}, and advances in the College Football Playoff.',
    'beats','defeats','gets past','wins against','prevails over','takes down','comes out ahead of','gets the better of','earns a win over','comes away with a win over')
forms('playoff.champion','NATIONAL CHAMPIONS: {school} ~ {opponent}, {score}, in the title game.',
    'beats','defeats','gets past','wins against','prevails over','takes down','comes out ahead of','gets the better of','earns a win over','comes away with a win over')
forms('playoff.result_analysis','{school} ~ after a {score} playoff win over {opponent}.',
    'moves on','advances','earns another game','keeps its title run alive','takes the next step','extends its postseason','stays in the championship chase','continues its playoff run','secures a place in the next round','remains in the hunt')
forms('playoff.champion_analysis','{school} ~ with a {score} win over {opponent} in the final.',
    'wins the national championship','finishes as national champion','claims the national title','ends the season on top','takes the national title','closes a championship season','is crowned national champion','earns the national championship','completes its national-title run','finishes the job for a national title')

forms('postseason.heisman','{school}\'s {playerName} ~. The Heisman decision is final.',
    'wins the Heisman Trophy','is the Heisman Trophy winner','takes home the Heisman','receives the Heisman Trophy','claims the Heisman','has won the Heisman','is this season\'s Heisman winner','earns the Heisman Trophy','finishes the Heisman race as the winner','is awarded the Heisman Trophy')
forms('postseason.award','{school}\'s {playerName} ~ the {award}. The annual award is final.',
    'wins','receives','takes home','claims','earns','has won','is awarded','is the winner of','has been awarded','is honored with')
forms('postseason.all-american','{school}\'s {playerName} ~ a {honor}.',
    'is named','has been named','is selected as','earns selection as','is officially','is recognized as','finishes the season as','has been selected as','receives recognition as','is honored as')
forms('postseason.award-team','{playerName} ~ the {award}. {nickname} proud. {hashtag}',
    'wins','receives','brings home','claims','earns','has won','is awarded','is the winner of','takes home','has earned')
forms('postseason.coach-fired','{school} ~ {coachName} as {role}. The search for a replacement is next.',
    'has dismissed','has moved on from','has parted ways with','has removed','is moving on from','ends the tenure of','has let go of','parts company with','has ended the tenure of','dismisses')
forms('postseason.coach-hired','{school} ~ {coachName} as its {role}.{contractTerm}',
    'has hired','has appointed','has named','has selected','is bringing in','turns to','appoints','names','hires','chooses')
forms('postseason.coach-retained','{school} ~ {coachName} as {role}.{contractTerm}',
    'retains','keeps','is keeping','will keep','is retaining','continues with','sticks with','will continue with','has retained','has kept')
forms('postseason.coach-retired','{school}\'s {role} {coachName} ~.',
    'is retiring','has a retirement transition ahead','is moving into retirement','is leaving the role for retirement','will retire from the role','is stepping away into retirement','is set to retire','is heading into retirement','will leave the role through retirement','has retirement as the next chapter')
forms('postseason.coach-pro','{school}\'s {role} {coachName} ~. The staff has an opening to address.',
    'is leaving for the pro game','is moving to pro football','is taking the next step at the pro level','is set to leave for professional football','is heading to the pro level','will move on to the pro game','is moving on to professional football','is leaving the college staff for the pro level','has a pro-football move ahead','is departing for the pro game')
forms('postseason.coach-open','{school} ~ at {role} after the contract situation involving {coachName}. No replacement is confirmed.',
    'has an opening','has a vacancy','has a job to fill','needs an appointment','has an unfilled position','faces a staff decision','has a position available','is seeking a replacement','still has a vacancy','has an open job')
forms('postseason.coach-contract','The {role} contract situation involving {coachName} at {school} ~. There is no confirmed new appointment.',
    'remains open','is unresolved','is not settled','still needs a decision','has not been settled','is still pending','remains a decision to watch','has yet to be resolved','is an open question','is awaiting a resolution')
forms('postseason.coach-pending','A {role} transition involving {coachName} at {school} ~. The replacement is not confirmed.',
    'is pending','is in progress','has not been completed','is still developing','remains pending','is not finalized','has yet to be finalized','is in the pending stage','still needs to be completed','is moving toward a change')
forms('postseason.coach-departed','{coachName}\'s job move ~ at {school}. The staff must fill the {role} position.',
    'creates an opening','leaves a vacancy','opens a staff role','creates a staff vacancy','leaves a role to fill','means a transition','brings a staff change','leaves an opening on the staff','creates a replacement decision','sets up a staff search')

forms('history.team-counter','{school} ~ its {ordinal} {achievement} in program history.',
    'records','celebrates','has recorded','reaches','marks','adds','registers','has reached','notches','has added')
forms('history.team-wins','{school} ~ {threshold} all-time wins. The current total is {total}.',
    'reaches','has reached','hits the mark of','gets to','has made it to','crosses the threshold of','records at least','has recorded at least','stands at or beyond','is at or beyond')
forms('history.player-career','{school}\'s {playerName} ~ {threshold} career {metric}. The total is now {total}.',
    'reaches','has reached','gets to','has made it to','hits the mark of','records at least','has recorded at least','crosses the threshold of','is at or beyond','stands at or beyond')
forms('history.coach-wins','{school} coach {coachName} ~ {threshold} career wins. The running total is {total}.',
    'reaches','has reached','gets to','has made it to','hits the mark of','records at least','has recorded at least','crosses the threshold of','is at or beyond','stands at or beyond')
forms('history.coach-counter','{school} coach {coachName} ~ his {ordinal} career {achievement}.',
    'records','celebrates','has recorded','reaches','marks','adds','registers','has reached','notches','has added')

forms('transactions.signed','{school} ~ {starDetail}{playerName}.{nilDetail}',
    'has signed','signs','announces the signing of','adds the signature of','secures a signature from','has a signed commitment from','gets a signature from','has completed the signing of','makes it official with','lands a signature from')
forms('transactions.coach-deal','{school} ~ {role} {coachName} on a new contract.{term}',
    'retains','keeps','has retained','has kept','is retaining','is keeping','will retain','will keep','continues with','moves forward with')
add('transactions.nil-change',
    '{school}: {playerName}\'s NIL deal is now {current}, {change} from {previous}.',
    '{playerName} at {school} has a {current} NIL deal, {change} by {difference}.',
    'NIL update for {school}\'s {playerName}: {previous} to {current}, a {difference} change.',
    'A {difference} NIL adjustment for {school}\'s {playerName}. The deal has {change} from {previous} to {current}.',
    '{school}\'s {playerName} now has {current} in NIL compensation. Previously: {previous}.',
    'The NIL figure for {playerName} at {school} has {change} to {current}. The prior deal was {previous}.',
    '{previous} becomes {current} for {school}\'s {playerName}. NIL compensation has {change} by {difference}.',
    'A deal update at {school}: {playerName}, {current} in NIL compensation, {change} from {previous}.',
    'New NIL figure for {school}\'s {playerName}: {current}. The adjustment from {previous} is {difference}.',
    '{playerName}\'s {school} NIL deal moves from {previous} to {current}. That is a {difference} change.')
add('transactions.nil-review',
    'Following last week\'s review, {school}\'s {playerName} has a {current} NIL deal, {change} from {previous}.',
    'Last week\'s NIL adjustment at {school}: {playerName}, {previous} to {current}.',
    'A follow-up from the season review: {playerName}\'s {school} NIL deal has {change} to {current}. It was {previous}.',
    '{school} NIL follow-up: {playerName} is at {current} after last week\'s adjustment from {previous}.',
    'From last week\'s roster review: {school}\'s {playerName} had a {difference} NIL change. The deal is now {current}.',
    'The season-review adjustment for {school}\'s {playerName}: {current}, {change} by {difference}.',
    '{playerName} at {school} has {current} in NIL compensation following last week\'s review. Prior figure: {previous}.',
    'One NIL update from the review week: {playerName} of {school}, {change} from {previous} to {current}.',
    'Last week\'s review changed {playerName}\'s NIL deal at {school}: {previous} to {current}, a {difference} adjustment.',
    'Review-week NIL news at {school}: {playerName}\'s deal is {current}. It {change} by {difference}.')
forms('transactions.position-change','{school} ~ {playerName} from {oldPosition} to {newPosition} during offseason position changes.',
    'is moving','has moved','switches','is switching','shifts','has shifted','is shifting','moves','makes a switch for','makes a position change for')
forms('carry.training','{school}\'s {position} {playerName} ~ in {area} during {period}.',
    'improved','made progress','developed','showed improvement','took a step forward','has improved','has made progress','has developed','showed development','made gains')
forms('carry.move','{school} ~ {oldConference} to {newConference} for the new season.',
    'moves from','has moved from','switches from','has switched from','is moving from','makes the move from','changes leagues from','is switching from','transitions from','makes a conference move from')
add('carry.history','{school}: {oldConference} last year, {newConference} this season.',
    '{school} was in {oldConference} last season. Its current league is {newConference}.',
    'A different league for {school}: {oldConference} previously, {newConference} now.',
    'Conference context at {school}: last year\'s {oldConference} membership gives way to {newConference}.',
    '{school} enters this season in {newConference} after playing in {oldConference} last year.',
    'The league column changes for {school}. It was {oldConference}; it is now {newConference}.',
    'For {school}, the conference backdrop is now {newConference}. Last season it was {oldConference}.',
    'New conference context: {school} played in {oldConference} last year and is in {newConference} this year.',
    '{school}\'s current {newConference} membership differs from last year\'s {oldConference} listing.',
    'Last season, {oldConference}. This season, {newConference}. That is {school}\'s league change.')
forms('carry.team-move','New conference. Same {nickname}. ~ {newConference}. {hashtag}',
    'Hello,','Our new home is','Ready for life in','Our next chapter is in','We are now part of','Looking ahead to','We are headed into','Here we come,','See you in','Looking forward to')
forms('carry.rename','~ {oldConference} is now {newConference}.',
    'Conference name update:','New league name:','A name change on the conference map:','The league has a new name:','An updated conference name:','Conference rebranding:','On the conference map:','A new name for the league:','The updated league name is official:','A conference naming change:')
forms('carry.departure-destination','{position} {playerName} ~ {school} and is now on {destination}\'s roster following {period}.',
    'has left','moves on from','has moved on from','departs','has departed','is moving on from','leaves','is departing','has transferred from','moves away from')
forms('carry.departure-portal','Following {period}, {position} {playerName} ~ after leaving {school}. No destination is confirmed.',
    'is in the transfer portal','is listed in the portal','appears among portal entrants','is among the transfer-portal entrants','has a portal entry','is on the portal list','is part of the portal pool','is listed as a portal entrant','is in the pool of transfer recruits','has entered the transfer pool')
forms('carry.departure','After {period}, {position} {playerName} ~ {school}. No destination is confirmed.',
    'is no longer with','will not return to','has left','has moved on from','is moving on from','has departed','departs','is leaving','will move on from','leaves')

for key,label in [('bowl-invite','bowl matchup'),('playoff-invite','playoff matchup')]:
    forms('postseason.'+key,'~: {nickname} vs. {opponent} in {venue}. {hashtag}',
        'Our '+label+' is set','The '+label+' is official','The '+label+' is confirmed','The next stop is set','Postseason plans are locked in','The postseason pairing is set','The destination is official','The postseason stage is set','Our next matchup is confirmed','The postseason schedule is official')
forms('postseason.bye-team-opponent','~: {nickname} vs. {opponent} in Week {quarterWeek}. {hashtag}',
    'Quarterfinal matchup set','Our quarterfinal opponent is confirmed','The quarterfinal pairing is official','The next playoff game is set','Quarterfinal plans are locked in','The bye is followed by this quarterfinal','The quarterfinal stage is set','Our next playoff opponent is known','The quarterfinal matchup is official','Our quarterfinal game is confirmed')
forms('postseason.honors-team','~: {nationalCount} All-Americans and {conferenceCount} All-Conference honorees for the {nickname}. {hashtag}',
    'Postseason recognition','Honors for our guys','The selections are official','Proud of this group','Congratulations to our honorees','Postseason honors roll','Celebrating our selections','Recognition for the squad','Our postseason honorees','A proud moment for this group')
forms('postseason.award-multiple','{school}\'s {playerName} ~ {count} national defensive player honors this season.',
    'collects','has collected','earns','has earned','receives','has received','takes home','has taken home','is recognized with','finishes with')
forms('postseason.coach-offer','{school} ~ {coachName} for its {role} job.{contractTerm} Acceptance is pending.',
    'has an offer out to','has made an offer to','has extended an offer to','has put a contract offer to','has offered a contract to','has a contract offer out to','has sent an offer to','has a pending offer to','has presented an offer to','has a job offer out to')
forms('postseason.coach-renewal-offer','{school} ~ {role} {coachName}.{contractTerm} No acceptance is confirmed.',
    'has made a renewal offer to','has extended a retention offer to','has offered a new contract to','has a new contract offer out to','has put a renewal offer to','has sent a retention offer to','has presented a renewal offer to','has a pending renewal offer for','has a proposed new deal for','has a retention proposal for')

add('draft.pick',*[
    'Pick {draftPick}: the {nflTeam} select {position} {playerName}, {school}. Round {draftRound}.',
    'Round {draftRound}, No. {draftPick} overall: {position} {playerName} ({school}) to the {nflTeam}.',
    'The {nflTeam} take {school}\'s {position} {playerName} with pick {draftPick} in Round {draftRound}.',
    '{school}\'s {position} {playerName} is the {nflTeam}\'s choice at No. {draftPick}. Round {draftRound}.',
    'At pick {draftPick}, the {nflTeam} go with {position} {playerName} from {school}. Round {draftRound}.',
    'Selection {draftPick}, Round {draftRound}: {nflTeam} — {position} {playerName}, {school}.',
    '{position} {playerName}, {school}, is headed to the {nflTeam}. Pick {draftPick}, Round {draftRound}.',
    'The next name off the board: {position} {playerName} ({school}). {nflTeam}, No. {draftPick}, Round {draftRound}.',
    'No. {draftPick} belongs to {position} {playerName} of {school}. The {nflTeam} make the Round {draftRound} selection.',
    'The {nflTeam} add {position} {playerName} from {school} at No. {draftPick} overall in Round {draftRound}.'])
forms('draft.top-ten','TOP 10: ~ {position} {playerName}, {school}. Pick {draftPick} to the {nflTeam}.',
    'Off the board goes','The selection is','A top-ten call for','The name called is','The choice is','A first-round moment for','A top-ten landing for','A high first-round pick for','The top-ten selection is','The pick brings in')
forms('draft.irrelevant','MR. IRRELEVANT: ~ {position} {playerName} from {school}. The {nflTeam} make pick {draftPick}, the final selection.',
    'The last name called is','The final pick is','The final selection is','The draft ends with','The closing selection is','The last call goes to','The board closes with','The last selection is','The final name off the board is','The last pick goes to')

# Rank-only fallback copy stays short when a complete stat line is unavailable.
add('beat.heisman',
    '{school}\'s {playerName} {rankChange} in the Heisman race.',
    'Heisman watch: {school}\'s {playerName} {rankChange}.',
    '{playerName} of {school} {rankChange} on the Heisman watch.',
    'The current Heisman list has {school}\'s {playerName}: he {rankChange}.',
    '{school} Heisman update: {playerName} {rankChange}.',
    'In the Heisman picture, {school}\'s {playerName} {rankChange}.',
    'The Heisman ranking for {school}\'s {playerName}: he {rankChange}.',
    'On this week\'s Heisman watch, {playerName} of {school} {rankChange}.',
    '{school}\'s {playerName} remains in the Heisman discussion: he {rankChange}.',
    'A Heisman-watch check on {playerName} at {school}: he {rankChange}.')
add('playoff.rank','CFP No. {rank}: {school}.',
    '{school} is No. {rank} in the latest CFP rankings.',
    'The latest playoff rankings put {school} No. {rank}.',
    'CFP update: No. {rank} belongs to {school}.',
    '{school} checks in at No. {rank} on the CFP list.',
    'No. {rank} in this edition of the CFP rankings: {school}.',
    'The new CFP list has {school} at No. {rank}.',
    'Playoff rankings check: {school}, No. {rank}.',
    '{school} occupies the No. {rank} spot in the CFP rankings.',
    'This week\'s CFP ranking for {school}: No. {rank}.')
add('playoff.preview','College Football Playoff: {away} vs. {home}.',
    'The next playoff matchup is {away} vs. {home}.',
    'The CFP stage is set for {away} and {home}.',
    '{home} faces {away} in the College Football Playoff.',
    'In the playoff: {home} vs. {away}.',
    '{away} and {home} meet on the playoff stage.',
    'Playoff matchup confirmed: {home} and {away}.',
    '{away} vs. {home}. A place in the next playoff round is on the line.',
    'The College Football Playoff brings together {away} and {home}.',
    'Next on the playoff schedule: {away} vs. {home}.')



root.joinpath('Content/Runtime/event-variety-pack.json').write_text(json.dumps({'revision':'event-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
