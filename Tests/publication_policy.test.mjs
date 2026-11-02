import test from 'node:test';
import assert from 'node:assert/strict';
import {publishOffer,currentPublicationPolicy} from '../Tools/publication_policy.mjs';
import {buildFeed} from '../Tools/feed_engine.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {resumeEdition} from '../Tools/runtime_archive.mjs';
const fixture=()=>({format:2,gameYear:27,sourceKind:'runtime',source:'runtime:10:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:10,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentWeek:1,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},teams:[{id:1,name:'Home',logo:1},{id:2,name:'Away',logo:2}],players:[],games:[],performances:[],heisman:[],offers:[],commitments:[],conferences:[]});
test('offer publication is approximately 20 percent, stable on refresh/rename and independent of the user team',()=>{
 const s=fixture(),events=Array.from({length:10000},(_,i)=>({id:`offer:${i%2+1}:recruit${i}`}));const admitted=events.filter(e=>publishOffer(s,e)).map(e=>e.id);assert.ok(admitted.length>=1800&&admitted.length<=2200,admitted.length);
 s.userTeamIndex=2;s.saveName='Renamed manual save';s.sha256='b'.repeat(64);assert.deepEqual(events.filter(e=>publishOffer(s,e)).map(e=>e.id),admitted);
 for(const team of [1,2]){const count=admitted.filter(id=>id.startsWith('offer:'+team+':')).length;assert.ok(count>=850&&count<=1150,count);}
});
test('unpublished offers remain observed events but have no standalone or orphan reply posts',()=>{
 const s=fixture();for(let n=0;n<1000;n++){const id='recruit'+n;s.players.push({id,name:'Recruit '+n,team:255,position:'WR',personality:'Neutral',injury:'Uninjured'});s.newOffers??=[];s.newOffers.push({player:id,team:n%2+1,rank:n+1});}
 const f=buildFeed(s),roots=f.stories.filter(p=>p.category==='offers'&&!p.replyTo);assert.equal(f.events.filter(e=>e.category==='offers').length,1000);assert.ok(roots.length>=160&&roots.length<=240,roots.length);const ids=new Set(f.stories.map(p=>p.id));assert.ok(f.stories.every(p=>!p.replyTo||ids.has(p.replyTo)));
 const repeated=buildFeed(s);assert.deepEqual(repeated.stories,f.stories);
});
test('the publication-policy change invalidates legacy offer caches without rerolling other active-week wording',()=>{
 const s=fixture();Object.assign(s.teams[0],{mediaRank:8,mediaLastRank:10});const a=updateRuntime(structuredClone(s)),legacy=structuredClone(a.state);assert.ok(a.catalog.stories.length);delete legacy.editions[0].feed.publicationPolicyVersion;assert.ok(resumeEdition(s,legacy));legacy.editions[0].feed.events.push({category:'offers'});assert.equal(resumeEdition(s,legacy),null);assert.equal(currentPublicationPolicy(legacy.editions[0].feed),false);
 s.players=[{id:'prospect',name:'Jay Moss',team:255,position:'WR',personality:'Neutral'}];s.offers=[{player:'prospect',team:1}];s.commitments=[{player:'prospect',team:1,rank:1,stage:'HardCommitted',week:1}];const b=updateRuntime(s,legacy);assert.ok(b.catalog.stories.some(p=>p.category==='recruiting'));for(const p of a.catalog.stories.filter(p=>!p.replyTo)){const next=b.catalog.stories.find(q=>q.id===p.id);assert.equal(next?.body,p.body);assert.equal(next?.likes,p.likes);}
});
