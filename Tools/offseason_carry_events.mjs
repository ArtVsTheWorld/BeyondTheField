import {publicPosition} from './player_references.mjs';
import {trainingArea} from './training_profile.mjs';
export function offseasonCarryEvents(s){
 if(s.season.CurrentStage!=='PreSeason'||s.season.CurrentWeekType!=='PreSeason'||s.reconstructed)return [];
 const facts=s.offseasonCarry??[],events=[],teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),counts=new Map();
 const add=(f,family,voice,team,values={},options={})=>events.push({id:f.id+':'+family,category:f.kind==='training'?'preseason':f.kind==='departure'?'transfer':'offseason',facts:{family:'carry.'+family,voice,carryoverKind:f.kind,sourceYear:f.sourceYear,eventFocus:'offseason-carryover',focusTier:2,focusTeams:team?[team.id]:[],school:team?.name,...values},options:{team:team?.id??null,national:false,priority:106,...options}});
 const ordered=[...facts].sort((a,b)=>(b.overall??0)-(a.overall??0)||a.id.localeCompare(b.id));
 for(const f of ordered){if(f.targetYear!==s.season.CurrentSeasonYear)continue;const t=teams.get(f.team),p=players.get(f.player),person=p&&p.name===f.name&&p.team===f.team?p:null;
  if(f.kind==='training'&&t&&person){
   if((counts.get(t.id)??0)>=2)continue;counts.set(t.id,(counts.get(t.id)??0)+1);
   const area=trainingArea(f.position,f.gains);
   if(!area)continue;const national=t.mediaRank>=1&&t.mediaRank<=25,values={playerName:f.name,position:publicPosition(f.position),area,period:f.evidence==='training-period'?'the training period':'the offseason',analystPersona:4};
   add(f,'training',national?'analyst':'beat',t,values,{player:person.id,national});
   if(t.id===s.userTeamIndex)add(f,person.position==='QB'?'player-training-qb':'player-training','player',t,values,{player:person.id,priority:96});
  }else if(f.kind==='departure'&&t){
   const destination=teams.get(f.destination),values={playerName:f.name,position:publicPosition(f.position),period:f.evidence==='observed-encourage'||f.evidence==='encourage-period'?'the offseason roster review':'the offseason',destination:destination?.name,analystPersona:1};
   add(f,destination?'departure-destination':f.portal?'departure-portal':'departure',f.overall>=85?'analyst':'beat',t,values,{national:f.overall>=85,relatedTeams:destination?[destination.id]:[]});
  }else if((f.kind==='realignment'||f.kind==='alignment-history')&&t){
   const values={oldConference:f.oldConference,newConference:f.newConference};add(f,f.kind==='realignment'?'move':'history','beat',t,values,{national:true});
   if(f.kind==='realignment')add(f,'team-move','official',t,values,{national:false,priority:102});
  }else if(f.kind==='rename')add(f,'rename','analyst',null,{oldConference:f.oldConference,newConference:f.newConference,analystPersona:1},{national:true,relatedTeams:f.teams});
 }return events;
}
