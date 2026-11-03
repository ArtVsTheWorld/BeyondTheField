import {focusFixtures} from './postseason_buzz.mjs';
import {newsCycle,programExpectations} from './season_context.mjs';
import {seasonEndings,recruitingClassRanks} from './season_ending_events.mjs';
import {hash} from './story_authors.mjs';
const final=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
export function offseasonEvents(s){
 if(s.reconstructed)return [];
 const cycle=newsCycle(s),ended=seasonEndings(s),teams=s.teams.filter(t=>t.id!==255),players=new Map(s.players.map(p=>[p.id,p])),events=[],ranks=recruitingClassRanks(s);
 if(cycle.key==='preseason')for(const t of teams){if(!Number.isFinite(t.prestigeStars))continue;const standard=t.prestigeStars>=4.5?'Championship contention is the expectation; a winning record by itself will not satisfy it.':t.prestigeStars>=3.5?'Competing for the conference title should be a serious goal.':t.prestigeStars<=2?'A winning season and a bowl run would be a meaningful building block.':'A winning season and a place in the conference race are reasonable goals.';events.push({id:'cycle:bar:'+t.id,category:'preseason',facts:{family:'cycle.program-bar',voice:t.prestigeStars>=4?'analyst':'beat',school:t.name,standard},options:{team:t.id,national:t.prestigeStars>=4.5,priority:92}});}
 if(cycle.key==='offseason')for(const t of teams)if(!ended.has(t.id))ended.set(t.id,{team:t});
 for(const [id,end] of ended){
  const t=end.team,expectation=programExpectations(s,t),roster=s.players.filter(p=>p.team===id),signature=(s.signings??[]).filter(c=>c.team===id&&players.has(c.player)).sort((a,b)=>(players.get(b.player).starRating??0)-(players.get(a.player).starRating??0)||a.player.localeCompare(b.player)),target=signature.length?signature[hash(id+'|class-spotlight|'+s.season.CurrentWeek)%Math.min(5,signature.length)]:null,recruit=target&&players.get(target.player);
  const add=(key,voice,facts={},options={})=>events.push({id:`cycle:${id}:${key}`,category:options.category??'offseason',facts:{family:'cycle.'+key,voice,school:t.name,nickname:t.nickname??t.name,record:expectation.record??`${t.wins}\u2013${t.losses}`,expectationNote:expectation.note,verdict:expectation.verdict,offseason:true,...facts},options:{team:id,national:false,priority:85,...options}});
  if(expectation.known)add('outlook','beat',{}, {priority:91});
  add('team-reset','official');
  if(t.headCoach?.name)add('staff-plan','beat',{coachName:t.headCoach.name});
  add(expectation.verdict==='negative'?'fan-standards':'fan-future','fan',{persona:1});
  const seniors=roster.filter(p=>p.classYear==='Senior'&&p.redshirt!=='Current'),returners=roster.filter(p=>p.classYear!=='Senior'&&p.injury!=='CareerEnding').sort((a,b)=>a.id.localeCompare(b.id)),p=returners[hash(id+'|next-season-player')%Math.max(1,returners.length)];
  if(p)add('player-reset','player',{playerName:p.name},{player:p.id,priority:84});
  const groups=new Map();for(const p of seniors)groups.set(p.position,(groups.get(p.position)??0)+1);
  const need=[...groups].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))[0];
  if(need)add('portal-needs','beat',{position:need[0],count:need[1],seniorLabel:need[1]===1?'listed senior':'listed seniors'},{priority:89});
  else add('portal-plan','beat');
  if(recruit){
   add('signed-spotlight','official',{playerName:recruit.name,position:recruit.position,tagPlayerId:recruit.id,stars:recruit.starRating,starDetail:recruit.starRating?recruit.starRating+'-star ':'',signed:true},{category:'recruiting',player:recruit.id,priority:89});
   add('recruit-fit','beat',{playerName:recruit.name,position:recruit.position,stars:recruit.starRating,starDetail:recruit.starRating?recruit.starRating+'-star ':'',signed:true},{category:'recruiting',player:recruit.id,priority:88});
  }else if(ranks.has(id))add('class-build','beat',{classRank:ranks.get(id)},{category:'recruiting'});
  // Named targets require an actual transfer-class recruit with this program
  // in the recorded top three. Ordinary active players are never called portal targets.
  const portal=(s.recruitStatuses??[]).filter(r=>r.recruitClass?.startsWith('Transfer')&&r.topSchools?.includes(id)&&!['Signed','HardCommitted'].includes(r.stage)).map(r=>players.get(r.player)).filter(p=>p?.team===255).sort((a,b)=>a.id.localeCompare(b.id))[0];
  if(portal)add('portal-target','beat',{playerName:portal.name,position:portal.position},{category:'recruiting',player:portal.id,priority:92});
 }
 return events;
}
// Filter the entire event pool, so ended programs cannot leak old in-season
// analytics back in through a second generator or another account voice.
export function applyNewsCycle(s,events){
 if(s.reconstructed)return events;
 const cycle=newsCycle(s),ended=seasonEndings(s),focus=focusFixtures(s),byId=new Map(s.games.map(g=>[g.id,g]));
 const liveCategories=new Set(['analytics','standings','streaks','watch','polls','heisman','conference-talk']);
 return events.filter(e=>{
  if(cycle.key==='offseason'&&liveCategories.has(e.category))return false;
  if(cycle.key==='postseason'&&e.category==='analytics'&&!e.facts.gameId)return false;
  if(!e.teamIds.some(id=>ended.has(id)))return true;
  if(liveCategories.has(e.category))return false;
  if(e.category==='injuries'&&!e.facts.newlyInjured&&!e.facts.recovered&&!e.facts.family)return false;
  if(['results','team-stats','player-stats','matchup-recap','upsets'].includes(e.category)){
   const g=byId.get(e.facts.gameId);return Boolean(g&&final(g)&&g.week>=s.season.CurrentWeek-1);
  }
  // Generic year-over-year/milestone roundups do not fill the national feed
  // week after week once these programs have started their offseason.
  if(e.category==='history'&&e.id.startsWith('late:'))return false;
  return true;
 }).filter(e=>!(e.id.startsWith('playoff:preview:')||e.id.startsWith('playoff:matchup:')||e.id.startsWith('playoff:result')||e.id.startsWith('preview:')||e.id.startsWith('watch:'))||!focus.some(f=>e.thread==='game:'+f.game.id)).map(e=>{
  const f=focus.find(f=>e.facts.gameId===f.game.id||e.thread==='game:'+f.game.id);
  if(!f){const team=s.teams.find(t=>t.id===e.teamIds[0]),expectation=team&&programExpectations(s,team);const family=e.facts.family;
   if(e.category==='injuries'&&e.teamIds.some(id=>ended.has(id)))return {...e,newsCycle:cycle.key,facts:{...e.facts,family:e.facts.recovered?'cycle.injury-recovery':'cycle.injury-rehab'}};
   const contextual=['late.turnaround','late.regression'].includes(family)&&expectation?.known?{...e.facts,family:family==='late.turnaround'?'cycle.context-turnaround':'cycle.context-regression',expectationNote:expectation.note,verdict:expectation.verdict}:e.facts;
   const shift=cycle.key==='opening'&&['schedule','results','player-stats'].includes(e.category)?8:cycle.key==='late'&&['cfp','championship','standings'].includes(e.category)?10:cycle.key==='offseason'&&['transactions','coaching','recruiting','signings'].includes(e.category)?10:0;
   return {...e,facts:contextual,priority:e.priority+shift,newsCycle:cycle.key};}
  const scopes=f.kind==='conference'&&!(f.grade>=10)?e.scopes.filter(k=>k!=='national'):e.scopes;
  return {...e,scopes,newsCycle:cycle.key,priority:e.id.startsWith('buzz:')?e.priority:Math.max(e.priority,f.kind==='title'?128:f.kind==='playoff'?118:100),facts:{...e.facts,eventFocus:f.kind,focusTier:f.tier,focusTeams:[f.game.home,f.game.away]}};
 });
}
