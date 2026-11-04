"""Prewritten personal reactions; Barstool and individual fans remain distinct."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.fancopy.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])

pairs('player.rivalry',[
    'Rivalry W with my guys.','That rivalry win means a lot to this group.',
    'Bragging rights with my brothers.','A win in this rivalry is a good feeling.',
    'Glad we could share this rivalry win with our fans.'],
    ['Appreciate everybody who was with us. {hashtag}','Love this team. {hashtag}'])
performance={
 'Leader':['Proud of how my teammates showed up.','Grateful for the guys who made this possible.',
    'A team win to go with a good day.','Glad we could share that win with our fans.',
    'Nothing about a game like that is just one person.'],
 'Intense':['{statLine}. Team W.','Got the win. Enjoyed that one.','A good day with my guys.',
    'The W was what we came for.','Happy with the result. Love this group.'],
 'Entertainer':['{statLine} and a win. Not a bad day lol','The highlights might get watched a few times.',
    'Got the W. My mentions are more fun tonight.','A pretty good day to be out there with my guys.',
    'I am keeping this game in the camera roll.'],
 'TeamPlayer':['My guys made a lot of this happen.','Love when we get to enjoy a win together.',
    'Shoutout to everybody doing their part.','A lot of teammates deserve love after that game.',
    'Could not do this without the people around me.'],
 'Unpredictable':['{statLine}. And we won. Interesting evening for my mentions.',
    'Got the W. I might leave my phone on for a while.','Some of the pregame opinions got quiet.',
    'I am enjoying the final exactly where it is.','A win and a few saved screenshots. Good day.'],
 'Neutral':['Good win with this group.','Happy we could get this one together.',
    'Grateful for another win with my teammates.','Appreciate the guys around me.',
    'Glad we got to share a win with our fans.'],
 'QB':['Proud of my teammates making plays.','A good team win.','Thankful for the guys around me.',
    'Appreciate everyone who helped us get this one.','Grateful we could get the win together.']}
for personality,leads in performance.items():pairs('player.performance.'+personality,leads,['Appreciate all the support. {hashtag}','Love representing {school}. {hashtag}'])
pairs('fan.narrow_win',[
    'The {nickname} won by {margin}.','A {margin}-point {school} win.','{school} got it by {margin}.',
    'The final margin for the {nickname}: {margin}.','{school} won another close one by {margin}.'],
    ['The scoreboard does not record how stressed I was','I would enjoy a slightly easier watch next time'])
pairs('fan.win',[
    'The {nickname} won.','A {school} W.','Good day to be a {school} fan.',
    'A win for the {nickname}.','{school} got the result.'],
    ['Suddenly the rest of the weekend looks better','I have several people to send this to'])
pairs('fan.rivalry',[
    '{school} {ownScore}, {opponent} {opponentScore}.','The {nickname} beat {opponent}.',
    'A rivalry win for {school}.','{school} over {opponent}. Save that score.',
    '{opponent} fans, the {nickname} won this one.'],
    ['The receipts are going to last a year','No need for anyone on the other side to rush back online'])
pairs('fan.loss',[
    '{school} lost {score} to {opponent}.','A {score} loss for the {nickname} against {opponent}.',
    '{opponent} {opponentScore}, {school} {ownScore}.','The {nickname} fell {score} to {opponent}.',
    '{school} loses to {opponent}. That {score} final is going to sit with me.'],
    ['Still a fan tomorrow. Extremely frustrated today','My phone and I need a little time apart'])
pairs('fan.picks',[
    'Two picks from {playerName} in a {school} loss.','{school} lost with two interceptions from {playerName}.',
    '{playerName} threw two picks. A rough part of this {school} loss.',
    'Those two {playerName} interceptions hurt in a loss.','Two interceptions for {playerName} and no {school} win.'],
    ['I want better for this team','Hard to enjoy the rest of the games after that'])
pairs('fan.performance',[
    '{playerName}: {statLine}.','What a day from {playerName}. {statLine}.',
    '{statLine} for {playerName}.','Give {playerName} some noise after {statLine}.',
    '{playerName} put up {statLine}.'],
    ['That is getting sent to several people','Keep that player involved'])
pairs('fan.breakout',[
    '{playerHandle}: {statLine}.','{statLine} from {playerHandle}.','A big day from {playerHandle}. {statLine}.',
    '{playerHandle} gave us {statLine}.','Some love for {playerHandle}: {statLine}.'],
    ['That performance deserves a few more posts','Please keep finding ways to get that production'])
forms('fan.poll_reply','{analystHandle} ~',
    'No. {pollRank} feels about right? The {nickname} fans have a different view',
    'The {nickname} keep winning and I am supposed to be thrilled with No. {pollRank}?',
    'I have a different idea of where {school} belongs than No. {pollRank}',
    'Respectfully, No. {pollRank} is not the {school} ranking I wanted to read',
    'The {school} side of this argument is going to need a little more convincing',
    'No. {pollRank} for the {nickname}. You knew the replies were coming',
    'I watched {school} too. We are not agreeing on No. {pollRank}',
    'The {nickname} have given us a reason to want better than No. {pollRank}',
    'No. {pollRank}? I have several {school} arguments ready',
    'We can disagree about {school}. No. {pollRank} does not feel generous to me')
forms('fan.holiday','{holiday} and college football. ~',
    'My plans are made','The schedule has my attention','That is the day sorted out',
    'I am not volunteering for other plans','There is a game to fit the day around',
    'The rest of the calendar can work around kickoff','No further entertainment required',
    'Give me the games and something to eat','I know how I want to spend the day','The game schedule wins this argument')
forms('fan.rank_up','{parentHandle} No. {rank} for the {nickname}, from No. {previousRank}. ~',
    'The screenshots are going out','I have people to remind about last week\'s opinions',
    'Everybody keep the same energy','A very enjoyable poll notification',
    'The {school} group chat likes this update','I will be posting about this more than necessary',
    'I am trying to stay normal about it','I have not forgotten the old rankings arguments',
    'A good day to check the rankings','That number looks good on the timeline')
forms('fan.preview.rivalry','{parentHandle} {opponent} week for the {nickname}. ~',
    'If you need me, I will be arguing with strangers','The rest of my calendar can wait',
    'I am already being annoying about this game','The receipts folder is ready',
    'Nobody is asking me to be neutral','I have had enough of the other side\'s predictions',
    'The usual football opinions just got louder','I will remember everything said this week',
    'This one has my full attention','There is a year of bragging rights attached to this')

pairs('fanclub.win',[
    '{school} beat {opponent}, {score}.','The {nickname} got the W over {opponent}, {score}.',
    'A {score} {school} win against {opponent}.','{school} over {opponent}. That {score} final looks good.',
    '{score}. {school} takes care of {opponent}.'],
    ['Opening the group chat like we called the plays','Good work, everybody. The memes can be happy ones'])
pairs('fanclub.rivalry-win',[
    '{school} {score} over {opponent}. Rivalry receipts are ready.',
    '{opponent} fans, {school} won {score}.','A {score} rivalry win for {school}.',
    '{school} beat {opponent}. Put that {score} final everywhere.',
    'The {school}-{opponent} result: {score} for our side.'],
    ['The bragging-rights subscription lasts a year','The posting department is going to be very busy'])
pairs('fanclub.loss',[
    '{school} falls {score} to {opponent}.','A {score} loss to {opponent} for the {nickname}.',
    '{school} loses to {opponent}, {score}.','The {nickname} did not get it against {opponent}. {score}.',
    '{score} against {opponent}. A tough result for {school}.'],
    ['Still supporting the team. Not pretending that was fun','See you next game. Will need a minute first'])
pairs('fanclub.bad-loss',[
    '{school} {score} against {opponent}. The memes cannot cover this one.',
    'A rough {score} result for {school} against {opponent}.','{opponent} beat {school}, {score}. That needs an answer.',
    '{school} loses {score}. {opponent} gave us plenty to be frustrated about.',
    '{score} vs. {opponent}. A bad day for the {nickname}.'],
    ['The football has to look a lot better next time','Supporting this team includes asking for better'])
pairs('fanclub.tie',[
    '{school} and {opponent}: {score}. A tie.','The {school}-{opponent} game ends level, {score}.',
    'A {score} tie for {school} vs. {opponent}.','Neither {school} nor {opponent} won. {score}.',
    '{school} ties {opponent}, {score}.'],
    ['The group chat needs a new reaction picture','Not sure which folder the memes go in now'])
pairs('fanclub.rivalry-week',[
    '{opponent} week for {school}.','The {school}-{opponent} rivalry is here.',
    'A very normal and relaxed {opponent} week for {school}. Obviously.',
    '{school} fans, the {opponent} game is the one on the calendar.',
    'The {nickname} have {opponent} this week.'],
    ['Please hydrate before being impossible in the replies','The rivalry posting schedule is officially active'])

root.joinpath('Content/Runtime/fan-variety-pack.json').write_text(json.dumps({'revision':'fan-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
