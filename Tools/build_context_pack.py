import json
from pathlib import Path
families={}
def add(key,*bodies):
    families[key]=[{'id':key+'.C77.'+str(i+1),'body':body} for i,body in enumerate(bodies)]
add('context.offense',
    "{school}'s {offense} approach is producing {ppg} points and {ypg} offensive yards per game, at {ypp} yards a play. {comparison}",
    "The full scoring/yardage picture for {school}: {ppg} PPG, {ypg} yards per game, {ypp} per play across {games} games. {comparison}")
add('context.passing',
    "{school}: {ypg} passing yards per game, {ypa} per attempt, {tdpg} passing TD and {intpg} INT per game. Pass attempts are {share}% of the recorded rushing/passing plays in its {offense} approach. {comparison}",
    "{school}'s passing volume is {ypg} yards per game; the efficiency is {ypa} per attempt. {tdpg} passing TD and {intpg} INT per game complete the picture. {comparison}")
add('context.rushing',
    "{school}'s ground game: {ypg} yards per game, {ypc} per carry and {tdpg} rushing TD per game. Carries make up {share}% of its recorded rushing/passing plays. {comparison}",
    "Within {school}'s {offense} approach, the run produces {ypg} yards per game at {ypc} per carry, plus {tdpg} rushing TD per game. {comparison}")
add('context.defense',
    "{school}'s opponents are scoring {ppga} points per game. Its {defense} unit allows {ypga} offensive yards per game and {yppa} per play. {comparison}",
    "Against {school}: {ppga} points and {ypga} offensive yards per game, {yppa} yards per play. The scheme is {defense}; the output is measurable. {comparison}")
add('context.pass-defense',
    "{school} allows {ypga} passing yards per game and {ypa} per opponent pass attempt, with {intpg} interceptions per game. {comparison}",
    "Pass-defense check for {school}: {ypga} yards allowed per game, {ypa} per attempt and {intpg} picks per game. {comparison}")
add('context.run-defense',
    "{school}'s run defense is allowing {ypga} yards per game and {ypc} per opponent carry. {comparison}",
    "The ground-game numbers against {school}: {ypga} yards per game, {ypc} a carry. That is the production allowed by its {defense} unit. {comparison}")
add('context.disruption',
    "{school}'s defense averages {sackpg} sacks and {takepg} takeaways per game. The takeaway split is {intpg} INT and {frpg} fumble recoveries per game. {comparison}",
    "Disruption at {school}: {sackpg} sacks, {intpg} INT and {frpg} fumble recoveries per game. That's {takepg} takeaways per game. {comparison}")
add('context.penalties',
    "{school} is averaging {penalties} penalties and {yards} penalty yards per game. {comparison}",
    "The discipline column for {school}: {penalties} flags, {yards} yards per game across {games} games. {comparison}")
add('context.ball-security',
    "{school} gives it away {givepg} times per game: {intpg} INT and {lostpg} lost fumbles. Interceptions occur on {rate}% of its pass attempts. {comparison}",
    "Ball security at {school}: {givepg} giveaways per game, including {intpg} picks and {lostpg} fumbles lost. The passing interception rate is {rate}%. {comparison}")
add('context.nil',
    "{school}'s current roster has {total} in listed NIL compensation. The biggest groups: {first}, {firstMoney} ({firstShare}%); {second}, {secondMoney} ({secondShare}%). A look at where the money is allocated.",
    "NIL allocation at {school}: {total} across the current roster. {first} account for {firstShare}% ({firstMoney}); {second} for {secondShare}% ({secondMoney}). This is current compensation, not a claim about cash already paid.")
add('context.coach-record',
    "{school} head coach {coachName}'s career record is {wins}-{losses}, a {rate}% win rate in those decisions. At this school: {schoolWins}-{schoolLosses}.",
    "{coachName}'s head-coaching resume at {school} comes with a {wins}-{losses} career record. That's {rate}% in recorded win/loss decisions.")
for key,label in [('ranked','against Top-25 opponents'),('rivalries','in rivalry games'),('bowls','in bowl games'),('playoffs','in playoff games')]:
    add('context.coach-'+key,
        "{school} coach {coachName} has a {wins}-{losses} career record "+label+". A {rate}% win rate in that part of the resume.",
        "One part of {coachName}'s coaching history: {wins}-{losses} "+label+" ({rate}%). The {school} coach's overall record doesn't tell every story.")
add('context.conference',
    "The {conference} strength argument has some numbers attached: {details}. Reputation starts the debate; these results help test it.",
    "Conference check on the {conference}: {details}. Useful context before another round of blanket claims about which league is better.")
add('context.conference-fan',
    "Every {otherConference} fan has a speech about conference strength ready. The {conference} isn't going anywhere. Bring some results to this argument, not just volume",
    "{otherConference} fans talking like the {conference} is a guest in this sport. Our conference threads are about to be extremely annoying. Show the receipts")
add('context.heisman',
    "{school}'s {playerName} is No. {rank} on the Heisman watch. Latest: {recentLine} in {result} against {opponent}. Season: {seasonLine}.",
    "Heisman watch, No. {rank}: {playerName}, {school}. Season totals: {seasonLine}. Last game against {opponent}: {recentLine}, in {result}.",
    "{school}'s {playerName} is No. {rank} on the Heisman watch. Against {opponent}: {recentLine}, in {result}. The whole stat line belongs in the conversation.")
add('context.heisman-recent',
    "{school}'s {playerName} is No. {rank} on the Heisman watch. Latest game against {opponent}: {recentLine}, in {result}. The ranking and the performance are separate facts.",
    "Heisman watch: {playerName} of {school}, No. {rank}. {recentLine} against {opponent}, in {result}. More context than a single yardage column.")
add('deep.broken-tackles',
    "{school}'s {playerName} has {broken} recorded broken tackles across {attempts} carries. That's the contact count to put beside his rushing production.",
    "The contact column for {school}'s {playerName}: {broken} broken tackles on {attempts} carries. Worth keeping alongside his yards and touchdowns.")
add('deep.after-contact',
    "{school}'s {playerName} has {yards} yards after first contact out of {rushing} rushing yards. That's {rate}% of his rushing production coming after contact.",
    "After-contact share for {school}'s {playerName}: {rate}% of his {rushing} rushing yards. {yards} yards have come after the first hit.")
add('deep.line-sacks',
    "{school}'s {playerName} has allowed {sacks} sacks across {snaps} offensive snaps: a {rate}% sack-allowed rate. The denominator includes run plays, not just pass-blocking snaps.",
    "{sacks} sacks allowed in {snaps} offensive snaps for {school}'s {playerName}, a {rate}% rate across those snaps. This is the whole offensive workload, including run plays.")
for name in ['marcus','tina','chris']:
    add('desk.'+name+'.neutral',
        "{analysisText} Worth keeping alongside the headline numbers.",
        "{analysisText}")
out={'format':1,'revision':'context-and-recovery-v77','families':families}
Path(__file__).resolve().parents[1].joinpath('Content/Runtime/context-pack.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'families':len(families),'variants':sum(map(len,families.values()))}))
