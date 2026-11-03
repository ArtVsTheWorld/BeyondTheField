import {championshipFinal,seasonReviewWeek,verifiedSeasonRecord,programExpectations} from './season_context.mjs';
import {gameStory} from './box_score_stories.mjs';
import {completeOffensiveLine} from './heisman_context.mjs';
import {nationalCoverage} from './national_editorial.mjs';
import {hash} from './story_authors.mjs';

// These are retrospective facts, not a replay of old breaking-news posts.
const confirmedStaff=new Set(['postseason.coach-hired','postseason.coach-retained','postseason.coach-fired','postseason.coach-retired','postseason.coach-pro','postseason.coach-departed','transactions.coach-deal']);
export function observedStaffMoves(feeds,year){
 const moves=new Map();
 for(const feed of feeds){if(feed.season!==year)continue;for(const e of feed.events??[]){
  if(!confirmedStaff.has(e.facts?.family)||!e.facts.coachName||!e.facts.role||!e.teamIds?.length)continue;
  const key=e.facts.family+'|'+e.teamIds[0]+'|'+e.facts.role+'|'+e.facts.coachName;
  moves.set(key,{id:e.id,team:e.teamIds[0],family:e.facts.family,coachName:e.facts.coachName,role:e.facts.role});
 }}return [...moves.values()];
}
export function seasonReviewEvents(s){
 if(!seasonReviewWeek(s))return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),events=[],g=championshipFinal(s),covered=nationalCoverage(s);
 const add=(id,family,voice,team,values={},options={})=>events.push({id:'review:'+id,category:options.category??'season-end',facts:{family:'review.'+family,voice,school:teams.get(team)?.name,...values},options:{team,national:true,priority:101,...options}});
 if(g){
  const win=teams.get(g.homeScore>g.awayScore?g.home:g.away),lose=teams.get(win.id===g.home?g.away:g.home),story=gameStory(s,g),base={gameId:g.id,winner:win.name,loser:lose.name,score:Math.max(g.homeScore,g.awayScore)+'\u2013'+Math.min(g.homeScore,g.awayScore),eventLabel:'national championship',importance:'major',eventFocus:'title',focusTier:3,focusTeams:[g.home,g.away]},opts={relatedTeams:[g.home,g.away],thread:'game:'+g.id,eventWeek:g.week,priority:150};
  add('title-insider','title-insider','analyst',win.id,{...base,analystPersona:1},opts);
  add('title-debate','title-debate','analyst',lose.id,{...base,analystPersona:2},opts);
  if(story)add('title-film','title-film','analyst',win.id,{...base,turningPoint:story.turningPoint,analystPersona:4},opts);
  for(const t of [win,lose]){
   const record=verifiedSeasonRecord(s,t),won=t.id===win.id,st=t.id===g.home?g.homeStats:g.awayStats,opp=t.id===g.home?g.awayStats:g.homeStats;
   if(record)add('finalist:'+t.id,won?'champion-season':'runnerup-season','beat',t.id,{...base,record:record.record,coachDetail:t.headCoach?.name?' under '+t.headCoach.name:''},{...opts,priority:147});
   if(st&&opp&&Number.isInteger(st.GIVEAWAYS)&&st.GIVEAWAYS>=0&&Number.isInteger(opp.GIVEAWAYS)&&opp.GIVEAWAYS>=0)add('ball-security:'+t.id,'title-turnovers','analyst',t.id,{...base,ownGiveaways:st.GIVEAWAYS,otherGiveaways:opp.GIVEAWAYS,opponent:won?lose.name:win.name,analystPersona:4},{...opts,priority:144});
   const rows=(s.performances??[]).filter(r=>r.game===g.id&&r.team===t.id&&/^GameOffensive(?:KPReturn)?Stats$/.test(r.type)),ids=new Set(),duplicates=new Set();for(const r of rows){if(ids.has(r.player))duplicates.add(r.player);ids.add(r.player);}
   const star=rows.filter(r=>!duplicates.has(r.player)).map(r=>{const p=s.players.find(p=>p.id===r.player);return p&&p.team===t.id?{p,line:completeOffensiveLine(p.position,r.stats),yards:(r.stats.PASSYARDS??0)+(r.stats.RUSHYARDS??0)+(r.stats.RECEIVEYARDS??0)}:null;}).filter(x=>x?.line&&x.yards>0).sort((a,b)=>b.yards-a.yards||a.p.id.localeCompare(b.p.id))[0];
   if(star)add('title-player:'+t.id,'title-player','analyst',t.id,{...base,playerName:star.p.name,line:star.line,analystPersona:5},{...opts,player:star.p.id,priority:146});
   else if(t.id===win.id){const roster=s.players.filter(p=>p.team===t.id),seniors=roster.filter(p=>p.classYear==='Senior').length,nonSeniors=roster.filter(p=>['Freshman','Sophomore','Junior'].includes(p.classYear)).length;if(roster.length&&seniors+nonSeniors===roster.length)add('title-roster','title-roster','analyst',t.id,{...base,seniors,nonSeniors,analystPersona:5},{...opts,priority:149});}
  }
 }
 // A national offseason conversation remains available even without a valid final.
 add('national-calendar','calendar','analyst',null,{analystPersona:3},{category:'offseason',priority:132});
 const spectators=[...teams.values()].filter(t=>!g||![g.home,g.away].includes(t.id)).sort((a,b)=>Number(b.id===s.userTeamIndex)-Number(a.id===s.userTeamIndex)||hash(a.id+'|season-over')-hash(b.id+'|season-over')).slice(0,6);
 for(const t of spectators)add('fan-calendar:'+t.id,'fan-calendar','fan',t.id,{persona:hash(t.id+'|review-fan')%2},{category:'offseason',priority:112});
 const records=[...teams.values()].map(t=>({t,r:verifiedSeasonRecord(s,t),expectation:programExpectations(s,t)})).filter(x=>x.r?.played.length>=8&&x.expectation.known&&covered.has(x.t.id)&&(!g||![g.home,g.away].includes(x.t.id))).sort((a,b)=>Number(b.t.id===s.userTeamIndex)-Number(a.t.id===s.userTeamIndex)||Math.abs(b.expectation.winRate-b.expectation.targetRate)-Math.abs(a.expectation.winRate-a.expectation.targetRate)||a.t.id-b.t.id).slice(0,12);
 for(const {t,r,expectation} of records)add('retrospect:'+t.id,'retrospect','analyst',t.id,{record:r.record,expectationNote:expectation.note,verdict:expectation.verdict,analystPersona:1},{priority:114});
 for(const m of s.seasonStaffMoves??[]){if(!teams.has(m.team))continue;const suffix=m.family.split('.').at(-1),action=({'coach-hired':'hired','coach-retained':'retained','coach-fired':'dismissed','coach-retired':'retired','coach-pro':'left for the pro level','coach-departed':'moved on','coach-deal':'signed a new contract'})[suffix];if(!action)continue;
  add('staff:'+m.id,suffix==='coach-hired'?'staff-hired':suffix==='coach-retained'||suffix==='coach-deal'?'staff-retained':suffix==='coach-fired'?'staff-fired':'staff-departed','analyst',m.team,{coachName:m.coachName,role:m.role,action,analystPersona:1},{category:'coaching',national:m.role==='head coach',priority:113,thread:'review-staff:'+m.team});
 }
 return events;
}

export function portalRiskEvents(s){
 if(s.reconstructed||s.season.CurrentStage!=='OffSeason'||s.season.CurrentWeekType!=='OffSeason')return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),covered=nationalCoverage(s),byTeam=new Map(),events=[];
 for(const p of s.players){
  // -1 is the native uninitialized sentinel. Seniors are not assumed to have
  // returning eligibility; a risk indicator is never an entry/commitment.
  if(!teams.has(p.team)||p.classYear==='Senior'||!Number.isInteger(p.transferRisk)||p.transferRisk<50||p.transferRisk>100)continue;
  const list=byTeam.get(p.team)??[];list.push(p);byTeam.set(p.team,list);
 }
 for(const [id,list] of byTeam)for(const p of list.sort((a,b)=>b.transferRisk-a.transferRisk||a.id.localeCompare(b.id)).slice(0,2)){
  const national=covered.has(id)&&p.transferRisk>=70;
  events.push({id:'retention-watch:'+p.id,category:'transfer',facts:{family:'review.retention-watch',voice:national?'analyst':'beat',analystPersona:5,school:teams.get(id).name,playerName:p.name,position:p.position},options:{team:id,player:p.id,national,priority:national?119:99,thread:'retention:'+id}});
 }return events;
}
