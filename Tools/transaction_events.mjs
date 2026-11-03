import {money,NIL_DOLLARS_PER_POINT} from './football_context.mjs';
import {postseasonTiming} from './postseason_timing.mjs';
export function transactionObservation(s){
 return {version:1,year:s.season.CurrentSeasonYear,
  players:s.players.filter(p=>p.team!==255).map(p=>({id:p.id,team:p.team,nil:p.nil})),
  coaches:s.teams.filter(t=>t.id!==255).flatMap(t=>['headCoach','offensiveCoordinator','defensiveCoordinator'].flatMap(role=>t[role]?.id?[{id:t[role].id,team:t.id,role,...t[role].contract}]:[])),
  signings:(s.signings??[]).map(c=>({player:c.player,team:c.team}))};
}
export function transactionEvents(s){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const base=s.transactionBaseline,valid=base?.version===1&&base.year===s.season.CurrentSeasonYear,oldPlayers=new Map((valid?base.players:[]).map(p=>[p.id,p])),oldCoaches=new Map((valid?base.coaches:[]).map(c=>[c.id,c])),oldSignings=new Set((valid?base.signings:[]).map(c=>c.team+':'+c.player)),teams=new Map(s.teams.map(t=>[t.id,t])),events=[];
 const add=(id,key,team,values,options={})=>events.push({id:'transaction:'+id,category:options.category??'transactions',facts:{family:'transactions.'+key,voice:'beat',school:teams.get(team)?.name,...values},options:{team,priority:98,...options}});
 if(valid)for(const p of s.players.filter(p=>p.team!==255)){
  const old=oldPlayers.get(p.id);if(!old||old.team!==p.team||!Number.isFinite(old.nil)||!Number.isFinite(p.nil)||old.nil<0||p.nil<0||p.nil===old.nil)continue;
  add('nil:'+p.id,'nil-change',p.team,{playerName:p.name,position:p.position,previous:money(old.nil*NIL_DOLLARS_PER_POINT),current:money(p.nil*NIL_DOLLARS_PER_POINT),change:p.nil>old.nil?'increased':'decreased',difference:money(Math.abs(p.nil-old.nil)*NIL_DOLLARS_PER_POINT),verdict:'neutral'},{category:'nil',player:p.id,thread:'nil:'+p.id});
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
