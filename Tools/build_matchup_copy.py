"""Static unit comparisons, complete Heisman lines and postseason position."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.matchcopy.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])
for kind in ['passing','rushing']:
    add('matchup.'+kind+'-preview',
        '{school}: {attack} '+kind+' yards a game through {games} games. {opponent}: {defense} allowed through {opponentGames}.',
        '{opponent} allows {defense} '+kind+' yards a game ({opponentGames} games). Next up: {school}, averaging {attack} ({games} games).',
        '{school}\'s '+kind+' average is {attack} across {games} games; {opponent}\'s allowed average is {defense} across {opponentGames}.',
        'The '+kind+' comparison: {school} produces {attack} yards per game; {opponent} allows {defense}. Samples: {games} and {opponentGames} games.',
        '{attack} '+kind+' yards a game from {school} meets {defense} allowed by {opponent}. {games} offensive games; {opponentGames} defensive games.',
        '{school} brings a {attack}-yard '+kind+' average through {games} games. {opponent} has allowed {defense} per game through {opponentGames}.',
        'A '+kind+' test for {opponent}: {school} averages {attack} yards over {games} games. The defense allows {defense} over {opponentGames}.',
        'Before kickoff: {school}, {attack} '+kind+' yards per game; {opponent}, {defense} allowed. The samples are {games} and {opponentGames} games.',
        '{opponent}\'s '+kind+' defense has allowed {defense} yards a game in {opponentGames} games. {school} produces {attack} in a {games}-game sample.',
        'Entering this matchup, {school} averages {attack} '+kind+' yards ({games} games). {opponent} allows {defense} ({opponentGames} games).')
    add('matchup.'+kind+'-recap',
        '{school} entered at {attack} '+kind+' yards a game; {opponent} had allowed {defense}. The actual matchup produced {actual} for {school}.',
        'Against {opponent}, {school} gained {actual} '+kind+' yards. Entering averages: {attack} produced by {school}, {defense} allowed by {opponent}.',
        'The '+kind+' comparison met the game: {school} finished with {actual} yards vs. {opponent}, after entering at {attack} against {defense} allowed.',
        '{actual} '+kind+' yards for {school} vs. {opponent}. The pregame figures were {attack} produced and {defense} allowed per game.',
        'Before the game, {school} averaged {attack} '+kind+' yards and {opponent} allowed {defense}. In the game: {actual} for {school}.',
        '{opponent} had allowed {defense} '+kind+' yards per game. {school} brought a {attack} average and finished this matchup at {actual}.',
        'The actual '+kind+' result for {school}: {actual} yards against {opponent}. Entering comparison: {attack} vs. {defense} per game.',
        '{school}\'s '+kind+' total vs. {opponent} was {actual}. Its entering average was {attack}; the defense\'s was {defense} allowed.',
        'Pregame '+kind+' averages: {school} {attack}, {opponent} {defense} allowed. Actual {school} production: {actual} yards.',
        'The '+kind+' matchup in retrospect: {school} entered at {attack}, {opponent} at {defense} allowed. {school} ended with {actual} yards.')
    unit='pass attempt' if kind=='passing' else 'carry'
    pairs('matchup.'+kind+'-preview-rates',[
        '{school} gains {attackRate} yards per '+unit+'; {opponent} allows {defenseRate}.',
        'The efficiency matchup: {school}, {attackRate} yards per '+unit+'; {opponent}, {defenseRate} allowed.',
        '{opponent} allows {defenseRate} yards per '+unit+'. {school} produces {attackRate}.',
        'Before the matchup: {school} {attackRate} yards per '+unit+' against {opponent}\'s {defenseRate} allowed.',
        '{school}\'s '+kind+' rate is {attackRate} yards per '+unit+'. {opponent}\'s defensive rate is {defenseRate}.'],
        ['{interpretation}','Per-game '+kind+' yardage: {attack} produced by {school}, {defense} allowed by {opponent}.'])
    pairs('matchup.'+kind+'-recap-rates',[
        '{school} finished with {actual} '+kind+' yards at {actualRate} per '+unit+' vs. {opponent}.',
        'Against {opponent}, {school} gained {actual} '+kind+' yards, {actualRate} per '+unit+'.',
        'Actual '+kind+' production: {school}, {actual} yards and {actualRate} per '+unit+' against {opponent}.',
        '{school}\'s '+kind+' game vs. {opponent}: {actual} yards, {actualRate} per '+unit+'.',
        '{actualRate} yards per '+unit+' for {school} against {opponent}, {actual} '+kind+' yards in total.'],
        ['Entering rates were {attackRate} produced and {defenseRate} allowed; those averages exclude this game.',
         'The pregame comparison was {attackRate} vs. {defenseRate} yards per '+unit+'.'])
add('matchup.protection-preview',
    '{school} allows {attack} sacks a game ({games} games); {opponent} produces {defense} ({opponentGames}). A protection matchup to watch.',
    '{opponent} averages {defense} sacks through {opponentGames} games. {school} has allowed {attack} a game through {games}.',
    'Protection comparison: {school}, {attack} sacks allowed per game. {opponent}, {defense} sacks produced. Samples: {games} and {opponentGames} games.',
    '{school}\'s line has allowed {attack} sacks a game. {opponent} gets {defense}. There are {games} offensive and {opponentGames} defensive games in the sample.',
    'Before kickoff: {school} allows {attack} sacks a game over {games} games. {opponent} records {defense} over {opponentGames}.',
    'A test for {school}\'s protection: {attack} sacks allowed a game faces {opponent}\'s {defense} sacks a game. Samples: {games}/{opponentGames} games.',
    '{opponent}\'s sack production is {defense} per game ({opponentGames} games). {school}\'s sacks allowed: {attack} ({games} games).',
    'The sack matchup starts at {attack} allowed per game by {school}, {defense} produced by {opponent}. {games} and {opponentGames} games behind the averages.',
    '{school} brings a {attack}-sack-allowed average into {opponent}, which averages {defense} sacks. The samples are {games} and {opponentGames} games.',
    'Protection watch: {school} has given up {attack} sacks per game in {games} games. {opponent} has produced {defense} per game in {opponentGames}.')
pairs('matchup.protection-recap',[
    '{school} allowed {actual} sacks against {opponent}.',
    'Against {opponent}, {school} conceded {actual} sacks.',
    'The game\'s protection result: {school}, {actual} sacks allowed vs. {opponent}.',
    'The actual {school}-{opponent} sack count: {actual} allowed by {school}.',
    '{opponent} finished this matchup with {actual} sacks against {school}.'],
    ['Entering the game, {school} allowed {attack} sacks a game and {opponent} produced {defense}.',
     'Pregame averages: {attack} allowed by {school}, {defense} produced by {opponent}.'])
pairs('matchup.receiver-secondary-preview',[
    '{school}\'s {receiver}: {catches} catches, {yards} yards. {opponent}\'s {defender}: {breakups} PBU, {interceptions} INT.',
    'Receiving and secondary production: {receiver} ({school}), {catches} catches for {yards}; {defender} ({opponent}), {breakups} PBU and {interceptions} INT.',
    '{receiver} has {catches} catches for {yards} at {school}. On {opponent}\'s side, {defender} has {breakups} PBU and {interceptions} INT.',
    'For the passing matchup: {school} has {receiver} ({catches} catches, {yards} yards); {opponent} has {defender} ({breakups} PBU, {interceptions} INT).',
    'Opposing-unit names: {school}\'s {receiver}, {catches} catches and {yards} yards; {opponent}\'s {defender}, {breakups} PBU and {interceptions} INT.'],
    ['This compares production, not individual coverage assignments.','Those are opponent-side totals.'])
pairs('matchup.receiver-secondary-recap',[
    '{school}\'s {receiver} had {actualCatches} catches for {actualYards} yards. {opponent}\'s {defender} had {actualBreakups} PBU and {actualInts} INT.',
    'Actual passing-matchup production: {receiver} ({school}), {actualCatches} catches, {actualYards} yards; {defender} ({opponent}), {actualBreakups} PBU, {actualInts} INT.',
    '{receiver} finished with {actualCatches} catches for {actualYards} at {school}; {defender} recorded {actualBreakups} PBU and {actualInts} INT for {opponent}.',
    'The receiving/secondary totals: {school}\'s {receiver}, {actualCatches} catches for {actualYards}; {opponent}\'s {defender}, {actualBreakups} PBU, {actualInts} INT.',
    'In this game, {receiver} had {actualCatches} catches and {actualYards} yards for {school}. {defender} posted {actualBreakups} PBU, {actualInts} INT for {opponent}.'],
    ['No individual coverage assignment implied.','These are opposing-player totals, not head-to-head targets.'])

add('context.heisman',
    'Heisman No. {rank}: {school}\'s {playerName}. Season: {seasonLine}. Latest vs. {opponent}: {recentLine}, in {result}.',
    '{school}\'s {playerName} is Heisman No. {rank}. Latest: {recentLine} vs. {opponent}, {result}. Season: {seasonLine}.',
    'The full Heisman line for {playerName} of {school}, No. {rank}: {seasonLine}. Against {opponent}: {recentLine}, {result}.',
    'No. {rank} in the Heisman race, {school}\'s {playerName}: {seasonLine} this season. Most recent: {recentLine} vs. {opponent}, {result}.',
    '{playerName} at {school}: {seasonLine} this season, Heisman No. {rank}. The {opponent} game brought {recentLine} in {result}.',
    'Heisman profile: {school}\'s {playerName}, No. {rank}. {seasonLine} this season; {recentLine} vs. {opponent} in {result}.',
    '{seasonLine} on the season for {school}\'s {playerName}. Heisman No. {rank}; most recently {recentLine} vs. {opponent}, {result}.',
    'The season and the latest game: {school}\'s {playerName}, {seasonLine}; {recentLine} vs. {opponent}, {result}. Heisman No. {rank}.',
    'For Heisman No. {rank} {playerName} ({school}), the season is {seasonLine}. Latest: {recentLine} vs. {opponent}, {result}.',
    '{school}\'s Heisman No. {rank} {playerName}: season {seasonLine}; latest {recentLine} against {opponent} in {result}.')
forms('context.heisman-recent','Heisman No. {rank}, {school}\'s {playerName}: {recentLine} vs. {opponent} in {result}. ~',
    'The full recent performance belongs in the discussion.','That is the latest game behind the watch-list position.',
    'Keep the complete line in view.','A recent performance to weigh in the race.',
    'The case goes beyond one headline number.','That is the latest on-field reference point.',
    'The whole game matters to the evaluation.','The production and result both belong in the picture.',
    'One more game in the season-long discussion.','The next game will add another piece to the case.')
forms('editorial.heisman-movement','{school}\'s {playerName} moves {movement} from Heisman No. {previousRank} to No. {rank}. Latest: {recentLine} vs. {opponent}, {result}. ~',
    'The rank and the recent line are both part of the update.','That is the latest watch-list movement.',
    'A performance and a ranking to consider together.','The move is an update, not an explanation of every vote.',
    'The recent game adds context to the position.','That is the current shape of this player\'s case.',
    'Keep the whole performance alongside the move.','The race has another game and another ranking to weigh.',
    'That is the newest entry in the Heisman discussion.','The latest game is part of a longer evaluation.')
forms('editorial.heisman-slip','{school}\'s {playerName} slips from Heisman No. {previousRank} to No. {rank} after {recentLine} in a win over {opponent}. ~',
    'A productive win and a ranking drop in the same week.','The strong performance did not prevent the drop.',
    'The result and production deserve mention beside the movement.','The rank fell even with that productive game.',
    'The individual line was stronger than the direction of the ranking.',
    'That is a ranking move worth discussing alongside the performance.',
    'A lower place on the watch list after a strong winning performance.',
    'The move is down; the recent game still belongs in the case.',
    'The drop did not come with a poor recent performance.',
    'A strong game in a win, with a lower spot on the watch list.')
forms('editorial.close-wins','{school} is {record}. All {wins} wins were by {maxMargin} points or fewer, {totalMargin} points combined. ~',
    'That is a very narrow winning margin.','The wins have left little room for error.',
    'The winning results have come with almost no separation.','The close finishes are part of the season\'s story.',
    'The win total hides how tight those games were.','The record includes repeated tight finishes.',
    'The team has been living on fine margins.','The combined gap is worth keeping beside the record.',
    'The scorelines give the wins more context.','The games that went its way were very close.')
forms('editorial.close-losses','{school} is {record}, with {count} losses by three points or fewer. Those losses total {totalMargin} points. ~',
    'The close results have taken a toll.','The record has a small-margin story underneath it.',
    'Those are narrow defeats with a large effect on the record.','The final record alone hides several fine margins.',
    'That is a painful collection of close finishes.','A few points have changed several outcomes.',
    'The close-game column is part of the evaluation.','The defeats have been costly despite the small gaps.',
    'The record deserves that context.','Those narrow losses help describe the season.')
forms('editorial.comebacks','{school} has {count} wins after trailing at halftime or entering the fourth. The record is {record}. ~',
    'Second-half responses are part of the story.','Those wins required recovery after a deficit.',
    'The team has repeatedly had to come from behind.','The halftime or third-quarter score has not settled those games.',
    'The record includes repeated recoveries.','The finishes have changed several early pictures.',
    'Those games needed a response after falling behind.','The wins have included more than one turnaround.',
    'The comeback element belongs in the season assessment.','The early deficit has not been the final answer in those games.')
forms('buzz.star','~ {school}\'s {playerName} enters the {eventLabel} with {line} this season.',
    'The player spotlight:','A name on the big stage:','The season-long production:',
    'A player line to know:','The individual profile:','The spotlight before kickoff:',
    'A postseason player watch:','The production entering the game:','One player in the matchup:',
    'The big-game stat profile:')
forms('buzz.record','{school} brings {record} into the {eventLabel} against {opponent}. ~',
    'That is the season-long result behind this matchup.','The full year gets another major test.',
    'The record meets a defining postseason game.','The next result carries more weight than an ordinary week.',
    'The stage gives that record another test.','The next game is a major point in the season\'s story.',
    'The postseason adds a new level to the evaluation.','That is the backdrop for the game.',
    'The season has earned a place on this stage.','The next opponent will test that record.')
pairs('buzz.matchup',[
    '{school}: {ppg} PPG, {ypg} yards a game, {ypp} per play. {opponent} allows {ppga} PPG, {ypga} yards, {yppa} per play.',
    '{opponent}\'s defense allows {ppga} PPG, {ypga} yards and {yppa} per play. {school} produces {ppg} PPG, {ypg} yards, {ypp} per play.',
    'Offense vs. defense: {school} {ppg} PPG, {ypg} YPG, {ypp} YPP; {opponent} allows {ppga} PPG, {ypga} YPG, {yppa} YPP.',
    'The {school} attack brings {ppg} points and {ypg} yards a game at {ypp} per play. {opponent} allows {ppga} points, {ypga} yards and {yppa} per play.',
    'Before kickoff: {school} produces {ppg} PPG, {ypg} YPG, {ypp} YPP. {opponent} concedes {ppga} PPG, {ypga} YPG, {yppa} YPP.'],
    ['That is one test in the {eventLabel}.','The {eventLabel} puts those units together.'])

root.joinpath('Content/Runtime/matchup-variety-pack.json').write_text(json.dumps({'revision':'matchup-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
