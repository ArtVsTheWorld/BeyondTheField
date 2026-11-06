import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const keyPattern=/^(0|[1-9]\d*):(0|[1-9]\d*)$/;
const text=v=>typeof v==='string'?v.replace(/[\t\r\n\x00-\x1f]/g,' ').trim():'';
const yearName=v=>({Freshman:'FR',Sophomore:'SO',Junior:'JR',Senior:'SR'})[v]??'';

// A small view of the existing capture: actual drafted players and rounds.
// Modeled picks and NFL destinations belong exclusively to Social Media.
export function draftSnapshot(raw){
 if(raw?.format!==1||raw.sourceKind!=='runtime'||!raw.records)throw Error('Not a live Dynasty capture');
 const all=Object.values(raw.records),season=raw.status?.season;
 if(!Number.isInteger(raw.status?.league)||!Number.isInteger(season?.CurrentSeasonYear))throw Error('Missing draft identity');
 const flow=all.find(r=>r.type==='FranchiseServer_CareerFlow')?.v;
 if(flow&&(!flow.IsStageActive||flow.IsStageAdvancing))throw Error('Dynasty is inactive or advancing');
 const resolve=key=>{if(key==null)return null;const r=raw.records[key];if(!r)throw Error('Unresolved draft capture record');return r;};
 const array=key=>{const r=resolve(key);if(!r)return [];if(!r.type.endsWith('[]'))throw Error('Not a captured array');return Object.entries(r.v).sort(([a],[b])=>Number(a.slice(6))-Number(b.slice(6))).map(([,v])=>resolve(v)).filter(Boolean);};
 const teams=all.filter(r=>r.type==='Team'&&r.capacity>1&&r.v.TeamIndex>=0&&r.v.TeamIndex<255).map(r=>({id:r.v.TeamIndex,name:text(r.v.DisplayName||r.v.LongName||r.v.ShortName),recordKey:r.key}));
 const byTeam=new Map(teams.map(t=>[t.id,t])),conferences=[];
 for(const r of all.filter(r=>r.type==='Conference')){
  const members=[...array(r.v.TeamSlots),...array(r.v.Divisions).flatMap(d=>array(d.v.Teams))].filter(r=>r.type==='Team').map(r=>r.v.TeamIndex).filter(id=>byTeam.has(id));
  if(!members.length)continue;
  const name=text(r.v.Name||r.v.ConferenceEnum);if(!name)continue;
  const c={id:r.key,name,teams:[...new Set(members)]};conferences.push(c);
  for(const id of c.teams){const t=byTeam.get(id);if(t.conferenceId&&t.conferenceId!==c.id)throw Error('Conflicting draft conference membership');t.conferenceId=c.id;t.conferenceName=name;}
 }
 const players=all.filter(r=>r.type==='Player'&&r.capacity>1).map(r=>({id:r.key,name:text(r.v.FirstName+' '+r.v.LastName),position:r.v.Position,team:r.v.TeamIndex,overall:r.v.OverallRating,classYear:r.v.SchoolYear,redshirt:r.v.RedshirtStatus}));
 const draftResults=[];
 for(const e of all.filter(r=>r.type==='PlayersLeavingEval'))for(const d of array(e.v.DraftClass)){
  const p=resolve(d.v.Player),round=d.v.ProjectRound;
  if(d.type==='LeavingPlayer'&&p?.type==='Player'&&Number.isInteger(round)&&round>=1&&round<=7&&d.v.LeaveType==='EarlyNFL_'+round)draftResults.push({player:p.key,round,leavingKey:d.key});
 }
 let userTeamIndex=null;
 for(const u of all.filter(r=>r.type==='FranchiseUser'&&!r.v.IsRetired)){
  const t=resolve(u.v.Team)??resolve(u.v.UserEntity);if(t?.type==='Team'&&byTeam.has(t.v.TeamIndex)&&(userTeamIndex===null||u.v.AdminLevel==='Owner'))userTeamIndex=t.v.TeamIndex;
 }
 // Keep identity validation consistent with the captured native LeagueID.
 const leagueId=all.find(r=>r.type==='Franchise')?.v.LeagueID??raw.status.league;
 if(!Number.isInteger(leagueId)||(leagueId>>>0)!==(raw.status.league>>>0))throw Error('Conflicting draft LeagueID');
 return {leagueId,season,userTeamIndex,teams,conferences,players,draftResults};
}

export function draftResultsView(s){
 if(s.season?.CurrentWeekType!=='OffSeason'||!Number.isInteger(s.season.CurrentWeek)||s.season.CurrentWeek<2)throw Error('Draft results are not available in this stage');
 const players=new Map(s.players.map(p=>[p.id,p])),teams=new Map(s.teams.filter(t=>t.id>=0&&t.id<255).map(t=>[t.id,t]));
 const actual=new Map();
 for(const d of s.draftResults){
  if(!Number.isInteger(d.round)||d.round<1||d.round>7)throw Error('Invalid actual draft round');
  const previous=actual.get(d.player);if(previous&&previous.round!==d.round)throw Error('Conflicting actual draft rounds');
  actual.set(d.player,d);
 }
 if(actual.size>1024)throw Error('Draft results exceed the bounded view');
 const rows=[...actual.values()].map(d=>{
  const p=players.get(d.player),t=teams.get(p?.team);
  if(!p||!t||!keyPattern.test(p.id)||!text(p.name)||!text(p.position)||!Number.isInteger(p.overall)||p.overall<0||p.overall>100)throw Error('Draft player display data is incomplete');
  if(!keyPattern.test(t.conferenceId)||!text(t.name)||!yearName(p.classYear))throw Error('Draft school/class data is incomplete');
  return {key:p.id,name:text(p.name),position:text(p.position),year:yearName(p.classYear)+(p.redshirt==='Previous'?' (RS)':''),overall:p.overall,team:t.id,school:text(t.name),conference:text(t.conferenceId),round:d.round};
 }).sort((a,b)=>a.round-b.round||a.school.localeCompare(b.school)||a.name.localeCompare(b.name)||a.key.localeCompare(b.key));
 const scopes=[{key:'national',label:'National',teams:[...teams.keys()]}];
 for(const c of [...s.conferences].sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id)))scopes.push({key:'conference:'+c.id,label:text(c.name),teams:c.teams.filter(id=>teams.has(id))});
 for(const t of [...teams.values()].sort((a,b)=>a.name.localeCompare(b.name)||a.id-b.id))scopes.push({key:'team:'+t.id,label:text(t.name),teams:[t.id]});
 const result={format:2,sourceKind:'runtime-draft-view',league:String(Number(s.leagueId)>>>0),season:s.season.CurrentSeasonYear,userTeam:s.userTeamIndex,actualRoundsOnly:true,rows,scopes};
 if(!/^(0|[1-9]\d*)$/.test(result.league)||!Number.isInteger(result.season)||result.season<1800||result.season>3000)throw Error('Invalid draft view identity');
 return result;
}

export async function exportDraftResults(input,output){
 const raw=JSON.parse(await fs.readFile(input,'utf8'));
 const data=draftResultsView(draftSnapshot(raw));await fs.mkdir(path.dirname(output),{recursive:true});
 const pending=output+'.tmp';await fs.writeFile(pending,JSON.stringify(data));await fs.rename(pending,output);
 return {event:'draft_results_ready',league:data.league,season:data.season,players:data.rows.length,scopes:data.scopes.length};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Usage: node export_draft_results.mjs runtime-raw.json draft-view.json');
 console.log(JSON.stringify(await exportDraftResults(input,output)));
}
