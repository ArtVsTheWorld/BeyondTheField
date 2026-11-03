import {verifiedPlayerStats} from './deep_analytics.mjs';
import {visibleGame,finalGame} from './football_context.mjs';
import {phaseIndex} from './publication_timeline.mjs';
import {chooseTemplate} from './story_templates.mjs';
const offense=/^GameOffensive(?:KPReturn)?Stats$/;
const number=(st,key)=>Number.isFinite(st?.[key])?st[key]:null;
export function completeOffensiveLine(position,st,{season=false}={}){
 const py=number(st,'PASSYARDS'),pt=number(st,'PASSTDS'),pi=number(st,'PASSINTS'),ry=number(st,'RUSHYARDS'),rt=number(st,'RUSHTDS'),y=number(st,'RECEIVEYARDS'),td=number(st,'RECEIVETDS'),c=number(st,'RECEIVECATCHES'),parts=[];
 if(position==='QB'){
  if(py!==null)parts.push(`${py} passing yards`);
  if(ry!==null&&ry>=(season?100:20))parts.push(`${ry} rushing yards`);
  if(pt!==null&&rt!==null)parts.push(`${pt+rt} passing/rushing TD`);else if(pt!==null)parts.push(`${pt} passing TD`);
  if(pi!==null)parts.push(`${pi} INT`);
 }else if(['HB','RB','FB'].includes(position)){
  if(ry!==null)parts.push(`${ry} rushing yards`);
  if(y!==null&&y>=(season?100:20))parts.push(`${y} receiving yards`);
  if(rt!==null&&td!==null)parts.push(`${rt+td} scrimmage TD`);else if(rt!==null)parts.push(`${rt} rushing TD`);
 }else{
  if(c!==null&&y!==null)parts.push(`${c} catches for ${y} yards`);
  if(ry!==null&&ry>=(season?100:20))parts.push(`${ry} rushing yards`);
  if(td!==null&&rt!==null)parts.push(`${td+rt} scrimmage TD`);else if(td!==null)parts.push(`${td} receiving TD`);
 }
 return parts.join(', ');
}
export function heismanContext(s,playerId,{historical=false,currentGameIds=null,validationSnapshot=null}={}){
 const p=s.players.find(p=>p.id===playerId);if(!p)return null;
 const games=new Map(s.games.filter(g=>visibleGame(s,g)&&(!historical||g.phase!==s.season.CurrentWeekType||g.week<s.season.CurrentWeek||currentGameIds?.has(g.id))).map(g=>[g.id,g]));
 const rows=s.performances.filter(r=>r.player===p.id&&r.team===p.team&&games.has(r.game)&&offense.test(r.type));
 if(!rows.length||new Set(rows.map(r=>r.game)).size!==rows.length)return null;
 const fields=['PASSYARDS','PASSTDS','PASSINTS','RUSHYARDS','RUSHTDS','RECEIVEYARDS','RECEIVETDS','RECEIVECATCHES'],stats={};
 for(const f of fields)if(rows.every(r=>Number.isFinite(r.stats[f])))stats[f]=rows.reduce((n,r)=>n+r.stats[f],0);
 const verified=verifiedPlayerStats(validationSnapshot??s,p,'offense');
 const seasonValid=verified&&fields.filter(f=>stats[f]!==undefined).every(f=>verified.read(f)!==null);
 const latest=[...rows].sort((a,b)=>phaseIndex(games.get(b.game).phase)-phaseIndex(games.get(a.game).phase)||games.get(b.game).week-games.get(a.game).week||a.game.localeCompare(b.game))[0],g=games.get(latest.game),st=latest.stats;
 const opponent=s.teams.find(t=>t.id===(g.home===p.team?g.away:g.home))?.name??(g.home===p.team?g.awayName:g.homeName),won=(g.home===p.team?g.homeScore:g.awayScore)>(g.home===p.team?g.awayScore:g.homeScore),tie=g.homeScore===g.awayScore;
 const total=(st.PASSYARDS??0)+(st.RUSHYARDS??0),scrimmage=(st.RUSHYARDS??0)+(st.RECEIVEYARDS??0),tds=p.position==='QB'?(st.PASSTDS??0)+(st.RUSHTDS??0):(st.RUSHTDS??0)+(st.RECEIVETDS??0);
 const verdict=p.position==='QB'?(st.PASSINTS>=3||total<200&&st.PASSINTS>=2?'negative':total>=300&&tds>=2&&(st.PASSINTS??0)<=1?'positive':'neutral'):scrimmage>=150||tds>=2?'positive':scrimmage<50&&tds===0?'negative':'neutral';
 return {playerName:p.name,position:p.position,games:rows.length,seasonLine:seasonValid?completeOffensiveLine(p.position,stats,{season:true}):null,recentLine:completeOffensiveLine(p.position,st),opponent,result:tie?'a tie':won?'a win':'a loss',verdict,gameId:g.id};
}
export function correctHeismanArchive(feed,s){
 if(feed.phase!=='RegularSeason'||feed.week>15||feed.season!==s.season.CurrentSeasonYear||!feed.stories.some(p=>p.category==='heisman'&&!p.heismanContextVersion))return feed;
 const events=new Map((feed.events??[]).map(e=>[e.id,e])),currentGameIds=new Set((feed.events??[]).filter(e=>e.category==='results'&&e.eventWeek===feed.week).map(e=>e.facts.gameId)),view={...s,season:{...s.season,CurrentWeekType:feed.phase,CurrentWeek:feed.week}},map=new Map();
 const stories=feed.stories.map(p=>{
  if(p.category!=='heisman'||p.heismanContextVersion)return p;
  const e=events.get(p.eventId);if(!e||!Number.isInteger(e.facts.rank))return p;
  const c=heismanContext(view,e.playerId,{historical:true,currentGameIds,validationSnapshot:s});if(!c?.recentLine||!c.opponent)return p;
  const values={...c,school:e.facts.school,rank:e.facts.rank};
  const rendered=chooseTemplate(c.seasonLine?'context.heisman':'context.heisman-recent',values,feed.key+'|'+p.id);if(!rendered)return p;
  const next={...p,...rendered,rawBody:rendered.body,voiceTemplateId:null,heismanContextVersion:1};map.set(p.id,next);return next;
 });
 return map.size?{...feed,stories,posts:(feed.posts??[]).map(p=>map.get(p.id)??p)}:feed;
}
