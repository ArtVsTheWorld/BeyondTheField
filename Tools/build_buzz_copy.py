"""Prewritten postseason conversations, with speaker-specific phrasing."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.buzzcopy.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def pair(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])

forms('buzz.title-stage','~ {home} vs. {away} for the national championship.',
    'One game for everything.','The last game of the season.','The title comes down to this.',
    'Two teams left, one champion to decide.','The biggest night of the season is next.',
    'The national title is on the line.','No next round after this.','The season\'s final stage is set.',
    'One final matchup for the trophy.','The championship is one game away.')
forms('buzz.stage','~ {home} vs. {away} in the {eventLabel}.',
    'The postseason stage is set.','A season-defining matchup.','The next big game is here.',
    'The stakes have changed.','The next postseason test is set.','A major stop on the postseason schedule.',
    'The spotlight moves here.','A game with a lot riding on it.','The next stage is ready.','The postseason focus turns here.')
picks={
 1:['My {eventLabel} pick: {pick}. {lineContext}',
    'For the {eventLabel}, I lean {pick}. {lineContext}',
    '{pick} gets my pick in the {eventLabel}. {lineContext}',
    'Looking at the {eventLabel}: {lineContext} I am taking {pick}.',
    '{lineContext} My choice for the {eventLabel} is {pick}.'],
 2:['Putting my name on it: {pick} in the {eventLabel}. {lineContext}',
    '{pick}. That is my {eventLabel} pick. {lineContext}',
    'Save the post: I am taking {pick} in the {eventLabel}. {lineContext}',
    'Not hiding behind a maybe. {pick} is my {eventLabel} choice. {lineContext}',
    '{lineContext} Give me {pick} in the {eventLabel}.'],
 3:['Leaning {pick} in the {eventLabel}. {lineContext}',
    '{pick} for me in the {eventLabel}. {lineContext}',
    'My {eventLabel} pick is {pick}. {lineContext}',
    '{lineContext} So yes, I am picking {pick}.',
    'I have {pick} in the {eventLabel}. {lineContext}'],
 4:['My {eventLabel} projection: {lineContext}',
    'For the {eventLabel}, {lineContext}',
    '{eventLabel} matchup view: {lineContext}',
    'The {eventLabel} numbers lead me here: {lineContext}',
    'On the {eventLabel} matchup, {lineContext}'],
 5:['I lean {pick} in the {eventLabel}. {lineContext}',
    'The {eventLabel} pick is {pick}. {lineContext}',
    '{pick} is my choice for the {eventLabel}. {lineContext}',
    'For the {eventLabel}: {lineContext} My pick is {pick}.',
    '{lineContext} I have {pick} in the {eventLabel}.']}
for persona,leads in picks.items():
    ends=['{shapeContext}','The game still has to be played.'] if persona not in [2,3] else ['{shapeContext}','The replies should be extremely calm about this.']
    pair('buzz.pick-'+str(persona),leads,ends)
pair('buzz.team-pregame',[
    '{nickname}. {opponent}. The {eventLabel}.',
    'Our next stage: {opponent} in the {eventLabel}.',
    'The {nickname} are ready for {opponent} in the {eventLabel}.',
    '{eventLabel} week for the {nickname}. Opponent: {opponent}.',
    'A big stage for the {nickname}. {opponent} in the {eventLabel}.'],['Together. {hashtag}','Let us hear you. {hashtag}'])
pair('buzz.fan-pregame',[
    '{school} in the {eventLabel}. {opponent} on the other side.',
    'The {eventLabel} against {opponent}. {school} has the chance right here.',
    'I have stared at the {school}-{opponent} matchup for long enough. {eventLabel} time.',
    '{school} vs {opponent} in the {eventLabel}. I am not built to be casual about this.',
    '{eventLabel} week. {school}. {opponent}. Everything else on the calendar can wait.'],
    ['Please let this be our day','Somebody remind me to breathe during the game'])
pregame={
 'QB':['The {eventLabel} against {opponent}. Proud to share this stage with my team.',
    'Ready for {opponent} in the {eventLabel}. Grateful for this group.',
    'A chance to play {opponent} in the {eventLabel} with my teammates. Thankful for it.',
    'Looking forward to the {eventLabel}. {opponent} is the next challenge.',
    'The next game is {opponent} in the {eventLabel}. Ready with my guys.'],
 'Leader':['The {eventLabel}. {opponent}. Proud of the group that got us here.',
    'Ready to share the {eventLabel} stage with this team. {opponent} next.',
    '{opponent} in the {eventLabel}. Thankful for everyone who helped us reach this point.',
    'A big stage with my teammates. {opponent} in the {eventLabel}.',
    'The {eventLabel} against {opponent}. This group means a lot to me.'],
 'TeamPlayer':['Would not trade this group. {opponent} in the {eventLabel}.',
    'My guys and the {eventLabel}. {opponent} next.',
    'Proud of everybody who helped us get here. {opponent} in the {eventLabel}.',
    'Ready for the {eventLabel} with my brothers. {opponent} on the other side.',
    'We get to share this stage together. {opponent}. {eventLabel}.'],
 'Entertainer':['{eventLabel} with the guys. {opponent} next. Yeah I am ready',
    'Big stage, same guys. {opponent} in the {eventLabel}!',
    'I have waited long enough to play this one. {eventLabel}. {opponent}.',
    '{opponent} in the {eventLabel}. My phone is going to have to wait',
    '{eventLabel} time with my guys. {opponent}, see you out there'],
 'Intense':['{opponent}. {eventLabel}. Locked in with my guys.',
    'This is the stage we wanted. {opponent} in the {eventLabel}.',
    'Ready for {opponent}. Ready for the {eventLabel}.',
    'The {eventLabel} is here. {opponent} on the other side.',
    'With my brothers. {opponent} in the {eventLabel}. Let\'s get it.'],
 'Unpredictable':['{eventLabel}. {opponent}. Hope yall are watching',
    'The {eventLabel} with my guys. Yeah I am looking forward to {opponent}',
    'Big stage. {opponent}. The {eventLabel}. Keep the phone nearby',
    'People have talked enough. {opponent} in the {eventLabel} next',
    'My group chat knows how long I have waited for this. {opponent}. {eventLabel}.'],
 'Neutral':['Ready for {opponent} in the {eventLabel} with this team.',
    'The {eventLabel}. Grateful I get to be here with my teammates.',
    '{opponent} next in the {eventLabel}. Looking forward to it.',
    'A chance to share the {eventLabel} stage with my guys.',
    'Excited for the {eventLabel} against {opponent}.']}
watching={
 'QB':['Watching {home} vs. {away} in the {eventLabel}.','Tuning in for {home} and {away}. Big {eventLabel} stage.',
    '{home} vs. {away} in the {eventLabel} is a game I want to watch.','Looking forward to watching {home}-{away} in the {eventLabel}.',
    'The {eventLabel}: {home} and {away}. I will be watching.'],
 'Leader':['Respect the teams that got here. {home} vs. {away} in the {eventLabel}.',
    'A big stage for both groups. Watching {home}-{away} in the {eventLabel}.','Tuning in for {home} and {away}. The {eventLabel} is here.',
    '{home} vs. {away}. The {eventLabel} should be worth watching.','Looking forward to the {eventLabel} between {home} and {away}.'],
 'TeamPlayer':['Watching {home} vs. {away} in the {eventLabel}. Respect to the guys on both sides.',
    'The {eventLabel} with {home} and {away}. Looking forward to watching these groups.',
    '{home}-{away} in the {eventLabel}. Respect what it took for both teams to get here.',
    'Tuning in for the {eventLabel}. {home} and {away} earned this stage.',
    'Watching the {eventLabel}: {home} vs. {away}. Good opportunity for both groups.'],
 'Entertainer':['{home} vs {away} for the {eventLabel}. Yeah I am watching that',
    'The group chat is about to have a lot of {home}-{away} opinions. {eventLabel} time',
    '{eventLabel}. {home}. {away}. Do not ask me to make plans',
    'Got a spot on the couch for {home}-{away} in the {eventLabel}',
    '{home} vs {away}. The {eventLabel} has my attention'],
 'Intense':['{home}-{away} in the {eventLabel}. I want to see this one.',
    'Watching the {eventLabel}. {home} and {away} get to settle it.',
    '{home}. {away}. {eventLabel}. Nothing to talk about after they kick it off.',
    'Got to watch {home}-{away} in the {eventLabel}.','The {eventLabel} is here. {home} vs {away}. Locked in as a fan tonight.'],
 'Unpredictable':['{home} vs {away} in the {eventLabel}. The group chat will have opinions',
    'I will be watching {home}-{away} in the {eventLabel}. And probably typing too much',
    '{eventLabel}. {home} and {away}. My phone might be the second screen',
    'The {home}-{away} {eventLabel} is about to test some old predictions',
    'Got time for {home}-{away} in the {eventLabel}. The timeline should be interesting'],
 'Neutral':['Watching {home} vs. {away} in the {eventLabel}.','Tuning in for the {eventLabel}: {home} and {away}.',
    'Looking forward to {home}-{away} in the {eventLabel}.','The {eventLabel} is next. {home} vs. {away}. I am watching.',
    '{home} and {away} on the {eventLabel} stage. Ready to watch some football.']}
for personality,leads in pregame.items():
    pair('buzz.player-pregame-'+personality,leads,['Appreciate everybody supporting us.','Love sharing this with my team.'])
for personality,leads in watching.items():
    pair('buzz.watcher-player-'+personality,leads,['Big stage for both teams.','Football fan for this one.'])
forms('buzz.final','{winner} ~ {loser}, {score}, in the {eventLabel}.',
    'beats','defeats','gets past','wins against','prevails over','takes down','finishes ahead of','gets the better of','earns a win over','comes out on top against')
pair('buzz.team-champion',[
    '{winner}. {eventLabel} winners. {score} over {loser}.',
    'The {eventLabel} belongs to {winner}. {score} vs. {loser}.',
    'Winners on this stage. {winner} {score} over {loser} in the {eventLabel}.',
    'A win for the {nickname}. {eventLabel}: {score} over {loser}.',
    '{eventLabel} winners: {winner}. A {score} final over {loser}.'],
    ['Thank you for being part of this run. {hashtag}','For the whole {nickname} family. {hashtag}'])
forms('buzz.team-final-loss','Final in the {eventLabel}: {winner} defeats the {nickname}, {score}. ~',
    'Thank you for supporting this run.','We appreciate everyone who was with us.','Grateful for our players, staff and fans.',
    'Thank you for every step of the journey.','We appreciate the season-long support.','Thank you to our whole football family.',
    'Grateful for everyone behind this group.','Thank you for standing with us.','We appreciate all of our supporters.',
    'Thank you for helping make this run matter.')
pair('buzz.fan-champion',[
    '{school} won the {eventLabel}. {score}.','The {eventLabel} belongs to {school}. {score}.',
    '{score}. {school} actually won the {eventLabel}.','The {nickname} got it done in the {eventLabel}. {score}.',
    '{school}. {eventLabel} winners. Put the {score} final everywhere.'],
    ['I will never be normal about this','Remember this group forever'])
pair('buzz.fan-final-loss',[
    '{score} in the {eventLabel}. That hurts, {school}.','The {school} run ends in the {eventLabel}. {score}.',
    'So close for {school}. {score} in the {eventLabel}.','{school} loses the {eventLabel}, {score}.',
    'A {score} final in the {eventLabel}. The {nickname} got so close.'],
    ['Still proud of the run. Going to need some time though','Getting this far makes it hurt more, not less'])
pair('buzz.player-champion',[
    '{eventLabel} winners with my brothers.','We won the {eventLabel}. With this group.',
    'The {eventLabel} with my guys. What a feeling.','{eventLabel} winners. Love this team.',
    'Got it done on the {eventLabel} stage with my teammates.'],
    ['Appreciate everybody who believed in us.','Thankful for everybody who helped us get here.'])
pair('buzz.player-final-loss',[
    'Grateful for this team and our whole run.','Appreciate everybody who was with us through this.',
    'A lot of love for my teammates.','Thankful for the people I got to share this run with.',
    'The support throughout this run meant a lot.'],
    ['Thank you to everybody behind us.','Love this group and everyone who rode with us.'])
for persona in range(6):
    endings={0:['The result is official.','The stage has its winner.'],1:['The pregame arguments now have a result to answer to.','That settles this stage of the postseason.'],2:['Own your old predictions. The scoreboard is right there.','No moving the goalposts after the final.'],3:['The scoreboard is not accepting appeals.','Some old posts will need a quiet re-read.'],4:['The scoring pattern and box score give the detail behind the result.','The final is the result; the game details explain the path.'],5:['A defining result for this group.','The biggest opportunity on the schedule ends with this group on top.']}[persona]
    pair('buzz.final-analysis-'+str(persona),[
        '{winner} wins the {eventLabel}, {score} over {loser}.',
        '{eventLabel} final: {winner} over {loser}, {score}.',
        '{winner} takes the {eventLabel}. Final against {loser}: {score}.',
        'A {score} win for {winner} in the {eventLabel}.',
        '{score}. {winner} beats {loser} on the {eventLabel} stage.'],endings)
pair('buzz.outside-final',[
    'Not a {school} game, but respect to {winner}. {score} in the {eventLabel}.',
    'The {eventLabel} goes to {winner}, {score}. Respect from this {school} fan.',
    'Watching as a {school} fan: {winner} earned the {eventLabel}, {score}.',
    '{winner} won the {eventLabel}, {score}. Credit where it is due from the {school} side.',
    '{score} for {winner} in the {eventLabel}. Not my {school} team, but that deserves respect.'],
    ['That group earned its moment','A big stage, a big result'])
pair('buzz.watcher-fan',[
    '{school}\'s season is done. For the {eventLabel}, I am borrowing {pick}.',
    'No more {school} games, so {pick} gets my support in the {eventLabel}.',
    'A temporary {pick} fan for the {eventLabel}. The {school} season is over.',
    'From the {school} side, rooting for {pick} in the {eventLabel}.',
    'The {school} schedule is finished. {pick} is my team for the {eventLabel}.'],
    ['A one-game arrangement','The regular fan arguments can resume afterward'])
forms('buzz.pick-reply','{parentHandle} ~',
    '{school} fans have a different prediction. Let them play first',
    'Writing {school} off already? Save a little room for the actual game',
    '{school} has a vote in how this ends too',
    'We can disagree about {school}. The field will settle it',
    'I will be coming back to this after the {school} game',
    'The {school} side of the argument is not signing off on that prediction',
    '{school} fans are going to have this bookmarked',
    'I would enjoy seeing {school} make this post look silly',
    'The {school} group chat respectfully disagrees',
    'Fine. {school} can give the answer on the field')

root.joinpath('Content/Runtime/buzz-variety-pack.json').write_text(json.dumps({'revision':'buzz-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
