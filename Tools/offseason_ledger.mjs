import {createHash} from 'node:crypto';
import {trainingFields} from './training_profile.mjs';
const key=p=>p.id+'|'+p.name.trim().toLowerCase();
const same=(a,b)=>Boolean(a&&b&&key(a)===key(b)&&(!a.presentationId||!b.presentationId||a.presentationId===b.presentationId));
const digest=s=>createHash('sha256').update(s).digest('hex').slice(0,20);
const senior=p=>/senior|graduate/i.test(p.classYear??'');
const validTeam=(s,id)=>id!==255&&s.teams.some(t=>t.id===id);
export function offseasonStage(s){
 if(s.season.CurrentWeekType!=='OffSeason'||s.season.CurrentStage!=='OffSeason')return null;
 const label=s.offseasonStageLabel??'';
 if(/training results/i.test(label))return 'training';
 if(/encourage|realign|custom conference/i.test(label))return 'encourage';
 // Verified CFB calendar: second signing day 6, training 7, final roster/alignment 8.
 return s.season.CurrentWeek===7?'training':s.season.CurrentWeek===8?'encourage':s.season.CurrentWeek<=6?'before-training':null;
}
function observePlayers(s,attributes=false){
 return s.players.filter(p=>p.rosterEligible!==false&&validTeam(s,p.team)&&p.name?.trim()&&p.position).map(p=>({id:p.id,name:p.name,position:p.position,team:p.team,presentationId:p.presentationId??null,classYear:p.classYear,overall:p.overall,
  ...(attributes?{attributes:{...p.trainingAttributes}}:{})}));
}
const conferences=s=>s.teams.filter(t=>t.id!==255&&t.conferenceName).map(t=>({team:t.id,school:t.name,id:t.conferenceId??null,code:t.conferenceCode??null,name:t.conferenceName}));
function trainingChanges(before,s,evidence){
 if(!before)return {};
 const now=new Map(s.players.map(p=>[p.id,p])),result={};
 for(const old of before.players){const p=now.get(old.id);if(!same(old,p)||p.team!==old.team||p.position!==old.position)continue;
  const fields=trainingFields(p.position);
  const gains=Object.entries(old.attributes??{}).flatMap(([field,value])=>fields.has(field)&&Number.isInteger(value)&&Number.isInteger(p.trainingAttributes?.[field])&&p.trainingAttributes[field]>value?[{field,gain:p.trainingAttributes[field]-value}]:[]).sort((a,b)=>b.gain-a.gain||a.field.localeCompare(b.field));
  if(!gains.length||!(gains[0].gain>=5||gains.filter(g=>g.gain>=3).length>=2))continue;
  result[key(old)]={kind:'training',player:old.id,name:old.name,position:old.position,team:old.team,presentationId:old.presentationId,overall:p.overall,evidence,gains};
 }return result;
}
function departures(c,s,evidence){
 const now=new Map(s.players.map(p=>[p.id,p])),result={};
 for(const old of c.beforeRoster??[]){const p=now.get(old.id),previous=c.departures?.[key(old)],midweek=offseasonStage(s)==='encourage'&&c.last?.stage==='encourage'&&c.last.week===s.season.CurrentWeek&&c.last.players.some(p=>same(old,p)&&p.team===old.team);
  if(same(old,p)&&p.team===old.team)continue;
  if(c.knownExits.includes(key(old)))continue;
  if(!previous&&senior(old)&&!midweek)continue;
  // A missing/reused record at rollover is not enough to infer a departure.
  if(!previous&&(!same(old,p)||p.team===old.team)&&!(midweek&&!p))continue;
  result[key(old)]={...old,player:old.id,kind:'departure',evidence:previous?.evidence??(midweek?'observed-encourage':evidence),destination:same(old,p)&&validTeam(s,p.team)?p.team:null,portal:s.portalEntrants?.includes(old.id)===true||previous?.portal===true};
 }return result;
}
function conferenceChanges(c,s,sourceYear){
 const now=conferences(s),events=[],renames=new Set(),covered=new Set(),equal=(a,b)=>a.trim().toLowerCase()===b.trim().toLowerCase();
 if(c?.conferenceBaselineTrusted){
  for(const old of c.beforeConferences){const n=now.find(n=>n.team===old.team);if(!n||old.school&&old.school!==n.school||equal(old.name,n.name))continue;covered.add(old.team);
   const sameLeague=old.code&&n.code?old.code===n.code:old.id&&n.id&&old.id===n.id;
   if(sameLeague){const id=old.name+'|'+n.name;if(!renames.has(id)){renames.add(id);events.push({kind:'rename',oldConference:old.name,newConference:n.name,teams:now.filter(t=>t.id===n.id).map(t=>t.team)});}continue;}
   events.push({kind:'realignment',team:old.team,oldConference:old.name,newConference:n.name});
  }
 }
 if(!c?.conferenceBaselineTrusted||c.conferenceBaselineLate)for(const t of s.teams){
  if(covered.has(t.id))continue;
  const rows=(t.seasonHistory??[]).filter(r=>r.Year===sourceYear&&r.ConferenceName);
  if(rows.length===1&&t.conferenceName&&!equal(rows[0].ConferenceName,t.conferenceName))events.push({kind:'alignment-history',team:t.id,oldConference:rows[0].ConferenceName,newConference:t.conferenceName});
 }return events;
}
export function observeOffseason(s,saved=null,{history=[]}={}){
 const year=s.season.CurrentSeasonYear,pre=s.season.CurrentStage==='PreSeason'&&s.season.CurrentWeekType==='PreSeason',stage=offseasonStage(s);
 if(!Number.isInteger(year)||!Number.isInteger(s.leagueId)||!Number.isInteger(s.userTeamIndex))throw Error('Invalid offseason ledger identity');
 const ledger=saved?structuredClone(saved):{version:1,leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,cycles:{}};
 if(ledger.version!==1||ledger.leagueId!==s.leagueId||ledger.userTeamIndex!==s.userTeamIndex||!ledger.cycles||typeof ledger.cycles!=='object')throw Error('Offseason ledger identity/version mismatch');
 for(const y of Object.keys(ledger.cycles))if(Number(y)>year||Number(y)<year-2)delete ledger.cycles[y];
 if(s.reconstructed)return {ledger,facts:[]};
 if(!stage){delete ledger.cycles[year];} // Rewinding before this year's offseason prunes its future facts.
 if(stage){
  const c=ledger.cycles[year]??={knownExits:[],training:{},departures:{},beforeRoster:null,beforeConferences:[],conferenceBaselineTrusted:false,last:null};
  const rewind=c.last&&s.season.CurrentWeek<c.last.week;
  if(rewind){c.last=null;c.knownExits=[];if(s.season.CurrentWeek<8){c.departures={};c.beforeRoster=null;}if(s.season.CurrentWeek<7)c.training={};}
  const exits=[...(s.draftResults??[]).map(d=>{const p=s.players.find(p=>p.id===d.player);return p&&key(p);}),...history.filter(f=>f.season===year&&(f.phase!=='OffSeason'||f.week<=s.season.CurrentWeek)).flatMap(f=>(f.events??[]).filter(e=>e.category==='draft'&&e.playerId&&e.facts.playerName).map(e=>e.playerId+'|'+e.facts.playerName.trim().toLowerCase()))].filter(Boolean);
  c.knownExits=[...new Set([...c.knownExits,...exits])];
  if(stage==='before-training'){c.baseline={week:s.season.CurrentWeek,players:observePlayers(s,true)};c.training={};c.departures={};c.beforeRoster=null;c.beforeConferences=conferences(s);c.conferenceBaselineTrusted=true;c.conferenceBaselineLate=false;}
  if(stage==='training'){c.training=trainingChanges(c.baseline,s,c.baseline?.week===6?'training-period':'offseason-period');c.beforeRoster=observePlayers(s);c.beforeConferences=conferences(s);c.conferenceBaselineTrusted=true;c.conferenceBaselineLate=false;}
  if(stage==='encourage'){
   if(!c.beforeConferences.length){c.beforeConferences=conferences(s);c.conferenceBaselineTrusted=true;c.conferenceBaselineLate=true;}
   if(!c.beforeRoster)c.beforeRoster=c.last?.players??observePlayers(s);
   c.departures=departures(c,s,c.last?.stage==='training'||c.last?.stage==='encourage'?'encourage-period':'offseason-period');
  }
  c.last={week:s.season.CurrentWeek,stage,players:observePlayers(s)};
 }
 const facts=[];
 if(pre){
  const sourceYear=year-1,c=ledger.cycles[sourceYear];
  if(c){
   if(!Object.keys(c.training).length)c.training=trainingChanges(c.baseline,s,'offseason-period');
   if(!c.beforeRoster)c.beforeRoster=c.last?.players??[];
   c.departures=departures(c,s,'offseason-period');
   const now=new Map(s.players.map(p=>[p.id,p]));
   for(const fact of Object.values(c.training)){const p=now.get(fact.player);if(same({...fact,id:fact.player},p)&&p.team===fact.team&&p.position===fact.position)facts.push(structuredClone(fact));}
   facts.push(...structuredClone(Object.values(c.departures)));
  }
  facts.push(...conferenceChanges(c,s,sourceYear));
  for(const f of facts){f.sourceYear=sourceYear;f.targetYear=year;f.id='carry:'+sourceYear+':'+f.kind+':'+digest(JSON.stringify([f.player??null,f.team??null,f.oldConference??null,f.newConference??null]));}
 }
 return {ledger,facts};
}
