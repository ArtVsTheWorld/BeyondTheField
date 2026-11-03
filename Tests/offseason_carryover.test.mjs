import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {observeOffseason,offseasonStage} from '../Tools/offseason_ledger.mjs';
import {offseasonCarryEvents} from '../Tools/offseason_carry_events.mjs';
import {offseasonLedgerFile,readOffseasonLedger} from '../Tools/offseason_ledger_store.mjs';
import {atomicJson} from '../Tools/runtime_archive.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {trainingArea} from '../Tools/training_profile.mjs';
function fixture(){
 const s={format:2,gameYear:27,sourceKind:'runtime',source:'runtime:19:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:19,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentStage:'OffSeason',CurrentWeekType:'OffSeason',CurrentWeek:6,RegularSeasonWeekConferenceChampionship:15},teams:[],players:[],games:[],performances:[],heisman:[],conferences:[],offers:[],commitments:[],signings:[],recruitStatuses:[],portalEntrants:[],draftResults:[]};
 for(let id=1;id<=3;id++)s.teams.push({id,name:'School '+id,nickname:'Club '+id,logo:id,mediaRank:id===1?6:40,brandExposure:'B',rivals:[],prestigeStars:3,depthChart:{},headCoach:{name:'Coach '+id},conferenceId:'c'+id,conferenceCode:'C'+id,conferenceName:'League '+id});
 for(let id=1;id<=4;id++)s.players.push({id:'p'+id,name:'First Family'+id,firstName:'First',team:id===4?2:1,position:id===1?'QB':'WR',overall:80,personality:'Leader',classYear:'Junior',nil:0,injury:'Uninjured',seasonStats:[],allSeasonStats:[],presentationId:100+id,trainingAttributes:{SpeedRating:80,AccelerationRating:80,ThrowAccuracyShortRating:80,ThrowAccuracyMidRating:80,CatchingRating:80}});
 return s;
}
function preseason(s){s.season={...s.season,CurrentYear:1,CurrentSeasonYear:2027,CurrentWeek:0,CurrentStage:'PreSeason',CurrentWeekType:'PreSeason'};s.offseasonStageLabel=null;return s;}
function grow(s){s.players[0].trainingAttributes.ThrowAccuracyShortRating+=5;s.players[1].trainingAttributes.CatchingRating+=5;}
function trained(){const s=fixture(),a=observeOffseason(s);s.season.CurrentWeek=7;grow(s);return {s,ledger:observeOffseason(s,a.ledger).ledger};}
test('verified calendar recognizes hidden stages without requiring a menu',()=>{
 const s=fixture();assert.equal(offseasonStage(s),'before-training');s.season.CurrentWeek=7;assert.equal(offseasonStage(s),'training');s.season.CurrentWeek=8;assert.equal(offseasonStage(s),'encourage');s.season.CurrentWeek=99;s.offseasonStageLabel='Training Results';assert.equal(offseasonStage(s),'training');preseason(s);assert.equal(offseasonStage(s),null);
});
test('full cycle publishes captured development, roster review and realignment in next preseason only',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;let a=observeOffseason(s,ledger);assert.equal(a.facts.length,0);s.players[2].team=255;s.teams[0].conferenceId='c2';s.teams[0].conferenceCode='C2';s.teams[0].conferenceName='League 2';a=observeOffseason(s,a.ledger);assert.equal(a.facts.length,0);
 const b=observeOffseason(preseason(s),a.ledger);assert.equal(b.facts.filter(f=>f.kind==='training').length,2);assert.equal(b.facts.filter(f=>f.kind==='departure').length,1);assert.equal(b.facts.filter(f=>f.kind==='realignment').length,1);assert.ok(b.facts.every(f=>f.sourceYear===2026&&f.targetYear===2027));assert.equal(b.facts.find(f=>f.kind==='departure').evidence,'observed-encourage');
});
test('ledger reload and repeated preseason observation preserve facts and publication wording',()=>{
 const {s,ledger}=trained();preseason(s);const a=observeOffseason(s,JSON.parse(JSON.stringify(ledger))),b=observeOffseason(s,a.ledger);assert.deepEqual(b,a);s.offseasonCarry=a.facts;const x=updateRuntime(structuredClone(s)),y=updateRuntime(structuredClone(s),x.state);assert.deepEqual(x.catalog,y.catalog);assert.ok(x.catalog.stories.some(p=>p.templateId.startsWith('carry.training')));assert.ok(x.catalog.stories.filter(p=>p.templateId.startsWith('carry.')).every(p=>!/[{}]|Rating|OVR|overall/i.test(p.body)&&p.body.length<=280));
});
test('observer does not mutate native snapshot or prior ledger',()=>{
 const {s,ledger}=trained(),before=structuredClone({s,ledger});observeOffseason(preseason(structuredClone(s)),ledger);assert.deepEqual({s,ledger},before);
});
test('position-relevant private gains qualify, unrelated kicker gains for QB do not',()=>{
 const s=fixture(),a=observeOffseason(s);s.season.CurrentWeek=7;s.players[0].trainingAttributes.KickAccuracyRating=99;s.players[1].trainingAttributes.SpeedRating+=3;s.players[1].trainingAttributes.AccelerationRating+=3;const b=observeOffseason(s,a.ledger),f=observeOffseason(preseason(s),b.ledger).facts;assert.equal(f.length,1);assert.equal(f[0].player,'p2');assert.equal(trainingArea('WR',f[0].gains),'his burst and movement');
});
test('recycled player slots, changed identities, position switches and new teams cannot invent training gains',()=>{
 for(const change of [s=>s.players[0].name='Another Person',s=>s.players[0].presentationId=999,s=>s.players[0].position='WR',s=>s.players[0].team=2]){
  const s=fixture(),a=observeOffseason(s);s.season.CurrentWeek=7;grow(s);change(s);const b=observeOffseason(s,a.ledger);assert.ok(!observeOffseason(preseason(s),b.ledger).facts.some(f=>f.kind==='training'&&f.player==='p1'));
 }
});
test('singleton template records never become roster or development stories',()=>{
 const s=fixture();s.players[0].rosterEligible=false;const a=observeOffseason(s);s.season.CurrentWeek=7;grow(s);const b=observeOffseason(s,a.ledger);assert.ok(!observeOffseason(preseason(s),b.ledger).facts.some(f=>f.player==='p1'));
});
test('cold load at Training Results does not invent a before-training baseline',()=>{
 const s=fixture();s.season.CurrentWeek=7;grow(s);const a=observeOffseason(s);assert.equal(observeOffseason(preseason(s),a.ledger).facts.length,0);
});
test('skipped training stage uses broad offseason attribution instead of claiming precise timing',()=>{
 const s=fixture(),a=observeOffseason(s);grow(s);const b=observeOffseason(preseason(s),a.ledger);assert.ok(b.facts.some(f=>f.kind==='training'));assert.ok(b.facts.every(f=>f.evidence==='offseason-period'));s.offseasonCarry=b.facts;assert.ok(offseasonCarryEvents(s).filter(e=>e.facts.family==='carry.training').every(e=>e.facts.period==='the offseason'));
});
test('missing player records alone cannot prove an encouraged transfer',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;s.players=s.players.filter(p=>p.id!=='p3');const a=observeOffseason(s,ledger),b=observeOffseason(preseason(s),a.ledger);assert.ok(!b.facts.some(f=>f.kind==='departure'));
});
test('graduation and known draft exits are excluded from encourage-transfer carryover',()=>{
 const {s,ledger}=trained();s.players[1].classYear='Senior';ledger.cycles[2026].beforeRoster.find(p=>p.id==='p2').classYear='Senior';s.season.CurrentWeek=8;s.players[1].team=255;s.players[2].team=255;const history=[{season:2026,phase:'OffSeason',week:2,events:[{category:'draft',playerId:'p3',facts:{playerName:s.players[2].name}}]}];const a=observeOffseason(s,ledger,{history}),b=observeOffseason(preseason(s),a.ledger);assert.ok(!b.facts.some(f=>f.kind==='departure'));
});
test('a senior actually removed during the observed roster-review stage can be reported',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;s.players[2].classYear='Senior';ledger.cycles[2026].beforeRoster.find(p=>p.id==='p3').classYear='Senior';let a=observeOffseason(s,ledger);s.players[2].team=255;a=observeOffseason(s,a.ledger);assert.ok(observeOffseason(preseason(s),a.ledger).facts.some(f=>f.kind==='departure'&&f.player==='p3'));
});
test('deletion observed within Encourage Transfers is a roster departure, deletion only at rollover is not',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;let a=observeOffseason(s,ledger);s.players=s.players.filter(p=>p.id!=='p3');a=observeOffseason(s,a.ledger);assert.ok(observeOffseason(preseason(s),a.ledger).facts.some(f=>f.kind==='departure'&&f.player==='p3'));
 const other=trained();other.s.season.CurrentWeek=8;let b=observeOffseason(other.s,other.ledger);other.s.players=other.s.players.filter(p=>p.id!=='p3');b=observeOffseason(preseason(other.s),b.ledger);assert.ok(!b.facts.some(f=>f.kind==='departure'));
});
test('a senior present at Encourage Transfers but graduating at rollover is not called a roster-review departure',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;s.players[2].classYear='Senior';ledger.cycles[2026].beforeRoster.find(p=>p.id==='p3').classYear='Senior';const a=observeOffseason(s,ledger);s.players[2].team=255;assert.ok(!observeOffseason(preseason(s),a.ledger).facts.some(f=>f.kind==='departure'&&f.player==='p3'));
});
test('different departures from one team receive distinct event identifiers',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;let a=observeOffseason(s,ledger);s.players[1].team=255;s.players[2].team=255;a=observeOffseason(s,a.ledger);const facts=observeOffseason(preseason(s),a.ledger).facts.filter(f=>f.kind==='departure');assert.equal(facts.length,2);assert.equal(new Set(facts.map(f=>f.id)).size,2);
});
test('verified departure persists through record deletion, but a restored roster removes it',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;let a=observeOffseason(s,ledger);s.players[2].team=255;a=observeOffseason(s,a.ledger);const restored=structuredClone(s);restored.players[2].team=1;assert.equal(Object.keys(observeOffseason(restored,a.ledger).ledger.cycles[2026].departures).length,0);s.players=s.players.filter(p=>p.id!=='p3');assert.ok(observeOffseason(preseason(s),a.ledger).facts.some(f=>f.kind==='departure'&&f.player==='p3'));
});
test('departure wording uses only verified portal status or destination and never assigns coach intent',()=>{
 for(const kind of ['unassigned','portal','destination']){
  const {s,ledger}=trained();s.season.CurrentWeek=8;let a=observeOffseason(s,ledger);s.players[2].team=kind==='destination'?2:255;if(kind==='portal')s.portalEntrants=['p3'];a=observeOffseason(s,a.ledger);const b=observeOffseason(preseason(s),a.ledger);s.offseasonCarry=b.facts;const e=offseasonCarryEvents(s).find(e=>e.facts.carryoverKind==='departure');assert.equal(e.facts.family,'carry.departure'+(kind==='unassigned'?'':'-'+kind));assert.ok(!/cut|forced|kicked/i.test(e.facts.period));
 }
});
test('rewinding to signing day removes future development, departures and conference moves',()=>{
 const {s,ledger}=trained();s.season.CurrentWeek=8;s.players[2].team=255;let a=observeOffseason(s,ledger);s.season.CurrentWeek=6;s.players=fixture().players;s.teams=fixture().teams;a=observeOffseason(s,a.ledger);const b=observeOffseason(preseason(s),a.ledger);assert.equal(b.facts.length,0);
});
test('restoring the prior regular season prunes that season future ledger',()=>{
 const {s,ledger}=trained();s.season.CurrentWeekType='RegularSeason';s.season.CurrentStage='NFLSeason';const a=observeOffseason(s,ledger);assert.equal(a.ledger.cycles[2026],undefined);assert.equal(observeOffseason(preseason(s),a.ledger).facts.length,0);
});
test('conference rename is grouped once and case-only names are ignored',()=>{
 const s=fixture();s.teams[1].conferenceId='c1';s.teams[1].conferenceCode='C1';s.teams[1].conferenceName='League 1';const a=observeOffseason(s);s.teams[0].conferenceName=s.teams[1].conferenceName='New League';s.teams[2].conferenceName=' LEAGUE 3 ';const b=observeOffseason(preseason(s),a.ledger);assert.equal(b.facts.length,1);assert.equal(b.facts[0].kind,'rename');assert.deepEqual(b.facts[0].teams,[1,2]);
});
test('team record replacement cannot masquerade as a conference move',()=>{
 const s=fixture(),a=observeOffseason(s);s.teams[0].name='New TeamBuilder';s.teams[0].conferenceId='other';s.teams[0].conferenceCode='Other';s.teams[0].conferenceName='New League';assert.equal(observeOffseason(preseason(s),a.ledger).facts.length,0);
});
test('cold preseason recovers unique prior-year conference context without inventing training or departures',()=>{
 const s=preseason(fixture());s.teams[0].seasonHistory=[{Year:2026,ConferenceName:'Old League'},{Year:2025,ConferenceName:'Older'}];s.teams[1].seasonHistory=[{Year:2026,ConferenceName:'Ambiguous A'},{Year:2026,ConferenceName:'Ambiguous B'}];s.teams[2].seasonHistory=[{Year:2025,ConferenceName:'Old'}];const a=observeOffseason(s);assert.equal(a.facts.length,1);assert.equal(a.facts[0].kind,'alignment-history');assert.equal(a.facts[0].oldConference,'Old League');
});
test('late cold start in Encourage Transfers retains history fallback without duplicating observed movement',()=>{
 const s=fixture();s.season.CurrentWeek=8;s.teams[0].seasonHistory=[{Year:2026,ConferenceName:'Prior League'}];const a=observeOffseason(s);s.teams[0].conferenceName='New League';s.teams[0].conferenceId='new';s.teams[0].conferenceCode='NEW';const b=observeOffseason(preseason(s),a.ledger);assert.equal(b.facts.length,1);assert.equal(b.facts[0].kind,'realignment');
});
test('ledger isolates leagues and user teams, rejects bad identity and never observes reconstructed editions',()=>{
 const {s,ledger}=trained();assert.throws(()=>observeOffseason({...s,leagueId:20},ledger),/mismatch/);assert.throws(()=>observeOffseason({...s,userTeamIndex:2},ledger),/mismatch/);assert.throws(()=>observeOffseason({...s,leagueId:null}),/identity/);const a=observeOffseason({...preseason(s),reconstructed:true},ledger);assert.equal(a.facts.length,0);assert.deepEqual(a.ledger,ledger);
});
test('cross-year file path is independent of manual-save names and year, and JSON persists atomically',async()=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'dynasty-carry-'));try{
  const {s,ledger}=trained(),file=offseasonLedgerFile(folder,s);s.source='another-manual-save';preseason(s);assert.equal(offseasonLedgerFile(folder,s),file);assert.notEqual(offseasonLedgerFile(folder,{...s,userTeamIndex:2}),file);assert.equal(await readOffseasonLedger(file),null);await fs.mkdir(path.dirname(file),{recursive:true});await atomicJson(file,ledger);assert.deepEqual(await readOffseasonLedger(file),ledger);assert.equal((await fs.readdir(path.dirname(file))).length,1);
 }finally{await fs.rm(folder,{recursive:true,force:true});}
});
