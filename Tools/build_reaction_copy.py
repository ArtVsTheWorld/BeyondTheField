"""Prewritten reaction alternatives; light slang belongs to the speaker."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.reaction.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def replies(key,*lines):add(key,*['{parentHandle} '+line for line in lines])
replies('reply.fan.player_win',
    'Yeah you earned the love after that one', 'My group chat owes you an apology',
    'I will be talking about this performance for a while', 'No slander about you on this timeline today',
    'Made my whole weekend better. Appreciate you', 'That is the kind of game I watch the highlights for twice',
    'You gave the {nickname} fans something to be loud about', 'The highlights are going straight into the group chat',
    'Keep playing like that and I will become even more annoying about this team', 'A lot of happy {school} fans because of you')
replies('reply.fan.beat_win',
    'You have to be professional about this. I absolutely do not', 'That final looks great typed out again',
    'Please give me ten minutes before we start worrying about next week', 'The {nickname} won. My mood has improved dramatically',
    'A win and a full weekend to be annoying about it', 'I have already sent this to people who did not ask',
    'Please keep posting this score. It does not get old', 'Reading this as if I did not just watch the whole game',
    'The {school} group chat is going to enjoy this', 'That is the kind of update I wanted today')
replies('reply.fan.beat_loss',
    'Reading the final a second time did not help', 'I need a break from my phone before I start offering lineup advice',
    'My mood did not need this update', 'I love {school}. I did not love watching that',
    'The postgame group chat is not going to be a pleasant place', 'Well that has ruined the rest of my football plans',
    'I saw the game. Somehow the final still looks worse written down', 'Going to stare at the wall for a bit',
    'Still a fan tomorrow. Extremely frustrated today', 'Would love a week where I do not have to defend this team online')
replies('reply.fan.analyst_low',
    'I hate when the numbers agree with my worst feelings', 'You could have let me enjoy being delusional a little longer',
    'It looked rough live and the numbers did not rescue it', 'This is why I should not read analysis before breakfast',
    'Was hoping the math would say something nicer', 'Now I have to be upset with evidence. Great',
    'I wanted to argue but those numbers are sitting right there', 'Somebody on the staff needs to be reading this too',
    'Love the {nickname}. Hate that this is a fair criticism', 'I was trying to avoid this exact conversation')
replies('reply.fan.analyst_high',
    'Finally some numbers I am happy to read', 'Keep going. I have people to send this to',
    'Been saying this without the math. Glad someone brought the math', 'I am choosing to believe every nice thing in this post',
    'The {school} group chat is getting a screenshot', 'You have my full attention when the numbers look like that',
    'This is the sort of research I can support', 'Exactly. Please repeat it for the other fanbases',
    'That is getting saved for the next argument', 'I knew watching the {nickname} had to be good for something')
replies('reply.fan.commit',
    'Welcome to the {nickname}. Already pretending I know your whole highlight reel',
    'That is the school right there. Welcome aboard', 'I have known about this for ten seconds and I am already invested',
    'Your highlights are about to become my entire personality', 'Good choice. Welcome to {school}',
    'Welcome! I am choosing to have wildly optimistic expectations', 'The group chat likes this one',
    'A new {nickname}. Love to see it', 'Coach {coachLastName} keeps giving us things to talk about',
    'We have already started talking ourselves into your future highlights')
replies('reply.fan.offer',
    'Congrats! Hope we get to see you in {school} colors', 'Good offer. Would love to see you with the {nickname}',
    'Come see what {school} is about', 'Congrats on the offer. The {nickname} fans are paying attention',
    'This would be a fun fit. Congrats on the offer', 'Welcome to the part where {school} fans watch all your highlights',
    'Hope this turns into a visit to {school}', 'Congrats! Adding this to my recruiting watch list',
    'I have already decided you would look good in these colors', 'Love this offer. Come be a {nickname}')
replies('reply.player.offer',
    'Congrats on the offer!', 'Happy for you. Big opportunity', 'Congrats man. Keep it going',
    'Good news! Appreciate seeing you get the opportunity', 'Congrats. Love to see the work getting noticed',
    'That is a good feeling. Congrats on the offer', 'Happy for you and your people', 'Congrats! Keep enjoying the process',
    'Good stuff. Wishing you the best with it', 'Congrats on this one. Keep going')
commit={
 'Leader':['Welcome to the {nickname}. Looking forward to having you with us.','Congrats to you and your family. Glad you are joining us.','Welcome aboard. Excited to share a team with you.','Good decision. Looking forward to meeting you.','Happy for you. Welcome to {school}.','Congrats on your commitment. Glad to have you with us.','Welcome to this group. Appreciate you choosing {school}.','Excited for you and your next chapter with the {nickname}.'],
 'TeamPlayer':['Welcome to the family!','Glad you are joining the group. Congrats man.','Happy for you and your people. Welcome aboard.','Looking forward to having you around the guys.','Congrats! Good to have another {nickname}.','Welcome to {school}. Excited to be teammates.','Love seeing this. Congrats to your family too.','Welcome! Looking forward to sharing the field.'],
 'Intense':['Let\'s get it. Welcome.','Good choice. Ready to see you compete.','The {nickname} got another one.','Welcome to the group. Let\'s go.','Yeah we needed this one.','Glad you picked {school}. Ready to get after it.','Good stuff. Welcome to our side.','Welcome aboard. Time to see what we can do.'],
 'Entertainer':['Yall see who we just got??','Okay then! Welcome to the {nickname}.','Had to come say welcome. Good choice lol','The group chat likes this decision','Another {nickname}! Yeah I can get used to this','Guess we are teammates now. Welcome!!','Now this is a good update to open my phone to','Good choice. Your mentions are about to be busy lol'],
 'Unpredictable':['Oh we got one.','This just improved my day.','I see you. Welcome.','Good decision. I might be biased','The group chat has thoughts. All good ones today','That is what I wanted to see on my phone','Welcome to our side. Interesting times ahead','Yeah I am posting about this one. Welcome'],
 'Neutral':['Congrats on the commitment!','Welcome to the {nickname}.','Happy for you. Welcome aboard.','Looking forward to having you with us.','Congrats! Excited to be teammates.','Good to see this. Welcome to {school}.','Glad you are joining us.','Welcome! Congrats to you and your family.']}
for personality,lines in commit.items():replies('reply.player.commit.'+personality,*lines)
replies('reply.player.teammate',
    'Love seeing you get yours.', 'That was fun to watch.', 'You were moving out there.', 'Proud of you, brother.',
    'The work is showing up.', 'You earned the love today.', 'Keep getting after it.', 'Could not be happier for you.',
    'Love sharing a field with you.', 'Yeah this one deserves a post.')
replies('reply.player.award',
    'Thankful for this. Appreciate my guys.', 'Love the support. Nobody does it alone.',
    'Thank you! Grateful for everybody helping me along the way.', 'Appreciate the love. Means a lot.',
    'My teammates are a big part of this. Thank you.', 'A lot of people helped me get here. Appreciate all of you.',
    'Grateful for this team and everyone behind us.', 'Thank you to my family and teammates.',
    'Honored. Love this group.', 'Appreciate everybody showing love today.')
replies('reply.fan.award',
    '{playerName} earned that. Love the recognition', 'Well deserved for {playerName}. Say the name a little louder',
    'Put some respect on {playerName}. {nickname} getting recognized', 'That award found the right player. Congrats {playerName}',
    'Been telling people about {playerName}. Happy to see this', '{playerName} deserves every bit of that',
    'The {school} timeline will be posting this for a while', 'A proud day for everyone who has watched {playerName}',
    'Give {playerName} the flowers. Earned them', 'Love seeing our guys get their recognition. Congrats {playerName}')
for key,subject in [('coach_good','{coachName}'),('player_good','{playerName}')]:
    replies('reply.fan.'+key,
        subject+' deserves more credit for this', 'Give '+subject+' some flowers. Real production at {school}',
        'Been trying to tell people about '+subject, 'This is why I keep defending '+subject,
        'I would like the '+subject+' appreciation posts to be a little louder',
        subject+' has earned some positive noise on this timeline', 'The numbers back it up for '+subject,
        'Finally some credit for '+subject+'. Keep it going', 'No complaints from me about '+subject+' right now',
        'The {nickname} are getting something real from '+subject)
for key,subject in [('coach_bad','{coachName}'),('player_bad','{playerName}')]:
    replies('reply.fan.'+key,
        'I want '+subject+' to turn it around. Cannot pretend this is working',
        'Those '+subject+' numbers are rough. Something has to change',
        'How long are we supposed to act like this part of {school} is fine?',
        subject+' needs to give us a reason to feel better about this',
        'Love {school}, but defending '+subject+' is getting difficult',
        'I would love to be wrong about '+subject+'. Please give me a reason',
        'The {nickname} need more from '+subject+'. It is fair to say it',
        'Criticism of '+subject+' is not the same thing as wanting the team to fail',
        'Wish these numbers looked different. Looking at you, '+subject,
        'I am still rooting for '+subject+'. I am also frustrated')
replies('reply.fan.recruit_number_one',
    'THE NUMBER ONE PLAYER. To {school}. I need a minute',
    'The No. 1 recruit picked US. Sorry in advance for how I will act about this',
    'No. 1 in the country and a future {nickname}. This is massive',
    'Somebody tell me to calm down. Actually do not. Number one!!',
    'The top player in the entire class. {school} actually did that',
    'The group chat is not going to sleep. No. 1 to the {nickname}',
    'The best-ranked recruit in the country chose {school}. Read that again',
    'I will be bringing up this commitment in unrelated conversations',
    'We got the NUMBER ONE recruit. There is no normal way for me to react',
    'That is the kind of news that gets pinned on the {school} timeline')
replies('reply.fan.recruit_program_changer',
    'A {stars}-star chose {school}?! This changes the mood around here',
    '{stars} stars. The {nickname}. This is the sort of pickup we watched other schools celebrate',
    'This is a HUGE deal for {school}. I am not going to act casual about it',
    'We used to watch these announcements hoping for a mention. A {stars}-star to US',
    'A {stars}-star in these colors. That is a different kind of recruiting day',
    'This is the kind of commitment the whole {school} fanbase notices',
    'The {nickname} really landed a {stars}-star. Keep saying it until it sounds normal',
    'Call it a program moment. That is what a pickup like this means here',
    '{school} fans have earned the right to be loud about this one',
    'A {stars}-star picked us. I am going to need a few more highlight clips')
replies('reply.fan.recruit_five_star',
    'Five stars. Welcome to the {nickname}', 'Another serious talent for {school}. Love this pickup',
    'A 5-star is always worth celebrating. Welcome aboard', 'FIVE STAR. The {nickname} keep building',
    'A big addition for {school}. Excited to see this one develop', 'Five stars in these colors. I like that',
    'Plenty of talent coming in. Welcome to {school}', 'A 5-star chose the {nickname}. Good recruiting day',
    'This is why I keep checking the recruiting news', 'Five-star news is the kind of notification I want')
replies('reply.fan.recruit_questioned',
    'A {stars}-star for {school}? I hope the staff sees a fit I am missing',
    'Not writing anybody off, but I expected a bigger pickup at our level',
    'The {nickname} usually aim higher. I would like to understand this one',
    'Hope you prove the rankings wrong. This is a surprising signing for {school}',
    'I am rooting for it to work. I also have questions about the recruiting approach',
    'A {stars}-star at {school} is not automatically a bad player. Still a strange fit on paper',
    'This is where I want the staff to explain what it sees beyond the stars',
    'Would love to be wrong about this pickup. It is fair to ask questions',
    'The signing surprised me. Hope the staff found something the rest of us missed',
    'Not the kind of announcement I expected from {school}. We will see')
replies('reply.fan.flip',
    'All that recruiting for {newSchool} to get the commitment. That is annoying',
    'From {oldSchool} to {newSchool}. Yeah I do not love seeing that',
    'Guess those {oldSchool} welcome posts aged fast. This one hurts',
    'Losing a commitment to {newSchool} was not the update I wanted',
    'Cool. We can apparently enjoy a commitment right up until {newSchool} calls',
    'The flip from {oldSchool} to {newSchool} has ruined my recruiting mood',
    'That is a rough notification for {oldSchool} fans to open',
    'Would have preferred literally any {oldSchool} update other than this flip',
    'I know recruiting changes. I do not have to enjoy {newSchool} taking this one',
    'The {oldSchool} group chat is going to need a minute after that flip')
replies('reply.fan.decommit',
    'Losing this commitment hurts. Staff has work to do', 'Reopened the recruitment? Yeah I do not love that',
    'This is why I should stop getting attached before signing day',
    'Cool cool cool. Another reason for me to keep refreshing recruiting news',
    'I was enjoying the commitment. Would have enjoyed keeping it more',
    'The class did not need that update. Time for the staff to respond',
    'Not the recruiting notification I wanted to open', 'This one is frustrating. Back to the board',
    'Hope the staff has another plan because I was counting on this one', 'I know nothing is final. Still hurts to lose the commitment')
replies('reply.fan.upset',
    '{winner} over {loser}. This sport is ridiculous', 'That upset is going to fuel the timeline for a week',
    '{winner} actually did that to {loser}. I love college football',
    'The {loser} group chats are having a very different evening',
    'Respect to {winner}. That is how you change the conversation',
    'Please keep the {winner}-{loser} final on my screen a little longer',
    '{winner} just gave every underdog fan something to smile about',
    'Some preseason arguments are going to look very funny after {winner} beat {loser}',
    'The upset alert was not a drill. {winner} got it done',
    '{loser} fans are going to be hearing about {winner} for a while')

root.joinpath('Content/Runtime/reaction-variety-pack.json').write_text(json.dumps({'revision':'reaction-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
