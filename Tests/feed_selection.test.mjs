import test from 'node:test';
import assert from 'node:assert/strict';
import {curate,scopeViews,publishWeek,buildCatalog} from '../Tools/feed_selection.mjs';
const story=(id,scope,priority=80,category=id)=>({id,scopes:[scope],priority,category,thread:id,curated:true});
test('curated mix hits 35/25/40 when strong distinct candidates are available',()=>{
  const pool=['national','conference','team'].flatMap(scope=>Array.from({length:15},(_,i)=>story(scope+i,scope,100-i)));
  const selected=curate(pool);assert.equal(selected.length,20);
  assert.deepEqual(Object.fromEntries(['national','conference','team'].map(s=>[s,selected.filter(p=>p.scopes[0]===s).length])),{national:7,conference:5,team:8});
});
test('sparse scope redistributes available slots without filler or duplicate stories',()=>{
  const pool=Array.from({length:25},(_,i)=>story('n'+i,'national'));pool.push(story('t','team'));
  const f=curate(pool);assert.equal(f.length,20);assert.equal(f.filter(p=>p.scopes[0]==='team').length,1);assert.equal(new Set(f.map(p=>p.id)).size,20);
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
