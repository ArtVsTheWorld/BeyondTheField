import {publicPosition} from './player_references.mjs';
import {seasonReviewWeek} from './season_context.mjs';
import {money,NIL_DOLLARS_PER_POINT} from './football_context.mjs';
import {postseasonTiming} from './postseason_timing.mjs';
export function transactionObservation(s){
 return {version:1,year:s.season.CurrentSeasonYear,
  players:s.players.filter(p=>p.team!==255).map(p=>({id:p.id,name:p.name,presentationId:p.presentationId,position:p.position,team:p.team,nil:p.nil})),
  coaches:s.teams.filter(t=>t.id!==255).flatMap(t=>['headCoach','offensiveCoordinator','defensiveCoordinator'].flatMap(role=>t[role]?.id?[{id:t[role].id,team:t.id,role,...t[role].contract}]:[])),
  signings:(s.signings??[]).map(c=>({player:c.player,team:c.team}))};
}
export function transactionEvents(s){
 if(s.reconstructed||!['NFLSeason','OffSeason'].includes(s.season.CurrentStage))return [];
 const base=s.transactionBaseline,valid=base?.version===1&&base.year===s.season.CurrentSeasonYear,oldPlayers=new Map((valid?base.players:[]).map(p=>[p.id,p])),oldCoaches=new Map((valid?base.coaches:[]).map(c=>[c.id,c])),oldSignings=new Set((valid?base.signings:[]).map(c=>c.team+':'+c.player)),teams=new Map(s.teams.map(t=>[t.id,t])),events=[];
 const add=(id,key,team,values,options={})=>events.push({id:'transaction:'+id,category:options.category??'transactions',facts:{family:'transactions.'+key,voice:'beat',school:teams.get(team)?.name,...values},options:{team,priority:98,...options}});
 if(valid&&!seasonReviewWeek(s))for(const p of s.players.filter(p=>p.team!==255)){
  const old=oldPlayers.get(p.id);if(!old||old.team!==p.team||!Number.isFinite(old.nil)||!Number.isFinite(p.nil)||old.nil<0||p.nil<0||p.nil===old.nil)continue;
  add('nil:'+p.id,'nil-change',p.team,{playerName:p.name,position:p.position,previous:money(old.nil*NIL_DOLLARS_PER_POINT),current:money(p.nil*NIL_DOLLARS_PER_POINT),change:p.nil>old.nil?'increased':'decreased',difference:money(Math.abs(p.nil-old.nil)*NIL_DOLLARS_PER_POINT),verdict:'neutral'},{category:'nil',player:p.id,thread:'nil:'+p.id});
 }
 for(const c of s.delayedNILChanges??[]){
  const p=s.players.find(p=>p.id===c.id);if(!p||!teams.has(c.team)||!Number.isFinite(c.before)||!Number.isFinite(c.after)||c.before<0||c.after<0||c.before===c.after)continue;
  add('nil-review:'+c.id,'nil-review',c.team,{playerName:p.name,position:p.position,previous:money(c.before*NIL_DOLLARS_PER_POINT),current:money(c.after*NIL_DOLLARS_PER_POINT),change:c.after>c.before?'increased':'decreased',difference:money(Math.abs(c.after-c.before)*NIL_DOLLARS_PER_POINT)},{category:'nil',player:p.id,thread:'nil-review:'+p.id});
 }
 if(valid&&s.season.CurrentStage==='OffSeason'&&(s.season.CurrentOffseasonStage===7||s.season.CurrentOffseasonStage==null&&s.season.CurrentWeek===6))for(const p of s.players){
  const old=oldPlayers.get(p.id);if(!old||old.team!==p.team||old.name!==p.name||!old.position||!p.position||publicPosition(old.position)===publicPosition(p.position)||old.presentationId&&p.presentationId&&old.presentationId!==p.presentationId||!teams.has(p.team))continue;
  add('position:'+p.id,'position-change',p.team,{playerName:p.name,position:p.position,oldPosition:publicPosition(old.position),newPosition:publicPosition(p.position)},{player:p.id,priority:100});
 }
 const selection=postseasonTiming(s);
 if(valid||selection.locked&&s.season.CurrentWeekType==='BowlSeason1')for(const c of s.signings??[]){
  if(oldSignings.has(c.team+':'+c.player))continue;
  const p=s.players.find(p=>p.id===c.player);if(!p||!teams.has(c.team))continue;
  const points=Number.isFinite(c.nilOfferPoints)&&c.nilOfferPoints>0?c.nilOfferPoints:null;
  add('signing:'+c.team+':'+c.player,'signed',c.team,{playerName:p.name,position:p.position,voice:p.starRating>=4?'analyst':'beat',analystPersona:c.rank===1?0:5,starDetail:p.starRating?p.starRating+'-star ':'',nilDetail:points!==null?' The listed NIL offer is '+money(points*NIL_DOLLARS_PER_POINT)+'.':'',stars:p.starRating,nationalRecruitRank:c.rank>0?c.rank:null,signed:true,importance:p.starRating===5?'major':'normal'},{category:'signings',player:p.id,national:p.starRating===5||c.rank>0&&c.rank<=100,priority:p.starRating===5?110:98,thread:'signed:'+p.id});
 }
 if(valid)for(const t of s.teams.filter(t=>t.id!==255))for(const role of ['headCoach','offensiveCoordinator','defensiveCoordinator']){
  const c=t[role],old=c&&oldCoaches.get(c.id),n=c?.contract;if(!old||old.team!==t.id||old.role!==role||!n||n.status&&n.status!=='Signed')continue;
  const renewal=Number.isInteger(n.count)&&Number.isInteger(old.count)&&n.count>old.count||Number.isInteger(n.remaining)&&Number.isInteger(old.remaining)&&n.remaining>old.remaining;
  if(!renewal)continue;const years=Number.isInteger(n.length)&&n.length>0?n.length:null;
  add('coach-deal:'+c.id,'coach-deal',t.id,{coachName:c.name,role:({headCoach:'head coach',offensiveCoordinator:'offensive coordinator',defensiveCoordinator:'defensive coordinator'})[role],term:years?' The recorded contract term is '+years+(years===1?' year.':' years.'):'',analystPersona:1},{category:'coaching',national:role==='headCoach',priority:106});
 }
 return events;
}

// Only net changes between two verified observations of the same season/team.
export function blueprintNILChanges(before,after){
 if(before?.version!==1||after?.version!==1||before.year!==after.year)return [];
 const old=new Map(before.players.map(p=>[p.id,p]));
 return after.players.flatMap(p=>{const a=old.get(p.id);return a&&a.team===p.team&&[a.nil,p.nil].every(n=>Number.isFinite(n)&&n>=0)&&a.nil!==p.nil?[{id:p.id,team:p.team,before:a.nil,after:p.nil}]:[];});
}
