"""Static preseason and opening-week copy; future outcomes remain predictions."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.opening.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])

forms('preseason.poll.beat','{school} ~ No. {rank} in the preseason AP poll. The games will test that starting point.',
    'opens at','begins at','starts at','checks in at','is ranked','enters the season at','comes in at','is listed at','starts the year at','is placed at')
forms('preseason.team.hype','~ {nickname}. {hashtag}',
    'A new season for the','Ready for another year,','The countdown is on,','The next chapter belongs to the',
    'New year. Same pride for the','Ready for football,','The season is getting closer,','Your team. Your',
    'Getting ready to represent the','The next season is coming for the')
pairs('preseason.fan.excited',[
    'The {school} season cannot get here fast enough.','Ready for the {nickname} to take over my weekends again.',
    'Already counting down to {school} football.','The schedule is out and I am making everything else fit around {school}.',
    'Another {school} season is coming. I have talked myself into being excited again.'],
    ['Bring on kickoff','The waiting is the worst part'])
pairs('preseason.fan.nervous',[
    'I love {school}. I would also love a slightly less stressful football season.',
    'New {school} season, same inability to relax about any of it.',
    'The {nickname} are almost back. My optimism and my nerves are having an argument.',
    'I want to believe in {school}. I also know how much of my fall mood depends on this.',
    'Every year I promise to be calm about {school}. Every year kickoff gets closer and that falls apart.'],
    ['Please make this fun','I am going to need some good Saturdays'])
personal={
 'Leader':['Excited to share another season with this group.','Proud of the people around me. Ready for the season.',
    'Grateful to start another year with my teammates.','Ready to represent this team again.','Looking forward to what we can do together this year.'],
 'Intense':['Ready to get after it with my guys.','Been counting down to this season.','The season cannot get here fast enough.',
    'Another year to compete with my brothers.','Ready for football. Ready for this group.'],
 'Entertainer':['Football season needs to hurry up.','Missed this feeling with my guys.','The countdown is getting checked way too often.',
    'I have waited long enough to wear these colors on game day.','Almost football time again. Yeah I missed this.'],
 'TeamPlayer':['Another year with my brothers. Would not trade this group.','Excited to get back out there with my teammates.',
    'The guys make this time of year special.','Ready to share another season with this team.','My teammates and a new season. A lot to be thankful for.'],
 'Unpredictable':['Season cannot get here fast enough. Keep that same energy.','Ready for the season and everything people have been saying.',
    'The talking part of the year has lasted long enough.','Almost time to let football take over the timeline.',
    'A new season. I know a few people have predictions to remember.'],
 'Neutral':['Ready to get back out there.','Looking forward to the season with my teammates.','Excited for another year with this team.',
    'Grateful for another chance to play with my guys.','The next season is almost here. Looking forward to it.'],
 'QB':['Excited for another season with this group.','Ready to get the season started with my teammates.',
    'Grateful to represent this team again.','Looking forward to sharing another year with my guys.',
    'Proud to be part of this group heading into the season.']}
for personality,leads in personal.items():pairs('preseason.player.'+personality,leads,['Appreciate everybody supporting us. {hashtag}','Thankful for the people behind us. {hashtag}'])
forms('preseason.opener.beat','{school} ~ against {opponent}. Camp will give way to an actual game.',
    'opens the season','starts the season','begins the year','plays its opener','gets the season started','begins its schedule','kicks off the season','opens the year','starts its schedule','gets its first test')
forms('preseason.honor.beat','{school}\'s {playerName} ~ as a {award} selection. The regular-season work is still ahead.',
    'enters the season','starts the year','has preseason recognition','heads into the season','opens the year','starts camp','begins the season','has been recognized','has a place on the list','comes into the year')
forms('preseason.outlook.analyst','{school} has {count} national preseason All-America {selectionLabel}, including {playerName}. ~',
    'That is one source of preseason expectation.','The games will test whether the production follows the recognition.',
    'Those are expectations to measure against actual play.','A starting point for evaluating the talent on this roster.',
    'Preseason recognition gives us names to track.','Keep those expectations in view once the games begin.',
    'The honors are preseason recognition, with the season still to play.','A useful set of names before the first kickoff.',
    'The recognition puts some individual expectations on this team.','Watch how that preseason recognition translates on the field.')
forms('preseason.recruit.watch','~ {starDetail}{position} {playerName}, No. {nationalRank} nationally.{recruitRankDetail}',
    'Preseason recruiting watch:','A recruiting name to know:','On the recruiting radar:',
    'A prospect to follow this year:','The early recruiting notebook:','One name for the recruiting watch list:',
    'Recruiting spotlight:','The prospect watch:','A name in the upcoming class:','On the preseason prospect list:')
add('preseason.recruit.self','Ready for another season with my guys.','A lot to look forward to this year. Ready for football.',
    'Missed playing with my teammates. Ready to get back out there.','Another season coming. Thankful for the opportunity.',
    'Excited to be back on the field with this group.','Been looking forward to getting the season started.',
    'Ready to make more memories with my guys.','The season needs to hurry up.','A new season with my teammates. Ready for it.',
    'Looking forward to this year. Appreciate everybody supporting me.')
forms('preseason.gauntlet.analyst','{school} faces {count} preseason AP-ranked opponents in Weeks {startWeek}-{endWeek}: {opponents}. ~',
    'That is a concentrated stretch of the schedule.','The difficult matchups are clustered together.',
    'That window stands out before a game has been played.','Keep that part of the schedule in view.',
    'A demanding window on the preseason schedule.','That is the stretch to circle on the calendar.',
    'Those weeks pack several early tests together.','The preseason rankings make that a notable run of opponents.',
    'The schedule does not spread all those tests out.','Several preseason measuring sticks arrive in the same window.')
for key,stance in [('respect','higher'),('caution','lower')]:
    forms('preseason.'+key+'.analyst','{school}: AP No. {rank}, our title-model board No. {modelRank}. ~',
        'The model is '+stance+' on the roster than the voters.','Two different preseason evaluations, with the games still ahead.',
        'That gap deserves a closer look once the season begins.','There is a disagreement to test on the field.',
        'The poll and the model start in different places.','That is a useful preseason argument, not a settled answer.',
        'The season gets to decide which view holds up.','Watch whether the games support the poll or the model.',
        'The roster model and the AP voters do not see the same starting point.','A reason to watch, rather than a promise about the season.')
forms('preseason.debate.fan','{analystHandle} ~',
    'You can argue about the model. I am ready to watch the {nickname} play',
    'The {nickname} have to play actual football before I lose sleep over a model',
    'I would enjoy settling this with {school} games instead of another spreadsheet',
    'The {school} season has not started and we are already debating the rankings. Of course',
    'Let the {nickname} get on the field. We will have plenty to argue about then',
    'The {school} part of this discussion needs a football game',
    'I have opinions about {school}. I would prefer a kickoff to support them',
    'Fine. The {nickname} get a whole season to answer',
    'Bookmark it. I would love for {school} to settle this on the field',
    'You have a model. I have unreasonable {school} optimism. Let the games decide')
forms('preseason.coaches.beat','{school}: preseason AP No. {rank}, Coaches poll No. {coachesRank}. ~',
    'Two polls, two different starting points.','The coaches and the AP voters do not agree on the spot.',
    'That is the preseason poll comparison.','The two preseason lists see the same team differently.',
    'Both rankings are starting points for the season.','A poll split to keep in mind before kickoff.',
    'There is already a difference between the two preseason ballots.','The field will test both evaluations.',
    'That is where the two polls place this roster.','The preseason ranking discussion has two reference points.')
forms('preseason.talent.analyst','{conference} preseason All-Conference picture: {leaders} {leadVerb} with {leaderCount} selections. {count} different players were selected across the league. ~',
    'That is where the preseason recognition is concentrated.','The games will test those individual expectations.',
    'The honors give us one view of the conference talent map.','Those are the preseason names to track.',
    'One starting point for the league\'s talent discussion.','The selections put some early expectations on those rosters.',
    'This is recognition before the season, rather than a final verdict.','The preseason recognition is unevenly spread.',
    'Keep those expectations in view once league play begins.','Those players enter the year with recognition to justify.')
forms('poll.initial.beat','The current CFP rankings ~ {school} at No. {rank}. This is the playoff-picture reference point.',
    'place','have','list','put','rank','show','position','feature','include','introduce')

forms('launch.return','{school} ~ a {wins}-{losses} season. The question is what carries into this year.',
    'is coming off','follows','returns after','enters camp after','starts the year after','begins the new season after',
    'comes back after','opens camp following','prepares for the next year after','turns the page on')
forms('launch.rebuild','{school} ~ a {wins}-{losses} season. Improvement has to show up on the field.',
    'is trying to rebuild after','needs a response to','looks for a reset after','starts over after','seeks progress after',
    'has work to do after','is looking for a better direction after','must take a step forward after','needs to change the picture after','faces a rebuilding task after')
forms('launch.champion','~ {nickname}. The national champions begin a new season. {hashtag}',
    'A new chapter for the','The title defense starts here,','Back for another season,','The champions are back,',
    'A new year for your','The next season is coming,','Ready for a new challenge,','The next chapter awaits,',
    'Champions entering a new year,','Time for the next season,')
forms('launch.conference_defense','~ {nickname}. Conference champions entering a new season. {hashtag}',
    'The next chapter starts here,','The defense begins,','Ready for a new year,','The champions are back,',
    'Another season for the','The new season is coming,','Ready for the next challenge,','A new year for the',
    'The next chapter awaits,','Time for another season,')
forms('launch.playoff_return','{school} reached the {finish} after going {wins}-{losses} last season. ~',
    'That is the reference point for this team.','The next roster has a postseason finish to measure against.',
    'A new season starts with that run in the background.','Getting back is the first challenge.',
    'The program enters this season with that run on its resume.','That finish gives the new season a clear backdrop.',
    'The next team has an example to follow.','The season starts with a concrete postseason benchmark.',
    'The challenge now is carrying that into another year.','The next schedule will test whether the program can sustain it.')
forms('launch.bowl_return','{school} comes off {wins}-{losses} and {bowlResult}. ~',
    'The next season starts with that bowl finish in the background.','That is a result to build from.',
    'A concrete finish to compare with the next team.','The next roster has a bowl-season result to compare against.',
    'The new roster will be judged against that season.','The next schedule offers the chance to build on it.',
    'That gives the season outlook a real reference point.','Bowl participation is part of the program\'s recent resume.',
    'The new year has a postseason finish to measure against.','The next challenge is turning that into continuity.')
forms('launch.new_coach','~ {coach} at {school}. The opener begins the evaluation of a new staff.',
    'The first season for','Year one for','A new start under','The opening year under','The first year for',
    'A first season ahead for','A new era under','The first campaign for','The debut season for','A fresh start with')
forms('launch.veteran_coach','~ {school}: {coach} enters Year {seasonNumber}.',
    'Continuity at the top for','A returning head coach at','The staff context for','The coaching backdrop at',
    'The head-coaching timeline at','A familiar leader at','The head-coach note for','The season\'s coaching context at',
    'The coaching tenure at','The returning staff leader at')
forms('launch.recruiter','{coach} ~ at {school}. The long-term task is turning incoming talent into on-field results.',
    'brings a recruiting-focused background','has a strong recruiting focus','takes a recruiting-first approach',
    'emphasizes recruiting in his approach','has a background centered on recruiting','puts recruiting at the center of his approach',
    'brings a recruiter\'s background','leans on a recruiting background','has a recruiting-led approach','builds around a recruiting focus')
forms('launch.developer','{coach} ~ at {school}. Camp puts the next group of players in that development process.',
    'emphasizes player development','has a player-development focus','builds around player development',
    'puts development at the center of his approach','has a development-focused background','takes a development-led approach',
    'brings a player-development background','leans on player development','places an emphasis on developing players','has development as a central priority')
forms('launch.coordinator','{coordinator} ~ to the {school} {side}. How the scheme fits the roster is one question for the season.',
    'brings a scheme-focused approach','brings a scheme-led background','brings a strong scheme focus','adds a scheme-focused perspective',
    'brings a tactical focus','brings a scheme-centered background','adds a scheme-led approach','brings a scheme-oriented approach',
    'adds a tactical background','brings an emphasis on scheme')
forms('launch.battle','{school}\'s {position} picture includes {first} and {second}. ~',
    'Our camp evaluation puts them close enough for a genuine competition.','The preseason evaluation has little separating the two.',
    'The depth-chart order should not be treated as settled by the evaluation alone.','They are closely matched in the preseason evaluation.',
    'That is a close pairing to follow through camp.','There is little separation in our look at the two.',
    'The camp competition deserves a closer look.','The two are close enough to make the role worth tracking.',
    'This looks like a position competition to monitor.','A close preseason evaluation makes that pairing interesting.')
forms('launch.freshman','True freshman {position} {playerName} ~ at {school}. A role still has to be earned.',
    'is a newcomer to watch','belongs on the newcomer watch list','is a promising new face','is an incoming player to follow',
    'has caught the preseason eye','is part of the freshman watch','is one of the more interesting newcomers','is a young name to know',
    'is a freshman to keep on the radar','is worth watching through camp')
forms('launch.breakout','{school} breakout watch: {classLabel} {position} {playerName}. ~',
    'The talent makes this an interesting name before the numbers arrive.','The preseason evaluation suggests a player worth following.',
    'A bigger role would give that talent a chance to show.','There is a development story to monitor here.',
    'One of the names to follow as roles take shape.','Camp and the early games will test that promise.',
    'Watch how the role develops once play begins.','The opportunity still has to become production.',
    'This is an early evaluation, with the real work ahead.','A young player to keep in view this season.')
add('launch.senior','One more season with my guys. Going to appreciate all of it. {hashtag}',
    'My senior season is coming. Grateful for the people I get to share it with.',
    'Senior year with this group. Ready to make some more memories.',
    'Last season as a senior. Thankful I get to do this with my teammates.',
    'My senior season. The time went fast. Looking forward to every bit of this year.',
    'Another year with my brothers. Senior season means a lot.',
    'Senior year is here. Appreciate everyone who has been part of the journey.',
    'Ready for my senior season. Grateful for the guys around me.',
    'My senior season with this team. Want to take in every moment.',
    'A lot to be thankful for heading into senior year. Love this group.')
add('launch.nil','Appreciate the people supporting me on and off the field. {hashtag}',
    'Thankful for these opportunities and everyone who helped me get here.',
    'Grateful for the support beyond football too. Means a lot.',
    'Appreciate everybody giving me opportunities on and off the field.',
    'Thankful I get to represent good people. Appreciate the support.',
    'A lot of people helping me along the way. Grateful for all of it.',
    'Appreciate the opportunities and the people in my corner.',
    'Feeling thankful for the support on and off the field.',
    'Grateful for every opportunity to represent this team and my people.',
    'Thank you to everyone supporting what I do, on the field and beyond it.')
forms('launch.spotlight','~ {position} {playerName}: preseason All-American. {hashtag}',
    'A preseason spotlight for','Recognition for','Preseason honors for','A name to know:',
    'Our preseason All-American,','Honored before kickoff,','Proud to recognize','A preseason selection for',
    'A player in the spotlight,','The preseason recognition goes to')
forms('launch.heisman','{school}\'s {position} {playerName} ~. Production will decide the case.',
    'is an early Heisman name to monitor','belongs on an early Heisman watch','is a possible Heisman candidate',
    'has the talent to enter the Heisman conversation','is a preseason Heisman possibility','is an early name in the Heisman discussion',
    'is a player to follow for a possible Heisman push','is on the early Heisman radar','is worth tracking as a Heisman possibility',
    'has a chance to enter the Heisman picture')
forms('launch.darkhorse','{school} is unranked in the preseason AP poll. ~',
    'Our roster evaluation makes it a team to watch.','I like this roster more than its absence from the poll suggests.',
    'A possible dark horse based on the preseason roster evaluation.','There is enough on this roster to make the team interesting.',
    'This is one unranked team I am keeping an eye on.','Our preseason evaluation sees more than the poll position.',
    'The roster offers a reason to look beyond the Top 25.','A roster-based outside contender to monitor.',
    'The preseason evaluation has it ahead of several ranked teams.','The games will test why our evaluation likes the roster.')
forms('launch.schedule_opportunity','None of {school}\'s scheduled regular-season opponents is in the preseason AP Top 25. ~',
    'An opportunity on paper, not a promise of easy wins.','That is the preseason snapshot; unranked is not harmless.',
    'The schedule offers an opening if the team can use it.','The rankings will change once the games begin.',
    'A favorable preseason view still has to become results.','There are no automatic wins hidden in that fact.',
    'The team still has every one of those games to play.','Preseason rankings describe the schedule before the tests.',
    'It is an opening, with the football still to settle.','The path looks favorable through one preseason lens.')
forms('launch.transfer','{school} adds {position} {playerName}, with last season\'s production at {formerSchool}. ~',
    'There is college experience behind this addition.','That brings a different starting point from a brand-new college player.',
    'An experienced newcomer to follow this year.','The next test is carrying that experience into a new program.',
    'A new school, with college production already on the resume.','The roster gets experience from another program.',
    'The new staff has an experienced player to work with.','Prior college experience is part of the fit.',
    'One of the experienced arrivals in this camp.','The role at the new school is the next story.')
forms('launch.kickoff','~ {nickname}. {hashtag}',
    'Football is back. Let\'s go,','A new season begins for the','The season starts now,','Opening week is here,',
    'Time for football,','The wait is over,','The next season is here,','New season. Same',
    'The games are back,','It is football season,')
forms('launch.venue','Opening week at {stadium}. ~ {nickname}. {hashtag}',
    'Our house. Our','Home for the','A home stage for the','Ready for the','Home turf for the',
    'The stage is ready for the','Our home. Your','The lights are ready for the','A new season for the','Game week for the')
forms('launch.opening_preview','{school} opens against {opponent}. ~',
    'The first game turns the camp discussion into actual football.','The opener gives us a first test against another team\'s plan.',
    'The first live matchup will tell us more than the preseason arguments.','A first chance to see how the roster works together.',
    'The opening game is the first real measuring stick.','The first test is here, with a full season still ahead.',
    'Camp gives way to a different team across the line.','The season starts with a real opponent instead of a projection.',
    'The first result will start answering the preseason questions.','The opener is a starting point for the evaluation.')
forms('launch.coach_debut','{coach} ~ at {school} against {opponent}.',
    'makes his head-coaching debut','begins his first season','opens his first year','starts his first campaign',
    'begins his tenure','opens his tenure','starts his first season','coaches his first game',
    'gets his first game','begins his opening season')
forms('launch.countdown','~ Week {openerWeek}, {nickname} vs. {opponent}. {hashtag}',
    'The opener is getting closer:','Our first game:','The countdown is on:','The season starts here:',
    'Opening-game plans:','The first matchup is set:','The next chapter begins:','Mark the opener:',
    'The first date on our schedule:','The opener on the calendar:')
forms('launch.depth','{classLabel} {playerName} ~ on {school}\'s current QB depth chart before the opener against {opponent}.',
    'is listed first','holds the first spot','is at the top','has the first-team listing','is in the top spot',
    'occupies the first spot','has the No. 1 listing','is the first name','has the first position','is the top listed player')
for key,leads in [('player_opening',[
    'Football is back. Ready with my brothers.','New season. My guys. Ready to get going.',
    'Opening week is here. Been waiting to get back out there.','Ready to start this season with my team.',
    'The games are finally here. Ready to go.']),('player_opening_qb',[
    'Excited to start this season with my teammates.','Ready for the opener with this group.',
    'Grateful to get another season started with my guys.','Looking forward to the first game with this team.',
    'Proud to represent this group as the season begins.'])]:
    pairs('launch.'+key,leads,['Appreciate all the support. {hashtag}','Thank you to everyone behind us. {hashtag}'])
forms('launch.favorite','My preseason {conference} lean is {school}. ~',
    'The roster model puts them at the front of the league.','They lead our roster-based conference evaluation.',
    'The roster evaluation makes them the early pick.','The projection favors this roster within the conference.',
    'The roster-based forecast starts them at the top.','They get the nod from the preseason roster model.',
    'The games still decide it, but the model starts here.','The early roster comparison favors them.',
    'The preseason evaluation gives them the edge.','The roster model gives them the conference\'s early advantage.')
forms('launch.recruit_watch','~ {school} this opening week.',
    'Definitely watching','Looking forward to watching','Got my eye on','Want to see how they play at',
    'Ready to watch','Interested to see','Going to be watching','Checking out the game for',
    'The watch list starts with','Want a closer look at')
forms('launch.recruit_tag','{tagHandle} ~ {school} this season.',
    'Good luck! Going to be watching','Good luck this year. Looking forward to watching',
    'Have a good season! Keeping an eye on','Good luck out there. Ready to watch',
    'Looking forward to seeing you play for','Good luck! Got my eye on',
    'Have a great year. Going to follow','Good luck with the season. Definitely watching',
    'Ready to watch you play for','Hope you have a great season with')
add('launch.high_school','High school season is coming. Ready to get out there with my guys.',
    'Another high school season with my teammates. Looking forward to it.',
    'Ready to start the high school season. Appreciate everyone supporting us.',
    'High school football is almost back. Missed playing with this group.',
    'Looking forward to the season with my high school teammates.',
    'My high school team and a new season. Ready for this.',
    'High school season is almost here. A lot to look forward to.',
    'Ready for another year on the field with my high school guys.',
    'The high school season cannot get here fast enough.',
    'Another season coming for my high school team. Thankful for the opportunity.')
forms('launch.visit','~ {school} for a visit this opening week. Excited to get around the team.',
    'Heading to','Visiting','Making a trip to','Looking forward to seeing','Going to',
    'Taking a trip to','Getting ready to visit','Ready to check out','Planning to see','Excited to visit')
forms('launch.dominant_debut','{school} ~ {opponent}, {score}, in the opener. A strong first result, with a season still to play.',
    'beats','defeats','takes down','gets past','wins against','prevails over','earns a win over','finishes ahead of','gets the better of','comes out on top against')
forms('launch.close_debut','{school} ~ {opponent}, {score}, in a close opener. The first win comes with plenty to review.',
    'edges','gets past','wins a close one against','comes out ahead of','earns a narrow win over','beats','finishes ahead of','prevails over','takes a tight one against','gets the better of')
forms('launch.opening_takeaway','{school} opens with a {score} win over {opponent}. ~',
    'One game in and the season-long predictions are already warming up.','Actual football to discuss. Trying not to make it an entire-season verdict yet.',
    'The first result gives us more than another camp argument.','One result is a start, not a full season evaluation.',
    'The first overreactions are going to be impressive.','Good to have a game instead of another projection.',
    'A first win and immediately a thousand season predictions.','We can learn from an opener without pretending it answers everything.',
    'The timeline has enough material for a week already.','The opener is in. Try to leave room for the rest of the season.')
forms('recruiting.catchup.commit','~ {starDescription}{position} {playerName} is committed to {school}, a new addition since Week {observedSinceWeek}.{recruitRankDetail}',
    'Recruiting catch-up:','Since our last check-in:','Catching up on the class:','A commitment update:',
    'The class since the last report:','A recruit to catch up on:','The recruiting update:',
    'An addition since our last report:','A catch-up from the recruiting trail:','The class update:')
forms('recruiting.catchup.offer','~ {school} has offered {position} {playerName} since our Week {observedSinceWeek} report.{recruitRankDetail}',
    'Offer catch-up:','Recruiting catch-up:','Since the last check-in:','A scholarship update:',
    'An offer since the last report:','The offer-board update:','Catching up on the board:',
    'From the recruiting catch-up:','An update on the scholarship board:','The recruiting-board note:')

root.joinpath('Content/Runtime/opening-variety-pack.json').write_text(json.dumps({'revision':'opening-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
