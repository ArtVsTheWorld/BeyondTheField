"""Authored postseason, draft and carryover copy; no runtime text generation."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):
    families[key]=[{'id':key+'.cyclecopy.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])

forms('playoff.position','~',
 "{school} is CFP No. {rank}. A strong position, with the next result still to earn.",
 "CFP No. {rank}: {school}. The ranking supports the case. It does not play the remaining games.",
 "The committee has {school} at No. {rank}. There is a real playoff argument behind that number.",
 "{school}'s current CFP position is No. {rank}. That is something to defend on the field.",
 "No. {rank} in the CFP rankings for {school}. The next challenge is keeping that position.",
 "The CFP picture has {school} at No. {rank}. A good place to be; the work continues.",
 "{school} sits at CFP No. {rank}. This is a contender's position, rather than a confirmed berth.",
 "Current committee view: {school}, No. {rank}. The remaining football still counts.",
 "CFP check: {school} is No. {rank}. The program has put itself firmly in the discussion.",
 "{school}, CFP No. {rank}. A meaningful ranking, with more results needed to finish the job.")
forms('playoff.bubble','~',
 "CFP No. {rank}: {school}. A playoff case to make, and other results worth watching.",
 "{school} is No. {rank} in the CFP rankings. Welcome to the scoreboard-watching part of the year.",
 "The committee has {school} at No. {rank}. Plenty left to argue about near this part of the field.",
 "CFP No. {rank} puts {school} in the conversation. It is a case, rather than a berth.",
 "{school}'s CFP position: No. {rank}. The next result matters more than another argument online.",
 "No. {rank} for {school}. This is where the CFP conversation starts involving everybody else's schedule.",
 "{school} is sitting at CFP No. {rank}. A little room for hope and a lot of reason to keep watching.",
 "Current CFP picture: {school}, No. {rank}. There is still a path to discuss, not an invitation to announce.",
 "{school} at CFP No. {rank}. The case is alive. The next game is still the most useful part of it.",
 "CFP check on {school}: No. {rank}. This part of the board can make a fan very interested in other games.")
forms('playoff.local','~',
 "{school} is No. {rank} in the CFP rankings. That is the local playoff-picture reference point this week.",
 "CFP update for {school}: No. {rank}. A ranking alone does not confirm a playoff berth.",
 "The committee's current placement for {school} is No. {rank}. That is where the discussion starts.",
 "{school}'s playoff watch begins at CFP No. {rank} this week. The next result remains the priority.",
 "No. {rank} in the CFP rankings for {school}. The program's case has a new reference point.",
 "On the {school} beat: CFP No. {rank}. The ranking is official; a berth needs its own announcement.",
 "Current CFP position for {school}: No. {rank}. We will keep the ranking and the actual field separate.",
 "{school} checks in at CFP No. {rank}. A useful marker for the weeks ahead.",
 "CFP No. {rank} is where {school} stands. More football remains before the final field is set.",
 "The CFP board lists {school} at No. {rank}. That is the current position to build from.")
pairs('playoff.fan_position',[
 "CFP No. {rank} for {school}.","{school} is CFP No. {rank}. I have read it several times.",
 "The committee put {school} at No. {rank}.","No. {rank}. {school}. Actual CFP rankings.",
 "{school} at CFP No. {rank} feels very real right now."],
 ["Trying to act normal about this. Mixed results","Please keep giving me reasons to refresh this page"])
pairs('playoff.fan_bubble',[
 "{school} is CFP No. {rank}.","CFP No. {rank} for {school}. My weekend has extra homework now.",
 "The committee has {school} at No. {rank}.","{school} at CFP No. {rank}. Let me check the other scores again.",
 "No. {rank} in the CFP rankings for {school}."],
 ["I am suddenly an expert on several schedules","Nobody ask how much time I have spent on playoff arguments"])
forms('playoff.matchup','~',
 "CFP No. {awayRank} {away} vs. CFP No. {homeRank} {home}. The committee order brought us here; football settles the matchup.",
 "Playoff matchup: CFP No. {awayRank} {away} and No. {homeRank} {home}. Both have a place in this field to defend.",
 "{away} enters at CFP No. {awayRank}; {home} at No. {homeRank}. A playoff meeting with a result still to earn.",
 "CFP No. {homeRank} {home} gets No. {awayRank} {away}. Now the comparison moves from the rankings to the field.",
 "The playoff pairs No. {awayRank} {away} with No. {homeRank} {home}. Committee numbers are only the starting point.",
 "{away} (CFP No. {awayRank}) meets {home} (No. {homeRank}). This is the matchup on the playoff board.",
 "Playoff watch: No. {awayRank} {away}, No. {homeRank} {home}. The rankings give context, not the final score.",
 "No. {homeRank} {home} and No. {awayRank} {away} have a playoff game to decide. The cases have become a matchup.",
 "CFP matchup check: {away}, No. {awayRank}, against {home}, No. {homeRank}. Time to find out on the field.",
 "The field gives us CFP No. {awayRank} {away} vs. No. {homeRank} {home}. No more settling this particular argument with a ranking.")
pairs('playoff.result_fan',[
 "{school} advances.","Another playoff win for {school}.","{school} is moving on. I need a minute.",
 "A playoff W. {school} gets another game.","{school} lives to play another one."],
 ["No voice left. Still plenty to say online","Nobody expect reasonable behavior from me tonight"])
pairs('playoff.champion_fan',[
 "{school}. NATIONAL CHAMPIONS.","{school} won the whole thing.","National champions. {school}. I am keeping this screenshot.",
 "{school} is on top of college football.","The national title belongs to {school}."],
 ["I will be bringing this up for the rest of my life","Tomorrow's problems can wait. This is everything tonight"])

forms('postseason.waiting-playoff','~',
 "{school} is {record}. The official playoff field and matchups arrive next week. For now, the debate continues.",
 "A {record} record for {school}, and a week to wait for the official playoff announcement.",
 "{school} has its {record} record on the board. Next week brings the official field, byes and matchups.",
 "Waiting week for {school} at {record}. Playoff projections are still projections until next week's announcement.",
 "The next date for {school}: the official playoff field next week. Its record stands at {record}.",
 "{school}, {record}. Plenty of playoff arguments to read while the official matchups wait until next week.",
 "One more week before the playoff picture becomes official. {school} waits with a {record} record.",
 "At {record}, {school} has reached the waiting part. Field, byes and playoff matchups come next week.",
 "{school}'s record is {record}. This week is for waiting on the field announcement, not announcing a projected berth.",
 "Playoff watch for {school}: {record}, with the official selection news due next week.")
forms('postseason.waiting-bowl','~',
 "{school} finishes the regular slate at {record}. Bowl selections come next week; no destination is official yet.",
 "A {record} record for {school}. Now comes the wait for next week's official bowl selections.",
 "Bowl watch for {school} at {record}. The matchup announcement belongs to next week.",
 "{school}, {record}. No farewell or bowl destination to announce before next week's selections.",
 "The regular schedule is in the books at {record} for {school}. Bowl news becomes official next week.",
 "{school} waits at {record}. The bowl discussion is still a discussion until selections arrive next week.",
 "Waiting on the bowl announcement: {school}, {record}. We should have the official answer next week.",
 "For {school}, {record} is the record and next week is the selection date. No assigned bowl matchup yet.",
 "{school}'s bowl plans remain unconfirmed at {record}. Official selections are a week away.",
 "Next week's bowl announcements will settle the next step for {school}. It waits with a {record} record.")
pairs('postseason.waiting-fan',[
 "{school} fans have a week until the announcement.","Still waiting for the official news on {school}.",
 "A whole waiting week for {school}.","{school} fans have entered the refreshing-everything stage.",
 "One week until the bowl news is official for {school}."],
 ["My phone battery is not enjoying the process","Apparently checking again does not make them announce it faster"])
forms('postseason.bye-path','~',
 "{school} has a first-round bye and will meet the {first}-{second} winner in the Week {quarterWeek} quarterfinal.",
 "Quarterfinal path for {school}: a bye, then the winner of {first} vs. {second} in Week {quarterWeek}.",
 "{first} and {second} play for a Week {quarterWeek} quarterfinal meeting with {school}, which has a first-round bye.",
 "{school}'s bye is set. Its Week {quarterWeek} quarterfinal opponent comes from {first} vs. {second}.",
 "A first-round bye for {school}. Next is the {first}-{second} winner in Week {quarterWeek}.",
 "The bracket gives {school} a bye into Week {quarterWeek}. Either {first} or {second} will be waiting in the quarterfinal.",
 "{school} can watch {first} vs. {second} with a clear interest: the winner is its Week {quarterWeek} quarterfinal opponent.",
 "First-round bye: {school}. Quarterfinal opponent: {first} or {second}, in Week {quarterWeek}.",
 "{school} enters the bracket in the Week {quarterWeek} quarterfinal, against the {first}-{second} winner.",
 "{school} gets the bye. {first} and {second} decide who reaches its side of the Week {quarterWeek} quarterfinal.")
forms('postseason.bye-opponent','~',
 "{opponent} is now {school}'s Week {quarterWeek} quarterfinal opponent after the first-round result.",
 "Quarterfinal set: {school} vs. {opponent}, Week {quarterWeek}. The first round has supplied the opponent.",
 "The wait for an opponent is over for {school}: {opponent}, Week {quarterWeek}, in the quarterfinal.",
 "{school}'s bye leads to a quarterfinal against {opponent} in Week {quarterWeek}.",
 "{opponent} advances into a Week {quarterWeek} quarterfinal with {school}.",
 "The bracket now pairs {school} and {opponent} in the Week {quarterWeek} quarterfinal.",
 "After watching the first round, {school} has its answer: {opponent} in Week {quarterWeek}.",
 "Week {quarterWeek} quarterfinal watch: {school} gets {opponent}. The opponent is confirmed.",
 "{school} vs. {opponent} is the quarterfinal matchup for Week {quarterWeek}.",
 "The first-round result sends {opponent} to meet {school} in the Week {quarterWeek} quarterfinal.")
forms('postseason.bye-team','~ {hashtag}',
 "Quarterfinal bound. {nickname} vs. the {first}-{second} winner. Week {quarterWeek}.",
 "A bye, then the {first}-{second} winner. {nickname}, get ready for Week {quarterWeek}.",
 "The path is set. {nickname} meet the winner of {first} vs. {second} in Week {quarterWeek}.",
 "Next for the {nickname}: the {first}-{second} winner. Quarterfinal. Week {quarterWeek}.",
 "Waiting in the quarterfinal. {nickname} vs. {first} or {second}, Week {quarterWeek}.",
 "Quarterfinal plans: {nickname}, {first} or {second}, Week {quarterWeek}.",
 "One of {first} and {second} is next. {nickname} return in the Week {quarterWeek} quarterfinal.",
 "Eyes on the bracket. {nickname} face the {first}-{second} winner in Week {quarterWeek}.",
 "A quarterfinal date awaits. {nickname} vs. the {first}-{second} winner, Week {quarterWeek}.",
 "{nickname} have the bye. Next: {first} or {second}, Week {quarterWeek}.")
pairs('postseason.bye-fan',[
 "{school} gets the {first}-{second} winner.","{first} vs. {second} decides who gets {school} next.",
 "A bye for {school}. {first} and {second} get to settle the opponent.",
 "{school} fans watching {first} and {second} like it is a scouting assignment.",
 "{first} or {second}. That is the next one for {school}."],
 ["No game for us and I am somehow still stressed","The bye did not come with the relaxed weekend I imagined"])
pairs('postseason.bye-fan-opponent',[
 "{opponent} it is. {school} has its quarterfinal.","{school} vs. {opponent}. The wait is over.",
 "Quarterfinal opponent confirmed: {opponent}. Let's go, {school}.",
 "{opponent} is next for {school}.","{school} gets {opponent}. My week now has a very clear focus."],
 ["Ready for the game. Less ready for my nerves","I have already started having conversations about this matchup"])
pairs('postseason.award-player',[
 "The {award} means a lot.","Grateful for the {award}.","Honored to receive the {award}.",
 "Bringing the {award} back to {school}.","Still taking in the {award}."],
 ["Love my teammates and everybody at {school}. Thank you for being with me","A lot of people helped me get here. Appreciate all of you at {school}"])
pairs('postseason.signed',[
 "Signed {document}. It's official, {school}.","{document} signed. Ready for {school}.",
 "Made it official with {school}. Signed {document}.","Next chapter: {school}. Signed {document}.",
 "My {document} is signed. {school}, let's go."],
 ["Thank you to everyone who helped me get here","Grateful for my family and coaches. Excited for what is next"])
forms('postseason.signed-class','~ {count} signed: {fiveStars} five-stars, {fourStars} four-stars.{rankDetail}',
 "Early signing check for {school}.","{school}'s early signing group is taking shape.",
 "Signatures on the board for {school}.","Early signing update from {school}.",
 "A look at the signed group for {school}.","Early signing count at {school}.",
 "The current signed class for {school}.","Checking the early signatures at {school}.",
 "{school}'s early signing numbers.","Signed-recruit check: {school}.")
pairs('postseason.coach-fan',[
 "The {role} decision is part of {school}'s offseason now.","{school} has a {role} situation to sort out.",
 "Keeping an eye on the {role} news at {school}.","The {role} conversation at {school} is getting very real.",
 "{school} fans have another {role} decision to argue about."],
 ["Please give us good football, not just a good press conference","I am interested in the plan long after the introduction is over"])
pairs('context.conference-fan',[
 "The {conference} vs. {otherConference} arguments have found my timeline again.",
 "{otherConference} fans have another speech ready about the {conference}.",
 "The {conference} is not taking conference lectures from the {otherConference} today.",
 "Every {conference}-{otherConference} debate has the same volume setting.",
 "{otherConference} fans, the {conference} heard you the first time."],
 ["Bring results to the conversation","Some of you are treating this like your personal conference audition"])

forms('draft-talk.team-leader','~ {leaders} {leadVerb} with {count} first-round selections.',
 "First-round production:","Checking the first-round school totals:","The school count at the front of this draft:",
 "Round 1 school leaderboard:","First-round talent coming out together:","A look at the school leaders:",
 "On this year's first-round board:","The largest first-round school count:","School draft check:","First-round school tally:")
forms('draft-talk.conference-leader','~ {conferences} {leadVerb} with {count} first-round picks.',
 "Conference draft check:","Round 1 by conference:","First-round conference totals:","The conference lead in Round 1:",
 "Looking across this year's first round:","First-round talent by league:","The conference draft count:",
 "At the front of the draft:","A look at the conference leaders:","This year's first-round conference tally:")
pairs('draft-talk.congrats',[
 "{count} {school} players drafted. Congrats to {names}{more}.",
 "{school} had {count} drafted: {names}{more}. Love seeing that call come.",
 "Shoutout to {names}{more}. {count} drafted from {school}.",
 "{count} draft picks for {school}. {names}{more} earned this moment.",
 "{names}{more} got drafted. {count} picks out of {school}."],
 ["Will be keeping an eye on those careers","Always going to cheer for our guys"])
pairs('draft-talk.empty',[
 "No {school} players drafted this year.","An empty draft board for {school} this time.",
 "{school} finished the draft with no selections.","No draft calls for {school} players this year.",
 "A draft without a {school} selection. That hurts."],
 ["Hope our guys find a free-agent chance and make somebody regret passing","Still pulling for our guys to find their next opportunity"])
pairs('draft-talk.conference-fan',[
 "{count} first-round picks out of {school}.","{school} sent {count} players into the first round.",
 "Round 1 gave {school} {count} picks.","{count} {school} players drafted in the first round.",
 "A first-round count of {count} for {school}."],
 ["You're welcome, {conference}. I will be mentioning this again","{conference} group chat is hearing about this all summer"])
forms('draft-talk.top-ten','~',
 "No. {pick}: the {nflTeam} select {school}'s {position} {playerName}. A top-ten investment puts the development plan under a spotlight.",
 "{school}'s {position} {playerName} goes No. {pick} to the {nflTeam}. The next question is how they put that talent to use.",
 "The {nflTeam} use No. {pick} on {school}'s {position} {playerName}. Top-ten expectations arrive with the phone call.",
 "{position} {playerName}, {school}, No. {pick} to the {nflTeam}. That is a major piece of their draft investment.",
 "A top-ten landing for {school}'s {position} {playerName}: No. {pick}, {nflTeam}. Opportunity and expectations in the same announcement.",
 "{school} sees {position} {playerName} come off the board at No. {pick}. The {nflTeam} have made their investment.",
 "At No. {pick}, the {nflTeam} turn to {school}'s {position} {playerName}. Now comes the work of building a role.",
 "Top-ten watch: {school}'s {position} {playerName} to the {nflTeam}, No. {pick}. A draft position that attracts plenty of attention.",
 "The No. {pick} selection is {school}'s {position} {playerName}, headed to the {nflTeam}. Big draft capital behind this one.",
 "{nflTeam}, No. {pick}: {position} {playerName} from {school}. How they develop this top-ten pick is the next story.")
forms('draft-talk.nfl-haul','~',
 "A draft group I want to follow: the {nflTeam} brought in {names}. The next step is turning the picks into useful roles.",
 "The {nflTeam} landed {names}. That group gives me a reason to keep watching their development plan.",
 "One haul worth discussing: {names} to the {nflTeam}. A starting point to like, with the actual work ahead.",
 "Looking at the {nflTeam} class: {names}. Interested in what those players become together.",
 "The {nflTeam} draft group includes {names}. There is something to work with in that collection.",
 "{names} are part of the {nflTeam} haul. Draft-night promise still has to become productive football.",
 "A closer look at the {nflTeam}: {names}. That is one of the groups on my follow-up list.",
 "The {nflTeam} came away with {names}. I like the foundation; development decides the rest.",
 "Draft class to revisit: {nflTeam}, with {names}. The fit on the field is what comes next.",
 "Keeping a note on the {nflTeam} group of {names}. Worth watching beyond the draft announcement.")

pairs('carry.player-training',[
 "Good offseason with my teammates.","Grateful for the time working with this group.",
 "Been a good stretch of work with my guys.","Love the people I get to work with every day.",
 "Appreciate my teammates pushing each other this offseason."],
 ["Ready to get back out there for {school}","Looking forward to another season with {school}"])
pairs('carry.player-training-qb',[
 "Good offseason with this group.","Appreciate the guys putting the time in together.",
 "A lot of work with teammates I trust.","Grateful for another offseason with my guys.",
 "Love the work this group has put in together."],
 ["Ready to take the field for {school}","Looking forward to getting {school} football started"])
pairs('carry.fan-training',[
 "Good to hear about {playerName}'s offseason at {school}.","{school} getting encouraging news on {playerName}.",
 "An offseason step forward for {playerName} at {school}.","{playerName}'s progress is a good {school} update.",
 "Keeping an eye on {playerName} after that {school} offseason."],
 ["Ready to see that work show up on Saturdays","I have talked myself into getting excited again"])
pairs('carry.fan-move',[
 "{school} in the {newConference}.","A new conference for {school}: {newConference}.",
 "The {newConference} is {school}'s new home.","{school} has a whole {newConference} schedule to get used to.",
 "New {school} chapter in the {newConference}."],
 ["A new set of fanbases to argue with. I will adapt","Going to take a little time before that sounds normal"])
pairs('carry.fan-departure',[
 "Wishing {playerName} well after leaving {school}.","Good luck to {playerName} in the next chapter after {school}.",
 "Appreciate {playerName}'s time at {school}.","{playerName} moving on from {school} still feels strange.",
 "Hope things work out for {playerName} after {school}."],
 ["Roster changes feel different when you have cheered for the guy","Still a person behind every roster decision"])

# These are optional analyst wrappers. The underlying analysis supplies all facts
# and can stand alone when it already uses most of the 280-character allowance.
desks={
 'marcus.positive':['That should get your attention.','There is a case worth hearing.','Give them some credit.','This deserves a little noise.','A useful answer to the doubters.','That is worth talking about.','Do not overlook that.','Put that in the conversation.'],
 'marcus.negative':['That is a problem.','This needs a better answer.','Hard to wave this away.','There is a concern here.','That deserves scrutiny.','Do not skip that part.','They have work to do.','That will raise questions.'],
 'tina.positive':['Well, that seems useful.','Someone is enjoying the film this week.','Not bad at all.','A reason to open the group chat.','There is something to smile about.','Worth a second look.','A pretty good detail to have.','That part should travel well.'],
 'tina.negative':['Not exactly ideal.','The film session should be interesting.','A detail they could do without.','That is going to need some attention.','Probably not the plan.','A little less fun on that side.','Someone has homework.','A reason to keep the discussion going.'],
 'chris.positive':['Worth keeping on the radar.','A useful part of the evaluation.','There is something to build on.','A detail that belongs in the discussion.','Good context for the next look.','That strengthens the case.','Another reason to keep watching.','An encouraging piece of evidence.'],
 'chris.negative':['Something to keep watching.','That belongs in the evaluation too.','A concern for the next look.','A detail worth following up.','That needs more attention.','Part of the full assessment.','A question the next game can help answer.','One area to revisit.'],
 'marcus.neutral':['Here is the part worth arguing about.','Start with the evidence.','There is more to discuss here.','Put this in the comparison.','A useful reference point.','Keep this part in view.','One detail for the debate.','Read the numbers first.'],
 'tina.neutral':['A little context for the timeline.','Before the replies get going.','A detail for the group chat.','Here is something to chew on.','For anyone keeping score.','Worth having the numbers handy.','The actual football part.','A useful pause in the argument.'],
 'chris.neutral':['A note from the evaluation.','One piece of the full picture.','Context for the next look.','A useful checkpoint.','A detail to track.','Keep this in the assessment.','Part of the scouting discussion.','Evidence to work from.']}
for key,lines in desks.items():add('desk.'+key,'{analysisText}',*[line+' {analysisText}' for line in lines])
out={'format':1,'revision':'content-review-v100','families':families}
(root/'Content/Runtime/final-cycle-variety-pack.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
