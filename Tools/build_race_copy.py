"""Prewritten conference, bowl and rivalry coverage with calendar gates elsewhere."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.races.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])

forms('late.conference-race','The {conference} leaders: {leaders}. ~',
    'The standings are not a championship invitation yet.','The remaining results and tiebreakers still decide the matchup.',
    'That is the standings picture, with the title-game field still to settle.','League position is one step; an assigned championship matchup is another.',
    'There is still a title-race argument to settle on the field.','The championship pairing is not confirmed by the standings alone.',
    'Those are the programs leading the race right now.','The conference run-in still has a say in the final pairing.',
    'The late league games will decide how this turns out.','The title conversation is tightening around those records.')
forms('late.contender','{school}: {wins}-{losses} in {conference} play, No. {place} in the standings. ~',
    'The late league results carry extra weight now.','That is the current conference-race position.',
    'The title discussion starts with that league column.','There is a place in the title-race conversation to protect.',
    'The remaining conference games will decide the final position.','The late-season conference picture is worth watching.',
    'This is the current standing, not an assigned championship berth.','League play is still shaping the final title picture.',
    'The next league result matters to that position.','The title-race discussion is getting more immediate.')
forms('late.title-invite','~ {nickname} vs. {opponent} for the {conference} title in Week {championshipWeek}. {hashtag}',
    'Championship matchup confirmed:','The title date is set:','Next stop, the title game:',
    'The conference championship pairing is official:','A title-game place is confirmed:',
    'Championship plans are set:','Our title-game opponent is known:','The championship invitation is official:',
    'The trophy matchup is set:','The championship stage is ready:')
forms('late.title-history','{school} last won the conference title in {lastYear}. {opponent} is next in the {conference} championship. ~',
    'There is a long-term marker behind this matchup.','That title history adds context to the game.',
    'The program has a chance to end the wait.','The trophy has a history beyond this season\'s race.',
    'A new title would change that date.','The next game offers a chance to update the history.',
    'That is the historical backdrop for the title game.','The wait for another conference title reaches this matchup.',
    'There is a championship gap to close.','The title chase has a place in the program\'s longer story.')
forms('late.title-result','{school} ~ the {conference} championship, {score} over {opponent}.',
    'wins','claims','takes','secures','earns','has won','has claimed','brings home','takes home','comes away with')
pairs('late.title-fan',[
    '{school} and {opponent} for the {conference} title.','A {conference} championship on the line against {opponent}. {school} has the chance.',
    '{school} has {opponent} for the {conference} trophy.','The {conference} title comes down to {school} and {opponent}.',
    'A trophy game for {school}. {opponent} in the {conference} final.'],
    ['I have already decided I will be unbearable if we win','The timeline is going to hear about this one'])
forms('late.bowl-one-away','{school} is {wins}-{losses}, one win from six with {remaining} regular-season games left. ~',
    'Six wins would reach the usual bowl threshold, not guarantee a destination.','The next victory would reach six; the invitation is a later step.',
    'The immediate bowl-chase target is one more win.','A sixth win and an official bowl selection are separate developments.',
    'There is one clear near-term target in the bowl conversation.','The next win would change the eligibility discussion.',
    'The six-win mark is within one result.','Reaching six comes before learning an actual bowl assignment.',
    'One more win would put that threshold behind them.','The bowl chase has a clear next milestone.')
forms('late.bowl-position','{school} stands {wins}-{losses}, with the six-win threshold covered. ~',
    'No bowl matchup has been assigned yet.','The next question is the eventual postseason destination.',
    'The official bowl assignment comes later.','Where they land remains a postseason-selection question.',
    'A destination still has to be confirmed.','The bowl discussion turns from the win threshold to the eventual assignment.',
    'The actual invitation is a separate step.','The next postseason update needs to be an official selection.',
    'No confirmed bowl opponent yet.','The bowl picture is still waiting on the selection stage.')
forms('late.bowl-no-room','{school} is {wins}-{losses}, needing {needed} wins from {remaining} remaining games to reach six. ~',
    'There is no spare result in that chase.','The route to six requires winning out.',
    'Every remaining regular-season game is needed.','The bowl chase has no room for another loss.',
    'The arithmetic leaves one route to six.','Each of those remaining games matters to the threshold.',
    'The next loss would close the route to six wins.','The team needs the whole remaining slate.',
    'The six-win target requires a clean finish.','There is no cushion left on the schedule.')
forms('late.bowl-invite','~ {nickname} vs. {opponent} in {venue}. {hashtag}',
    'Bowl matchup set:','Our bowl plans are official:','Postseason destination confirmed:',
    'The bowl invitation is in:','The bowl pairing is official:','Our postseason trip is set:',
    'The next postseason stop:','A bowl date is confirmed:','Our bowl opponent is known:',
    'The postseason plan is locked in:')
forms('late.playoff-berth','{school} ~ against {opponent}.{historyDetail}',
    'has a confirmed opening-round playoff matchup','is in the playoff field with an opening-round game',
    'has an assigned first-round playoff game','is confirmed for the playoff opener',
    'has a first-round CFP matchup','enters the playoff field with a first-round pairing',
    'has an opening-round CFP assignment','has an official first-round playoff matchup',
    'has a confirmed first-round CFP game','is set for the opening playoff round')
forms('late.cfp-stakes','{school} is {wins}-{losses} and CFP No. {rank}, with {opponent} up next. ~',
    'The next result becomes part of the playoff argument.','That is a position to defend, not an invitation.',
    'The late-season resume gets another test.','The ranking and the next result are linked now.',
    'The playoff case still has a game to answer for.','The next matchup is the most immediate part of the playoff picture.',
    'There is little time left to change the resume.','The ranking alone does not secure a berth.',
    'The next game can change how the current position is viewed.','The field is not settled by this ranking alone.')
forms('late.title-appearance-history','{school} ~ since {lastYear}. {opponent} is the national-title opponent.',
    'reaches the national championship game for the first time','is back in the national final for the first time',
    'returns to the title game for the first time','makes its first national-final appearance',
    'is in the national championship game for the first time','has its first national-title-game appearance',
    'returns to the national championship for the first time','is back on the national-final stage for the first time',
    'gets to the national final for the first time','has made the national final for the first time')
for key in ['turnaround','regression']:
    forms('late.'+key,'{school}: {wins}-{losses} this season, after {priorWins}-{priorLosses} in {previousYear}. ~',
        'That is the year-to-year comparison.','The change belongs in the season assessment.',
        'The current record has a different backdrop from last year.','A concrete comparison with the previous finish.',
        'The next evaluation needs to include that prior season.','The year-over-year shift is part of this team\'s story.',
        'The previous finish provides a real benchmark.','That comparison reaches beyond one week\'s result.',
        'The full-season trend has changed.','The record looks different when placed beside the prior finish.')
forms('late.conference-change','{school}: No. {place}, {wins}-{losses} in the {conference}; No. {priorPlace}, {priorWins}-{priorLosses} in {previousYear}. ~',
    'A different position in the same league.','The conference picture has changed for this program.',
    'A substantial shift in league position.','The year-to-year league comparison is clear.',
    'The current standing has a different backdrop.','That is the change in the conference column.',
    'The standings tell a different story this year.','That is a useful comparison within the same conference.',
    'The league position is meaningfully different.','The program has a different place in the league race.')
forms('late.rivalry-team','{opponent} week. ~ {nickname}. {hashtag}',
    'You know what this means,','The rivalry is here,','This one matters,','Ready for this one,',
    'Our rivalry week is here,','Time to represent,','The week we know you circled,','Ready to make some noise,',
    'It is that week,','This game has its own meaning,')
pairs('late.rivalry-fan',[
    '{opponent} week. The {school} part of my brain is taking over.',
    'The {school}-{opponent} game is here. Nobody ask me to be neutral.',
    '{opponent} fans are talking. Good. {school} gets a game to answer.',
    'It is {opponent} week and I have very little interest in anybody else\'s game.',
    '{school} vs. {opponent}. The rivalry opinions are already warmed up.'],
    ['I will be unreasonable about this game','The result is going to live online for a year'])
forms('late.rivalry-stakes','{school} enters {opponent} week at {wins}-{losses} in {conference} play. ~',
    'The rivalry has more than a standings column attached.','The result comes with a year of bragging rights.',
    'The conference record is only part of the stakes.','That game carries its own weight beyond league position.',
    'The rivalry adds a different kind of pressure.','The standings matter, and so does hearing about the result afterward.',
    'The rivalry has a place in the story beyond the record.','The next result will matter to both the standings and the fan argument.',
    'There is a lot of meaning in this game for both sides.','League position is part of a bigger rivalry week.')
forms('late.conference-beef','{school} is {wins}-{losses} in the {conference}. ~',
    '{opponent} fans might want to leave room for somebody else in the conversation',
    '{opponent} fans talk like the league is their personal property',
    'The {opponent} victory speech can wait until the actual race is settled',
    'Every league argument turns into a {opponent} fan explaining why nobody else counts',
    '{opponent} fans are not the only people who can read the standings',
    '{opponent} does not get to own every conference conversation',
    'Some {opponent} fans have already awarded themselves the whole conference. Interesting',
    '{opponent} fans, please make a little room in your conference monologue',
    'The rest of the league exists even when {opponent} fans are posting',
    '{opponent} fans might enjoy a quick look at the other teams in the standings')
forms('late.fan-reply','{parentHandle} ~',
    '{school} fans are not taking confidence lessons from {opponent}',
    'Let the football talk. {school} has heard plenty from {opponent}',
    'The {school} side of this argument will be saving that post',
    '{opponent} fans have given {school} plenty of material already',
    '{school} is not signing off on the {opponent} victory speech',
    'Keep that confidence after {school} gets its chance on the field',
    '{school} fans can talk too. This is not just the {opponent} timeline',
    'Respectfully, {school} is not taking the {opponent} version as the final answer',
    'The {school} replies are going to remember this',
    '{opponent} fans have said enough. {school} gets a football answer')
forms('late.title-week','~ {nickname} vs. {opponent} for the {conference} title. {hashtag}',
    'Championship week:','One game for the trophy:','The title game is here:',
    'The conference trophy is on the line:','Our title-game week:','The championship stage is ready:',
    'The trophy game is next:','The title matchup has arrived:','A championship is at stake:',
    'Our conference final:')
pairs('late.title-week-fan',[
    'The {conference} trophy is on the line this week. {school} vs. {opponent}.',
    'No more scenarios. {school} and {opponent} for the {conference} title.',
    '{school} has a championship game this week. {opponent} on the other side.',
    'A {conference} title game for {school}. We are actually here.',
    '{school}. {opponent}. The {conference} championship. This week.'],
    ['Everything else can wait','I have absolutely no plans to be calm about this'])
forms('history.win-percentage','{school}\'s all-time win rate has moved {direction} {boundary}, on a {wins}-{losses}-{ties} record. ~',
    'Ties count as half a win in that calculation.','The calculation gives half a win for each tie.',
    'That rate counts a tie as half a victory.','The percentage treats ties as half-wins.',
    'Each tie receives half-win credit.','Half-win credit for ties is included.',
    'Ties are weighted at half a win.','The all-time calculation includes half a win per tie.',
    'That figure includes tie credit at one-half.','The win-rate calculation includes ties as half-wins.')

root.joinpath('Content/Runtime/race-variety-pack.json').write_text(json.dumps({'revision':'race-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
