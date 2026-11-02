export const ranked=n=>Number.isInteger(n)&&n>=1&&n<=25;
// A partial/stale CFP row is not evidence of a published poll. Require the
// complete native Top 25; never substitute the game's hidden team ordering.
export function completePoll(teams,field){
 const rows=teams.filter(t=>t.id!==255&&ranked(t[field]));
 return rows.length===25&&new Set(rows.map(t=>t[field])).size===25;
}
export function publicPoll(s,previous=null){
 const cfp=s.season.CurrentStage==='NFLSeason'&&s.season.CurrentWeekType!=='PreSeason'&&completePoll(s.teams,'cfpRank');
 const key=cfp?'cfp':'ap',field=cfp?'cfpRank':'mediaRank',lastField=cfp?'cfpLastRank':'mediaLastRank';
 const comparable=!cfp||completePoll(s.teams,lastField)&&(!previous?.publicPoll||previous.publicPoll.key===key);
 return {key,name:cfp?'CFP rankings':'AP poll',field,lastField,comparable,
  ranks:Object.fromEntries(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t[field]??null]))};
}
