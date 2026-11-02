import {postseasonTiming} from './postseason_timing.mjs';
import {phaseIndex} from './publication_timeline.mjs';
import {hash} from './story_authors.mjs';
import {verifiedPlayerStats} from './deep_analytics.mjs';
const final=g=>g.published!==false&&Number.isFinite(g.homeScore)&&Number.isFinite(g.awayScore)&&(g.status==='HomeWon'&&g.homeScore>g.awayScore||g.status==='AwayWon'&&g.awayScore>g.homeScore||g.status==='Tie'&&g.homeScore===g.awayScore);
const edition=s=>`${s.season.CurrentWeekType}/${s.season.CurrentWeek}`;
const notFuture=(s,g)=>phaseIndex(g.phase)>=0&&(phaseIndex(g.phase)<phaseIndex(s.season.CurrentWeekType)||g.phase===s.season.CurrentWeekType&&g.week<=s.season.CurrentWeek);
export function seasonEndings(s){
 const ended=new Map();if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return ended;
 const champWeek=s.season.RegularSeasonWeekConferenceChampionship;
 if(s.season.CurrentWeekType==='RegularSeason'&&(!Number.isInteger(champWeek)||s.season.CurrentWeek<champWeek))return ended;
 for(const t of s.teams.filter(t=>t.id!==255)){
  const games=s.games.filter(g=>g.year===s.season.CurrentYear&&(g.home===t.id||g.away===t.id));
  if(games.some(g=>['Unplayed','HomeScheduled','AwayScheduled'].includes(g.status))||(s.postseasonAssignments??s.playoffBracket??[]).some(g=>g.year===s.season.CurrentYear&&(g.home===t.id||g.away===t.id)&&!final(g)))continue;
  const played=games.filter(g=>notFuture(s,g)&&final(g));
  if(played.length<8||!Number.isInteger(t.wins)||!Number.isInteger(t.losses))continue;
  const own=g=>g.home===t.id?g.homeScore:g.awayScore,other=g=>g.home===t.id?g.awayScore:g.homeScore;
  if(played.length!==t.wins+t.losses+(t.ties??0)||played.filter(g=>own(g)>other(g)).length!==t.wins||played.filter(g=>own(g)<other(g)).length!==t.losses)continue;
  const last=[...played].sort((a,b)=>phaseIndex(b.phase)-phaseIndex(a.phase)||b.week-a.week||a.id.localeCompare(b.id))[0];
  const playoff=last.isPlayoff===true||last.phase==='NationalChampionship',bowl=last.phase.startsWith('BowlSeason')&&Boolean(last.bowlName),lost=own(last)<other(last);
  const postseasonFinished=last.phase==='NationalChampionship'||playoff&&lost||bowl&&!playoff;
  // A missing bowl assignment during title week cannot finish an eligible
  // season. Keep five-win teams pending as well until postseason scheduling.
  const seasonClosed=phaseIndex(s.season.CurrentWeekType)>=phaseIndex('NationalChampionship');
  const noPostseason=last.phase==='RegularSeason'&&(t.wins<5||postseasonTiming(s).locked||seasonClosed);
  if(!postseasonFinished&&!noPostseason)continue;
  if(!postseasonFinished&&last.week===champWeek&&!postseasonTiming(s).locked)continue;
  ended.set(t.id,{team:t,last,played,winless:t.wins===0,undefeated:(postseasonFinished||seasonClosed)&&t.wins>0&&t.losses===0&&(t.ties??0)===0,pointsFor:played.reduce((n,g)=>n+own(g),0),pointsAgainst:played.reduce((n,g)=>n+other(g),0)});
 }
 return ended;
}
export function recruitingClassRanks(s){
 const committed=new Set([...(s.commitments??[]),...(s.signings??[])].map(c=>c.team)),rows=s.teams.filter(t=>t.id!==255&&committed.has(t.id)&&Number.isInteger(t.nativeRecruitingRank)&&t.nativeRecruitingRank>=0);
 const ranks=rows.map(t=>t.nativeRecruitingRank);if(rows.length<2||new Set(ranks).size!==ranks.length)return new Map();
 // Native order is audited separately; never fabricate a ranking from stars.
 const base=Math.min(...ranks)===0?0:Math.min(...ranks)===1?1:null;if(base===null)return new Map();
 return new Map(rows.map(t=>[t.id,t.nativeRecruitingRank+(base===0?1:0)]));
}
export function seedSeasonEndPublications(s,previous={}){
 const ended=seasonEndings(s),ledger={};for(const [id] of ended)ledger[id]=previous[id]??edition(s);s.seasonEndPublications=ledger;return ledger;
}
export function seasonEndingEvents(s){
 const events=[],ranks=recruitingClassRanks(s),index={players:new Map(),games:new Map(s.games.filter(g=>g.year===s.season.CurrentYear&&notFuture(s,g)&&final(g)).map(g=>[g.id,g]))};
 for(const r of s.performances){const a=index.players.get(r.player)??[];a.push(r);index.players.set(r.player,a);}
 for(const [id,end] of seasonEndings(s)){
  if(s.seasonEndPublications?.[id]&&s.seasonEndPublications[id]!==edition(s))continue;
  const t=end.team,negative=end.winless||t.losses>t.wins,mood=end.winless?'winless':end.undefeated?'perfect':negative?'rough':'normal',record=`${t.wins}\u2013${t.losses}`+((t.ties??0)>0?'\u2013'+t.ties:'');
  const values={seasonEnding:true,school:t.name,record,wins:t.wins,losses:t.losses,importance:end.undefeated?'major':'normal'};
  const add=(key,family,voice,facts={},options={})=>events.push({id:`season-end:${id}:${key}`,category:'season-end',facts:{...values,family:'ending.'+family,voice,...facts},options:{team:id,national:end.undefeated,priority:end.undefeated?112:end.winless?105:95,thread:'season-end:'+id,...options}});
  add('team','team.'+mood,'official');
  add('barstool','barstool.'+mood,'fan',{persona:1},{priority:98});
  add('afterdark','afterdark.'+mood,'fan',{persona:0},{priority:97});
  add('review','beat.'+mood,'analyst',{negative},{national:true,priority:99});
  const roster=s.players.filter(p=>p.team===id&&p.injury!=='CareerEnding').sort((a,b)=>a.id.localeCompare(b.id)),seniors=roster.filter(p=>p.classYear==='Senior'&&p.redshirt!=='Current');
  const senior=seniors.length?seniors[hash(s.leagueId+'|farewell|'+id)%seniors.length]:null,p=senior??roster[hash(s.leagueId+'|thanks|'+id)%Math.max(1,roster.length)];
  if(p)add('player',senior?end.undefeated?'player.senior-perfect':'player.senior':end.undefeated?'player.perfect':'player.thanks','player',{playerName:p.name},{player:p.id,national:false});
  const prior=(t.seasonHistory??[]).filter(r=>r.Year===s.season.CurrentSeasonYear-1);
  if(prior.length===1&&Number.isInteger(prior[0].Wins)&&Number.isInteger(prior[0].Losses))add('comparison','comparison','beat',{previousYear:prior[0].Year,priorWins:prior[0].Wins,priorLosses:prior[0].Losses,previousConference:prior[0].ConferenceName??'their conference'});
  const rank=ranks.get(id);if(rank)add('recruiting','recruiting','beat',{classRank:rank},{national:false});
  if(['HotSeat','Low'].includes(t.headCoach?.jobSecurity))add('coach','coach-pressure','beat',{coachName:t.headCoach.name,negative:true},{national:false});
  if(negative){
   const n=end.played.length,staff=end.pointsAgainst/n>=32?t.defensiveCoordinator:end.pointsFor/n<=18?t.offensiveCoordinator:null,coach=staff??t.headCoach;
   if(coach?.name)add('accountability','fan-accountability','fan',{coachName:coach.name,persona:0},{priority:96});
   const qbs=roster.filter(p=>p.position==='QB').map(p=>({p,stats:verifiedPlayerStats(s,p,'offense',index)})).filter(x=>x.stats&&x.stats.read('PASSATTEMPTS')>=100).sort((a,b)=>b.stats.read('PASSATTEMPTS')-a.stats.read('PASSATTEMPTS')||a.p.id.localeCompare(b.p.id));
   const qb=qbs[0],td=qb?.stats.read('PASSTDS'),ints=qb?.stats.read('PASSINTS');if(qb&&td!==null&&ints>=8&&ints>=td)add('qb-review','fan-qb','fan',{playerName:qb.p.name,touchdowns:td,interceptions:ints,persona:1},{player:qb.p.id,priority:96});
  }
 }
 return events;
}
