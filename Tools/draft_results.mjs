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
 const seed=s.leagueId+'|'+s.season.CurrentSeasonYear,order=[...clubs].sort((a,b)=>hash(seed+'|club|'+a)-hash(seed+'|club|'+b)||a.localeCompare(b)),board=[],selected=new Map(clubs.map(c=>[c,[]]));
 const unit=pos=>['LT','LG','C','RG','RT'].includes(pos)?'OL':['LE','RE','LEDG','REDG'].includes(pos)?'EDGE':['FS','SS'].includes(pos)?'S':['LOLB','ROLB','MLB','SAM','MIKE','WILL'].includes(pos)?'LB':pos;
 for(let round=1;round<=7;round++){
  const candidates=rows.filter(r=>r.round===round);
  for(const [i,nflTeam] of order.entries()){
   const taken=selected.get(nflTeam),earlyQB=taken.some(x=>x.position==='QB'&&x.round<=3);
   // Preserve the native round; build a balanced synthetic class for each club.
   const canAvoidQB=round<=3&&earlyQB&&candidates.some(r=>players.get(r.player).position!=='QB');
   const score=r=>{const p=players.get(r.player),same=taken.filter(x=>unit(x.position)===unit(p.position)).length;
    const repetition=same*(unit(p.position)==='OL'?2:unit(p.position)==='EDGE'?4:10);
    return (p.overall??0)+(premium[p.position]??0)*(round===1?1:0.55)-repetition+(hash(seed+'|need|'+nflTeam+'|'+unit(p.position))%700)/100+(hash(seed+'|prospect|'+p.id)%100)/100;};
   const r=candidates.filter(r=>!canAvoidQB||players.get(r.player).position!=='QB').sort((a,b)=>score(b)-score(a)||a.player.localeCompare(b.player))[0];
   candidates.splice(candidates.indexOf(r),1);board.push({...r,pick:(round-1)*32+i+1,roundPick:i+1,nflTeam});selected.get(nflTeam).push({position:players.get(r.player).position,round});
  }
 }return board;
}
export function undraftedBoard(s,prior=[]){
 if(!portalOpening(s))return [];
 const board=s.draftBoard??draftBoard(s);if(board.length!==224)return [];
 const players=new Map(s.players.map(p=>[p.id,p])),drafted=new Set(board.map(d=>d.player)),portal=new Set([...(s.portalEntrants??[]),...(s.recruitStatuses??[]).filter(r=>r.recruitClass?.startsWith('Transfer_')).map(r=>r.player)]),teams=new Set(s.teams.filter(t=>t.id!==255).map(t=>t.id));
 const floors=new Map();for(const d of board.filter(d=>d.round>=6)){const p=players.get(d.player);if(Number.isFinite(p?.overall))floors.set(p.position,Math.min(floors.get(p.position)??99,p.overall));}
 const quality=p=>{const rows=(p.seasonStats??[]).filter(r=>r.stats?.SEAS_YEAR===s.season.CurrentYear),st=Object.assign({},...rows.map(r=>r.stats));
  const standout=st.PASSYARDS>=3000||st.RUSHYARDS>=1100||st.RECEIVEYARDS>=1000||((st.DLINESACKS??0)+(st.DLINEHALFSACK??0)/2)>=8||st.DSECINTS>=4||st.DEFTACKLES>=85;
  return {eligible:Number.isFinite(p.overall)&&p.overall>=Math.max(60,(floors.get(p.position)??75)-6)||standout,score:(p.overall??0)-(floors.get(p.position)??75)+(standout?7:0)-(['K','P'].includes(p.position)?6:0)};
 };
 // Exhausted eligibility is required. An ordinary active junior or a senior
 // currently redshirting cannot become an invented professional signing.
 const candidates=s.players.filter(p=>p.rosterEligible!==false&&teams.has(p.team)&&p.classYear==='Senior'&&['Previous','Ineligible'].includes(p.redshirt)&&!drafted.has(p.id)&&!portal.has(p.id)).map(p=>({p,...quality(p)})).filter(x=>x.eligible).sort((a,b)=>b.score-a.score||a.p.id.localeCompare(b.p.id));
 const selected=[],positionCounts=new Map();for(const candidate of candidates){const pos=candidate.p.position,cap=['K','P'].includes(pos)?1:pos==='QB'?3:5;if((positionCounts.get(pos)??0)>=cap)continue;selected.push(candidate);positionCounts.set(pos,(positionCounts.get(pos)??0)+1);if(selected.length===25)break;}
 const byId=new Map(candidates.map(x=>[x.p.id,x.p])),count=selected.length;
 if(prior.length===count&&new Set(prior.map(d=>d.player)).size===count&&prior.every(d=>byId.has(d.player)&&clubs.includes(d.nflTeam)))return prior;
 const seed=s.leagueId+'|'+s.season.CurrentSeasonYear+'|undrafted',order=[...clubs].sort((a,b)=>hash(seed+'|'+a)-hash(seed+'|'+b)||a.localeCompare(b));
 return selected.map(({p},i)=>({player:p.id,nflTeam:order[i],team:p.team}));
}
export function draftEvents(s){
 if(!portalOpening(s))return [];
 const board=s.draftBoard??draftBoard(s),players=new Map(s.players.map(p=>[p.id,p]));
 const picks=board.flatMap(d=>{const p=players.get(d.player),team=s.teams.find(t=>t.id===p?.team&&t.id!==255);if(!p||!team)return [];
  return [{id:'draft:'+s.season.CurrentSeasonYear+':'+d.player,category:'draft',facts:{family:d.pick===224?'draft.irrelevant':d.pick<=10?'draft.top-ten':'draft.pick',voice:'nflDraft',school:team.name,playerName:p.name,position:p.position,nflTeam:d.nflTeam,draftRound:d.round,draftPick:d.pick,roundPick:d.roundPick,modeledDestination:true,importance:d.pick<=10||d.pick===224?'major':'normal'},options:{team:team.id,player:p.id,national:true,priority:d.pick<=10?125:d.pick===224?120:90,thread:'draft:'+d.pick}}];
 });
 const freeAgents=s.undraftedSignings??undraftedBoard({...s,draftBoard:board});
 return [...picks,...freeAgents.flatMap(d=>{const p=players.get(d.player),team=s.teams.find(t=>t.id===p?.team&&t.id!==255);return p&&team?[{id:'undrafted:'+s.season.CurrentSeasonYear+':'+p.id,category:'draft',facts:{family:'draft.undrafted',voice:'nflDraft',school:team.name,playerName:p.name,position:p.position,nflTeam:d.nflTeam,modeledDestination:true},options:{team:team.id,player:p.id,national:true,priority:86,thread:'undrafted:'+p.id}}]:[];})];
}
