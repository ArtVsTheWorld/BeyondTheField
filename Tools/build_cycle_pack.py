import json
from pathlib import Path
families = {}
def add(key, *lines):
    families[key] = [{'id': key + '.v80.' + str(i + 1), 'body': line} for i, line in enumerate(lines)]

add('narrative.game',
    '{winner} beats {loser}, {score}. {turningPoint} {detail}',
    '{winner} {score} over {loser}: {turningPoint}',
    'How {winner} got past {loser}, {score}: {turningPoint}')
add('ending.expectation-review',
    '{school} finishes {record}. {expectationNote}',
    'Season review for {school}: {record}. {expectationNote}')
add('cycle.outlook',
    "The {school} schedule is finished at {record}. {expectationNote} The conversation now moves to roster retention, the recruiting class and next season.",
    '{school}: {record}, with the season complete. {expectationNote} Recruiting and roster decisions are the next part of this story.')
add('cycle.staff-plan',
    '{school} is into the roster-building part of the calendar. For head coach {coachName}, retaining the core and finishing the incoming class are the next tests.',
    'The next {school} chapter is a roster question for {coachName}: who stays, who signs and which needs remain after those decisions.')
add('cycle.injury-recovery',
    'Offseason health update at {school}: {playerName} is no longer listed as injured. The team’s playing schedule is already finished.')
add('cycle.injury-rehab',
    '{school} offseason injury update: {playerName} is listed as injured. The next issue is recovery and preparation, with the team’s season on the field finished.')
add('cycle.team-reset',
    'Thank you for riding with the {nickname} this season. The work on the next chapter is already underway.',
    'Our season on the field is finished. Our program keeps moving. Thank you, {nickname} fans, for showing up for us.')
add('cycle.fan-standards',
    '{record} and now we wait through a whole offseason. {expectationNote} Need a real plan for this roster, not another slogan',
    '{school} fans deserve an offseason with some answers. {record} was not the goal. Get the roster right and give us a reason to believe again')
add('cycle.fan-future',
    'already checking the {school} recruiting class like it is going to make the offseason shorter. See everybody next season',
    '{school} football being over for the year is a terrible development for my weekends. Give me recruiting news. Give me something')
add('cycle.player-reset',
    'appreciate everybody who showed up for us this year. Already looking forward to being back with this group',
    'Season went fast. grateful for my teammates and everybody who supported us. Got a lot to look forward to')
add('cycle.portal-needs',
    '{school} has {count} {seniorLabel} at {position}. How that group is replenished belongs on the offseason watch list; the portal is one route to monitor.',
    'Roster planning at {school}: {count} {seniorLabel} at {position}. Returning eligibility still matters, but that is a group worth watching in recruiting and the portal.')
add('cycle.portal-plan',
    '{school} is into roster-planning season. Retaining its own players comes first; the portal conversation should follow actual needs, not a wish list of every available name.',
    'The next {school} story is who stays, who arrives and where the roster needs help. Portal fits matter more than collecting recognizable names.')
add('cycle.signed-spotlight',
    '{tagHandle} is part of our signed class. Excited for the future with the {nickname}.',
    'The next chapter includes {tagHandle}. Proud to have you in our signed class, {playerName}.')
add('cycle.recruit-fit',
    '{starDetail}{playerName} is already signed with {school}. With the season finished, that incoming {position} is part of the program\u2019s next chapter.',
    'Looking ahead at {school}: signed {starDetail}{playerName} adds to the incoming group at {position}. Recruiting is now central to the offseason conversation.')
add('cycle.class-build',
    '{school} is off the game schedule and back to roster building. Its current recruiting class sits No. {classRank}. That is a live ranking, not a final signing-day finish.',
    'Offseason watch at {school}: the current class is No. {classRank}. How the staff finishes that group matters more now that the games are done.')
add('cycle.portal-target',
    '{school} is among the recorded top three schools for transfer prospect {playerName}. A potential portal fit to monitor, not a commitment.',
    'One verified portal name connected to {school}: {playerName}, whose current top three includes the program. The recruitment is still open.')
add('cycle.team-welcome',
    'Welcome to the squad, {tagHandle}! {playerName} is officially signed with the {nickname}.',
    'Signed and part of the family. Welcome, {tagHandle}. Excited to have {playerName} joining the {nickname}.')
add('cycle.fan-loss-standard',
    '{school} loses to {opponent}, {score}. {expectationNote} We can talk about next steps without pretending this is the standard.',
    '{opponentScore}\u2013{ownScore} against {opponent}. {school} should be aiming higher than this. {expectationNote}')
add('cycle.program-bar',
    'The preseason standard at {school}: {standard} The roster and schedule will decide whether the program gets there.',
    'Setting expectations for {school}: {standard} That is the frame for the season, before the first result changes the mood.')

add('cycle.context-turnaround',
    '{school} is {wins}\u2013{losses}, after {priorWins}\u2013{priorLosses} last season. The year-over-year improvement is real. {expectationNote}')
add('cycle.context-regression',
    '{school}: {wins}\u2013{losses}, compared with {priorWins}\u2013{priorLosses} last season. {expectationNote}')

add('buzz.title-stage',
    'One game left. {home} vs. {away} for the national championship. No next round, no second chance. This is the biggest stage of the season.',
    'The national championship is here: {home} against {away}. Everything this season has led to this matchup.')
add('buzz.stage',
    '{home} vs. {away} in the {eventLabel}. A trophy or the next playoff round is on the line.',
    'The stage this week: {home}, {away}, the {eventLabel}. This is what the season has been building toward.')
add('buzz.pick-1',
    '{eventLabel}: my pick is {pick}. {lineContext} {shapeContext} This is still a game that has to be won on the field.',
    '{pick} is my lean against {opponent}. {lineContext} The {eventLabel} deserves a prediction with some context behind it.')
add('buzz.pick-2',
    'Putting a name on it: {pick}. {shapeContext} {lineContext} Save the post if you want. This is the {eventLabel}; taking a position is part of the fun.',
    'My {eventLabel} pick is {pick}. {shapeContext} {lineContext} I am not picking a tie in the argument.')
add('buzz.pick-3',
    'leaning {pick} for the {eventLabel}. {shapeContext} {lineContext} The replies to this one should be very normal',
    '{pick} is my pick. {lineContext} {shapeContext} Very excited for everyone to respond calmly to a {eventLabel} prediction.')
add('buzz.pick-4',
    'My {eventLabel} lean: {pick}. {lineContext} {shapeContext} The matchup matters more than assuming every postseason game is evenly balanced.',
    '{lineContext} {shapeContext} I lean {pick} in the {eventLabel}; an occasion this big still needs an honest matchup assessment.')
add('buzz.pick-5',
    '{pick} is my {eventLabel} choice. {shapeContext} {lineContext} This is the stage where individual matchups get everybody\u2019s attention.',
    'For the {eventLabel}, I lean {pick}. {lineContext} {shapeContext} Big-stage expectations do not make the matchup automatically even.')
add('buzz.team-pregame',
    '{nickname}. {opponent}. The {eventLabel}. One more stage to own.',
    'Everything for this moment. The {nickname} take on {opponent} in the {eventLabel}.')
add('buzz.fan-pregame',
    '{school} in the {eventLabel}. I have been staring at this matchup with {opponent} all week. Please let this be our day',
    'if anybody needs me during {school}\u2013{opponent} in the {eventLabel}, no you do not. This one has my whole attention')
player_lines={
 'QB': ('The {eventLabel} against {opponent}. Proud to be here with this group. Appreciate everybody supporting us.', 'Grateful for this opportunity with my teammates. {opponent} is next in the {eventLabel}.'),
 'Leader': ('The {eventLabel}. {opponent}. Proud to share this stage with this team. Let us hear you.', 'Love this group. Appreciate everybody riding with us into the {eventLabel} against {opponent}.'),
 'TeamPlayer': ('Would not trade this group for anything. {opponent} in the {eventLabel}. Let’s do this together.', 'Me and my teammates on this stage. {eventLabel} against {opponent}. That means everything.'),
 'Entertainer': ('{eventLabel} with the guys. {opponent} next. yeah I’m ready for this one', 'Big stage. {opponent}. {eventLabel}. We here now, let’s have some fun'),
 'Intense': ('{opponent}. {eventLabel}. Locked in with my brothers.', 'Been waiting for this stage. {opponent} in the {eventLabel}. Let’s go'),
 'Unpredictable': ('{eventLabel} and {opponent} on the other side. Hope y’all are watching this one', 'Yeah this {eventLabel} is personal to our whole group. {opponent} next. Let’s get it'),
 'Neutral': ('Appreciate the support. {opponent} in the {eventLabel}. Ready to go with this team.', 'The {eventLabel} with my teammates. {opponent} is next. Looking forward to this one.')
}
for style, lines in player_lines.items():
    add('buzz.player-pregame-'+style,*lines)
    add('buzz.watcher-player-'+style,
        'Tuning in for {home} vs. {away} in the {eventLabel}. Respect what both groups did to get here.' if style in ['QB','Leader','TeamPlayer'] else '{home} vs {away} for the {eventLabel}. yeah I’m watching that',
        'Looking forward to watching {home} against {away} in the {eventLabel}.' if style in ['QB','Neutral','Leader'] else 'My team’s games are done but {home} vs {away} in the {eventLabel}? gotta watch that one')
add('buzz.matchup',
    '{eventLabel} matchup: {school} scores {ppg} PPG with {ypg} yards a game and {ypp} per play. {opponent} allows {ppga} PPG, {ypga} yards and {yppa} per play. That is the test, not just the names on the helmets.',
    '{school}: {ppg} PPG, {ypp} offensive yards per play. Against {opponent}: {ppga} PPG allowed, {yppa} yards per play allowed. The {eventLabel} puts those units against each other.')
add('buzz.star',
    '{playerName} for {school} in the {eventLabel}: {line} this season.',
    '{school}’s {playerName} on this stage. Season totals: {line}. The {eventLabel} is the next test.')
add('buzz.record',
    '{school} brings a verified {record} record into the {eventLabel} against {opponent}. The full season gets one more defining test.',
    '{record} got {school} here. {opponent} stands between this program and its next postseason goal in the {eventLabel}.')
add('buzz.watcher-fan',
    '{school}\u2019s season is done, so I\u2019m borrowing {pick} for the {eventLabel}. Would never do this for a rival. For one game, let\u2019s go',
    'No {school} game left. I have {pick} in the {eventLabel}. Temporary fan agreement. Absolutely no long-term commitment')
add('buzz.pick-reply',
    '{parentHandle} {school} fans have a different prediction. Let them play it before you start writing the ending',
    '{parentHandle} fair enough. {school} gets to answer that pick on the field. That\u2019s the part I\u2019m waiting for')
add('buzz.final',
    '{winner} wins the {eventLabel}, {score} over {loser}. The biggest game on this stage has its answer.',
    'Final in the {eventLabel}: {winner} {score} over {loser}. This finish belongs in the season\u2019s defining moments.')
add('buzz.team-champion',
    '{winner}. {eventLabel} winners. Final: {score} over {loser}. Thank you for every step of this run.',
    'This one is for our people. {winner} wins the {eventLabel}, {score} over {loser}.')
add('buzz.team-final-loss',
    'Final in the {eventLabel}: {winner} defeats the {nickname}, {score}. Thank you to our players, staff and fans for this run.',
    'Our run ends in the {eventLabel}. Final: {winner} {score} over {school}. Thank you for standing with us.')
add('buzz.fan-champion',
    '{school} just won the {eventLabel}. {score}. I have no useful words left. Remember this group forever',
    '{winner} {score} over {loser}. The {eventLabel} belongs to us. I will be making this everybody\u2019s problem for a while')
add('buzz.fan-final-loss',
    '{score} in the {eventLabel}. That hurts. Still proud of the {school} run. Getting this close makes it harder, not easier',
    'Going to need some time after that {eventLabel}. {school} gave us a real run. Respect the players even when the ending hurts')
add('buzz.player-champion',
    '{eventLabel} winners. With my brothers. Appreciate everybody who believed in us',
    'Man. {eventLabel} winners. Love this team. Thank you for riding with us all the way')
add('buzz.player-final-loss',
    'grateful for this group and everybody who was with us through the run. The support meant a lot',
    'Appreciate our fans and my teammates. Will always remember getting to this stage with this group')
for persona, line in enumerate([
    '{winner} wins the {eventLabel}, {score}. That is the defining result of this stage, beyond any prediction made coming in.',
    '{score} for {winner} over {loser}. The {eventLabel} is settled. A season of positioning and argument reaches a real result.',
    '{winner}, {score}. The {eventLabel} answer is on the scoreboard. Predictions are something to own after the game too.',
    '{winner} wins the {eventLabel}, {score}. Some of us have old posts to revisit. The scoreboard is not accepting an appeal.',
    '{winner} over {loser}, {score} in the {eventLabel}. The result is clear; the box score and scoring pattern explain how it happened.',
    '{winner} wins the {eventLabel}, {score}. This group has made the defining statement on the biggest available stage.'
]): add('buzz.final-analysis-'+str(persona), line)
add('buzz.outside-final',
    'Not a {school} game, but respect to {winner}. {score} in the {eventLabel}. That group earned its moment',
    '{school} football has been done for a while. Still watched {winner} finish the {eventLabel}, {score}. Respect a run like that')

Path(__file__).resolve().parents[1].joinpath('Content/Runtime/cycle-pack.json').write_text(json.dumps({'format': 1, 'revision': 'intentional-news-cycles-v80', 'families': families}, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps({'families': len(families), 'variants': sum(map(len, families.values()))}))
