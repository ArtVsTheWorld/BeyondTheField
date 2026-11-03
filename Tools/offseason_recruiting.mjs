import {hash} from './story_authors.mjs';
import {publicPosition} from './player_references.mjs';
export const portalOpening=s=>!s.reconstructed&&s.season.CurrentStage==='OffSeason'&&s.season.CurrentWeekType==='OffSeason'&&s.season.CurrentWeek===2;
export function portalOrigin(s,p){
 const ids=new Set(p.allSeasonStats?.filter(r=>r.stats.SEAS_YEAR===s.season.CurrentYear&&r.stats.GAMESPLAYED>0).map(r=>r.stats.YEARBYYEARTEAMINDEX).filter(id=>id!==255&&s.teams.some(t=>t.id===id))??[]);
 return ids.size===1?[...ids][0]:s.portalOrigins?.[p.id]??null;
}
export function offseasonRecruitingEvents(s){
 if(s.reconstructed||s.season.CurrentStage!=='OffSeason'||s.season.CurrentWeekType!=='OffSeason'||s.season.CurrentWeek<2||s.season.CurrentWeek>5)return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),entrants=new Set(s.portalEntrants??[]),events=[];
 const add=(id,family,voice,team,values={},options={})=>events.push({id:'portal-opening:'+id,category:'recruiting',facts:{family:'portal.'+family,voice,analystPersona:hash(id+'|portal-desk')%3===0?3:5,eventFocus:'portal',focusTier:2,focusTeams:[],school:teams.get(team)?.name,...values},options:{team,national:false,priority:112,...options}});
 const open=r=>['Top10','Top5','Top3','Battle'].includes(r.stage),transfers=(s.recruitStatuses??[]).filter(r=>entrants.has(r.player)&&r.recruitClass?.startsWith('Transfer_')&&open(r)&&players.get(r.player)?.team===255).map(r=>({r,p:players.get(r.player)}));
 transfers.sort((a,b)=>(b.p.overall??0)-(a.p.overall??0)||(a.r.nationalRank??99999)-(b.r.nationalRank??99999)||a.p.id.localeCompare(b.p.id));
 const national=new Set(transfers.slice(0,24).map(x=>x.p.id)),local=new Map();
 for(const {r,p} of transfers){
  const origin=portalOrigin(s,p),interested=r.topSchools.filter(id=>teams.has(id)),team=teams.has(origin)?origin:interested[0]??null,covered=team!==null&&(local.get(team)??0)<2;
  if(!national.has(p.id)&&!covered&&!interested.includes(s.userTeamIndex))continue;
  if(covered)local.set(team,(local.get(team)??0)+1);
  const from=teams.get(origin),values={playerName:p.name,position:publicPosition(p.position),formerSchool:from?.name??null,originDetail:from?' after leaving '+from.name:'',nationalRecruitRank:r.nationalRank,positionRecruitRank:r.positionRank,stateRecruitRank:r.stateRank,recruitState:p.homeState,stars:p.starRating};
  add('entrant:'+p.id,'entrant',national.has(p.id)?'analyst':'beat',team,values,{player:p.id,national:national.has(p.id),relatedTeams:interested,priority:national.has(p.id)?123:114,thread:'portal:'+p.id});
  if(interested.length)add('interest:'+p.id,'interest',national.has(p.id)?'analyst':'beat',interested[0],{...values,family:'roster.interest',schools:interested.map(id=>teams.get(id).name).join(', ')},{player:p.id,relatedTeams:interested,national:national.has(p.id),priority:115,thread:'portal:'+p.id});
  if(from&&hash(p.id+'|portal-announcement')%3===0)add('player:'+p.id,'announcement','recruit',from.id,values,{player:p.id,national:false,priority:112,thread:'portal:'+p.id});
 }
 const remaining=(s.recruitStatuses??[]).filter(r=>(r.recruitClass==='HighSchool'||r.recruitClass?.startsWith('JuniorCollege_'))&&open(r)&&players.get(r.player)?.team===255&&Number.isInteger(r.nationalRank)&&r.nationalRank>0).sort((a,b)=>a.nationalRank-b.nationalRank||a.player.localeCompare(b.player));
 for(const [i,r] of remaining.entries()){
  const p=players.get(r.player),schools=r.topSchools.filter(id=>teams.has(id)),relevant=schools.includes(s.userTeamIndex)||(p.homePipeline&&s.teams.find(t=>t.id===s.userTeamIndex)?.pipelines?.includes(p.homePipeline));
  if(i>=20&&!relevant)continue;const values={...(r.recruitClass?.startsWith('JuniorCollege_')?{family:'roster.unsigned'}:{}),playerName:p.name,position:publicPosition(p.position),nationalRecruitRank:r.nationalRank,positionRecruitRank:r.positionRank,stateRecruitRank:r.stateRank,recruitState:p.homeState,stars:p.starRating,starDetail:p.starRating?p.starRating+'-star ':''};
  add('unsigned:'+p.id,i<20?'unsigned':'unsigned-local',i<20?'analyst':'beat',schools[0]??null,values,{player:p.id,relatedTeams:schools,national:i<20,priority:119,thread:'unsigned:'+p.id});
  if(schools.length)add('unsigned-schools:'+p.id,'unsigned-schools','beat',schools[0],{...values,schools:schools.map(id=>teams.get(id).name).join(', ')},{player:p.id,relatedTeams:schools,priority:113,thread:'unsigned:'+p.id});
 }
 return events;
}
