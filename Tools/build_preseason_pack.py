"""Prewritten preseason voices; no Dynasty data or extracted assets."""
import json
from pathlib import Path
families={}
def add(key,*bodies):families[key]=[{'id':key+'.'+str(i+1),'body':body+('{recruitRankDetail}' if key=='preseason.recruit.watch' and i%2==0 else '')} for i,body in enumerate(bodies)]
add('preseason.poll.beat',
    '{school} opens at No. {rank} in the preseason AP poll. A starting point for the season, with plenty still to prove once the games begin.',
    'Preseason AP: {school} is No. {rank}. That is the expectation heading into opening week. Now comes the part that counts.',
    '{school} starts the year ranked No. {rank} in the AP poll. The preseason conversation has a number attached to it now.')
add('preseason.team.hype',
    'A new season. Same {nickname} pride. {hashtag}',
    'The wait is almost over. {nickname}, let’s get to work. {hashtag}',
    'One team. A whole new season ahead. {nickname}. {hashtag}',
    'Ready to make some noise. {nickname} football is coming. {hashtag}')
add('preseason.fan.excited',
    'every year i tell myself i’m gonna be normal about {school} football. anyway i’m ready for kickoff',
    'missed spending my entire weekend thinking about the {nickname}. we’re so back',
    'new season and i’ve already talked myself into {school}. nobody try to be reasonable with me right now',
    'the {nickname} haven’t played a snap and i’m already planning my Saturdays around this team')
add('preseason.fan.nervous',
    'i love {school} football but please give me one season where watching feels good for my blood pressure',
    'the excitement and the fear are arriving at the exact same time. must be {nickname} season',
    'trying to keep my expectations reasonable for {school}. failing at that before we’ve even kicked off',
    'ready for {nickname} football. also terrified. pretty standard preseason for me')
player={
 'Leader':('love this group. ready to put it out there together {hashtag}','grateful for another season with my guys. can’t wait to see y’all {hashtag}'),
 'Intense':('counting down. ready to get after it with my guys {hashtag}','camp days stacking up. ready for that first one {hashtag}'),
 'Entertainer':('missed this feeling. football season needs to hurry up {hashtag}','y’all ready?? because i am {hashtag}'),
 'TeamPlayer':('another season with my brothers. wouldn’t trade it {hashtag}','love being around this team. ready to give y’all something to cheer for {hashtag}'),
 'Unpredictable':('season can’t get here fast enough. keep that same energy when it does {hashtag}','been quiet for a reason. see y’all soon {hashtag}'),
 'Neutral':('ready to get back out there. appreciate everybody riding with us {hashtag}','new season coming. thankful i get to do this {hashtag}'),
 'QB':('excited for another season with this team. appreciate all the support {hashtag}','can’t wait to get back out there with my guys. see y’all soon {hashtag}')
}
for voice,bodies in player.items():
    mixed=[]
    for i,body in enumerate(bodies):
        if i%2==0:body=body[0].upper()+body[1:]
        mixed.append(body)
    add('preseason.player.'+voice,*mixed)
add('preseason.opener.beat',
    '{school} opens the season against {opponent}. That is the first real checkpoint after camp, with the rest of the schedule still ahead.',
    'First up for {school}: {opponent}. An offseason of preparation is about to meet an actual opponent.',
    '{opponent} is the opener for {school}. Plenty of preseason talk; that matchup will give us something more concrete.')
add('preseason.outlook.analyst',
    '{school}: {count} national preseason All-America {selectionLabel}, with {playerName} on the list. A useful place to start when looking at where the expectations come from.',
    '{count} national preseason All-America {selectionLabel} for {school}. Keep an eye on {playerName} when the season opens.',
    '{school} brings {count} national preseason All-America {selectionLabel} into the year, with {playerName} on that list. Recognition is there; the games will tell us how it translates.')
add('preseason.honor.beat',
    '{school}’s {playerName} is a {award} selection. Recognition before the opening game, and a name to keep an eye on this season.',
    '{award} honors for {playerName} of {school}. A preseason nod with a full season still ahead.',
    '{playerName} of {school} makes the {award} team. One of the players carrying expectations into opening week.')
add('preseason.title.model',
    'Model title futures: {school} {odds}. A fictional preseason price from our roster-based model, not a sportsbook line. Plenty can change once the games start.',
    '{school}: {odds} in our model’s national-title futures. These are fictional preseason estimates, with the entire season still to be played.',
    'Our fictional title board has {school} at {odds}. A preseason model estimate, not a real betting market.')
add('preseason.recruit.watch',
    'Recruiting name to know: {starDetail}{position} {playerName}, No. {nationalRank} nationally. One of the prospects to watch as the season approaches.',
    '{playerName} is the No. {nationalRank} recruit in the country, a {starDetail}{position}. Keeping that name on the radar heading into the season.',
    'Preseason recruiting watch: No. {nationalRank} {playerName}, {starDetail}{position}. A name worth following as this class takes shape.')
add('preseason.recruit.self',
    'ready to get back on the field. a lot to look forward to this year',
    'new season almost here. appreciate everybody showing love',
    'football can’t get here fast enough. ready to go')
add('preseason.gauntlet.analyst',
    '{school} faces {count} preseason AP-ranked opponents across Weeks {startWeek}–{endWeek}: {opponents}. The rankings will change, but that stretch already stands out on the schedule.',
    'Circle Weeks {startWeek}–{endWeek} for {school}. {count} opponents from the preseason AP Top 25 in that window: {opponents}. A concentrated test rather than a schedule that spreads those games out.')
add('preseason.respect.analyst',
    '{school} is No. {rank} in the preseason AP poll, but No. {modelRank} on our fictional title-model board. The model is higher on this roster than the voters are. Worth watching once the games start.',
    'One preseason disagreement: AP has {school} No. {rank}; our fictional title model puts them No. {modelRank}. That gap is a reason to watch, not a guarantee the voters got it wrong.')
add('preseason.caution.analyst',
    '{school} starts No. {rank} in the AP poll. Our fictional title model has them No. {modelRank}. The voters see a stronger contender than the model does; the season will settle that argument.',
    'The AP voters have {school} No. {rank}, compared with No. {modelRank} on our fictional title-model board. A preseason ranking to keep in mind when judging what this team actually does.')
add('preseason.debate.fan',
    '{analystHandle} y’all can argue about the model all day. i’m ready to watch the {nickname} actually play',
    '{analystHandle} saving this for later. {school} hasn’t even kicked off yet and we’re already doing this lol',
    '{analystHandle} preseason arguments are undefeated. just give me {nickname} football already')
add('preseason.coaches.beat',
    'The preseason polls disagree on {school}: No. {rank} in the AP poll, No. {coachesRank} in the Coaches poll. Two different starting points for the same team.',
    '{school} opens at No. {rank} with the AP and No. {coachesRank} with the Coaches poll. A real gap in how the two voting groups view this team before kickoff.')
add('preseason.talent.analyst',
    '{conference} preseason talent map: {leaders} {leadVerb} with {leaderCount} players on the All-Conference teams. {count} different players earned selections across the league. Those honors show where expectations are concentrated.',
    '{leaders} {leadVerb} in preseason All-{conference} representation: {leaderCount} players. The conference’s first and second teams recognize {count} different players overall.')
add('poll.initial.beat',
    'CFP rankings: {school} checks in at No. {rank}. The committee’s view of the playoff picture is now the ranking to watch.',
    '{school} is No. {rank} in the published CFP rankings. The playoff conversation has the committee’s numbers attached to it.')
Path('Content/Runtime/preseason-pack.json').write_text(json.dumps({'format':1,'revision':'voices-5-preseason','families':families},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({'newFamilies':len(families),'newVariants':sum(map(len,families.values()))})
