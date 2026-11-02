import test from 'node:test';
import assert from 'node:assert/strict';
import {avatarFor} from '../Tools/story_avatars.mjs';
import {chooseTemplate,contentPack} from '../Tools/story_templates.mjs';
import {curate,scopeViews,conversationOrder} from '../Tools/feed_selection.mjs';
import {renderStories} from '../Tools/story_renderer.mjs';
const root=(id,extra={})=>({id,category:'results',priority:80,thread:id,curated:true,scopes:['team','national'],voice:'beat',handle:'@'+id,...extra});
const fixture=()=>({leagueId:10,userTeamIndex:1,season:{CurrentSeasonYear:2027,CurrentWeek:8,CurrentWeekType:'RegularSeason'},teams:[{id:1,name:'Harbor State',nickname:'Captains',logo:11,hashtags:['#AllAboard']}],players:[{id:'recruit',name:'Evan Mercer',team:255,position:'QB',personality:'Leader',portrait:234},{id:'qb',name:'Caleb Moss',team:1,position:'QB',personality:'Leader',injury:'Uninjured',portrait:146}],games:[]});
test('generated recruits and players use nonblank native portraits without an NIL requirement',()=>{
 for(const role of ['player','recruit'])assert.deepEqual(avatarFor(role,{logo:11},{portrait:146,isNil:false}),{imageLibrary:1,imageValue:146});
 for(const player of [{portrait:0},{portrait:65535},{portrait:146,portraitForcedSilhouette:true}])assert.deepEqual(avatarFor('player',{logo:11},player),{imageLibrary:0,imageValue:11});
 assert.deepEqual(avatarFor('official',{logo:11},{portrait:146}),{imageLibrary:0,imageValue:11});
});
test('cooldowns prefer another phrase for the same author across weeks and freeze same-week wording',()=>{
 const values={nickname:'Captains',hashtag:'#AllAboard'},a=chooseTemplate('fan.win',values,'seed',{handle:'@fan',week:7});
 const history=[{week:7,stories:[{...a,handle:'@fan'}]}],b=chooseTemplate('fan.win',values,'seed',{handle:'@fan',week:8,history});assert.notEqual(a.templateId,b.templateId);assert.equal(b.cooldownFallback,false);
 const frozen={...b,renderKey:'same',contentRevision:contentPack.revision};const c=chooseTemplate('fan.win',values,'changed-seed',{handle:'@fan',week:8,history,sameStory:frozen,renderKey:'same'});assert.equal(c.body,b.body);assert.equal(c.templateId,b.templateId);
 const all={week:7,stories:contentPack.families['fan.win'].map(t=>({templateId:t.id,handle:'@fan'}))};assert.equal(chooseTemplate('fan.win',values,'seed',{handle:'@fan',week:8,history:[all]}).cooldownFallback,true);
});
test('curated replies retain their real parent, stay together, and count toward the 20-post limit',()=>{
 const parent=root('parent',{priority:20,thread:'conversation'}),reply=root('reply',{replyTo:'parent',voice:'fan',priority:100,thread:'conversation'}),pool=[parent,reply,...Array.from({length:30},(_,i)=>root('n'+i,{scopes:['national'],category:'misc'+i,voice:['beat','official','analyst','player','fan','recruit'][i%6]}))];
 const list=curate(pool);assert.equal(list.length,20);assert.ok(list.some(p=>p.id==='reply'));assert.equal(list.findIndex(p=>p.id==='reply'),list.findIndex(p=>p.id==='parent')+1);
 const hidden=root('hidden',{curated:false});assert.ok(!curate([hidden,{...reply,replyTo:'hidden'}]).length);
});
test('orphan and cyclic replies cannot appear in any scope, while roots retain full dedicated coverage',()=>{
 const p=root('parent',{scopes:['national']}),child=root('child',{replyTo:'parent',scopes:['team']}),orphan=root('orphan',{replyTo:'missing'}),cycle=[root('a',{replyTo:'b'}),root('b',{replyTo:'a'})];
 const views=scopeViews([p,child,orphan,...cycle]);assert.deepEqual(views.team,[]);assert.deepEqual(views.national,['parent']);assert.deepEqual(conversationOrder(cycle),[]);
});
test('one account cannot dominate All Posts and caps do not silently remove dedicated facts',()=>{
 const pool=Array.from({length:20},(_,i)=>root('p'+i,{handle:'@same',category:'category'+i}));assert.equal(curate(pool).length,3);assert.equal(scopeViews(pool).team.length,20);
});
test('a real hard commitment gets a roster-player reply with persisted handles; an offer never says welcome',()=>{
 const s=fixture(),event={id:'commit',category:'recruiting',facts:{playerName:'Evan Mercer',school:'Harbor State',newlyObserved:true,commitment:'HardCommitted',position:'QB'},teamIds:[1],playerId:'recruit',scopes:['team','national'],priority:90,thread:'commit',curated:true};
 const a=renderStories(s,[event]),parent=a.stories.find(p=>p.voice==='recruit'),reply=a.stories.find(p=>p.voice==='player');assert.ok(parent&&reply);assert.equal(reply.replyTo,parent.id);assert.ok(reply.body.includes(parent.handle));assert.equal(reply.imageLibrary,1);assert.equal(parent.imageValue,234);assert.ok(reply.body.length<=280);
 const offer={...event,id:'offer',category:'offers',facts:{school:'Harbor State',playerName:'Evan Mercer'}};const b=renderStories(s,[offer]);assert.ok(b.stories.every(p=>!p.replyTo||!(/welcome|joining|committed/i.test(p.body))));
});

test('high-priority midweek recruiting does not evict existing conversations to satisfy reaction caps',()=>{
 const s=fixture(),fact=(id,metric,extra)=>({id,category:'analytics',facts:{school:'Harbor State',metric,sampleGames:4,...extra},teamIds:[1],scopes:['team'],priority:80,thread:id,curated:true});
 const events=[fact('third','thirdDownConversionRate',{conversions:8,attempts:36,rate:8/36}),fact('red','redZoneTouchdownRate',{trips:25,touchdowns:9,rate:9/25}),fact('turnover','turnoverMargin',{takeaways:1,giveaways:8,margin:-7})];
 const a=renderStories(s,events);assert.equal(a.stories.filter(p=>p.replyTo).length,3);
 const offer={id:'new-offer',category:'offers',facts:{school:'Harbor State',playerName:'Evan Mercer'},teamIds:[1],playerId:'recruit',scopes:['team'],priority:100,thread:'offer',curated:true};
 const b=renderStories(s,[...events,offer],{authors:a.authors,sameWeek:{stories:a.stories,dialogueEventOrder:a.dialogueEventOrder}});for(const old of a.stories)assert.equal(b.stories.find(p=>p.id===old.id)?.body,old.body,old.id);assert.ok(b.stories.some(p=>p.id==='new-offer:main'));
});
