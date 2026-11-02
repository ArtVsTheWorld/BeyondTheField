// Computed football measures, with explicit sample sizes and coverage gates.
const final=g=>['HomeWon','AwayWon','Tie'].includes(g.status);
const count=x=>Number.isSafeInteger(x)&&x>=0;
export function teamAnalytics(s){
 if(s.season.CurrentWeekType!=='RegularSeason'||s.season.CurrentStage!=='NFLSeason')return {teams:[],milestones:[],coverage:{nationalFieldKnown:false}};
 const population=new Set((s.conferences??[]).flatMap(c=>c.teams).filter(id=>Number.isInteger(id)&&id!==255));
 const nationalFieldKnown=population.size>0&&[...population].every(id=>s.teams.some(t=>t.id===id));
 const names=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t.name]));
 const scheduled=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase==='RegularSeason'&&g.week<=s.season.CurrentWeek);
 const completed=[...new Map(scheduled.filter(final).map(g=>[g.id,g])).values()];
 const rows=new Map();
 const row=id=>{if(!rows.has(id))rows.set(id,{teamId:id,school:names.get(id),gamesPlayed:0,rushingGames:0,rushingYards:0,thirdDownGames:0,thirdDownConversions:0,thirdDownAttempts:0,turnoverGames:0,giveaways:0,takeaways:0});return rows.get(id);};
 for(const g of completed)for(const [id,stats] of [[g.home,g.homeStats],[g.away,g.awayStats]]){
  if(id===255||!names.has(id))continue;const r=row(id);++r.gamesPlayed;
  if(Number.isSafeInteger(stats?.OFFRUSHYARDS)){++r.rushingGames;r.rushingYards+=stats.OFFRUSHYARDS;}
  if(count(stats?.THIRDDOWNCONV)&&count(stats?.THIRDDOWNS)&&stats.THIRDDOWNCONV<=stats.THIRDDOWNS){++r.thirdDownGames;r.thirdDownConversions+=stats.THIRDDOWNCONV;r.thirdDownAttempts+=stats.THIRDDOWNS;}
  if(count(stats?.GIVEAWAYS)&&count(stats?.TAKEAWAYS)){++r.turnoverGames;r.giveaways+=stats.GIVEAWAYS;r.takeaways+=stats.TAKEAWAYS;}
 }
 // The native TeamSeasonStats array is current-first, not indexed by CurrentYear.
 // Validate its W/L/T against the live team record before using its counters.
 for(const t of s.teams.filter(t=>population.has(t.id)||rows.has(t.id))){
  const r=row(t.id);r.resultGames=r.gamesPlayed;
  const recordKnown=count(t.wins)&&count(t.losses)&&count(t.ties??0),expected=recordKnown?t.wins+t.losses+(t.ties??0):null;
  r.resultCountMatchesRecord=recordKnown&&r.resultGames===expected;
  const official=t.seasonStats,stats=official?.stats;
  const current=Boolean(official&&official.season===s.season.CurrentSeasonYear&&official.slot===0&&count(stats?.WINS)&&count(stats?.LOSSES)&&count(stats?.TIES)&&recordKnown&&stats.WINS===t.wins&&stats.LOSSES===t.losses&&stats.TIES===(t.ties??0));
  if(current){
   r.source='currentSeasonStats';r.gamesPlayed=expected;r.rushingGames=Number.isSafeInteger(stats.OFFRUSHYARDS)?expected:0;r.rushingYards=stats.OFFRUSHYARDS??0;
   const validThird=count(stats.THIRDDOWNCONV)&&count(stats.THIRDDOWNS)&&stats.THIRDDOWNCONV<=stats.THIRDDOWNS;
   r.thirdDownGames=validThird?expected:0;r.thirdDownConversions=validThird?stats.THIRDDOWNCONV:0;r.thirdDownAttempts=validThird?stats.THIRDDOWNS:0;
   const validTurnovers=count(stats.GIVEAWAYS)&&count(stats.TAKEAWAYS);r.turnoverGames=validTurnovers?expected:0;r.giveaways=validTurnovers?stats.GIVEAWAYS:0;r.takeaways=validTurnovers?stats.TAKEAWAYS:0;
  }else r.source='gameCaches';
  r.metricRecordMatches=current||r.resultCountMatchesRecord;
  r.rushingYardsPerGame=r.metricRecordMatches&&r.gamesPlayed>0&&r.rushingGames===r.gamesPlayed?r.rushingYards/r.gamesPlayed:null;
  r.thirdDownRate=r.metricRecordMatches&&r.thirdDownGames===r.gamesPlayed&&r.thirdDownAttempts>0?r.thirdDownConversions/r.thirdDownAttempts:null;
  r.turnoverMargin=r.metricRecordMatches&&r.turnoverGames===r.gamesPlayed?r.takeaways-r.giveaways:null;
 }
 const missingPastFinals=scheduled.filter(g=>g.week<s.season.CurrentWeek&&!final(g)).length;
 const members=[...population].map(id=>rows.get(id)).filter(r=>r?.gamesPlayed>0);
 const recordCoverageComplete=nationalFieldKnown&&[...population].every(id=>rows.get(id)?.resultCountMatchesRecord);
 const rushingCoverageComplete=nationalFieldKnown&&[...population].every(id=>{const r=rows.get(id);return r?.metricRecordMatches&&(r.gamesPlayed===0||r.rushingYardsPerGame!==null);});
 for(const r of rows.values()){
  r.rushingRank=rushingCoverageComplete&&r.gamesPlayed>0&&population.has(r.teamId)?1+members.filter(o=>o.rushingYards*r.gamesPlayed>r.rushingYards*o.gamesPlayed).length:null;
  r.rushingRankTied=r.rushingRank!==null&&members.filter(o=>o.rushingYards*r.gamesPlayed===r.rushingYards*o.gamesPlayed).length>1;
 }
 const qualifying=completed.filter(g=>Math.abs(g.homeScore-g.awayScore)>=42&&population.has(g.homeScore>g.awayScore?g.home:g.away));
 const earliestWeek=qualifying.length?Math.min(...qualifying.map(g=>g.week)):null;
 const earliest=qualifying.filter(g=>g.week===earliestWeek),milestones=[];
 // With multiple qualifying wins in the earliest week, completion order is unknown.
 // Suppress a unique "first" claim rather than guessing from row order or kickoff.
 if(recordCoverageComplete&&missingPastFinals===0&&earliest.length===1){const g=earliest[0],winner=g.homeScore>g.awayScore?g.home:g.away;
  milestones.push({kind:'first_fbs_win_by_at_least',threshold:42,gameId:g.id,eventWeek:g.week,teamId:winner,school:names.get(winner),opponent:winner===g.home?g.awayName??names.get(g.away):g.homeName??names.get(g.home),winnerScore:Math.max(g.homeScore,g.awayScore),loserScore:Math.min(g.homeScore,g.awayScore),margin:Math.abs(g.homeScore-g.awayScore)});
 }
 return {teams:[...rows.values()],milestones,coverage:{nationalFieldKnown,populationSize:population.size,definition:'conference membership including independents; excludes generic FCS entries',recordCoverageComplete,rushingCoverageComplete,missingPastFinals,completedGames:completed.length}};
}
