import {nationalCoverage} from './national_editorial.mjs';
// The decisions screen precedes the portal opening and final draft results.
// Discuss roster retention/pro preparation without promoting a risk to a fact.
export function playersLeavingEvents(s){
 if(s.reconstructed||s.season.CurrentStage!=='OffSeason'||s.season.CurrentWeekType!=='OffSeason'||s.season.CurrentWeek!==1)return [];
 const events=[],covered=nationalCoverage(s),teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t]));
 const add=(id,family,team,values={},options={})=>events.push({id:'leaving:'+id,category:'offseason',facts:{family:'leaving.'+family,voice:'analyst',school:teams.get(team)?.name,...values},options:{team,national:true,priority:115,...options}});
 add('calendar','calendar',null,{analystPersona:1});
 add('retention','retention',null,{analystPersona:5});
 add('fan-clock','fan-clock',null,{analystPersona:3});
 const departing=new Set((s.draftResults??[]).map(p=>p.player));
 const seniors=s.players.filter(p=>teams.has(p.team)&&p.rosterEligible!==false&&p.classYear==='Senior'&&['Previous','Ineligible'].includes(p.redshirt));
 const leaders=[...teams.values()].map(t=>({t,players:seniors.filter(p=>p.team===t.id)})).filter(x=>x.players.length&&covered.has(x.t.id)).sort((a,b)=>b.players.length-a.players.length||a.t.id-b.t.id).slice(0,5);
 for(const {t,players} of leaders)add('class:'+t.id,'senior-class',t.id,{count:players.length,analystPersona:4});
 const prospects=s.players.filter(p=>departing.has(p.id)&&teams.has(p.team)&&covered.has(p.team)).sort((a,b)=>(b.overall??0)-(a.overall??0)||a.id.localeCompare(b.id)).slice(0,6);
 for(const p of prospects)add('pro:'+p.id,'pro-watch',p.team,{playerName:p.name,position:p.position,analystPersona:5},{player:p.id});
 return events;
}
