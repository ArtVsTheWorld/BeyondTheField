"""Static calendar-aware reactions and season retrospectives."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.cyclecopy.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])

for kind,verdict in [('normal','The season is complete.'),('rough','A difficult season is complete.'),('winless','A winless season comes to a close.'),('perfect','A full season, undefeated.')]:
    forms('ending.team.'+kind,'{record}. '+verdict+' ~ {nickname} fans. {hashtag}',
        'Thank you,','Grateful for you,','We appreciate you,','Your support matters,','All our thanks to you,',
        'Proud to represent you,','Our thanks go to you,','Thank you for standing with us,','We appreciate the season-long support,','Thank you for being part of this season,')
for kind,label in [('normal','season'),('rough','losing season'),('winless','winless season'),('perfect','undefeated season')]:
    forms('ending.beat.'+kind,'{school} ~ at {record}. The '+label+' is complete; attention turns to the next roster.',
        'finishes','ends the year','closes the season','finishes its schedule','wraps up the year','completes the season','ends its schedule','closes out the year','ends the season','completes its schedule')
normal=[
    '{school} finishes {record}. Now what am I supposed to plan my weekend around?',
    'The {school} season is done at {record}. See everybody in the recruiting replies.',
    '{record}. A whole {school} season gone already. Thanks for the memories and the group-chat material.',
    '{school} football is over. {record}. Going to need a minute before I act like an offseason person.',
    'Final record: {record}. Miss the {nickname} already. Who approved the season ending?',
    '{school} ends {record}. The weekend calendar suddenly has a very unfortunate opening.',
    'That is a wrap for {school}: {record}. I will somehow be checking roster news by tomorrow.',
    '{record} for the {nickname}. The games end; the group chat absolutely does not.',
    'No more {school} games after a {record} finish. Already thinking about the next season.',
    '{school}: {record}. Thank you for another fall of giving me something to care way too much about.'
]
rough=[
    '{school} ends {record}. Still love the team. Would also enjoy more wins next fall.',
    '{record}. The {school} offseason group chat will have several agenda items.',
    'Final record is {record}. Supporting the {nickname} and asking for better football can happen at the same time.',
    '{school} closes {record}. We can be loyal without pretending that was fun to watch every week.',
    'A {record} finish for {school}. The next roster needs more than a good announcement graphic.',
    '{record}. The {nickname} will have my attention next year. They do need to give us more back.',
    '{school} finishes {record}. An offseason plan would be a nice change from an offseason slogan.',
    'The {school} season is done at {record}. I am ready to retire a few of the excuses too.',
    '{record}. Love {school}. Not giving that whole season a free pass.',
    'Final: {record} for the {nickname}. Please make next year easier to watch.'
]
winless=[
    '{school} went {record}. Zero wins. The offseason cannot be business as usual.',
    'A full {school} season and not one win. {record}. The fans deserve an explanation.',
    '{record}. Not a single win for {school}. Please do not ask us to clap for a slogan right now.',
    'Zero wins is not a small rough patch. {school} finishes {record}. Something has to change.',
    '{school}: {record}. The fans kept showing up. The football needs to meet them somewhere.',
    '{record}. I am still a {school} fan. I am also tired of defending a season with zero wins.',
    'The {nickname} finish {record}. Not winning once should have consequences for the plan.',
    '{school} ends {record}. The next offseason update needs to be about actual change.',
    'A winless {school} season. {record}. This is not something we should be asked to get used to.',
    '{record}. Every other fanbase has jokes. {school} needs answers.'
]
perfect=[
    '{school} finished {record}. UNDEFEATED. We will be reminding everybody for a very long time.',
    'Nobody beat the {nickname}. {record}. Please plan accordingly when you see our posts.',
    '{record}. A perfect {school} season. The timeline is about to become a scrapbook.',
    'The entire {school} season. Zero losses. {record}. Still sounds amazing every time I say it.',
    '{school} did not lose once. {record}. We have earned at least a few annoying posts.',
    '{record}. The {nickname} finished what they started. No losses to explain away.',
    'A full undefeated season for {school}. {record}. I will be bringing this up at unreasonable times.',
    '{record}. Perfect from start to finish for the {nickname}. Save every highlight.',
    '{school} went {record}. Nobody gets to add an asterisk where a loss should be.',
    'The {nickname} season ends {record}, undefeated. This group is going to be remembered.'
]
for kind,lines in [('normal',normal),('rough',rough),('winless',winless),('perfect',perfect)]:add('ending.barstool.'+kind,*lines)
afterdark={
 'normal':['{school} ends {record} and I am already sad. Would sign up for the whole thing again.',
    'The {school} season is over at {record}. I spent too much of it yelling and I would like another game immediately.',
    '{record}. Already miss the {nickname}. This is what being way too invested gets me.',
    'No more {school} games. {record}. My weekend has lost its main emotional event.',
    '{school} finishes {record}. I was not ready for the last game to actually be the last game.',
    '{record}. Good or bad, {school} football makes the fall feel like the fall. Going to miss it.',
    'The {nickname} are done at {record}. Somebody give me a roster update before I get sentimental.',
    '{school}: {record}. I already want to do it all over again. There is probably something wrong with me.'],
 'rough':['{record}. Love {school}. Need a much better plan than whatever got us here.',
    '{school} ended {record}. Please do not spend the entire offseason telling me everything is fine.',
    '{record}. I defended the {nickname} all year. I am tired. Show me something different.',
    'The {school} season is over at {record}. Less talking about culture, more fixing the football.',
    '{record}. Still here for {school}. Absolutely not pretending that season was good enough.',
    '{school} gave us {record}. I would like an offseason that does not feel like reruns of the excuses.',
    'A {record} finish. I can be loyal to the {nickname} and furious with the season. Watch me.',
    '{school} ends {record}. The next press conference better have something besides optimism.'],
 'winless':winless,
 'perfect':['{school} went {record}. NOBODY BEAT US. I will make that relevant to every conversation.',
    '{record}. Perfect {school} season. I am going to be a problem about this forever.',
    'Zero losses for the {nickname}. {record}. I do not have to be reasonable today.',
    '{school}: {record}. Nobody gets a turn talking me out of enjoying this.',
    'An undefeated {school} season. {record}. My screen time is going to be embarrassing.',
    '{record}. The {nickname} finished unbeaten and I intend to remind every person I know.',
    '{school} never lost. {record}. I have so many receipts to post.',
    '{record}. A whole season of {school} football and not one loss. I will never be normal about it.']}
for kind,lines in afterdark.items():add('ending.afterdark.'+kind,*lines)
thanks=[
    'Thank you {school}. {record} is the final record, but the people are what I will remember.',
    'Season done at {record}. Grateful for my teammates and everybody supporting {school}.',
    '{school}, appreciate all the love this year. Thankful I got to share this season with my guys.',
    'A lot of memories from this {school} season. Thank you to everybody who was with us.',
    'Thankful for every person who supported us at {school}. {record}. Love this group.',
    'The season is over. Appreciate everyone who kept showing up for us at {school}.',
    'Grateful for another season with my teammates. {school}, thank you for the support.',
    'A lot of love for {school} and everybody who rode with us this year. Thank you.',
    'Going to miss being out there with this group. Appreciate you, {school}.',
    'Final record {record}. A lot more than a record to me. Thank you {school}.'
]
add('ending.player.thanks',*thanks)
add('ending.player.senior',*[
    'My senior season at {school} is over. Thank you to everyone who made these years matter.',
    '{school}, thank you for my senior year. Love the guys and the memories I get to take with me.',
    '{record} to finish my senior season. Grateful for everybody at {school} who was part of it.',
    'The games from my senior season are done. The people at {school} will stay with me. Thank you.',
    'My senior season. {record}. Thank you {school} for the memories and the support.',
    'Hard to put my senior year at {school} into one post. Appreciate all of you.',
    'A lot of love for {school}. My senior season is over, but I am keeping these memories.',
    'Thank you to my teammates, my family and our fans. My senior season at {school} meant a lot.',
    'My senior year ends at {record}. Grateful I got to be part of {school}.',
    '{school}, thank you. The people made my senior season something I will always remember.'
])
perfect_player=[
    '{record}. An undefeated season with my guys. Love this team and everyone at {school}.',
    'A whole season without a loss. {record}. Thank you {school} for riding with us.',
    'UNDEFEATED. {record}. Could not do this without my teammates and everybody behind us.',
    '{school}, we went {record}. A perfect season with a group I will always remember.',
    'Nobody beat this team. {record}. Thankful for every person who helped us get here.',
    'Perfect season. {record}. My guys. Our fans. So much to be thankful for.',
    '{record}. Grateful I got to be part of an undefeated {school} team.',
    'The whole season, no losses. Love my teammates. Thank you {school}.',
    '{school}: {record}. A perfect year with my brothers. Keeping these memories forever.',
    'Finished undefeated at {record}. Appreciate everyone who was with us from the start.'
]
add('ending.player.perfect',*perfect_player)
add('ending.player.senior-perfect',*[line+' My senior season. Could not ask for better memories.' for line in perfect_player])

forms('ending.recruiting','{school} finishes {record}. ~ No. {classRank} nationally; it is not a final signing-day ranking.',
    'The current recruiting class is','The class now sits','Recruiting stands at','Its live class ranking is','The recruiting class checks in at','The incoming class currently ranks','Its class is currently','The class ranking stands at','The current national recruiting ranking is','The recruiting class is now')
forms('ending.coach-pressure','After a {record} finish at {school}, coach {coachName} ~. No coaching change is announced.',
    'faces job-security pressure','is under job-security pressure','has job security to address','enters a difficult job-security discussion','has job security in the spotlight','faces questions about job security','has his job security under scrutiny','enters a pressure-filled offseason','is under scrutiny over job security','has job-security concerns to navigate')
forms('ending.expectation-review','~ {school} finishes {record}. {expectationNote}',
    'The full-season verdict:','Season review:','The final record is in:','The offseason starts here:','Looking back at the season:','A season in context:','The final line:','Evaluating the finish:','The season-long result:','The full-year picture:')
forms('cycle.outlook','{school} finishes {record}. {expectationNote} ~',
    'Next comes roster retention and recruiting.','The next roster is the offseason priority.','Attention shifts to building next season\'s group.',
    'Retention and the incoming class come next.','The next questions concern who stays and who arrives.',
    'Roster planning now replaces game planning.','The offseason focus is the players coming back and the incoming class.',
    'Next season starts with the roster decisions.','Recruiting and retention will shape the next team.',
    'The next step is deciding what to keep and where to improve the roster.')
forms('cycle.staff-plan','With {school}\'s season over, {coachName} ~.',
    'turns to roster retention and the incoming class','has the next roster to build','faces an offseason of roster decisions',
    'must fit the incoming class around the returning roster','has retention and recruiting to address','looks to shape the next team',
    'turns from weekly preparation to roster building','has the next roster cycle to plan','has returning players and incoming recruits to fit together',
    'has roster continuity and recruiting needs to balance')
forms('cycle.injury-recovery','Offseason availability update: {school}\'s {playerName} ~. The team\'s season is already complete.',
    'is no longer listed as injured','has come off the injury list','no longer has the injury designation','has had the injury listing cleared',
    'is off the current injury list','is no longer on the injury list','is not carrying the injured listing now','has a cleared injury status',
    'is not currently listed as injured','has seen the injured designation removed')
forms('cycle.injury-rehab','{school}\'s season is over, and {playerName} ~. The focus is recovery before the next season.',
    'remains listed as injured','is on the current injury list','still has an injury designation','is still listed as injured',
    'continues to carry an injured designation','has an injury to recover from','remains on the injury list','is still on the injury list',
    'has not cleared the injured listing','still carries an injury status')
forms('cycle.portal-needs','{school} has {count} {seniorLabel} at {position}. ~',
    'That position belongs on the offseason roster watch.','The staff has an experience gap to plan for there.',
    'Replacing that experience is part of the roster discussion.','The portal is one possible route to replenish the room.',
    'That is one group to monitor during roster turnover.','Returning depth and incoming additions will matter in that room.',
    'Recruiting and development both have a role in replenishing that group.','The next depth chart will need a plan for that experience.',
    'How the staff refreshes that room is an offseason question.','That group is part of the next roster-building task.')
forms('cycle.portal-plan','{school}\'s offseason begins with its own roster. ~',
    'Who stays helps determine the portal needs.','Retention comes before a complete portal shopping list.',
    'The staff needs to know its returners before filling the gaps.','Keeping contributors can matter as much as a new arrival.',
    'The portal plan depends on the players already in the building.','The remaining roster will shape which positions need help.',
    'Departures and returners set the next recruiting priorities.','Roster continuity is part of the portal calculation.',
    'Available spots and returning experience will drive the next additions.','The next additions have to fit what is staying.')
forms('cycle.recruit-fit','{starDetail}{playerName} is signed with {school}. ~',
    'An incoming player to follow as the next roster takes shape.','A confirmed part of the incoming class.',
    'The focus turns from recruiting the player to finding the right role.','One of the new names in next season\'s roster discussion.',
    'A signature that belongs in the offseason roster plan.','The next step is the move into the program.',
    'That is a signed addition, rather than an open recruitment.','A name in the incoming class to keep on the local radar.',
    'Part of the roster-building work already completed.','An addition to the next chapter of the program.')
forms('cycle.class-build','{school}\'s recruiting class currently ranks No. {classRank}. ~',
    'That is a live ranking, with signing work still ahead.','The class is still taking shape.','This is the current position, not a final signing-day result.',
    'The remaining recruitments can still change it.','The staff still has the rest of the class to finish.',
    'The rank can move as more signatures arrive.','Recruiting continues beyond this snapshot.','The offseason class picture remains open.',
    'Treat that as the current class position.','The final class is not set by this update.')
forms('cycle.portal-target','{school} ~ for transfer prospect {playerName}. No commitment is confirmed.',
    'is among the recorded top three schools','appears in the top three','is in the listed top three','has a place among the top three schools',
    'is one of the top three schools listed','shows up in the current top three','is included among the three leading schools',
    'has a spot on the current top-three list','is one of the three schools in the leading group','features in the recorded top three')
forms('cycle.program-bar','~ {school}: {standard}',
    'The preseason standard at','The expectation entering the season at','The starting expectation for','What a successful season should mean at',
    'The season outlook at','The program standard for','The bar entering the season at','The expectation to judge against at',
    'The preseason ambition at','The season\'s starting bar for')

root.joinpath('Content/Runtime/cycle-variety-pack.json').write_text(json.dumps({'revision':'cycle-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
