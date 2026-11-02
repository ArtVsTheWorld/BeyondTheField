// Computed football measures, with explicit sample sizes and coverage gates.
const final=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const count=x=>Number.isSafeInteger(x)&&x>=0;
export function teamAnalytics(s){
 if(s.season.CurrentWeekType!=='RegularSeason'||s.season.CurrentStage!=='NFLSeason')return {teams:[],milestones:[],coverage:{nationalFieldKnown:false}};
 const population=new Set((s.conferences??[]).flatMap(c=>c.teams).filter(id=>Number.isInteger(id)&&id!==255));
 const nationalFieldKnown=population.size>0&&[...population].every(id=>s.teams.some(t=>t.id===id));
 const names=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t.name]));
 const scheduled=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase==='RegularSeason'&&g.week<=s.season.CurrentWeek);
 const completed=[...new Map(scheduled.filter(final).map(g=>[g.id,g])).values()];
 const rows=new Map();
 const row=id=>{if(!rows.has(id))rows.set(id,{teamId:id,school:names.get(id),gamesPlayed:0,rushingGames:0,rushingYards:0,thirdDownGames:0,thirdDownConversions:0,thirdDownAttempts:0,turnoverGames:0,giveaways:0,takeaways:0,redZoneGames:0,redZoneTrips:0,redZoneTouchdowns:0,resultWins:0,resultLosses:0,resultTies:0,publicationKnown:true});return rows.get(id);};
 for(const g of completed)for(const [id,stats] of [[g.home,g.homeStats],[g.away,g.awayStats]]){
  if(id===255||!names.has(id))continue;const r=row(id);++r.gamesPlayed;r.publicationKnown&&=g.published===true;const own=id===g.home?g.homeScore:g.awayScore,other=id===g.home?g.awayScore:g.homeScore;if(own>other)++r.resultWins;else if(own<other)++r.resultLosses;else ++r.resultTies;
  if(Number.isSafeInteger(stats?.OFFRUSHYARDS)){++r.rushingGames;r.rushingYards+=stats.OFFRUSHYARDS;}
  if(count(stats?.THIRDDOWNCONV)&&count(stats?.THIRDDOWNS)&&stats.THIRDDOWNCONV<=stats.THIRDDOWNS){++r.thirdDownGames;r.thirdDownConversions+=stats.THIRDDOWNCONV;r.thirdDownAttempts+=stats.THIRDDOWNS;}
  if(count(stats?.OFFREDZONES)&&count(stats?.OFFREDZONETDS)&&stats.OFFREDZONETDS<=stats.OFFREDZONES){++r.redZoneGames;r.redZoneTrips+=stats.OFFREDZONES;r.redZoneTouchdowns+=stats.OFFREDZONETDS;}
  if(count(stats?.GIVEAWAYS)&&count(stats?.TAKEAWAYS)){++r.turnoverGames;r.giveaways+=stats.GIVEAWAYS;r.takeaways+=stats.TAKEAWAYS;}
 }
 // The native TeamSeasonStats array is current-first, not indexed by CurrentYear.
 // Corroborate W/L/T against published results or the separate live team record.
 for(const t of s.teams.filter(t=>population.has(t.id)||rows.has(t.id))){
  const r=row(t.id);r.resultGames=r.gamesPlayed;
  const recordKnown=count(t.wins)&&count(t.losses)&&count(t.ties??0),expected=recordKnown?t.wins+t.losses+(t.ties??0):null;
  r.resultCountMatchesRecord=recordKnown&&r.resultGames===expected;
  const official=t.seasonStats,stats=official?.stats;
  const publishedRecord=Boolean(official?.season===s.season.CurrentSeasonYear&&official?.slot===0&&r.publicationKnown&&stats&&stats.WINS===r.resultWins&&stats.LOSSES===r.resultLosses&&stats.TIES===r.resultTies);
  r.resultRecordMatches=recordKnown&&r.resultWins===t.wins&&r.resultLosses===t.losses&&r.resultTies===(t.ties??0);
  r.resultCorroborated=r.resultRecordMatches||publishedRecord;
  const current=Boolean(official&&official.season===s.season.CurrentSeasonYear&&official.slot===0&&count(stats?.WINS)&&count(stats?.LOSSES)&&count(stats?.TIES)&&((recordKnown&&stats.WINS===t.wins&&stats.LOSSES===t.losses&&stats.TIES===(t.ties??0))||publishedRecord));
  if(current){
   r.source='currentSeasonStats';r.gamesPlayed=stats.WINS+stats.LOSSES+stats.TIES;const verifiedGames=r.gamesPlayed;r.rushingGames=Number.isSafeInteger(stats.OFFRUSHYARDS)?verifiedGames:0;r.rushingYards=stats.OFFRUSHYARDS??0;
   const validThird=count(stats.THIRDDOWNCONV)&&count(stats.THIRDDOWNS)&&stats.THIRDDOWNCONV<=stats.THIRDDOWNS;
   r.thirdDownGames=validThird?verifiedGames:0;r.thirdDownConversions=validThird?stats.THIRDDOWNCONV:0;r.thirdDownAttempts=validThird?stats.THIRDDOWNS:0;
   const validRedZone=count(stats.OFFREDZONES)&&count(stats.OFFREDZONETDS)&&stats.OFFREDZONETDS<=stats.OFFREDZONES;r.redZoneGames=validRedZone?verifiedGames:0;r.redZoneTrips=validRedZone?stats.OFFREDZONES:0;r.redZoneTouchdowns=validRedZone?stats.OFFREDZONETDS:0;
   const validTurnovers=count(stats.GIVEAWAYS)&&count(stats.TAKEAWAYS);r.turnoverGames=validTurnovers?verifiedGames:0;r.giveaways=validTurnovers?stats.GIVEAWAYS:0;r.takeaways=validTurnovers?stats.TAKEAWAYS:0;
  }else r.source='gameCaches';
  r.metricRecordMatches=current||r.resultCorroborated;
  r.rushingYardsPerGame=r.metricRecordMatches&&r.gamesPlayed>0&&r.rushingGames===r.gamesPlayed?r.rushingYards/r.gamesPlayed:null;
  r.thirdDownRate=r.metricRecordMatches&&r.thirdDownGames===r.gamesPlayed&&r.thirdDownAttempts>0?r.thirdDownConversions/r.thirdDownAttempts:null;
  r.redZoneTouchdownRate=r.metricRecordMatches&&r.redZoneGames===r.gamesPlayed&&r.redZoneTrips>0?r.redZoneTouchdowns/r.redZoneTrips:null;
  r.turnoverMargin=r.metricRecordMatches&&r.turnoverGames===r.gamesPlayed?r.takeaways-r.giveaways:null;
 }
 const missingPastFinals=scheduled.filter(g=>g.week<s.season.CurrentWeek&&!final(g)).length;
 const members=[...population].map(id=>rows.get(id)).filter(r=>r?.gamesPlayed>0);
 const recordCoverageComplete=nationalFieldKnown&&[...population].every(id=>rows.get(id)?.resultCorroborated);
 const rushingCoverageComplete=nationalFieldKnown&&[...population].every(id=>{const r=rows.get(id);return r?.metricRecordMatches&&(r.gamesPlayed===0||r.rushingYardsPerGame!==null);});
 for(const r of rows.values()){
  r.rushingRank=rushingCoverageComplete&&r.gamesPlayed>0&&population.has(r.teamId)?1+members.filter(o=>o.rushingYards*r.gamesPlayed>r.rushingYards*o.gamesPlayed).length:null;
  r.rushingRankTied=r.rushingRank!==null&&members.filter(o=>o.rushingYards*r.gamesPlayed===r.rushingYards*o.gamesPlayed).length>1;
 }
 // Generic season superlative, not an arbitrary fixed-margin trigger.
 const wins=completed.filter(g=>g.homeScore!==g.awayScore&&population.has(g.homeScore>g.awayScore?g.home:g.away));
 const best=wins.length?Math.max(...wins.map(g=>Math.abs(g.homeScore-g.awayScore))):null;
 const leaders=wins.filter(g=>Math.abs(g.homeScore-g.awayScore)===best),milestones=[];
 if(recordCoverageComplete&&missingPastFinals===0&&completed.length>=2&&leaders.length===1){const g=leaders[0],winner=g.homeScore>g.awayScore?g.home:g.away;
  milestones.push({kind:'season_largest_winning_margin',gameId:g.id,eventWeek:g.week,teamId:winner,school:names.get(winner),opponent:winner===g.home?g.awayName??names.get(g.away):g.homeName??names.get(g.home),winnerScore:Math.max(g.homeScore,g.awayScore),loserScore:Math.min(g.homeScore,g.awayScore),margin:best,comparisonGames:completed.length});
 }
 return {teams:[...rows.values()],milestones,coverage:{nationalFieldKnown,populationSize:population.size,definition:'conference membership including independents; excludes generic FCS entries',recordCoverageComplete,rushingCoverageComplete,missingPastFinals,completedGames:completed.length}};
}
