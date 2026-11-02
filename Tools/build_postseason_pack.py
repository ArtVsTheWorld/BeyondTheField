import json
from pathlib import Path
families={}
def add(key,*bodies):
    families['postseason.'+key]=[{'id':'P76-'+key+'-'+str(i+1),'body':body} for i,body in enumerate(bodies)]
add('waiting-playoff',
    "A {record} record is in the books for {school}. This is the waiting week: the official playoff field, byes and matchups come next week. Plenty of arguments left; no need to turn a projection into an announcement.",
    "{school} is {record} and waiting for the official postseason picture next week. The games have paused. The resume arguments absolutely have not.")
add('waiting-bowl',
    "{school} finishes the regular slate at {record}. Bowl selections aren't official until next week. For now it's a waiting game, rather than a confirmed destination or an end-of-season farewell.",
    "At {record}, {school} is waiting to learn its postseason plans next week. Nothing official to announce yet; an empty future schedule this week is not the final answer.")
add('waiting-fan',
    "One week until it's official. {school} fans are refreshing everything like the bowl people are going to notice our dedication",
    "{school} postseason waiting week. I have read the projections. All of them. Repeatedly. Would really enjoy an actual announcement next week")
add('playoff-invite',
    "Playoff matchup confirmed. {nickname} vs. {opponent} in {venue}. {hashtag}",
    "The field is official. {nickname} will face {opponent} in {venue}. {hashtag}")
add('bowl-invite',
    "Bowl plans are official: {nickname} vs. {opponent} in {venue}. {hashtag}",
    "Destination confirmed. {nickname} are headed to {venue} to face {opponent}. {hashtag}")
add('bye-path',
    "{school} has a first-round bye. Its Week {quarterWeek} quarterfinal opponent will be the winner of {first} vs. {second}. That side of the bracket is set; the opponent is still to be decided.",
    "The path for {school}: a first-round bye, then the {first}-{second} winner in the Week {quarterWeek} quarterfinal. A confirmed bracket connection, with a game still needed to fill it.")
add('bye-opponent',
    "{school}'s quarterfinal opponent is now {opponent}, after the first-round result. The matchup is set for Week {quarterWeek}.",
    "The bye is over for {school}: {opponent} is the confirmed Week {quarterWeek} quarterfinal opponent.")
add('bye-team',
    "Quarterfinal bound. {nickname} will face the {first}-{second} winner in Week {quarterWeek}. {hashtag}",
    "A first-round bye, then the winner of {first} vs. {second}. See you in the Week {quarterWeek} quarterfinal. {hashtag}")
add('bye-team-opponent',"Quarterfinal matchup set. {nickname} vs. {opponent} in Week {quarterWeek}. {hashtag}")
add('bye-fan',
    "{school} gets to watch {first} and {second} play for the right to ruin our week. Bye secured. Stress somehow still fully operational",
    "A bye does not mean {school} fans are taking a week off. We're becoming extremely opinionated about {first} vs {second}")
add('bye-fan-opponent',"{opponent} it is. {school} fans had one week with no game and somehow spent all of it stressed anyway. Quarterfinal time")
add('heisman',
    "The Heisman Trophy goes to {school}'s {playerName}. The race is finished, the award is official, and this season has its winner.",
    "Official: {playerName} of {school} wins the Heisman Trophy. An award-season conversation becomes a place in college football history.")
add('award',
    "{playerName} receives the {award} for his season with {school}. The annual award is official.",
    "An official award-season honor for {playerName} at {school}: the {award}.")
add('award-multiple',
    "{school}'s {playerName} has collected {count} national defensive player honors. The annual awards are official; this is more than one entry on the resume.",
    "Multiple national defensive honors for {playerName} at {school}: {count} annual awards. A season recognized in more than one award decision.")
add('award-team',
    "{playerName}. {award}. Bringing it home to the {nickname}. {hashtag}",
    "Congratulations to {playerName}, winner of the {award}. {nickname} proud. {hashtag}")
add('award-player',
    "Appreciate everybody who helped me get here. The {award} means a lot but nobody does this alone. Love my teammates and everyone at {school}",
    "Thank you {school}. My teammates, my family, everyone who supported me. Honored to receive the {award}")
add('all-american',
    "{school}'s {playerName} is an official {honor}. The postseason selections are out, and this is a final season honor rather than a preseason projection.",
    "Postseason honors: {playerName} of {school} has been named a {honor}. The selection is official.")
add('honors-team',
    "Postseason honors for the {nickname}: {nationalCount} All-Americans and {conferenceCount} All-Conference players. Congratulations to our guys. {hashtag}",
    "The selections are official. {nickname}: {nationalCount} All-Americans | {conferenceCount} All-Conference honorees. {hashtag}")
add('signed',
    "Signed {document}. It's official, {school}! Appreciate everyone who helped me get here. Ready for this next chapter",
    "Pen to paper. Officially signed with {school}. This {starDescription}{position} is ready to get to work. Love everyone who's been part of the journey")
add('signed-class',
    "Early signing check for {school}: {count} recruits have signed, including {fiveStars} five-stars and {fourStars} four-stars.{rankDetail} These are signatures, not just verbal commitments.",
    "{school} has {count} signed additions at this point, with {fiveStars} five-stars and {fourStars} four-stars.{rankDetail} The remaining recruiting work continues beyond this first signing group.")
add('coach-fired',
    "{school} has moved on from {coachName} as {role}. The opening is confirmed; the next hire is a separate decision.",
    "Coaching change at {school}: {coachName} is out as {role}. Attention turns to the search.")
add('coach-pending',
    "{school} has a pending change at {role}, with {coachName}'s position entering the transition. The replacement has not been confirmed.",
    "The {role} situation at {school} is moving toward a change involving {coachName}. The departure process is pending; this is not a completed replacement hire.")
add('coach-retired',
    "A retirement transition at {school}: {coachName} is leaving the {role} position. That creates an offseason decision for the program.",
    "{school} is navigating {coachName}'s retirement from the {role} role. The next appointment will matter for the program's direction.")
add('coach-pro',
    "{school}'s {coachName} is set to leave the {role} position for the pro game. The college staff now has a transition to manage.",
    "A pro-football departure is part of {school}'s staff picture: {coachName}, the {role}, is on that path. The replacement decision comes next.")
add('coach-departed',
    "{school} is dealing with a job-move departure involving {coachName} at {role}. The opening is part of this year's coaching carousel.",
    "A staff transition for {school}: {coachName}'s move creates a {role} decision for the program.")
add('coach-open',"{school} has a {role} opening after the contract situation involving {coachName}. A replacement has not been confirmed.")
add('coach-contract',"{school}'s {role} contract decision involving {coachName} remains open. An offer or a vacancy listing is not a confirmed new hire.")
add('coach-hired',
    "{school} has appointed {coachName} as {role}. The hire is confirmed, rather than just an outstanding offer.",
    "A coaching appointment is set: {coachName} is {school}'s {role}.")
add('coach-retained',
    "{school} is retaining {coachName} as {role} after an accepted contract offer. Continuity wins out in this staff decision.",
    "{coachName} will stay with {school} as {role}. The contract offer has been accepted.")
add('coach-offer',
    "{school} has an outstanding offer to {coachName} for the {role} job. An offer is on the table; an acceptance has not been confirmed.",
    "Coaching carousel: {school} has offered its {role} position to {coachName}. The offer is pending, so this is a candidate development rather than a hire announcement.")
add('coach-renewal-offer',"{school} has a pending contract offer to retain {coachName} as {role}. An agreement has not been confirmed.")
add('coach-fan',
    "The {role} situation is now part of {school}'s offseason. Please let the next decision be about good football and not just winning the introductory press conference",
    "{school} fans are about to become experts on the {role} candidate pool. I am asking for a normal, sensible coaching decision. Apparently that's a lot to ask")
out={'format':1,'revision':'postseason-decisions-v76','families':families}
Path(__file__).resolve().parents[1].joinpath('Content/Runtime/postseason-pack.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'families':len(families),'variants':sum(map(len,families.values()))}))
