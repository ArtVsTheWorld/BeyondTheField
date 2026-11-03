import test from 'node:test';
import assert from 'node:assert/strict';
import {canonicalTopic,deduplicateConversations} from '../Tools/conversation_topics.mjs';
import {curate,publishWeek} from '../Tools/feed_selection.mjs';
const post=(id,category='analytics',scope='team')=>({id,category,scopes:[scope],priority:90,thread:id,handle:'@'+id,voice:'beat',body:'Distinct story '+id,curated:true,teamIds:[1]});
test('routine recruiting shares a seven-post regular-season allowance, including attached reactions',()=>{
 const pool=Array.from({length:40},(_,i)=>post('r'+i,i%3===0?'signings':i%3===1?'recruiting':'offers')),others=Array.from({length:40},(_,i)=>post('n'+i,'analytics','national'));const result=curate([...pool,...others]);assert.equal(result.length,30);assert.ok(result.filter(p=>['signings','recruiting','offers'].includes(p.category)).length<=7);
});
test('major recruiting reports can exceed the routine allowance without hiding dedicated stories',()=>{
 const stories=Array.from({length:12},(_,i)=>({...post('major'+i,'recruiting'),priority:120}));const f=publishWeek({leagueId:1,userTeamIndex:1,season:2027,phase:'RegularSeason',week:5,key:'x',stories});assert.equal(f.views.team.length,12);assert.ok(f.posts.length>7);
});
test('one exact sentence from two accounts is selected once while both remain browsable',()=>{
 const stories=[post('a'),{...post('b'),body:'Distinct story a'}],f=publishWeek({season:2027,phase:'RegularSeason',week:2,key:'x',stories});assert.equal(f.stories.length,2);assert.equal(f.posts.length,1);
});
test('an available local recap, performance and preview precede unrelated recruiting flavor',()=>{
 const locals=['results','player-stats','schedule'].map((c,i)=>({...post('l'+i,c),priority:70})),pool=[...Array.from({length:50},(_,i)=>({...post('r'+i,'recruiting','national'),priority:100})),...locals,...Array.from({length:30},(_,i)=>post('n'+i,'analytics','national'))];const chosen=curate(pool);assert.ok(locals.every(p=>chosen.some(q=>q.id===p.id)));
});
test('portal entry and interest share an open topic; commitment and signature are distinct updates',()=>{
 const e={id:'portal-opening:entrant:p',playerId:'p',facts:{recruitKind:'transfer',school:'Home'}};assert.equal(canonicalTopic(e),canonicalTopic({...e,id:'portal-opening:interest:p'}));assert.notEqual(canonicalTopic(e),canonicalTopic({...e,facts:{...e.facts,newlyObserved:true}}));assert.notEqual(canonicalTopic({...e,facts:{...e.facts,newlyObserved:true}}),canonicalTopic({...e,facts:{...e.facts,signed:true}}));
});
test('one fan reacts once to a portal topic and different fans keep their actual parents',()=>{
 const a={...post('a'),canonicalTopic:'portal:p:open'},b={...post('b'),canonicalTopic:'portal:p:open'},r={...post('r'),voice:'fan',handle:'@fan',replyTo:'a',canonicalTopic:a.canonicalTopic},s={...post('s'),voice:'fan',handle:'@fan',replyTo:'b',canonicalTopic:b.canonicalTopic},t={...post('t'),voice:'fan',handle:'@other',replyTo:'b',canonicalTopic:b.canonicalTopic};const kept=deduplicateConversations([a,b,r,s,t]);assert.ok(!kept.includes(s));assert.ok(kept.includes(r)&&kept.includes(t));assert.equal(t.replyTo,'b');
});
test('removing a duplicate root removes dependent replies, with factual exemptions intact',()=>{
 const a=post('a'),b={...post('b'),body:a.body,handle:a.handle},r={...post('r'),replyTo:'b'};assert.deepEqual(deduplicateConversations([a,b,r]).map(p=>p.id),['a']);assert.equal(deduplicateConversations([a,{...b,coverageExempt:true}]).length,2);
});
