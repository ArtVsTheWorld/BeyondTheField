import fs from 'node:fs';
import {hash} from './story_authors.mjs';
import {portalOpening} from './offseason_recruiting.mjs';
const clubs=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/nfl-teams.json',import.meta.url),'utf8')).teams;
const premium={QB:9,LE:7,RE:7,LEDG:7,REDG:7,WR:6,LT:6,RT:5,CB:4,DT:3};
export function draftBoard(s,prior=[]){
 if(!portalOpening(s))return [];
 const rows=s.draftResults??[],players=new Map(s.players.map(p=>[p.id,p])),ids=new Set(rows.map(r=>r.player));
 if(rows.length!==224||ids.size!==224||rows.some(r=>!players.has(r.player)||!Number.isInteger(r.round)||r.round<1||r.round>7))return [];
 for(let r=1;r<=7;r++)if(rows.filter(p=>p.round===r).length!==32)return [];
 if(prior.length===224&&new Set(prior.map(p=>p.player)).size===224&&prior.every(p=>rows.some(r=>r.player===p.player&&r.round===p.round))&&new Set(prior.map(p=>p.pick)).size===224&&prior.every(p=>p.pick>=1&&p.pick<=224&&clubs.includes(p.nflTeam)&&p.round===Math.floor((p.pick-1)/32)+1&&p.roundPick===(p.pick-1)%32+1)&&Array.from({length:7},(_,i)=>new Set(prior.filter(p=>p.round===i+1).map(p=>p.nflTeam)).size).every(n=>n===32))return prior;
 const seed=s.leagueId+'|'+s.season.CurrentSeasonYear,order=[...clubs].sort((a,b)=>hash(seed+'|club|'+a)-hash(seed+'|club|'+b)||a.localeCompare(b)),board=[];
 for(let round=1;round<=7;round++){
  const score=p=>(p.overall??0)+(premium[p.position]??0)+(hash(seed+'|prospect|'+p.id)%100)/50;
  const candidates=rows.filter(r=>r.round===round).sort((a,b)=>score(players.get(b.player))-score(players.get(a.player))||a.player.localeCompare(b.player));
  for(const [i,r] of candidates.entries())board.push({...r,pick:(round-1)*32+i+1,roundPick:i+1,nflTeam:order[i]});
 }return board;
}
export function draftEvents(s){
 if(!portalOpening(s))return [];
 const board=s.draftBoard??draftBoard(s),players=new Map(s.players.map(p=>[p.id,p]));
 return board.flatMap(d=>{const p=players.get(d.player),team=s.teams.find(t=>t.id===p?.team&&t.id!==255);if(!p||!team)return [];
  return [{id:'draft:'+s.season.CurrentSeasonYear+':'+d.player,category:'draft',facts:{family:d.pick===224?'draft.irrelevant':d.pick<=10?'draft.top-ten':'draft.pick',voice:'nflDraft',school:team.name,playerName:p.name,position:p.position,nflTeam:d.nflTeam,draftRound:d.round,draftPick:d.pick,roundPick:d.roundPick,modeledDestination:true,importance:d.pick<=10||d.pick===224?'major':'normal'},options:{team:team.id,player:p.id,national:true,priority:d.pick<=10?125:d.pick===224?120:90,thread:'draft:'+d.pick}}];
 });
}
