import {publicPosition} from './player_references.mjs';
import {draftBoard} from './draft_results.mjs';
import {hash} from './story_authors.mjs';
export function draftDiscourse(s){
 if(s.reconstructed||s.season.CurrentStage!=='OffSeason'||s.season.CurrentWeek<2||s.season.CurrentWeek>5)return [];
 const board=s.draftBoard?.length?s.draftBoard:s.recentDraftClass?.length?s.recentDraftClass:draftBoard(s);if(board.length!==224||new Set(board.map(d=>d.player)).size!==224)return [];
 const players=new Map(s.players.map(p=>[p.id,p])),teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),events=[];
 for(const d of board)if(d.teamId!==undefined&&d.playerName&&d.position)players.set(d.player,{id:d.player,team:d.teamId,name:d.playerName,position:d.position});
 if(board.some(d=>!teams.has(players.get(d.player)?.team)))return [];
 const add=(id,family,team,values,voice='analyst',persona=5,relatedTeams=[])=>events.push({id:'draft-talk:'+id,category:'draft-discourse',facts:{family:'draft-talk.'+family,voice,analystPersona:persona,school:teams.get(team)?.name,...values},options:{team,relatedTeams,national:voice==='analyst',priority:105,thread:'draft-talk:'+id}});
 const counts=[...teams.values()].map(t=>({t,all:board.filter(d=>players.get(d.player)?.team===t.id),first:board.filter(d=>d.round===1&&players.get(d.player)?.team===t.id)}));
 const leaders=counts.filter(c=>c.first.length).sort((a,b)=>b.first.length-a.first.length||a.t.id-b.t.id),high=leaders[0]?.first.length;
 if(high){const tied=leaders.filter(c=>c.first.length===high);add('team-leader','team-leader',tied[0].t.id,{leaders:tied.map(c=>c.t.name).join(', '),count:high,leadVerb:tied.length>1?'tie for the most':'has the most'},'analyst',5,tied.map(c=>c.t.id));}
 const conferences=(s.conferences??[]).map(c=>({c,n:board.filter(d=>d.round===1&&c.teams.includes(players.get(d.player)?.team)).length})).filter(c=>c.n).sort((a,b)=>b.n-a.n||a.c.name.localeCompare(b.c.name));
 if(conferences.length){const high=conferences[0].n,tied=conferences.filter(c=>c.n===high);add('conference-leader','conference-leader',null,{conferences:tied.map(c=>c.c.name).join(', '),count:high,leadVerb:tied.length>1?'share the lead':'leads the way'},'analyst',3,tied.flatMap(c=>c.c.teams));}
 for(const c of counts){
  if(c.all.length){const names=c.all.slice(0,3).map(d=>{const p=players.get(d.player);return publicPosition(p.position)+' '+p.name;}).join(', ');add('congrats:'+c.t.id,'congrats',c.t.id,{count:c.all.length,names,more:c.all.length>3?' and the rest of this class':''},'fan',1);}
  else add('empty:'+c.t.id,'empty',c.t.id,{},'fan',0);
  if(c.first.length)add('first:'+c.t.id,'conference-fan',c.t.id,{count:c.first.length,conference:c.t.conferenceName??'our conference'},'fan',1);
 }
 for(const d of board.filter(d=>d.pick<=10)){const p=players.get(d.player),t=teams.get(p?.team);if(!p||!t)continue;
  add('top-ten:'+d.pick,'top-ten',t.id,{playerName:p.name,position:p.position,pick:d.pick,nflTeam:d.nflTeam,analystPersona:hash(p.id)%2?5:3},'analyst',5);
 }
 // An explicitly subjective favorite, supported by its actual selections on
 // the mod's persisted simulated NFL board, not a claim about future success.
 const nfl=[...new Set(board.map(d=>d.nflTeam))].map(name=>({name,picks:board.filter(d=>d.nflTeam===name)})).sort((a,b)=>a.picks[0].pick-b.picks[0].pick);
 for(const club of nfl.slice(0,3)){const picks=club.picks.slice(0,2),names=picks.map(d=>{const p=players.get(d.player);return publicPosition(p.position)+' '+p.name+' (Round '+d.round+')';}).join(' and ');add('nfl:'+club.name,'nfl-haul',null,{nflTeam:club.name,names},'analyst',club===nfl[0]?5:3,picks.map(d=>players.get(d.player).team));}
 return events;
}
