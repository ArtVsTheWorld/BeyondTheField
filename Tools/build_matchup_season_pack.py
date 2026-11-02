import json
from pathlib import Path
families={}
def add(key,*bodies):
    families[key]=[{'id':'S75-'+key.replace('.','-')+'-'+str(i+1),'body':body} for i,body in enumerate(bodies)]

add('late.title-week',
    "Championship week. {nickname} vs. {opponent} for the {conference} trophy. {hashtag}",
    "One game. The {conference} title on the line. {nickname} vs. {opponent} this week. {hashtag}")
add('late.title-week-fan',
    "It's actually championship week. {school} vs {opponent}, {conference} trophy on the line. I am going to be completely normal about this. Obviously",
    "No more scenarios. No more scoreboard watching. {school} and {opponent} for the {conference} title THIS WEEK. Let's do this")
add('matchup.passing-preview',
    "{school}'s passing attack has averaged {attack} yards across {games} games entering this matchup. {opponent} has allowed {defense} per game across {opponentGames}. A useful clash of production and resistance this week.",
    "Passing-game check: {school} brings {attack} yards per game into {opponent}, whose defense has allowed {defense}. Samples: {games} games for the offense, {opponentGames} for the defense. Worth watching how those trends meet.")
add('matchup.rushing-preview',
    "{school} is averaging {attack} rushing yards entering the game; {opponent} has allowed {defense} per game. That's {games} games of offense against {opponentGames} of run defense. The ground game deserves a place in this preview.",
    "On the ground, {school} has produced {attack} yards per game. {opponent} has conceded {defense}. Different opponents shaped those averages, but this week's matchup puts the two units in the same frame.")
add('matchup.protection-preview',
    "Protection watch for {school}: {attack} sacks allowed per game entering this week. {opponent}'s defense has averaged {defense} sacks. {games} offensive games, {opponentGames} defensive games behind those numbers.",
    "{school}'s protection and {opponent}'s pass rush meet this week: {attack} sacks allowed per game versus {defense} sacks recorded. Workload isn't identical, but it puts a useful question on the matchup.")
add('matchup.passing-recap',
    "{school} entered averaging {attack} passing yards; {opponent} had allowed {defense} per game. The actual matchup produced {actual} passing yards for {school}. A look at what happened when those season trends met.",
    "The passing matchup in numbers: {school}, {attack} yards per game coming in; {opponent}, {defense} allowed. {school} finished this game with {actual}. The entering averages now have a head-to-head result beside them.")
add('matchup.rushing-recap',
    "{school} brought a {attack}-yard rushing average into a defense allowing {defense}. Against {opponent}, the actual total was {actual}. The ground-game comparison tells part of this result.",
    "Entering the matchup: {school} averaged {attack} rushing yards and {opponent} allowed {defense}. In the game itself, {school} ran for {actual}. That's the head-to-head answer to the pregame numbers.")
add('matchup.protection-recap',
    "{school} entered allowing {attack} sacks per game against a {opponent} defense averaging {defense}. In this matchup, {school} allowed {actual}. Protection was one measurable part of how the units met.",
    "A protection recap: {school} allowed {actual} sacks against {opponent}. The entering averages were {attack} allowed by {school} and {defense} recorded by {opponent}. Those baselines exclude this game.")
add('matchup.receiver-secondary-preview',
    "{school}'s {receiver} brings {catches} catches and {yards} yards into a {opponent} secondary featuring {defender} ({breakups} passes defended, {interceptions} INT). Two productive names on opposite units, rather than a promised one-on-one assignment.",
    "Receiver/secondary watch: {receiver}, {school} ({catches} catches, {yards} yards), against a {opponent} group featuring {defender} ({breakups} PBU, {interceptions} INT). The coverage may vary; the production on both sides is worth following.")
add('matchup.receiver-secondary-recap',
    "Across the receiving/secondary matchup, {school}'s {receiver} finished with {actualCatches} catches for {actualYards} yards. On the other side, {opponent}'s {defender} recorded {actualBreakups} PBU and {actualInts} INT. No individual coverage assignment implied.",
    "Two lines from opposing units: {receiver} had {actualCatches} catches for {actualYards} yards for {school}; {defender} had {actualBreakups} passes defended and {actualInts} INT for {opponent}. Different jobs, same matchup.")
for kind,label in [('passing','pass attempt'),('rushing','carry')]:
    add('matchup.'+kind+'-preview-rates',
        "{school} enters averaging {attack} "+kind+" yards per game and {attackRate} per "+label+". {opponent} has allowed {defense} per game, {defenseRate} per "+label+". Volume and efficiency point to the same matchup from different angles.",
        "{school} vs. {opponent}, "+kind+" efficiency: {attackRate} yards per "+label+" produced against {defenseRate} allowed. The per-game baselines are {attack} and {defense}. A useful unit comparison before kickoff.")
    add('matchup.'+kind+'-recap-rates',
        "{school} entered at {attackRate} yards per "+label+"; {opponent} had allowed {defenseRate}. Against that defense, {school} finished with {actual} "+kind+" yards at {actualRate} per "+label+". The entering averages exclude this game.",
        "The "+kind+" matchup resolved at {actualRate} yards per "+label+" for {school} against {opponent}. Entering baselines: {school} produced {attackRate}, {opponent} allowed {defenseRate}. {actual} yards in the actual game.")

add('fanclub.win',
    "{school} {score} over {opponent}. Me opening the group chat like I personally called every play. Good work, everybody",
    "Final: {school} {score} over {opponent}. A win for the team and a terrible development for everyone who has to hear from us this week")
add('fanclub.rivalry-win',
    "{school} {score} over {opponent}. Rivalry receipts department is OPEN. Please form an orderly line",
    "{opponent} week has concluded with a {score} {school} win. We would like to thank their fans for supplying the offseason content")
add('fanclub.loss',
    "{school} falls {score} to {opponent}. Supporting the team and pretending that was fun are two different things. See you next game",
    "{score} against {opponent}. {school} fans will be staring at the ceiling for a bit. Still our team. Still some things that need fixing")
add('fanclub.bad-loss',
    "{school} {score} against {opponent}. The memes are not going to cover this one. We need a much better football answer next time",
    "A {score} loss to {opponent}. We can make jokes on here, but {school} has real work to do after that one")
add('fanclub.tie',"{school} and {opponent}: {score}. Group chat doesn't even know which reaction picture to use.")
add('fanclub.rivalry-week',
    "{opponent} week. {school} fans, please hydrate before spending the next several days being impossible in the replies",
    "Our official position on {opponent} week: {school} by enough that we can start being annoying early")

add('ending.team.normal',
    "{record}. Thank you for being with the {nickname} all season. Your support made every home and road game matter. {hashtag}",
    "The {nickname} season ends at {record}. To everyone who showed up and stayed with us: thank you. {hashtag}")
add('ending.team.rough',
    "Final season record: {record}. Thank you for standing with the {nickname}. Your support means everything. {hashtag}",
    "Our season closes at {record}. Thank you to every fan who supported the {nickname} through it. {hashtag}")
add('ending.team.winless',
    "{record}. A difficult season comes to a close. Thank you to the fans who stood with the {nickname}. {hashtag}",
    "The season ends without a win. Thank you to every fan who kept supporting the {nickname} through a {record} year. {hashtag}")
add('ending.team.perfect',
    "{record}. An undefeated season, start to finish. Thank you for every moment, {nickname} fans. {hashtag}",
    "Every game. Every time. {record}. Thank you for being part of an undefeated {nickname} season. {hashtag}")
add('ending.barstool.normal',
    "{school} finishes {record}. Now what am I supposed to organize my entire weekend around? Thanks for the season, everybody",
    "{record}, and that's the season for {school}. Already miss it. Please respect our privacy while we become recruiting experts overnight")
add('ending.barstool.rough',
    "{school} ends {record}. The offseason group chat is going to have some questions. Love this team. Would also enjoy watching more wins next year",
    "Season over at {record}. {school} fans have earned a short break from finding creative ways to explain the football. Better days, please")
add('ending.barstool.winless',
    "{school} finished {record}. Zero wins. There is no reaction picture that fixes that. Fans kept showing up; the football needs to give them something back",
    "{record}. {school} fans deserve actual answers this offseason, not another hype video. Still our school. That was a brutal year")
add('ending.barstool.perfect',
    "{school} finished {record}. UNDEFEATED. We are warning everyone now: the posting is going to be unbearable for an extended period",
    "The whole season. Not one loss. {school}, {record}. Saving the standings, framing the schedule, becoming a problem in every group chat")
add('ending.afterdark.normal',
    "{school}'s season is over at {record} and I'm already sad. Spent half the fall yelling at the screen. Would sign up for every second again",
    "No more {school} football until next season. {record} and somehow it still went way too fast. Saturdays are about to feel empty")
add('ending.afterdark.rough',
    "{record}. I love {school}, but that season took years off my life. Don't sell me slogans all offseason. Show me something different next fall",
    "{school} finishes {record}. Sad it's over, furious at how much of it went, somehow already hopeful about next year. This team has a ridiculous hold on me")
add('ending.afterdark.winless',
    "ZERO WINS. {school} went {record} and I'm supposed to just move on? The fans gave this program more than it gave us this season. Somebody needs to answer for it",
    "{record}. Every single week I talked myself into {school} getting one. Not even ONE. I'm still a fan. I'm also absolutely sick of this")
add('ending.afterdark.perfect',
    "{school} went {record}. Nobody beat us. Nobody. I'm going to bring this season up in conversations that have nothing to do with football",
    "I watched every game. Yelled through every close moment. {school} finished {record} and I genuinely don't know what to do with all this joy. Perfect season")
for mood,copy in {
 'normal':("{school}'s season is complete at {record}. The focus moves from weekly preparation to roster retention, recruiting and deciding what carries into next fall.","The final line for {school}: {record}. Now the season can be evaluated as a whole, with the offseason roster still to take shape."),
 'rough':("{school} ends {record}, with more losses than wins. An offseason evaluation has to address the football that produced that record, not just the expectations that preceded it.","A {record} finish leaves {school} with plenty to examine. Staff decisions, player development and the next recruiting class will shape the response; none of those answers is automatic."),
 'winless':("{school} finishes {record} without a win. That is a full-season failure to turn any game into a victory. The offseason questions reach well beyond one position or one Saturday.","No wins for {school}: {record}. Any offseason optimism needs to account for how far the results have to move. There is no positive spin for the record itself."),
 'perfect':("{school} has completed the full season undefeated at {record}. No remaining game to protect the record, no hypothetical finish: this team's perfect season is complete.","An undefeated final record for {school}: {record}. Getting through the entire schedule without a loss is the defining fact of this season review.")}.items():add('ending.beat.'+mood,*copy)
add('ending.player.senior',
    "{school}, thank you for everything this senior season. {record} is the final record but I'll remember the people, the locker room and everybody who kept showing up for us. Much love",
    "Last game of my senior season is done. Appreciate my teammates and every {school} fan who rode with us. {record}. A lot of memories in this jersey")
add('ending.player.senior-perfect',
    "My senior season. {record}. UNDEFEATED. Thank you {school}, my brothers in that locker room, everybody who supported us. Couldn't ask for a better way to remember this team",
    "{record} in my senior year. Nobody beat us. {school}, thank you for everything. Going to carry this team and this season with me forever")
add('ending.player.thanks',
    "Season's done at {record}. Appreciate everyone who supported us at {school}, home and away. Going to miss being out there with the guys",
    "Thank you {school}. Every game, every trip, everybody who showed love. {record} and a whole lot of memories with this team")
add('ending.player.perfect',
    "{record}. Whole season undefeated. Love this team and everybody who rode with {school}. Going to remember this forever",
    "Nobody beat us all year. {record}. Thank you {school}, my teammates, the fans, all of y'all. What a season")
add('ending.comparison',
    "{school}'s final record is {record}, after a {priorWins}-{priorLosses} finish in {previousYear}. That earlier season was played in the {previousConference}. A concrete year-over-year reference for the offseason discussion.",
    "Season comparison for {school}: {record} now, {priorWins}-{priorLosses} in {previousYear} as a {previousConference} program. The final records are in; the next roster is still being built.")
add('ending.recruiting',
    "With {school}'s season finished at {record}, its recruiting class currently sits No. {classRank} nationally. That's a live class ranking, not a final signing-day finish.",
    "Next up for {school}: the offseason. The team finished {record}; its current recruiting class is No. {classRank}. That recruiting picture can still change.")
add('ending.coach-pressure',
    "{school} closes at {record}, and head coach {coachName} enters the offseason under job-security pressure. That is a situation to follow, not an announced coaching change.",
    "The {record} finish puts {school}'s coaching situation in focus, with {coachName} under pressure. No firing or replacement has been announced here.")
add('ending.fan-accountability',
    "{school} finished {record}. I want to hear what {coachName} is actually changing. Not a motivational speech. What is going to look different on the field?",
    "{record}. {coachName} needs to give {school} fans a reason to expect better football next year. I will support this team forever. I do not have to pretend that was good")
add('ending.fan-qb',
    "{school} ends {record}. {playerName} finished with {touchdowns} passing TD and {interceptions} picks. That quarterback conversation isn't going away because the season is over",
    "Love {school}. Can't ignore {playerName}'s {touchdowns} passing TD and {interceptions} interceptions in a {record} year. The offseason QB discussion needs to be honest")

out={'format':1,'revision':'matchup-season-v75','families':families}
Path(__file__).resolve().parents[1].joinpath('Content/Runtime/matchup-season-pack.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'families':len(families),'variants':sum(map(len,families.values()))}))
