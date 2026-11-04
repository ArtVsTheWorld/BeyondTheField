"""Prewritten retrospectives and context without adding unobserved details."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.retrospective.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])

forms('review.title-insider','{winner} ~ after a {score} win over {loser}. The national championship is settled.',
    'finishes on top','is the national champion','claims the title','takes the national title','ends the season as champion',
    'wins the national championship','stands as national champion','closes a championship season','earns the national title','finishes a championship run')
pairs('review.title-debate',[
    '{winner} won the championship, {score}. Losing the final does not erase {loser}\'s entire season.',
    '{loser} came up short against {winner}, {score}. Getting to the final still counts for something.',
    'The title belongs to {winner}, {score}. Calling {loser} a bad team after reaching the final is a bad argument.',
    '{winner} earned the title. {loser} lost the last game, {score}, after a run to the final.',
    'A {score} title-game loss for {loser}. Give {winner} the title without pretending the other finalist had a worthless season.'],
    ['Judge the whole year.','Credit the champion and evaluate the runner-up fairly.'])
forms('review.title-film','~ {winner} over {loser}, {score}, for the national title. {turningPoint}',
    'How the final unfolded:','The title-game detail:','Looking back at the final:','The championship in context:',
    'From the championship review:','The final beyond the score:','Reviewing the title game:','Inside the final:',
    'The title-game picture:','The championship recap:')
forms('review.champion-season','{school} ~ at {record}{coachDetail}, with the national championship.',
    'finishes the season','closes the season','ends the year','completes the year','finishes its schedule','wraps up the season',
    'ends its run','completes its run','closes the year','wraps up the year')
forms('review.runnerup-season','{school} ~ at {record}{coachDetail}, one win short of the national title.',
    'finishes the season','closes the season','ends the year','completes the year','finishes its schedule','wraps up the season',
    'ends its run','completes its run','closes the year','wraps up the year')
forms('review.title-turnovers','~ {school} had {ownGiveaways} giveaways; {opponent} had {otherGiveaways}. Final: {winner}, {score}.',
    'Championship ball security:','The turnover comparison from the final:','A title-game possession detail:',
    'Giveaways in the championship:','Reviewing the final\'s ball security:','The title-game turnover line:',
    'Possessions in the final:','The championship giveaway numbers:','Ball security on the final stage:',
    'From the title-game box score:')
forms('review.title-player','~ {school}\'s {playerName}: {line}.',
    'In the national championship,','The title-game line for','Championship production from','A final-game performance from',
    'The national-title stat line for','On the championship stage,','In the final,','A look back at the final for',
    'From the national-title game,','The championship performance by')
forms('review.title-roster','~ {school} has {seniors} listed seniors and {nonSeniors} non-seniors. These are class counts, not confirmed return decisions.',
    'The post-title roster question:','After the championship,','Looking at the next roster:',
    'The roster continuity picture:','A post-championship roster snapshot:','As the championship gives way to the offseason,',
    'The next roster-building context:','The class balance after the title:','For the next roster cycle,','A starting point for roster planning:')
add('review.calendar',
    'The season is done. No next-game preview, just championship arguments and offseason roster questions.',
    'No more college football games this season. The title is settled. The timeline arguments are not.',
    'The final is over and there is no game next weekend. Welcome to the roster-refresh part of the year.',
    'College football has reached the part where everyone says they need a break and checks recruiting news ten minutes later.',
    'Another season in the books. The championship conversation will last longer than the celebration.',
    'The games are over. Who stays, who leaves and who improves will now take over the timeline.',
    'No next Saturday on the schedule. Just the offseason and several months of convincing ourselves it will go quickly.',
    'The title game ends the season. Somehow it also starts at least three new arguments about next year.',
    'The final whistle has gone on the whole season. Time for roster decisions and people announcing that next year is their year.',
    'No more games to preview this year. The championship is decided and the offseason conversation is officially here.')
pairs('review.fan-calendar',[
    'No college football left this season. {school} news is going to have to carry my weekends.',
    'The whole season is actually over. Already miss {school} football.',
    'No next game. No next Saturday. Somebody send me a {school} recruiting update.',
    'College football is done and apparently I have to make normal weekend plans. Miss the {nickname} already.',
    'Another season gone. {school} football had me stressed and I would immediately sign up for more.'],
    ['This offseason better move fast','See everybody in the recruiting replies'])
forms('review.retrospect','~ {school} finished {record}. {expectationNote}',
    'The season in retrospect:','The full-year assessment:','Looking back at the year:','The final evaluation starts here:',
    'The season-end picture:','The full-season result:','The season review:','Evaluating the finish:',
    'The final record in context:','The completed season:')
for key,verb in [('hired','hired'),('retained','retained'),('fired','dismissed')]:
    forms('review.staff-'+key,'~ {school} '+verb+' {coachName} as {role} during this cycle.',
        'Coaching-cycle recap:','Looking back at the staff moves:','A confirmed change from the cycle:',
        'One staff decision to remember:','The carousel in review:','A coaching-cycle note:',
        'The staff picture in retrospect:','From the coaching-cycle recap:','Reviewing the staff decisions:',
        'A staff move from this cycle:')
forms('review.staff-departed','~ {school} {role} {coachName} {action} during this cycle.',
    'Coaching-cycle recap:','Looking back at the staff moves:','A confirmed departure from the cycle:',
    'One staff decision to remember:','The carousel in review:','A coaching-cycle note:',
    'The staff picture in retrospect:','From the coaching-cycle recap:','Reviewing the staff decisions:',
    'A staff move from this cycle:')
forms('review.retention-watch','{school}\'s {playerName} ~. There is no confirmed portal entry.',
    'is a name to monitor in roster-retention discussions','belongs on the offseason retention watch',
    'is a player worth keeping an eye on during roster decisions','is part of the retention conversation',
    'is a retention situation to follow','is one of the roster situations to monitor',
    'deserves attention in the retention picture','is a player to watch as retention decisions develop',
    'is on the retention radar','is a name to follow during the roster-decision period')

forms('ending.comparison','~ {school} finished {record}, after {priorWins}-{priorLosses} in {previousYear} as a member of {previousConference}.',
    'Year-over-year check:','The season comparison:','Putting the finish in context:','A look at the previous finish:',
    'The two-season view:','The record comparison:','Looking back one year:','The season-end comparison:',
    'The year-to-year result:','A previous-season reference:')
pairs('ending.fan-accountability',[
    '{school} finished {record}. I want to hear what {coachName} is actually changing.',
    '{record}. Coach {coachName} has to give {school} fans something concrete to believe in.',
    'The {school} season ended {record}. {coachName}, what is the actual plan?',
    '{school}: {record}. I have questions for {coachName} about what will be different next fall.',
    '{coachName} and {school} end at {record}. The offseason needs some actual answers.'],
    ['Less slogan, more football','I am tired of the same speech'])
forms('ending.fan-qb','{school} ends {record}. {playerName}: {touchdowns} passing TD, {interceptions} INT. ~',
    'That quarterback conversation is not going away.','The offseason does not erase those numbers.',
    'The staff has to look at the whole passing-game picture.','Those numbers deserve a real offseason conversation.',
    'It is fair for fans to ask what changes.','I am not pretending the season ending answers the quarterback questions.',
    'I want the next passing-game discussion to include a plan.','Still rooting for the team. Still have questions.',
    'There is a real passing-game discussion behind that finish.','The next season needs a better answer.')
forms('cycle.team-reset','~ {nickname} fans. Building the next chapter together. {hashtag}',
    'Thank you,','Grateful for you,','We appreciate you,','All our thanks to you,','Your support matters,',
    'Thank you for being with us,','We appreciate the season-long support,','Thank you for standing with us,',
    'Proud to represent you,','Thank you for every step of the season,')
pairs('cycle.fan-standards',[
    '{record} was not what we wanted at {school}.','The {school} season ended {record}. I expected more.',
    '{school}: {record}. There is work to do.','A {record} finish for {school}. This cannot be the whole plan.',
    '{record}. Love the {nickname}. That was below what I wanted from this season.'],
    ['Need a real roster plan this offseason','Next year needs to look different'])
pairs('cycle.fan-future',[
    '{school} football is done and I am checking recruiting news already.','The {nickname} season ended and my next hobby is apparently roster speculation.',
    'No more {school} games. Time to become unreasonably invested in the next roster.',
    'The {school} offseason is here. I am already refreshing the timeline.',
    'Miss {school} football. I will substitute way too many recruiting opinions.'],
    ['This is going to be a long offseason','Next year has my attention already'])
forms('cycle.player-reset','~ Grateful for my teammates and looking forward to being back.',
    'Thank you for supporting us this season.','Appreciate everyone who was with us this year.',
    'A lot of love for the people behind us.','Thank you to everyone who kept showing up for us.',
    'The support this season meant a lot.','Thankful for everybody who rode with us.',
    'Appreciate all the support this year.','Grateful for the people who kept believing in us.',
    'Thank you to our fans and our families.','Love everybody who supported this group.')
forms('cycle.fan-loss-standard','{school} loses {score} to {opponent}. {expectationNote} ~',
    'We can ask for better without giving up on the team.','Pretending that is fine does not help anyone.',
    'I would like a different conversation after the next game.','Loyalty does not require enjoying this result.',
    'It is fair to talk about what needs to change.','The next step has to look better than this.',
    'I want more from the team, not more excuses.','We are allowed to care and be frustrated.',
    'That should be the start of the discussion.','The standard still matters after a bad result.')
for family in ['cycle.context-turnaround','cycle.context-regression']:
    forms(family,'~ {school}: {wins}-{losses} this season; {priorWins}-{priorLosses} last year. {expectationNote}',
        'A year-over-year look:','The two-season comparison:','The record in context:','Looking back a season:',
        'The year-to-year shift:','Comparing the finishes:','The season-to-season picture:',
        'A change in the record:','The result across two years:','The latest season comparison:')
forms('narrative.game','~ {winner} over {loser}, {score}. {turningPoint}',
    'How it unfolded:','The game beyond the final:','The recap:','The story of the game:',
    'A closer look at the result:','The turning point:','Inside the final:',
    'Looking back at the game:','The scoring story:','The game in context:')

root.joinpath('Content/Runtime/retrospective-variety-pack.json').write_text(json.dumps({'revision':'retrospective-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
