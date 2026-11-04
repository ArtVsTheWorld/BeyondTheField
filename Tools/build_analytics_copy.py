"""Author numeric-desk alternatives from football-specific fact clauses.

The output is a static, inspectable prewritten template pack. Each form keeps
the same fact, unit and denominator; it never adds a qualitative verdict.
"""
import json
from pathlib import Path
families = {}
def add(key, bodies):
    families[key] = [{'id': key+'.variety.'+str(i+1), 'body': text} for i,text in enumerate(dict.fromkeys(bodies))]
def measure(key, subject, label, quantity, sample, leading=None, tail=''):
    leading = leading or sample[:1].upper()+sample[1:]
    # Mix a concise data card with prose, rather than padding a fixed tweet
    # with interchangeable conclusions that do not add information.
    add(key, [
        f'{subject}: {quantity} {sample}. {tail}',
        f'{label.capitalize()} for {subject}: {quantity} ({sample}). {tail}',
        f'{leading}: {subject}, {quantity}. {tail}',
        f'{subject}\'s {label}: {quantity} {sample}. {tail}',
        f'A look at {subject}: {quantity} {sample}. {tail}',
        f'Checking {label} at {subject}: {quantity} {sample}. {tail}',
        f'{quantity} for {subject} {sample}. {tail}',
        f'The {label} figure for {subject} is {quantity} {sample}. {tail}',
        f'{leading}, the {label} number for {subject} is {quantity}. {tail}',
        f'{subject} in numbers: {quantity} {sample}. {tail}',
    ])
T='{school}'
P="{school}'s {playerName}"
team={
 'scoring-offense':('scoring average','{value} points a game','through {games} games'),
 'scoring-defense':('points allowed','{value} points allowed a game','through {games} games'),
 'scoring-margin':('average scoring margin','{value} points','through {games} games'),
 'yards-per-attempt':('offensive efficiency','{value} yards per pass/rush attempt','across {attempts} recorded attempts'),
 'passing-efficiency':('passing efficiency','{value} yards per pass attempt','on {attempts} throws'),
 'rushing-efficiency':('rushing efficiency','{value} yards per carry','across {attempts} carries'),
 'offensive-balance':('offensive balance','{value}% {approach} attempts','among recorded pass/rush plays through {games} games'),
 'interception-rate':('interception rate','{value}% of throws intercepted','with {interceptions} INT on {attempts} pass attempts'),
 'passing-td-rate':('passing touchdown rate','{value}% of pass attempts ending in TD','with {touchdowns} TD on {attempts} throws'),
 'fourth-down':('fourth-down conversion rate','{value}%','with {conversions} conversions on {attempts} tries'),
 'run-defense':('rushing yards allowed','{value} yards allowed a game','through {games} games'),
 'pass-defense':('passing yards allowed','{value} yards allowed a game','through {games} games'),
 'takeaways':('takeaway production','{value} takeaways a game','with {takeaways} total through {games} games'),
 'sack-pressure':('sack production','{value} sacks a game','with {sacks} total through {games} games'),
 'red-zone-field-goals':('red-zone scoring split','{value}% field goals','among {scoringTrips} TD/FG scoring trips, including {fieldGoals} field goals'),
 'penalty-discipline':('penalty yardage','{value} penalty yards a game','through {games} games'),
 'second-half':('second-half scoring margin','{value} points a game','through {games} games, excluding overtime'),
 'red-zone-defense':('red-zone touchdown rate allowed','{value}%','with {touchdowns} TD allowed on {trips} opponent trips'),
}
for key,(label,quantity,sample) in team.items():measure('analysis.team.'+key,T,label,quantity,sample)
for key,label in [('passing-yards-leader','passing yards'),('passing-td-leader','passing touchdowns'),('rushing-yards-leader','rushing yards'),('receiving-yards-leader','receiving yards'),('sacks-leader','sacks'),('interceptions-leader','interceptions')]:
    add('analysis.player.'+key,[
        P+' {lead} {field} with {value} {metricLabel}.',
        'At the top of {field}: '+P+' {lead} with {value} {metricLabel}.',
        '{value} {metricLabel} for '+P+'. He {lead} {field}.',
        'The {field} leaderboard has '+P+' at the top: {value} {metricLabel}. He {lead} that group.',
        'Production watch: '+P+' {lead} {field}, with {value} {metricLabel}.',
        '{school} has a leader in {playerName}: he {lead} {field} with {value} {metricLabel}.',
        P+' has {value} {metricLabel}, a mark that {lead} {field}.',
        'Leaderboard check: '+P+', {value} {metricLabel}. He {lead} {field}.',
        'Looking at {field}, '+P+' {lead} with {value} {metricLabel}.',
        P+' sets the pace in {field}: {value} {metricLabel}. He {lead} the field.',
    ])
player={
 'completion-rate':('completion rate','{value}% completions','on {attempts} pass attempts'),
 'passing-yards-per-attempt':('passing efficiency','{value} yards per pass attempt','across {attempts} throws'),
 'td-int-ratio':('passing touchdown/interception split','{touchdowns} TD against {interceptions} INT','this season'),
 'rushing-yards-per-carry':('rushing efficiency','{value} yards per carry','with {yards} yards on {carries} attempts'),
 'yards-per-catch':('receiving efficiency','{value} yards per catch','across {catches} receptions'),
 'yards-after-catch':('yards after the catch','{value} YAC per reception','across {catches} catches'),
 'receiving-td-rate':('receiving touchdown rate','{value}% of catches ending in TD','with {touchdowns} scores on {catches} receptions'),
 'scrimmage-yards':('scrimmage production','{value} rushing/receiving yards a game','with {yards} total through {games} games'),
 'dual-threat':('dual-threat production','{passing} passing yards and {rushing} rushing yards a game','this season'),
 'carry-share':('share of the ground game','{value}% of the team\'s carries','with {carries} attempts'),
 'catch-share':('share of the passing game','{value}% of the team\'s completed passes','with {catches} catches'),
 'touchdown-share':('share of offensive touchdowns','{value}% of the team\'s rushing/passing TD total','with {touchdowns} rushing/receiving scores'),
 'tackles':('tackle production','{value} total tackles a game','with {tackles} solo/assisted tackles through {games} games'),
 'tackles-for-loss':('backfield disruption','{value} tackles for loss','this season'),
 'forced-fumbles':('forced fumbles','{value} forced fumbles','this season'),
 'pass-breakups':('pass breakups','{value} passes broken up','this season'),
 'field-goals':('field-goal accuracy','{value}%','with {made} makes on {attempts} field-goal attempts'),
 'long-field-goals':('long-distance kicking','{made} field goals on {attempts} attempts','from 50 yards or more this season'),
 'net-punting':('net punting','{value} net yards per punt','across {punts} punts'),
}
for key,(label,quantity,sample) in player.items():measure('analysis.player.'+key,P,label,quantity,sample)
measure('analysis.team.halftime-comebacks',T,'halftime comebacks','{count} wins after trailing at halftime','this season')
measure('analysis.team.fourth-quarter-losses',T,'late leads lost','{count} losses after leading through three quarters','this season')
measure('analysis.team.home-road-split',T,'scoring-margin split','{homeMargin} points at home and {roadMargin} away','across {homeGames} home and {roadGames} road games')
measure('analysis.team.close-games',T,'one-score games','{wins} wins and {losses} losses','across {count} games decided by seven points or fewer')
measure('analysis.team.opponent-records',T,'opponents\' combined record','{wins}-{losses}','excluding their games against {school}')
measure('analysis.team.offense-defense-contrast',T,'scoring balance','{pointsFor} points scored and {pointsAgainst} allowed a game','this season')
measure('analysis.player.freshman-production',P,'freshman production','{production}','this season as a freshman')
for key,label in [('tackles-game','total tackles'),('sacks-game','sacks'),('tfl-game','tackles for loss'),('ints-game','interceptions'),('pbu-game','passes defended'),('forced-game','forced fumbles'),('recoveries-game','fumble recoveries')]:
    measure('deep.'+key,P,label,'{rate} '+label+' a game','with {total} total in {games} appearances')
measure('deep.after-contact',P,'rushing yards after contact','{rate}% of rushing production after contact','with {yards} after-contact yards out of {rushing} rushing yards')
measure('deep.broken-tackles',P,'broken-tackle production','{broken} tackles broken','on {attempts} rushing attempts')
measure('deep.receiving-back',P,'backfield production','{rushing} rushing yards and {receiving} receiving yards','including {catches} catches')
measure('deep.dual-qb-game',P,'dual-threat game','{passing} passing yards and {rushing} rushing yards','in the same game')
measure('deep.dual-back-game',P,'rushing/receiving game','{rushing} rushing yards and {receiving} receiving yards','in the same game')
measure('deep.yac-share',P,'receiving yards after the catch','{rate}% of receiving yardage after the catch','with {yac} YAC out of {yards} receiving yards')
measure('deep.drops',P,'catch-or-drop rate','{rate}% drops','with {drops} drops and {catches} catches',tail='This uses catches plus drops, not all targets.')
measure('deep.line-sacks',P,'sacks allowed','a {rate}% sack-allowed rate','with {sacks} allowed on {snaps} offensive snaps',tail='The snap count includes run plays.')
measure('deep.pancakes',P,'pancake blocks','{rate} pancakes a game','with {total} total through {games} games')
for key,distance in [('long-kicks','50-plus'),('mid-kicks','40-49')]:measure('deep.'+key,P,distance+'-yard field goals','{rate}% accuracy','with {made} makes on {attempts} tries from '+distance+' yards')
measure('deep.touchbacks',P,'kickoff touchbacks','a {rate}% touchback rate','with {total} touchbacks on {attempts} kickoffs')
measure('deep.punt-placement',P,'punts inside the 20','{rate}% of punts downed inside the 20','with {total} of {attempts} punts inside the 20 and {touchbacks} touchbacks')
for key,label in [('kick-return','kick returns'),('punt-return','punt returns')]:measure('deep.'+key,P,label,'{rate} yards per return','with {yards} yards and {touchdowns} TD on {attempts} returns')
for key,label in [('ranked','Top-25 opponents'),('rivalries','rivalry games'),('bowls','bowl games'),('playoffs','playoff games')]:measure('context.coach-'+key,"{school} coach {coachName}",'career record against '+label if key=='ranked' else 'career record in '+label,'{wins}-{losses} ({rate}% wins)','across those career decisions')
measure('context.coach-record',"{school} coach {coachName}",'career record','{wins}-{losses} ({rate}% wins)','with a {schoolWins}-{schoolLosses} record at this school')
measure('context.nil',T,'NIL allocation','{total} in roster compensation','with {first} at {firstMoney} ({firstShare}%) and {second} at {secondMoney} ({secondShare}%)')
measure('context.conference','the {conference}','conference strength','{details}','this season')
measure('context.penalties',T,'penalties','{penalties} flags and {yards} penalty yards a game','this season',tail='{comparison}')
measure('context.run-defense',T,'run defense','{ypga} rushing yards allowed a game and {ypc} per opponent carry','this season',tail='{comparison}')
measure('context.pass-defense',T,'pass defense','{ypga} passing yards allowed a game, {ypa} per opponent attempt and {intpg} INT a game','this season',tail='{comparison}')
measure('context.ball-security',T,'turnovers','{givepg} giveaways a game ({intpg} INT, {lostpg} lost fumbles)','with {rate}% of pass attempts intercepted',tail='{comparison}')
measure('context.disruption',T,'defensive disruption','{sackpg} sacks and {takepg} takeaways a game','including {intpg} INT and {frpg} fumble recoveries a game',tail='{comparison}')
measure('context.rushing',T,'ground game','{ypg} yards a game, {ypc} per carry and {tdpg} rushing TD a game','with carries accounting for {share}% of pass/rush attempts',tail='{comparison}')
measure('context.offense',T,'offensive production','{ppg} points, {ypg} yards a game and {ypp} yards per play','in its {offense} approach',tail='{comparison}')
measure('context.defense',T,'defensive production','{ppga} points and {ypga} offensive yards allowed a game, {yppa} yards per opponent play','in its {defense} approach',tail='{comparison}')
measure('context.passing',T,'passing game','{ypg} yards a game, {ypa} per attempt, {tdpg} passing TD and {intpg} INT a game','with throws making up {share}% of recorded pass/rush attempts',tail='{comparison}')
for key in families:
    for row in families[key]:row['body']=row['body'].strip()
Path(__file__).resolve().parents[1].joinpath('Content/Runtime/analytics-variety-pack.json').write_text(json.dumps({'revision':'analytics-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
