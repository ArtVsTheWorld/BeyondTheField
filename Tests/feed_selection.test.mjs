import test from 'node:test';
import assert from 'node:assert/strict';
import {curate,scopeViews,publishWeek,buildCatalog,conversationOrder} from '../Tools/feed_selection.mjs';
const story=(id,scope,priority=80,category=id)=>({id,scopes:[scope],priority,category,thread:id,curated:true});
test('editorial order ignores likes, keeps replies adjacent and is deterministic',()=>{
 const pool=[{...story('low','team',999),likes:20},{...story('high','national',1),likes:900},{...story('middle','conference'),likes:300},{...story('reply','team'),likes:15,replyTo:'high'},{...story('tie','national'),likes:300}];
 assert.deepEqual(conversationOrder(pool).map(p=>p.id),['low','middle','tie','high','reply']);
 assert.deepEqual(curate(pool).map(p=>p.id),['low','middle','tie','high','reply']);assert.deepEqual(conversationOrder(pool.map(p=>({...p,likes:20000-(p.likes??0)}))).map(p=>p.id),conversationOrder(pool).map(p=>p.id));
 assert.deepEqual(scopeViews(pool).national,['tie','high']);
});
test('curated mix favors the user team at 40/27/33 when strong distinct candidates are available',()=>{
  const pool=['national','conference','team'].flatMap(scope=>Array.from({length:20},(_,i)=>story(scope+i,scope,100-i)));
  const selected=curate(pool);assert.equal(selected.length,30);
  assert.deepEqual(Object.fromEntries(['national','conference','team'].map(s=>[s,selected.filter(p=>p.scopes[0]===s).length])),{national:10,conference:8,team:12});
});
test('sparse scope redistributes available slots without filler or duplicate stories',()=>{
  const pool=Array.from({length:35},(_,i)=>story('n'+i,'national'));pool.push(story('t','team'));
  const f=curate(pool);assert.equal(f.length,30);assert.equal(f.filter(p=>p.scopes[0]==='team').length,1);assert.equal(new Set(f.map(p=>p.id)).size,30);
});
test('dedicated views retain all qualifying stories and permit overlap',()=>{
  const pool=Array.from({length:40},(_,i)=>story('n'+i,'national',80,'player-stats'));pool.push({...story('both','team',100),scopes:['team','national','conference']});
  const v=scopeViews(pool);assert.equal(v.national.length,41);assert.ok(v.all.length<pool.length);
  for(const k of ['national','conference','team'])assert.ok(v[k].includes('both'));assert.equal(v.all.filter(id=>id==='both').length,1);
});
test('combined feed limits repeated topics while scope views retain their detail',()=>{
  const pool=Array.from({length:10},(_,i)=>({...story('offer'+i,'team',99,'offers'),thread:'offers:1'}));
  const v=scopeViews(pool);assert.equal(v.team.length,10);assert.equal(v.all.length,1);
  const old={...story('old-board','team'),curated:false};assert.ok(!scopeViews([old]).all.length);assert.deepEqual(scopeViews([old]).team,['old-board']);
});
const edition=(week)=>publishWeek({engineVersion:2,leagueId:1,userTeamIndex:1,season:2027,phase:'RegularSeason',week,key:`1/2027/RegularSeason/${week}`,sourceModifiedMs:week,stories:[story('result','team')]});
test('publication week groups recaps and current news into one edition',()=>{
  const f=edition(8);f.stories[0].eventWeek=7;
  const grouped=publishWeek({...f,stories:[f.stories[0],{...story('rank','national'),eventWeek:8},{...story('award','team'),eventWeek:7},{...story('preview','team'),eventWeek:8}]});
  assert.ok(grouped.stories.every(p=>p.publication.week===8));assert.equal(grouped.stories[0].eventWeek,7);
});
test('catalog lists observed single weeks, defaults to active week, and excludes future/other saves',()=>{
  const active=edition(8),old=edition(7),future=edition(9),other={...edition(5),leagueId:2};
  const c=buildCatalog(active,[old,future,other,edition(6)]);assert.deepEqual(c.weeks.map(w=>w.week),[6,7,8]);assert.equal(c.activeWeekKey,active.key);assert.ok(!c.weeks.some(w=>w.week==='All Weeks'));
  assert.equal(buildCatalog(edition(7),[edition(8)]).weeks.length,1);
});
test('archives preserve their own facts instead of borrowing the latest rankings',()=>{
  const old=edition(7);old.stories[0].body='Ranked #6';const current=edition(8);current.stories[0].body='Ranked #5';
  const c=buildCatalog(current,[old]);assert.equal(c.weeks[0].stories[0].body,'Ranked #6');assert.equal(c.weeks[1].stories[0].body,'Ranked #5');
});
test('preseason and regular Week 0 are distinct single editions in chronological order',()=>{
 const current=edition(0),pre=publishWeek({...edition(0),phase:'PreSeason',key:'1/2027/PreSeason/0'}),future=publishWeek({...edition(0),phase:'BowlSeason1',key:'1/2027/BowlSeason1/0'});
 pre.stories[0].body='The original preseason story';current.stories[0].body='The regular-season story';const c=buildCatalog(current,[future,pre]);assert.equal(c.catalogVersion,2);assert.deepEqual(c.weeks.map(w=>[w.phase,w.week]),[['PreSeason',0],['RegularSeason',0]]);assert.equal(c.activeWeekKey,current.key);assert.equal(c.weeks[0].stories[0].body,'The original preseason story');assert.equal(c.weeks[1].stories[0].body,'The regular-season story');
 assert.equal(buildCatalog(pre,[current,future]).weeks.length,1);
});

test('For You fills a final slot by relaxing soft variety caps, while preserving offer and account limits',()=>{
 const pool=Array.from({length:80},(_,i)=>({...story('p'+i,'team',100-i,'analytics'),handle:'@account'+Math.floor(i/3),voice:'analyst',templateId:'shared'}));
 const selected=curate(pool);assert.equal(selected.length,30);assert.equal(new Set(selected.map(p=>p.id)).size,30);
 for(const handle of new Set(selected.map(p=>p.handle)))assert.ok(selected.filter(p=>p.handle===handle).length<=3);
});

test('publication picker labels hide internal phase names and respect native offseason stages',async()=>{
 const {publicationLabel}=await import('../Tools/publication_timeline.mjs');for(const [phase,expected] of [['BowlSeason1','Bowl Week 1'],['BowlSeason2','Bowl Week 2'],['BowlSeason3','Bowl Week 3'],['NationalChampionship','National Championship']])assert.equal(publicationLabel({phase,week:18,season:2028}),expected+', 2028');assert.equal(publicationLabel({phase:'OffSeason',week:9,offseasonStage:9,season:2028}),'Encourage Transfers / Conference Realignment, 2028');assert.ok(publicationLabel({phase:'OffSeason',week:6,offseasonStage:7,season:2028}).includes('Position Changes'));
});

test('For You keeps every user draft signing beyond its normal curated limit',()=>{
 const posts=Array.from({length:36},(_,i)=>({...story('pick'+i,'team'),voice:'nflDraft',category:'draft',teamIds:[1],draftPick:i+1}));
 const f=publishWeek({...edition(8),stories:posts});assert.equal(f.views.all.length,30);assert.equal(f.views['all:required'].length,36);assert.equal(f.views['all:default'].length,36);
});
