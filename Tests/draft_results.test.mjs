import assert from 'node:assert/strict';
import {draftSnapshot,draftResultsView,exportDraftResults} from '../Tools/export_draft_results.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';

function capture(){
 const records={},add=(key,type,v,capacity=300)=>records[key]={key,type,v,capacity};
 add('1:0','Team',{TeamIndex:1,DisplayName:'Custom U',LongName:'Custom University'});
 add('1:1','Team',{TeamIndex:2,DisplayName:'State'});
 add('2:0','Conference',{Name:'Custom Conference',ConferenceEnum:'Custom',TeamSlots:'3:0',Divisions:null});
 add('2:1','Conference',{Name:'Another Conference',ConferenceEnum:'Other',TeamSlots:null,Divisions:'4:0'});
 add('3:0','Team[]',{Member0:'1:0'});add('3:1','Team[]',{Member0:'1:1'});
 add('4:0','Division[]',{Member0:'5:0'});add('5:0','Division',{Teams:'3:1'});
 add('6:0','FranchiseUser',{IsRetired:false,AdminLevel:'Owner',Team:'1:0',UserEntity:null});
 add('7:0','FranchiseServer_CareerFlow',{IsStageActive:true,IsStageAdvancing:false});
 add('7:1','Franchise',{LeagueID:-12345});
 const draft={};
 for(let i=0;i<224;i++){
  add('8:'+i,'Player',{FirstName:'Player',LastName:String(i),TeamIndex:i%2+1,Position:['QB','WR','CB','LT','DT','HB'][i%6],OverallRating:74+i%26,SchoolYear:'Senior',RedshirtStatus:i%3===0?'Previous':'Never'});
  const round=Math.floor(i/32)+1;add('9:'+i,'LeavingPlayer',{Player:'8:'+i,ProjectRound:round,LeaveType:'EarlyNFL_'+round});draft['Member'+i]='9:'+i;
 }
 add('10:0','LeavingPlayer[]',draft);add('11:0','PlayersLeavingEval',{DraftClass:'10:0'});
 return {format:1,sourceKind:'runtime',status:{league:-12345,season:{CurrentStage:'OffSeason',CurrentWeekType:'OffSeason',CurrentWeek:2,CurrentSeasonYear:2028}},records};
}
const raw=capture(),before=JSON.stringify(raw),s=draftSnapshot(raw),view=draftResultsView(s);
assert.equal(s.leagueId,-12345,'Captured Dynasty identity changed');
assert.equal(view.rows.length,224);assert.equal(view.league,String(-12345>>>0));assert.equal(view.userTeam,1);
assert.equal(view.format,2);assert.equal(view.actualRoundsOnly,true);
const actual=new Map(s.draftResults.map(r=>[r.player,r.round]));
for(const row of view.rows){
 assert.equal(row.round,actual.get(row.key),'Actual native round changed');
 assert.ok(!('pick' in row)&&!('roundPick' in row)&&!('nflTeam' in row),'Modeled draft details leaked into the native table view');
 const player=s.players.find(p=>p.id===row.key);assert.equal(row.overall,player.overall);
 assert.equal(row.year,player.redshirt==='Previous'?'SR (RS)':'SR');
}
for(let i=1;i<view.rows.length;i++)assert.ok(view.rows[i-1].round<=view.rows[i].round,'Actual round order changed');
assert.deepEqual(view.scopes.map(s=>s.label),['National','Another Conference','Custom Conference','Custom U','State']);
assert.equal(view.rows.filter(r=>r.conference==='2:0').length,112);
assert.equal(view.rows.filter(r=>r.team===1).length,112);
assert.equal(JSON.stringify(raw),before,'Capture was mutated');
const missing=capture();delete missing.records['9:0'];assert.throws(()=>draftSnapshot(missing),/Unresolved/);
const partial=capture();partial.records['10:0'].v.Member0=null;assert.equal(draftResultsView(draftSnapshot(partial)).rows.length,223,'Actual class was forced to 224 picks');
const empty=capture();empty.records['10:0'].v={};assert.equal(draftResultsView(draftSnapshot(empty)).rows.length,0);
const duplicate=draftSnapshot(capture());duplicate.draftResults.push({...duplicate.draftResults[0]});assert.equal(draftResultsView(duplicate).rows.length,224);
duplicate.draftResults.at(-1).round=7;assert.throws(()=>draftResultsView(duplicate),/Conflicting actual draft/);
const advancing=capture();advancing.records['7:0'].v.IsStageAdvancing=true;assert.throws(()=>draftSnapshot(advancing),/inactive or advancing/);
const earlier=draftSnapshot(capture());earlier.season.CurrentWeek=1;assert.throws(()=>draftResultsView(earlier),/not available/);
earlier.season.CurrentWeek=2;earlier.season.CurrentWeekType='RegularSeason';assert.throws(()=>draftResultsView(earlier),/not available/);
const collision=capture();collision.records['2:1'].v.TeamSlots='3:0';assert.throws(()=>draftSnapshot(collision),/Conflicting/);
const folder=await fs.mkdtemp(path.join(os.tmpdir(),'dynasty-draft-view-'));
try{
 const input=path.join(folder,'capture.json'),output=path.join(folder,'view.json');
 await fs.writeFile(input,JSON.stringify({...raw,priorDraftBoard:[{pick:1,nflTeam:'Ignored fictional destination'}]}));
 const report=await exportDraftResults(input,output);assert.equal(report.players,224);
 assert.deepEqual(JSON.parse(await fs.readFile(output,'utf8')),view,'Export depended on a modeled board or history');
 assert.equal(await fs.readFile(input,'utf8'),JSON.stringify({...raw,priorDraftBoard:[{pick:1,nflTeam:'Ignored fictional destination'}]}),'Input capture changed');
}finally{
 const actual=await fs.realpath(folder),temporary=await fs.realpath(os.tmpdir());
 assert.equal(path.dirname(actual),temporary);assert.ok(path.basename(actual).startsWith('dynasty-draft-view-'));
 await fs.rm(actual,{recursive:true,force:true});
}
console.log('Draft view: actual rounds only, National/conference/team scopes, class sizes, identity and failure guards pass; no modeled pick/team or archive dependency');
