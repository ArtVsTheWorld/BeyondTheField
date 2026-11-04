import test from 'node:test';import assert from 'node:assert/strict';
import {chooseTemplate,templateHistory,contentPack} from '../Tools/story_templates.mjs';

test('lazy selection matches exhaustive rendering through missing slots, byte limits, duplicate bodies and cooldown',()=>{
 const family='test.lazy-equivalence',old=contentPack.families[family];
 contentPack.families[family]=[
  {id:'long',body:'x'.repeat(281),style:'measured'},{id:'bytes',body:'界'.repeat(200)},
  {id:'missing',body:'{unavailable}'},{id:'a',body:'{school} is ready.',style:'measured'},
  {id:'b',body:'Ready for {school}.',style:'conversational'},{id:'c',body:'{school} is ready.',style:'expressive'},
  {id:'d',body:'A new year for {school}.',style:'measured'}];
 try{for(let i=0;i<120;i++){
  const history=[{week:1,stories:[{handle:'@a',templateId:i%2?'a':'b'}]}],opts={week:2,history,handle:'@a',style:['measured','conversational',null][i%3],avoidBodies:new Set(i%2?['Harbor is ready.']:['Ready for Harbor.']),transformBody:t=>t};
  const eager=chooseTemplate(family,{school:'Harbor'},String(i),{...opts,onCandidates:()=>{}}),lazy=chooseTemplate(family,{school:'Harbor'},String(i),{...opts,usage:templateHistory(history,null,2)});assert.deepEqual(lazy,eager);
 }}finally{if(old)contentPack.families[family]=old;else delete contentPack.families[family];}
});
test('normal selection avoids formatting unused candidates',()=>{
 const family='test.lazy-transform',old=contentPack.families[family];contentPack.families[family]=Array.from({length:20},(_,i)=>({id:'lazy-'+i,body:'{school}, version '+i+'.'}));
 try{let lazy=0,eager=0;const a=chooseTemplate(family,{school:'Harbor'},'same',{transformBody:t=>(lazy++,t)}),b=chooseTemplate(family,{school:'Harbor'},'same',{transformBody:t=>(eager++,t),onCandidates:()=>{}});assert.deepEqual(a,b);assert.equal(lazy,1);assert.equal(eager,20);
 }finally{if(old)contentPack.families[family]=old;else delete contentPack.families[family];}
});
test('Air Force team index zero does not make its history global to other users',()=>{
 const publication={leagueId:4,userTeamIndex:63,season:2028,phase:'RegularSeason',week:2},history=[{...publication,userTeamIndex:0,week:1,stories:[{handle:'@test',templateId:'foreign'}]}];
 assert.equal(templateHistory(history,publication,2).byHandle.has('@test'),false);
 assert.equal(templateHistory(history,{...publication,userTeamIndex:0},2).byHandle.get('@test').has('foreign'),true);
});

test('compact copy is a fallback until richer copy has been used recently',()=>{
 const family='test.compact';contentPack.families[family]=[{id:'detail',body:'{school} wins 31-24 over Harbor.'},{id:'compact',body:'A {school} win.',fallback:true}];
 try{for(let i=0;i<20;i++)assert.equal(chooseTemplate(family,{school:'ULM'},String(i)).templateId,'detail');
 assert.equal(chooseTemplate(family,{school:'ULM'},'s',{handle:'@a',week:2,history:[{week:1,stories:[{handle:'@a',templateId:'detail'}]}]}).templateId,'compact');
 }finally{delete contentPack.families[family];}
});

test('every configured story family has at least eight distinct authored choices',()=>{
 for(const [family,lines] of Object.entries(contentPack.families))assert.ok(new Set(lines.map(t=>t.body)).size>=8,family);
 assert.ok(new Set(Object.values(contentPack.families).flat().map(t=>t.body)).size>=5000);
});
test('a prospect watch with an explicit national rank does not repeat the same rank detail',async()=>{
 const {recruitRankDetail}=await import('../Tools/recruit_ranks.mjs');assert.equal(recruitRankDetail({nationalRecruitRank:1},'r',{excludeNational:true}),'');
 assert.match(recruitRankDetail({nationalRecruitRank:1,stateRecruitRank:2,recruitState:'Florida'},'r',{excludeNational:true}),/No. 2 in Florida/);
});
