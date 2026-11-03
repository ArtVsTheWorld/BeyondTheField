import json
from pathlib import Path

families = {}


def add(key, *lines):
    families[key] = [{'id': key + '.v81.' + str(i + 1), 'body': line} for i, line in enumerate(lines)]


add('review.title-insider',
    'The season ends with {winner} on top: {score} over {loser} in the national championship. The offseason begins with every contender trying to answer what this team just accomplished.',
    '{winner} closes the season as national champion after beating {loser}, {score}. That is the final answer on the field. Roster retention and the next coaching cycle are the next questions.')
add('review.title-debate',
    '{winner} earned the championship, {score}. Give {loser} credit for getting there, too. Losing the final does not turn an entire season into a failure. Those two things can both be true.',
    '{loser} lost the title game to {winner}, {score}. The title belongs to the winner. Calling the runner-up a bad team because of one result is still a terrible argument.')
add('review.title-film',
    '{winner} over {loser}, {score}, for the title. {turningPoint}',
    'The championship in context: {turningPoint} Final: {winner} {score} over {loser}.')
add('review.champion-season',
    '{school} finishes {record}{coachDetail}, with the national championship as the final chapter. This season has a permanent place in the program’s history.',
    'Season complete: {school}, {record}{coachDetail}, national champions. There will be roster decisions soon. First, a season worth remembering.')
add('review.runnerup-season',
    '{school} finishes {record}{coachDetail}. The national championship loss hurts, but the full season still includes a run to the final. The next question is how much of that core comes back.',
    'The {school} season ends at {record}{coachDetail}, one win short of the title. Evaluate the whole run before turning every offseason discussion into an argument about the last game.')
add('review.title-turnovers',
    'One championship detail: {school} had {ownGiveaways} giveaways; {opponent} had {otherGiveaways}. That is the actual ball-security comparison from the final, not a prediction based on season averages.',
    'Reviewing the national final: {school} finished with {ownGiveaways} giveaways against {opponent}’s {otherGiveaways}. Final result: {winner}, {score}.')
add('review.title-player',
    '{school}’s {playerName} in the national championship: {line}. The full offensive line belongs in the discussion of how this final played out.',
    'A final-game line worth revisiting: {school}’s {playerName}, {line}. That is part of the championship story beyond the final score.')
add('review.title-roster',
    'The next {school} evaluation is roster continuity: {seniors} listed seniors and {nonSeniors} non-seniors. Those are roster counts, not a prediction about who returns or enters the portal. A championship does not answer every offseason question.')
add('review.calendar',
    'The college football season is officially in the rearview. No game preview for next weekend. Just title arguments, roster questions and people convincing themselves the offseason will go quickly.',
    'No more college football games this season. The championship is settled; the arguments about it are absolutely not. Next up: who stays, who moves and which programs can build on this year.')
add('review.fan-calendar',
    'wait so the season is actually over? {school} football already had me missing Saturdays and now there is no college football left at all. This offseason better move fast',
    'The worst part of the final is remembering there is no next week. See y’all in the {school} recruiting replies until football comes back',
    'Another college football season gone. Going to miss this. I will still be arguing about {school} by tomorrow morning but let me be sentimental for a minute',
    'No more games and somehow I am expected to have normal weekends again. {school} news is going to have to carry me through this')
add('review.retrospect',
    'Season in retrospect: {school} finishes {record}. {expectationNote} That is the starting point for evaluating its offseason, before the next recruiting headline changes the mood.',
    '{school}: {record}, season complete. {expectationNote} Judge the next roster decisions against that context, rather than pretending every program had the same goals.')
add('review.staff-hired',
    'Carousel recap: {school} hired {coachName} as {role} during this cycle. With the season finished, the focus shifts from the announcement to the roster and staff taking shape.',
    'One confirmed move from this coaching cycle: {coachName} was hired as {school}’s {role}. The offseason is where that change starts affecting the program’s next chapter.')
add('review.staff-retained',
    'Staff recap at {school}: {role} {coachName} secured a new deal this cycle. That is a confirmed contract development, with the next roster-building phase still ahead.')
add('review.staff-fired',
    'Looking back at the carousel: {school} dismissed {role} {coachName} this cycle. That decision belongs in the season review alongside the results on the field.')
add('review.staff-departed',
    'Coaching-cycle recap at {school}: {role} {coachName} {action}. That is one of the confirmed staff changes as the program turns toward next season.')
add('review.retention-watch',
    '{school}’s {playerName} belongs on the offseason retention watch. His current transfer-risk indicator is elevated. That is a reason to monitor his situation, not a report that he has entered the portal.',
    'A name to monitor at {school}: {playerName}. The current retention indicator flags transfer risk. There is no confirmed portal entry or destination to report.')
add('transactions.nil-review',
    'Following last week’s season review, {school}’s {playerName} has a listed NIL deal of {current}, {change} from {previous}. The observed adjustment is {difference}.',
    'NIL follow-up from last week’s review: {school} {playerName}, {previous} to {current}. Listed compensation {change} by {difference}.')

Path(__file__).resolve().parents[1].joinpath('Content/Runtime/season-review-pack.json').write_text(
    json.dumps({'format': 1, 'revision': 'season-review-v81', 'families': families}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'families': len(families), 'variants': sum(map(len, families.values()))}))
