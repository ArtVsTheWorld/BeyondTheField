import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {updateRuntime,scopeKey} from '../Tools/runtime_lifecycle.mjs';
import {resumeEdition,loadArchives,readHistory,atomicJson,writeHistory} from '../Tools/runtime_archive.mjs';
function fixture(){return {format:2,gameYear:27,sourceKind:'runtime',source:'runtime:1:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:1,userTeamIndex:1,season:{CurrentSeasonYear:2026,CurrentYear:0,CurrentWeek:0,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},teams:[{id:1,name:'Home',logo:11,mediaRank:6,mediaLastRank:8}],players:[],games:[],performances:[],offers:[],commitments:[],heisman:[],conferences:[]};}
test('unchanged native facts resume exact posts and likes after a reload or save-name change without rewriting history',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s)),before=JSON.stringify(a.state);s.saveName='Different manual save';const feed=resumeEdition(s,a.state);assert.ok(feed);assert.deepEqual(feed.stories,a.catalog.stories);assert.deepEqual(feed.views,a.catalog.views);assert.equal(JSON.stringify(a.state),before);
});
test('a changed fact hash, identity, week, phase, revision or rewind never restores a stale cache',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s));for(const change of [x=>x.sha256='b'.repeat(64),x=>x.leagueId=2,x=>x.userTeamIndex=2,x=>x.season.CurrentWeek=1,x=>x.season.CurrentWeekType='PreSeason',x=>x.season.CurrentSeasonYear=2027]){const next=structuredClone(s);change(next);assert.equal(resumeEdition(next,a.state),null);}
 const old=structuredClone(a.state);old.editions[0].feed.contentRevision='old wording';assert.equal(resumeEdition(s,old),null);
 const rewind=structuredClone(a.state);rewind.editions.push({...rewind.editions[0],week:1});assert.equal(resumeEdition(s,rewind),null);assert.equal(resumeEdition(s,null),null);
});
test('disk archives expose stored preseason text in regular Week 0 and never borrow another league, year or future phase',async t=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'dynasty-archive-'));assert.equal(path.dirname(folder),path.resolve(os.tmpdir()));t.after(()=>fs.rm(folder,{recursive:true,force:true}));
 const s=fixture(),p=structuredClone(s);p.season.CurrentWeekType='PreSeason';p.season.CurrentStage='PreSeason';const pre=updateRuntime(p);pre.state.editions[0].feed.stories[0].body='Frozen preseason wording';
 const file=path.join(folder,'RuntimeHistory',scopeKey(p),'history.json');await fs.mkdir(path.dirname(file),{recursive:true});await atomicJson(file,pre.state);
 const future=path.join(folder,'RuntimeHistory','1','1','2026','BowlSeason1','history.json');await fs.mkdir(path.dirname(future),{recursive:true});await fs.writeFile(future,'unread future file');
 const archived=await loadArchives(folder,s),current=updateRuntime(structuredClone(s),undefined,{archives:archived});assert.deepEqual(current.catalog.weeks.map(w=>w.phase),['PreSeason','RegularSeason']);assert.equal(current.catalog.weeks[0].stories[0].body,'Frozen preseason wording');assert.equal(current.state.editions.length,1);
 assert.deepEqual((await loadArchives(folder,p)),[]);for(const changed of [{...s,leagueId:2},{...s,season:{...s.season,CurrentSeasonYear:2027}}])assert.deepEqual(await loadArchives(folder,changed),[]);
 assert.equal((await readHistory(file)).editions[0].feed.stories[0].body,'Frozen preseason wording');assert.equal(await readHistory(path.join(folder,'missing.json')),null);
 const resumed=resumeEdition(s,current.state,archived);assert.equal(resumed.weeks[0].stories[0].body,'Frozen preseason wording');assert.equal(resumed.activeWeekKey,current.catalog.key);
});

test('indexed history preserves legacy bytes, all editions and exact reload output while loading only needed snapshots',async t=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'dynasty-index-'));assert.equal(path.dirname(folder),path.resolve(os.tmpdir()));t.after(()=>fs.rm(folder,{recursive:true,force:true}));
 const file=path.join(folder,'history.json'),s=fixture();let result;
 for(let week=0;week<5;week++){s.season.CurrentWeek=week;s.sha256=String(week).repeat(64);result=updateRuntime(structuredClone(s),result?.state);}
 await atomicJson(file,result.state);const legacy=await fs.readFile(file);
 await writeHistory(file,result.state);assert.deepEqual(await fs.readFile(file),legacy);
 const full=await readHistory(file);assert.deepEqual(JSON.parse(JSON.stringify(full)),JSON.parse(JSON.stringify(result.state)));
 const partial=await readHistory(file,{activeWeek:4});assert.ok(partial.editions[4].snapshot.players);assert.ok(partial.editions[3].snapshot.players);assert.equal(partial.editions[0].snapshot.players,undefined);
 assert.deepEqual(JSON.parse(JSON.stringify(resumeEdition(s,partial).weeks)),JSON.parse(JSON.stringify(result.catalog.weeks)));
 const before=JSON.parse(await fs.readFile(path.join(folder,'history.index.json'),'utf8'));
 s.season.CurrentWeek=5;s.sha256='f'.repeat(64);const next=updateRuntime(structuredClone(s),partial);await writeHistory(file,next.state);
 const after=JSON.parse(await fs.readFile(path.join(folder,'history.index.json'),'utf8'));
 for(let i=0;i<5;i++){assert.equal(after.editions[i].snapshotFile,before.editions[i].snapshotFile);assert.equal(after.editions[i].feedFile,before.editions[i].feedFile);}
 assert.deepEqual((await readHistory(file)).editions[0].snapshot,JSON.parse(JSON.stringify(result.state.editions[0].snapshot)));
 assert.deepEqual(await fs.readFile(file),legacy);
 const rewind=structuredClone(s);rewind.season.CurrentWeek=2;rewind.sha256='2'.repeat(64);const pruned=updateRuntime(rewind,await readHistory(file,{activeWeek:2}));await writeHistory(file,pruned.state);
 assert.deepEqual((await readHistory(file)).editions.map(e=>e.week),[0,1,2]);assert.deepEqual(await fs.readFile(file),legacy);
});

test('archive-only indexed reads retain cross-phase milestone and postseason baselines',async t=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'dynasty-carry-index-'));assert.equal(path.dirname(folder),path.resolve(os.tmpdir()));t.after(()=>fs.rm(folder,{recursive:true,force:true}));
 const s=fixture();s.season.CurrentWeekType='PreSeason';s.season.CurrentStage='PreSeason';const result=updateRuntime(s);const e=result.state.editions[0];e.snapshot.milestoneTotals={version:1,year:2026,teams:{1:{wins:22}}};e.snapshot.postseasonPublications={invite:'sent'};
 const file=path.join(folder,'RuntimeHistory',scopeKey(s),'history.json');await writeHistory(file,result.state);
 const regular=fixture(),old=await loadArchives(folder,regular);assert.equal(old.length,1);assert.deepEqual(old[0].milestoneObservation,e.snapshot.milestoneTotals);assert.deepEqual(old[0].postseasonPublications,e.snapshot.postseasonPublications);
});

test('index corruption and foreign paths fail closed instead of reverting to a stale legacy archive',async t=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'dynasty-corrupt-index-'));assert.equal(path.dirname(folder),path.resolve(os.tmpdir()));t.after(()=>fs.rm(folder,{recursive:true,force:true}));
 const file=path.join(folder,'history.json'),result=updateRuntime(fixture());await atomicJson(file,result.state);await writeHistory(file,result.state);
 const indexFile=path.join(folder,'history.index.json'),index=JSON.parse(await fs.readFile(indexFile,'utf8')),blob=path.join(folder,'.history-data',index.editions[0].feedFile);
 await fs.appendFile(blob,' ');await assert.rejects(readHistory(file),/checksum/);
 index.editions[0].feedFile='../history.json';await atomicJson(indexFile,index);await assert.rejects(readHistory(file),/reference/);
});
