"""Build the editable, factual late-season/history/advanced-analysis wording."""
import json
from pathlib import Path

families = {}
def add(key, *bodies):
    families[key] = [{'id': 'H74-' + key.replace('.', '-') + '-' + str(i+1), 'body': b} for i,b in enumerate(bodies)]

add('deep.broken-tackles',
    "{school}'s {playerName}: {broken} broken tackles on {attempts} carries. That's {rate} broken tackles per 100 carries. Tackles made at the first opportunity matter against this runner.",
    "The first defender hasn't been the whole story for {school}'s {playerName}: {broken} broken tackles across {attempts} carries, or {rate} per 100 carries this season.")
add('deep.after-contact',
    "{playerName} has gained {yards} yards after first contact for {school}, averaging {rate} per carry across {attempts} attempts. Getting to him and getting him down are different jobs.",
    "{school}'s {playerName} is producing {rate} yards after first contact per carry. {yards} of those yards on {attempts} rushes. That's a useful bit of context beyond the rushing total.")
add('deep.yac-share',
    "{yac} of {playerName}'s {yards} receiving yards for {school} have come after the catch. That's {rate}% of his yardage. The catch is only the start of the assignment for the defense.",
    "A closer look at {school}'s {playerName}: {yards} receiving yards, {yac} after the catch. {rate}% of the total has come with the ball already in his hands.")
add('deep.drops',
    "{school}'s {playerName} has {catches} catches and {drops} recorded drops. Drops account for {rate}% of those catch-or-drop opportunities. That isn't a target-based drop rate, but it does put the missed chances in context.",
    "{drops} drops alongside {catches} receptions for {school}'s {playerName}. That's {rate}% of recorded catches plus drops. A few more finished plays would change the look of that stat line.")
add('deep.receiving-back',
    "{school} is getting more than carries from {playerName}: {rushing} rushing yards, plus {receiving} receiving yards on {catches} catches. The backfield production doesn't stop when they throw it.",
    "{playerName}'s workload for {school} travels across the playbook: {rushing} yards on the ground and {receiving} through the air. {catches} catches make him more than a handoff-only concern.")
for key, label in [('tackles-game','tackles'),('sacks-game','sacks'),('tfl-game','tackles for loss'),('ints-game','interceptions'),('pbu-game','passes defended'),('forced-game','forced fumbles'),('recoveries-game','fumble recoveries')]:
    add('deep.'+key,
        "{school}'s {playerName} has {total} "+label+" in {games} appearances: {rate} per game. That's his own games-played sample, including the quieter afternoons.",
        "The per-game view of {playerName}'s season at {school}: {rate} "+label+" per appearance, with {total} across {games} games. Useful context alongside the raw total.")
add('deep.line-sacks',
    "{school}'s {playerName} has allowed {sacks} sacks across {snaps} offensive snaps: {rate} per 100 snaps. These are all offensive snaps, not just pass-blocking plays.",
    "{sacks} sacks allowed in {snaps} offensive snaps for {school}'s {playerName}. That works out to {rate} per 100 snaps. A workload-adjusted look, with run plays included in the denominator.")
add('deep.pancakes',
    "{playerName} has {total} pancake blocks in {games} games for {school}, averaging {rate} per appearance. The box score has something for the offensive line, too.",
    "{school}'s {playerName}: {total} pancakes, {games} appearances, {rate} per game. Not every productive afternoon comes with a touchdown attached.")
for key, distance in [('long-kicks','50-plus'),('mid-kicks','40-49')]:
    add('deep.'+key,
        "{school}'s {playerName} is {made}-for-{attempts} from "+distance+" yards this season ({rate}%). Distance matters when you're judging the kicking numbers.",
        "From "+distance+" yards, {playerName} has made {made} of {attempts} field-goal attempts for {school}. {rate}% from that band, rather than lumping every kick together.")
add('deep.touchbacks',
    "{school}'s {playerName} has {total} touchbacks on {attempts} kickoffs, a {rate}% touchback rate. One part of the field-position story that rarely gets its own headline.",
    "{total} of {playerName}'s {attempts} kickoffs for {school} have been touchbacks ({rate}%). A little special-teams context beyond the scoring column.")
add('deep.punt-placement',
    "{playerName} has put {total} of {attempts} punts inside the 20 for {school}: {rate}%. Just {touchbacks} have been touchbacks. Placement belongs next to distance in this discussion.",
    "{school}'s punting picture: {playerName}, {attempts} punts, {total} inside the 20 ({rate}%), {touchbacks} touchbacks. There's more to the job than the longest kick.")
for key, label in [('kick-return','kick'),('punt-return','punt')]:
    add('deep.'+key,
        "{school}'s {playerName} is averaging {rate} yards per "+label+" return: {yards} yards on {attempts} returns, with {touchdowns} TD. Field position is part of his production, too.",
        "Don't skip the return column for {school}'s {playerName}: {attempts} "+label+" returns, {yards} yards, {touchdowns} TD. That's {rate} yards each time he brings one back.")
add('deep.dual-qb-game',
    "{playerName} made {opponent} defend both sides of his game: {passing} passing yards and {rushing} rushing yards for {school}. A passing line alone doesn't describe that afternoon.",
    "{school}'s {playerName} against {opponent}: {passing} through the air, {rushing} on the ground. That second number matters when you're deciding how to defend the first.")
add('deep.dual-back-game',
    "{rushing} rushing yards and {receiving} receiving yards for {school}'s {playerName} against {opponent}. Productive on handoffs, productive when they threw him the ball.",
    "{playerName} gave {school} a two-way backfield contribution against {opponent}: {rushing} on the ground, {receiving} receiving. The rushing total only tells part of it.")

add('late.conference-race',
    "The {conference} race is getting tight on time. Current leaders: {leaders}. Those are the standings, not a championship invitation; the remaining games and tiebreakers still matter.",
    "Late-season {conference} check: {leaders} lead the standings. Plenty to argue about, but no need to turn a standings position into a berth before the matchup is assigned.")
add('late.contender',
    "{school} is No. {place} in the {conference} standings at {wins}-{losses} in league play. The title-race discussion is becoming a weekly part of the beat now.",
    "Keep the conference column in view for {school}: {wins}-{losses}, No. {place} in the {conference} standings. These last league results carry a lot of weight.")
add('late.title-invite',
    "Championship date set. {nickname} vs. {opponent} for the {conference} title in Week {championshipWeek}. {hashtag}",
    "Next stop: the {conference} championship game. {nickname} will face {opponent} in Week {championshipWeek}. {hashtag}")
add('late.title-history',
    "{school} will face {opponent} for the {conference} championship. The program's last conference title came in {lastYear}. That's some history sitting behind this matchup.",
    "A conference title has been missing from {school}'s trophy case since {lastYear}. {opponent} is the opponent in this year's {conference} championship game.")
add('late.title-result',
    "{school} takes the {conference} championship, beating {opponent} {score}. The conference race is settled; the postseason conversation gets its next chapter.",
    "Conference champions: {school}. A {score} win over {opponent} finishes the {conference} title race on the field.")
add('late.title-fan',
    "{school} and {opponent} for the {conference} title. I've already decided I'm going to be unbearable if we win this",
    "A whole {conference} championship on the line and {opponent} fans are still talking. {school}, we have the chance to make this very funny")
add('late.bowl-one-away',
    "{school} is {wins}-{losses}, one win from the six-win bowl threshold with {remaining} regular-season games left. Reaching six and receiving a bowl invitation are separate steps.",
    "The next win would get {school} to six. At {wins}-{losses} with {remaining} games remaining, the bowl conversation has a very clear near-term target.")
add('late.bowl-position',
    "{school} sits at {wins}-{losses}, past the six-win threshold. Now the bowl discussion turns toward where they could land. No assigned matchup yet.",
    "At {wins}-{losses}, {school} has the six-win mark covered. Bowl destination is the next question, with the actual invitation still to come.")
add('late.bowl-no-room',
    "{school} is {wins}-{losses} with {remaining} regular-season games left. It needs all {needed} to reach six wins. There's no spare result left in that chase.",
    "The route to six wins for {school} is down to winning out: {needed} needed, {remaining} games remaining. Their current record is {wins}-{losses}.")
add('late.bowl-invite',
    "Bowl plans are set. {nickname} vs. {opponent} in {venue}. {hashtag}",
    "Postseason destination: {venue}. {nickname} will face {opponent}. {hashtag}")
add('late.playoff-berth',
    "{school} is in the College Football Playoff field, with an assigned opening-round matchup against {opponent}.{historyDetail}",
    "Playoff matchup confirmed: {school} vs. {opponent} in {venue}.{historyDetail}")
add('late.cfp-stakes',
    "CFP No. {rank} {school} is {wins}-{losses} with {opponent} up this week. This late in the year, the playoff argument and the next result are tied together. The ranking is a position to defend, not an invitation.",
    "{school}'s next playoff talking point will be written against {opponent}. They're {wins}-{losses} and No. {rank} in the CFP rankings. Very little room left for the resume to change before the field is set.")
add('late.title-appearance-history',
    "{school} is back in the national championship game for the first time since {lastYear}. {opponent} stands between this team and the title.",
    "The last time {school} reached the national championship game was {lastYear}. Now the program returns to that stage against {opponent}.")
add('late.turnaround',
    "{school} finished {previousYear} at {priorWins}-{priorLosses} in the {previousConference}. This season it's already {wins}-{losses}. That's a different kind of November conversation.",
    "A year-over-year check on {school}: {priorWins}-{priorLosses} last season, {wins}-{losses} now. The win total is already well beyond the previous finish.")
add('late.regression',
    "{school} went {priorWins}-{priorLosses} in {previousYear}. It's {wins}-{losses} this season, with more losses already on the board. The change in direction is hard to ignore.",
    "Last season: {priorWins}-{priorLosses}. This season: {wins}-{losses}. {school}'s {previousYear} finish in the {previousConference} is a difficult comparison right now.")
add('late.conference-change',
    "{school} finished No. {priorPlace} in the {conference} at {priorWins}-{priorLosses} in {previousYear}. This year it's No. {place} at {wins}-{losses}. That is a substantial change in the conference picture.",
    "A conference comparison for {school}: No. {priorPlace}, {priorWins}-{priorLosses} in {previousYear}; No. {place}, {wins}-{losses} now. Same {conference}, very different place in the standings.")
add('late.rivalry-team',
    "{opponent} week. You know what this one means. {nickname}, let's go. {hashtag}",
    "This week: {nickname} vs. {opponent}. A game that needs no extra introduction. {hashtag}")
add('late.rivalry-fan',
    "{opponent} week and suddenly everybody has a strong opinion. Good. Been waiting all year for {school} to settle this one on the field",
    "Already seeing {opponent} fans talk like the game is over. It's literally game week. {school}, please make these people log off")
add('late.rivalry-stakes',
    "Rivalry week for {school}: {opponent} is up next, with a {wins}-{losses} {conference} record in the background. This one reaches beyond the conference column.",
    "{school} enters the {opponent} rivalry game {wins}-{losses} in {conference} play. Standings matter. So does hearing about this result for the next year.")
add('late.conference-beef',
    "{opponent} fans acting like they own the {conference}. {school} is sitting right here at {wins}-{losses} in league play. Might want to leave some space in that victory speech",
    "Every {conference} thread somehow turns into {opponent} fans explaining why nobody else counts. {school} is {wins}-{losses} in the league. We can read the standings too")
add('late.fan-reply',
    "{parentHandle} {school} fans aren't taking confidence lessons from {opponent}. Let's let the football do some talking",
    "{parentHandle} screenshotting this for later. {school} fans have heard plenty from {opponent} this week already")

add('history.team-counter',
    "{school} has recorded its {ordinal} {achievement} in program history. This season now has another place in the school's record book.",
    "{school} adds another chapter: its {ordinal} {achievement} in program history. A milestone beyond this week's result.")
add('history.team-wins',
    "{school} has reached {threshold} all-time wins. The program's running total is now {total}. A round number with a lot of seasons behind it.",
    "Another program milestone for {school}: at the {threshold}-win mark all-time, now at {total} victories.")
add('history.win-percentage',
    "{school}'s all-time winning percentage has moved {direction} {boundary}. Its record is {wins}-{losses}-{ties}, counting ties as half a win. A small shift this week with a long history behind it.",
    "An all-time threshold for {school}: its winning percentage is now {direction} {boundary}, on a {wins}-{losses}-{ties} program record. Ties count as half a win in that calculation.")
add('history.player-career',
    "{school}'s {playerName} has reached {threshold} career {metric}. His career total is now {total}. This week's production has a longer-term marker attached.",
    "Career milestone for {playerName} at {school}: at least {threshold} {metric}, now at {total}. More than a one-week stat line.")
add('history.coach-wins',
    "{coachName} has reached {threshold} career wins, with his total now at {total}. The {school} head coach adds another milestone to his record.",
    "{school} coach {coachName} has reached the {threshold}-win mark for his career. {total} victories now, across his head-coaching record.")
add('history.coach-counter',
    "{school} head coach {coachName} has recorded his {ordinal} career {achievement}. Another addition to the coaching resume.",
    "A career milestone for {coachName}: his {ordinal} {achievement}. The {school} head coach adds another line to his postseason record.")

out = {'format': 1, 'revision': 'history-analysis-v74', 'families': families}
Path(__file__).resolve().parents[1].joinpath('Content/Runtime/history-analysis-pack.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'families':len(families),'variants':sum(map(len,families.values()))}))
