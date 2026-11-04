"""Static authoring source for personal and team voices. Run offline only."""
import json
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
base_names=['first-pack','analysis-pack','preseason-pack','season-launch-pack','account-refresh-pack','playoff-desk-pack','history-analysis-pack','matchup-season-pack','postseason-pack','context-pack','transactions-pack','cycle-pack','season-review-pack','portal-draft-pack','offseason-discourse-pack','offseason-carryover-pack','editorial-variety-pack','review-corrections-pack']
original={}
original_styles={}
for name in base_names:
    loaded=json.loads(root.joinpath('Content/Runtime/'+name+'.json').read_text(encoding='utf-8'))['families']
    original.update({key:[r['body'] for r in rows] for key,rows in loaded.items()})
    original_styles.update({(key,r['body']):r['style'] for key,rows in loaded.items() for r in rows if 'style' in r})
families={}
def add(key,*bodies):
    families[key]=[{'id':key+'.voices.'+str(i+1),'body':b,**({'style':original_styles.get((key,b),'expressive' if '!!' in b or ' lol' in b else 'measured' if re.sub(r'\s*\{hashtag\}$','',b).rstrip().endswith('.') else 'conversational')} if key.startswith(('player.','recruit.','roster.announce.','roster.transfer-announce.')) else {})} for i,b in enumerate(dict.fromkeys(bodies))]
def extend(key,*bodies):add(key,*(original.get(key,[])+list(bodies)))

add('team.win',"That's a {nickname} WIN! {score} over {opponent}. {hashtag}",
    '{nickname} take it, {score}. {hashtag}', 'A {score} win over {opponent}. For the {nickname} family. {hashtag}',
    'Final: {nickname} {score} over {opponent}. Got the W. {hashtag}',
    'The {nickname} finish on top. {score} vs. {opponent}. {hashtag}',
    'That winning feeling. {score} over {opponent}. {hashtag}',
    'All smiles for the {nickname}. {score} over {opponent}. {hashtag}',
    '{score}. {opponent} behind us. A win for the {nickname}. {hashtag}',
    'A team WIN. {nickname} {score} over {opponent}. {hashtag}',
    'Put it in the win column. {score} against {opponent}. {hashtag}')
add('team.narrow_win','Earned every bit of it. {nickname} {score} over {opponent}. {hashtag}',
    'A battle. A {nickname} WIN. {score} over {opponent}. {hashtag}',
    'Finished the job. {score} against {opponent}. {hashtag}',
    'Together to the finish. {nickname} win {score} over {opponent}. {hashtag}',
    'Tight game. Team win. {score} vs. {opponent}. {hashtag}',
    'Found a way. {nickname} {score} over {opponent}. {hashtag}',
    'Nothing easy about that one. {score} over {opponent}. {hashtag}',
    'One hard-earned W. {nickname} {score} against {opponent}. {hashtag}',
    'Every point mattered. {nickname} win {score} over {opponent}. {hashtag}',
    'A win we earned together. {score} over {opponent}. {hashtag}')
add('team.rivalry_win','Bragging rights secured. {school} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'You know what this one means. {school} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'The rivalry. The WIN. {school} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'We will remember this one. {school} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'For everyone who wanted this one. {school} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'This week belongs to the {nickname}. {winnerScore}-{loserScore} over {opponent}. {hashtag}',
    'Extra sweet. {nickname} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'A rivalry win for the family. {school} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'Scoreboard says it all. {school} {winnerScore}, {opponent} {loserScore}. {hashtag}',
    'A good day to be a {nickname} fan. {winnerScore}-{loserScore} over {opponent}. {hashtag}')
add('team.shutout','ZERO allowed. {school} {winnerScore}, {opponent} 0. {hashtag}',
    'Shut it down. {school} {winnerScore}, {opponent} 0. {hashtag}',
    'No points conceded. A {winnerScore}-0 win over {opponent}. {hashtag}',
    'The {nickname} defense left no room. {winnerScore}-0 against {opponent}. {hashtag}',
    'A clean sheet on the scoreboard. {school} {winnerScore}, {opponent} 0. {hashtag}',
    'Defense brought the zero. {winnerScore}-0 over {opponent}. {hashtag}',
    'A {nickname} shutout. {winnerScore}-0 vs. {opponent}. {hashtag}',
    'Not a point. {school} {winnerScore}, {opponent} 0. {hashtag}',
    '{winnerScore} for us. Zero for {opponent}. {hashtag}',
    'All the way to zero. {nickname} win {winnerScore}-0 over {opponent}. {hashtag}')
add('team.loss','Final: {school} {ownScore}, {opponent} {opponentScore}.',
    'Final score: {opponent} {opponentScore}, {school} {ownScore}.',
    '{school} {ownScore}, {opponent} {opponentScore}. Final.',
    'The final from this one: {school} {ownScore}, {opponent} {opponentScore}.',
    'Final. {nickname} {ownScore}, {opponent} {opponentScore}.',
    'At the finish: {school} {ownScore}, {opponent} {opponentScore}.',
    'Final result: {school} {ownScore}, {opponent} {opponentScore}.',
    '{opponent} {opponentScore}, {school} {ownScore}. Thank you for the support.',
    'Final score. {nickname}: {ownScore}. {opponent}: {opponentScore}.',
    'Final: {opponent} takes it, {opponentScore}-{ownScore}.')
add('team.poll_up','Moving up. No. {rank} in the {pollName}, from No. {previousRank}. {hashtag}',
    'The {nickname} climb to No. {rank}. Previous: No. {previousRank}, {pollName}. {hashtag}',
    'A new number. Same {nickname}. No. {rank} in the {pollName}, up from {previousRank}. {hashtag}',
    'Up the board. {pollName}: No. {previousRank} to No. {rank}. {hashtag}',
    '{nickname} on the rise. No. {rank} in the {pollName} after No. {previousRank}. {hashtag}',
    'The latest {pollName}: {school} No. {rank}, previously No. {previousRank}. {hashtag}',
    'Climbing. {nickname}: No. {previousRank} -> No. {rank}, {pollName}. {hashtag}',
    'A move up for the {nickname}. No. {rank}, from No. {previousRank}, in the {pollName}. {hashtag}',
    'Checking in higher. No. {rank} in the {pollName}; No. {previousRank} last time. {hashtag}',
    'The {pollName} has the {nickname} at No. {rank}. Up from No. {previousRank}. {hashtag}')
add('team.upcoming','Next up: {opponent}. {hashtag}', 'The {nickname} take on {opponent} this week. {hashtag}',
    '{nickname}. {opponent}. This week. {hashtag}', 'A date with {opponent}. Ready, {nickname} fans? {hashtag}',
    'The next challenge: {opponent}. {hashtag}', 'Game week for the {nickname}. Opponent: {opponent}. {hashtag}',
    'Coming this week: {nickname} vs. {opponent}. {hashtag}', 'Our focus this week is {opponent}. {hashtag}',
    'Get ready for {opponent}, {nickname} fans. {hashtag}', 'Another week. Another test. {opponent} next. {hashtag}')
add('team.performance','{playerName}. What a day. {statLine}. {hashtag}',
    'A big one from {playerName}: {statLine}. {hashtag}', '{statLine}. Take a bow, {playerName}. {hashtag}',
    'Put the spotlight on {playerName}. {statLine}. {hashtag}', '{playerName} delivered. {statLine}. {hashtag}',
    'That performance from {playerName}: {statLine}. {hashtag}', 'Let the numbers speak. {playerName}: {statLine}. {hashtag}',
    'A day to remember for {playerName}. {statLine}. {hashtag}', '{playerName} put in a shift. {statLine}. {hashtag}',
    'Some love for {playerName}. {statLine}. {hashtag}')

offers={
 'Leader':['Grateful for the opportunity from {school}. Thank you to everyone who helped me reach this point.',
    'An offer from {school}. Proud to share this with my family and grateful for the staff\'s belief in me.',
    'Thank you {school} for the offer. The support means a lot to me.',
    'Appreciate {school} giving me an opportunity. Thankful for my family and the coaches in my corner.',
    'Excited to add an offer from {school}. I do not take any of this for granted.',
    '{school} offered. A lot of people have helped me along the way and I appreciate all of you.'],
 'Intense':['An offer from {school}. More motivation to keep going.', 'Appreciate the offer {school}. Still hungry.',
    '{school} offer in. This is why I keep putting the time in.', 'Thank you {school}. Another reason to stay locked in.',
    'Got the offer from {school}. Feeling good about the work I have been putting in.',
    '{school} gave me a shot. Appreciate it. More to come.'],
 'Entertainer':['{school} offered and I have been smiling at my phone for ten minutes',
    'Had to tell the family this one. Offer from {school}!!', 'Pretty good day to check my phone. {school} offered!',
    '{school} offer! My family might be more excited than me right now',
    'New offer from {school}. Yeah I am posting this one everywhere lol',
    'This one made the group chat happy. Appreciate the offer {school}'],
 'TeamPlayer':['Offer from {school}! My teammates know how much this means to me.',
    'Thankful for {school} and for everybody helping me chase this.', 'We get to celebrate another one. Thank you {school} for the offer.',
    'Sharing this one with my family. Appreciate the offer from {school}.',
    'My coaches have done a lot for me. Proud to share an offer from {school}.',
    'An offer from {school}. Thankful I have good people around me for moments like this.'],
 'Unpredictable':['{school} offered. Had to sit with that for a second', '{school} just made my day interesting. Appreciate the offer!',
    'Was not expecting that update on my phone. Thank you {school} for the offer.',
    'New offer from {school}. Okay now we have something to talk about',
    'Checking my phone paid off today. {school} offered!', 'An offer from {school}!! Yeah that one got a reaction out of me'],
 'Neutral':['Excited to receive an offer from {school}. Thank you for the opportunity.',
    'Really appreciate the offer from {school}. Grateful to be in this position.',
    'An offer from {school}! Thankful for the people helping me get here.',
    '{school} offer came in. Appreciate the belief.', 'Happy to share an offer from {school}. Thank you to the staff.',
    'New opportunity from {school}. A lot to be thankful for.'],
 'faith':['AGTG! Thankful to receive an offer from {school}.', 'God is good. Blessed with an offer from {school}!',
    'All glory to God! Appreciate the offer from {school}.', 'Blessed and grateful for the {school} offer.',
    'AGTG. Another opportunity I am thankful for. {school} offered!',
    'Thank God for this journey. Blessed with an offer from {school}.']
}
for personality,lines in offers.items():extend('recruit.offer.'+personality,*lines)
wins={
 'Leader':['Proud to share this win with my teammates. Thank you to everyone supporting us. {hashtag}',
    'A team win. Grateful for all the people behind us. {hashtag}', 'Appreciate the support today. Good win for this group. {hashtag}',
    'Thankful for another win with my guys. Love representing {school}.',
    'That is a good feeling. Proud of my teammates. {hashtag}', 'A win for everybody who rides with the {nickname}. Thank you.'],
 'Intense':['Got the W. That is what we came for. {hashtag}', 'A win with my guys. Nothing better. {hashtag}',
    'The {nickname} got it done. Appreciate everyone riding with us.', 'W. I like how that looks. {hashtag}',
    'Good day to be on this side of the scoreboard. {hashtag}', 'We will enjoy this one. Love my guys. {hashtag}'],
 'Entertainer':['Got the win. My group chat can hear from me again lol {hashtag}',
    'W looks good on us. {hashtag}', 'I might watch the highlights more than once. Good win with my guys',
    'The timeline is a little more fun after a win lol {hashtag}', 'My guys!! Good day for the {nickname}',
    'A win and some very happy people in my phone. Love it. {hashtag}'],
 'TeamPlayer':['A lot of guys made this win happen. Proud to be part of this group. {hashtag}',
    'My teammates deserve the love today. Good team win. {hashtag}', 'One for the whole group. Appreciate our fans. {hashtag}',
    'Love seeing my guys celebrate. Thankful for the W. {hashtag}', 'Best part of a win is sharing it with this team.',
    'Nothing about this one was just one guy. Love my team. {hashtag}'],
 'Unpredictable':['A W and a whole lot of receipts on my phone. {hashtag}', 'Good win. Keeping my mentions open for a little bit',
    'Some people got real quiet after that W. Interesting. {hashtag}', 'I like the scoreboard exactly where it is. {hashtag}',
    'W. I know a few group chats are tired of hearing from me already', 'Got the win. We can all stop typing essays now lol'],
 'Neutral':['A win with this team means a lot. Appreciate the support. {hashtag}',
    'Thankful for a good day with the {nickname}.', 'Good team win. Love everybody who showed up for us. {hashtag}',
    'A W for the group. Glad we could share that with our fans.', 'Proud of my guys today. {hashtag}',
    'Great feeling getting the win with this group. Thank you for the love.'],
 'QB':['Thankful for a win with this team. Appreciate the support. {hashtag}',
    'Proud of how this group came together for the win. {hashtag}', 'A good team win. Grateful for my teammates.',
    'Appreciate everyone behind us. Glad to share a win with the {nickname} family.',
    'Love winning with this group. Thank you to our fans. {hashtag}', 'A team W. Grateful I get to be part of this. {hashtag}']
}
for personality,lines in wins.items():extend('player.win.'+personality,*lines)
for personality in ['Leader','Intense','Entertainer','TeamPlayer','Unpredictable','Neutral']:
    add('recruit.commit.'+personality,
        'Committed to {school}. Thankful for everyone who helped me get here. {hashtag}',
        'I am going to {school}! Excited to get started with this group. {hashtag}',
        '{school} is home. Appreciate all the support through this. {hashtag}',
        'Proud to say I am committed to {school}. Thank you to my family and coaches.',
        'The decision is made. {school}! Ready for the next chapter. {hashtag}',
        'It is {school} for me. Appreciate everybody who has been part of this.',
        'Committed. {school} feels like the right place for me. {hashtag}',
        'My next chapter is at {school}. Thankful for the opportunity.',
        '{school}! Excited to be part of this family. Committed. {hashtag}',
        'I found my next home at {school}. Thank you to everyone who stayed with me through the process.')

commit_personality={
 'Leader':['Proud to commit to {school}. Thankful for the people who helped me make this decision.',
    'I have decided to continue my career at {school}. Appreciate the trust and the opportunity.',
    'Committed to {school}. I want to thank my family, my coaches and everyone who believed in me.',
    'The next chapter is {school}. Grateful for the support that made this possible.',
    'Excited to join {school}. This decision means a lot to me and my family.',
    '{school} is where I want to be. Ready to represent this program. Committed!',
    'Thank you to the people who stayed in my corner. I am committed to {school}.',
    'Proud of this decision. I am going to {school} and I am thankful for the opportunity.'],
 'Intense':['{school}. Committed. Been waiting to make this one official.', 'Made my choice. {school}. Now I can focus on what is next.',
    'I am all in with {school}. Committed!', 'Found my spot at {school}. Ready to compete.',
    '{school} is the decision. Excited to prove myself.', 'Committed to {school}. This is the opportunity I wanted.',
    'Next stop, {school}. Ready for this challenge.', 'The decision is done. {school}, let\'s get it.'],
 'Entertainer':['It is {school}!! Yall are stuck with me now', 'Had to make the family wait a little but it is {school}!',
    '{school} is home! The group chat can finally stop asking me lol', 'I have something to tell yall. Committed to {school}!!',
    'So about my next chapter... {school}!!', 'Officially committed to {school}. My family is about to be unbearable about this',
    '{school}! Feels pretty good to finally post that', 'Decision made. {school}. Yeah I have been smiling all day'],
 'TeamPlayer':['Committed to {school}. My family and coaches have been with me through all of this. Thank you.',
    'I get to join the {school} family! Thankful for everyone who helped me find my next home.',
    'The next team is {school}. Ready to be part of this group. Committed!',
    'My people know how much this means to me. Committed to {school}.',
    'Excited to join {school} and meet my future teammates. Thank you for the support.',
    'Committed to {school}! This is a moment I get to share with my family.',
    '{school} is home. I am grateful for everyone who has helped along the way.',
    'Thank you to my family, teammates and coaches. I am going to {school}!'],
 'Unpredictable':['{school}. That is the decision. You can stop guessing now', 'Committed to {school}. A few group chats are going to have questions lol',
    'The answer was {school}. Appreciate everybody who let me make this decision my way.',
    'I know everybody had a prediction. Anyway, {school}!!', '{school}. Committed. That is the update.',
    'Plot update: I am going to {school}.', 'Made the choice that felt right to me. {school}. Committed.',
    '{school} it is. The timeline can do what it wants with that'],
 'Neutral':['Committed to {school}! Excited for the next chapter.', 'Thankful to have found my next home at {school}.',
    'I am going to {school}. Appreciate all the support through this process.',
    'Happy to say I am committed to {school}. Ready for what comes next.', 'The decision is {school}! Thankful for this opportunity.',
    '{school} is home. Looking forward to getting started.', 'Proud to be joining {school}. Thank you to everybody who helped me get here.',
    'Excited about my future at {school}. Committed!']
}
for personality,lines in commit_personality.items():
    add('recruit.commit.'+personality,*lines)
    add('roster.announce.'+personality,*lines)
    add('roster.transfer-announce.'+personality,*[line+' Appreciate my time at {formerSchool}.' for line in lines])

root.joinpath('Content/Runtime/voice-variety-pack.json').write_text(json.dumps({'revision':'voice-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
