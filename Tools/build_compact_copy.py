"""Authored compact alternatives for incomplete optional facts or long bodies.

These are lower-priority copy, never fabricated data or quiet-week filler.
"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.compact.'+str(i+1),'body':line,'fallback':True} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pair(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])
forms('team.win','~ {score}. {hashtag}',
    'A {nickname} win.','{nickname} win!','Final. {nickname} on top.','Win secured for the {nickname}.',
    'That is a {nickname} W.','A W for the {nickname}.','{nickname}. Winners today.',
    'Final score, {nickname} win.','The {nickname} take the win.','A winning finish for the {nickname}.')
forms('beat.team_stats','~ {school}: {passingYards} passing yards, {rushingYards} rushing yards, {firstDowns} first downs and {giveaways} giveaways against {opponent}.',
    'The box-score line for','Checking the game totals for','The offensive numbers for','From the game book for',
    'The final statistical line for','A look at the totals for','Inside the result for','The recorded numbers for',
    'Reviewing the production for','The game in numbers for')
pair('fan.rivalry',[
    'A rivalry win for {school}.','{school} won the rivalry game.','Rivalry bragging rights for {school}.',
    'The rivalry result belongs to {school}.','{school} fans have the rivalry receipts.'],
    ['I will be keeping these for a year','The other side can take its time getting back online'])
forms('fan.loss','~ {opponent} {opponentScore}, {school} {ownScore}.',
    'Reading this final hurts.','I wanted a much better ending.','A rough final to sit with.',
    'Well, that is the score I have to live with.','Not a final I enjoyed.','My weekend did not need this.',
    'The loss still looks bad typed out.','This one is going to bother me.','Still a fan. Very frustrated.',
    'A final to be unhappy about.')
pair('fan.poll_reply',[
    '{analystHandle} We have not forgotten {school}.','{analystHandle} {school} fans are reading this too.',
    '{analystHandle} I have a few thoughts from the {school} side.',
    '{analystHandle} Still backing {school}.','{analystHandle} {school} deserves a fair look.'],
    ['I am keeping the receipts','We can revisit this after more football'])
replies={
 'reply.fan.recruit_program_changer':[
    'This is a huge pickup for us','Somebody check on my group chat','Did not think I would get to post this one',
    'That is a big deal for this program','This deserves way more noise','I have been refreshing for this exact news',
    'A pickup worth being loud about','Give the staff some love for getting this done','My expectations just got a little less reasonable','I am going to enjoy this announcement for a while'],
 'reply.fan.flip':[
    'Changing schools after all that still stings','Well there goes the graphic I saved','The commitment post did not age well',
    'Not the recruiting update I wanted','I would have enjoyed literally any other update','Moving on, but I am definitely annoyed',
    'Some of us had already gotten excited about this','That recruitment took a turn I did not enjoy',
    'The group chat is going through it','Hope the next commitment comes with less drama'],
 'reply.fan.coach_bad':[
    'The staff needs a better answer than that','I want the coaching decisions to make sense on the field',
    'Getting tired of having this coaching conversation','The fans are allowed to ask for better football',
    'Please give us a plan that actually works','There is plenty for the staff to answer for',
    'I would love a reason to defend the coaching','Someone needs to explain that decision',
    'This team deserves better answers from the staff','Hard to keep giving the coaches a pass'],
 'reply.fan.player_bad':[
    'We need better from that spot','Still pulling for the guy. That was rough','Criticism is fair after that',
    'I want him to succeed. I also want much better football','That cannot keep happening','The frustration is pretty earned here',
    'There is a lot to improve from that performance','Not going to pretend I enjoyed watching that',
    'Hope he gives us a better answer next time','Backing the team does not mean calling every performance good'],
 'reply.fan.upset':[
    'This is why I watch the games','Someone save the pregame predictions','A lot of confident people got quiet',
    'What an unbelievable result','I need to see the reactions to this','College football is so ridiculous sometimes',
    'The final score has some explaining to do','That is going straight into the group chat',
    'Going to be a fun night reading the replies','The people who already called this game might want to log off'],
 'reply.fan.award':[
    'Earned it. Give the guy his flowers','Love seeing our guys get recognized','Very happy to see this award',
    'That one is getting shared around','Our fans have been saying it','A good day to cheer for this player',
    'Congrats. That recognition means something','I will be making some noise about this one',
    'Glad the work got noticed','A little recognition for a lot of good football']}
for key,lines in replies.items():add(key,*['{parentHandle} '+line for line in lines])
forms('playoff.rank_move','~ {school}: CFP No. {previousRank} to No. {rank}.',
    'The committee update for','A CFP ranking change for','New playoff-picture position for','The latest CFP move for',
    'Comparing the committee lists for','Current CFP news for','The ranking update on','The CFP change at',
    'A new committee placement for','This week on the CFP board for')
pair('late.fan-reply',[
    '{parentHandle} {school} fans have opinions too.','{parentHandle} Still backing {school}.',
    '{parentHandle} {school} heard that.','{parentHandle} Let us see what {school} does on the field.',
    '{parentHandle} I have my {school} receipts ready.'],
    ['Let the football settle the argument','No shortage of confidence on this side'])
pair('late.title-week-fan',[
    'Championship week for {school}.','{school} has a conference title to play for.',
    'A conference trophy is on the line for {school}.','{school} fans have a championship game this week.',
    'The conference title game includes {school}.'],
    ['I am trying to keep the nerves under control','The group chat is not going to be reasonable'])
for kind in ['passing','rushing']:
    unit='pass attempt' if kind=='passing' else 'carry'
    a=['A rate comparison:','Matchup efficiency check:','A useful matchup detail:','The efficiency figures:',
       'Looking at rates:','A closer comparison:','The matchup in rates:','One way into the matchup:',
       'An efficiency reference point:','The production-rate matchup:']
    key='matchup.'+kind+'-preview-rates'
    base=f'{{school}} produces {{attackRate}} yards per {unit}; {{opponent}} allows {{defenseRate}}.'
    lines=[lead+' '+base+' {interpretation}' for lead in a]
    lines += [lead+' '+base+' Per-game yardage: {attack} produced, {defense} allowed.' for lead in a]
    add(key,*lines)
pair('fanclub.rivalry-win',[
    '{school} won the rivalry game, {score}.','A {score} rivalry W for {school}.',
    '{school} on top in the rivalry. {score}.','Rivalry score: {school} win, {score}.',
    '{score}. {school} fans have their rivalry result.'],
    ['Receipts department is open','The bragging rights are going to get used'])
for key,leads in {
 'ending.player.senior':['Thank you, {school}.','Grateful for my time at {school}.','A lot of love for everybody at {school}.','Appreciate the people who made {school} home.','Always going to be grateful for {school}.'],
 'ending.player.senior-perfect':['An undefeated final season with {school}.','Leaving {school} after an unbeaten year means a lot.','A perfect last season with my {school} teammates.','My last season at {school} ended unbeaten.','An unbeaten finish to my time at {school}.'],
 'ending.player.thanks':['Thank you for being with us, {school}.','Grateful for everybody supporting {school}.','Love representing {school}.','Appreciate the support all season, {school}.','A lot of love for the {school} fans.'],
 'ending.player.perfect':['An unbeaten season for {school}.','{school} finished undefeated. Proud of my teammates.','A perfect year with this {school} group.','An undefeated finish with my guys at {school}.','{school} went unbeaten. That means a lot.']}.items():
    pair(key,leads,['Love the people who shared this season with me','Appreciate everyone who was there for us'])
for key in ['transactions.nil-change','transactions.nil-review']:
    leads=['Compensation update:','An NIL update:','The latest NIL figure:','A compensation note:',
       'NIL news:','Reviewing the compensation figures:','A new compensation figure:',
       'The NIL ledger update:','A closer look at the deal:','From the NIL review:']
    lines=[x+" {school}'s {playerName}: {previous} previously, {current} now." for x in leads]
    lines += [x+" {school}'s {playerName}: {current} now, a {difference} change." for x in leads]
    add(key,*lines)
for persona in range(1,6):
    leads={1:['My pick:','I lean','My choice is','I am taking','The pick for me:'],
       2:['Put me down for','Save the post:','My call is','I am backing','Give me'],
       3:['I have','Leaning','My pick is','Going with','I am taking'],
       5:['My selection:','I lean','My choice is','I am taking','The pick for me:']}
    if persona==4:
        forms('buzz.pick-4','~ {eventLabel}: {lineContext}',
            'My matchup projection for the','The matchup numbers for the','A statistical look at the',
            'My efficiency read for the','The comparison entering the','Looking at the matchup for the',
            'My projection entering the','The evidence behind my read of the','My forecast for the','The numbers behind the')
    else:pair('buzz.pick-'+str(persona),[x+' {pick}. {lineContext}' for x in leads[persona]],
        ['Looking forward to seeing this one played.','The result still has to be earned.'])
pair('buzz.player-pregame-Neutral',[
    'Ready for the {eventLabel}.','The {eventLabel} with my guys.','Grateful to play in the {eventLabel}.',
    'Looking forward to the {eventLabel}.','The {eventLabel}. A big chance with this group.'],
    ['Thankful for all the support','Love my teammates'])
forms('buzz.team-champion','~ {nickname} over {loser}, {score}, in the {eventLabel}. {hashtag}',
    'A win on this stage.','The final is ours.','One for our fans.','A win together.','A winning finish.',
    'The result we came for.','Thank you for being with us.','Enjoy this one.','The work paid off.','A team win.')
for persona in range(6):
    leads={0:['The final:','The result is in:','Final from the big stage:','The game is settled:','On the final scoreboard:'],
    1:['The result to discuss:','The winner tonight:','A result that counts:','The final word on the field:','The game has its winner:'],
    2:['The football settled it:','Save the actual result:','No debating the final:','The scoreboard answer:','The result is what matters:'],
    3:['Well, we have a final:','The group chat has its answer:','The actual football part is settled:','A final for the timeline:','Here is the result:'],
    4:['The scoreboard starting point:','The result before the film review:','Beginning with the final:','The game-book result:','The final to evaluate:'],
    5:['The result to evaluate:','The final before the next assessment:','One game now in the books:','The outcome to build from:','The final result to review:']}[persona]
    pair('buzz.final-analysis-'+str(persona),[x+' {winner} wins {score} in the {eventLabel}.' for x in leads],
        ['The winning team earned this result.','A major game with a result now on the board.'])
forms('carry.departure-fcs','~',
    "{playerName} is moving on from {school}. The next football chapter is at the FCS level.",
    "After leaving {school}, {playerName} is continuing his football career in the FCS.",
    "A new chapter for {playerName} after {school}: continuing at the FCS level.",
    "{school} departure {playerName} is taking his next football opportunity in the FCS.",
    "{playerName}'s next step after {school} is FCS football.",
    "From {school} to a new football chapter: {playerName} is continuing at the FCS level.",
    "{playerName} moves on from {school} for an opportunity in FCS football.",
    "The next chapter for former {school} player {playerName} comes in the FCS.",
    "After his time at {school}, {playerName} will keep playing at the FCS level.",
    "FCS football is next for {playerName} after his departure from {school}.")
(root/'Content/Runtime/compact-variety-pack.json').write_text(json.dumps({'format':1,'revision':'content-review-v100','families':families},indent=2,ensure_ascii=False)+'\n',encoding='utf8')
