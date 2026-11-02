import test from 'node:test';
import assert from 'node:assert/strict';
import {scopeCatalog,discoveryViews,filterConversations} from '../Tools/social_discovery.mjs';
import {conversationOrder,curate} from '../Tools/feed_selection.mjs';
import {brandAudience,likesFor,ENGAGEMENT_VERSION} from '../Tools/story_engagement.mjs';
import {avatarFor} from '../Tools/story_avatars.mjs';
import {buildFeed} from '../Tools/feed_engine.mjs';
const snapshot=()=>({format:2,gameYear:27,sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:1,userTeamIndex:1,source:'runtime',season:{CurrentYear:1,CurrentSeasonYear:2027,CurrentWeek:9,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},
 teams:[{id:1,name:'Zebra',logo:1,conferenceId:'actual-z',pipelines:['EastTexas'],homeState:'Texas'},{id:2,name:'Alpha',logo:2,conferenceId:'actual-a'},{id:3,name:'Beta',logo:3,conferenceId:'actual-a'},{id:255,name:'Generic'}],
 conferences:[{id:'actual-z',name:'Z Conference',teams:[1]},{id:'actual-a',name:'A Conference',teams:[2,3]}],players:[],games:[],performances:[],heisman:[],offers:[],commitments:[]});
test('scope catalog uses actual conference records, alphabetizes each group and deduplicates teams',()=>{
 const s=snapshot();s.teams.push(s.teams[0]);const options=scopeCatalog(s);
 assert.deepEqual(options.map(o=>o.label),['For You','National','A Conference','Z Conference','Alpha','Beta','Zebra']);
 s.conferences[0].teams=[1,2];s.conferences[1].teams=[3];
 assert.deepEqual(scopeCatalog(s).find(o=>o.key==='conference:actual-z').teamIds,[1,2]);
});
test('dedicated views retain entire conversations in parent-first order across both involved teams',()=>{
 const s=snapshot(),p={id:'root',teamIds:[2,3],priority:80,category:'polls',voice:'beat'},r={...p,id:'reply',replyTo:'root',voice:'fan'};
 const ordered=conversationOrder([r,p]),views=discoveryViews(ordered,scopeCatalog(s));
 assert.deepEqual(views['team:2'],['root','reply']);assert.deepEqual(views['team:3'],['root','reply']);assert.deepEqual(views['team:1'],[]);
 assert.deepEqual(filterConversations(ordered,'rankings').map(x=>x.id),['root','reply']);
 assert.deepEqual(filterConversations(ordered,'fan'),[]);assert.deepEqual(filterConversations(ordered,'beat').map(x=>x.id),['root','reply']);
});
test('outside-conference unranked results and previews exist without entering personalized curation',()=>{
 const s=snapshot();s.games=[{id:'outside',year:1,week:8,phase:'RegularSeason',published:true,status:'HomeWon',home:2,away:3,homeScore:21,awayScore:7},{id:'next',year:1,week:9,phase:'RegularSeason',status:'Unplayed',home:2,away:3}];
 const f=buildFeed(s);assert.ok(f.views['team:2'].length);assert.ok(f.stories.some(p=>p.eventId==='result:outside'));assert.ok(f.stories.some(p=>p.eventId==='preview:next'));
 assert.equal(f.posts.length,0);assert.ok(f.views['conference:actual-a'].length);
});
test('pipeline and same-state recruiting are relevant without falsely tagging the user team',()=>{
 const s=snapshot();s.players=[{id:'p',name:'Evan Mercer',team:255,homePipeline:'EastTexas',personality:'Leader',position:'QB'}];s.newOffers=[{player:'p',team:2,rank:500}];
 const f=buildFeed(s),post=f.stories.find(p=>p.category==='offers');assert.ok(post.scopes.includes('relevant'));assert.ok(!post.teamIds.includes(1));assert.ok(f.posts.includes(post));assert.deepEqual(f.views['team:1'],[]);
});
test('flavor engagement is deterministic, respects brand/rank and freezes same-week likes',()=>{
 const s=snapshot(),e={scopes:['national']},high={brandExposure:'Aplus',mediaRank:1},low={brandExposure:'F',mediaRank:99};
 assert.ok(brandAudience(high).brand>brandAudience(low).brand);
 const a=likesFor(s,'story','official',high,e);assert.equal(likesFor(s,'story','official',high,e),a);assert.ok(a>likesFor(s,'story','official',low,e));
 assert.equal(likesFor(s,'story','official',low,e,{likes:a,engagementVersion:ENGAGEMENT_VERSION}),a);assert.ok(a>likesFor(s,'story','fan',high,e));
});
test('only official accounts get team logos; uniforms require active-team membership and valid portrait',()=>{
 const t={id:1,logo:11},p={team:1,portrait:146};assert.deepEqual(avatarFor('player',t,p),{imageLibrary:1,imageValue:146,uniformTeamLogo:11});
 assert.equal(avatarFor('recruit',t,{...p,team:255}).uniformTeamLogo,undefined);
 for(const role of ['beat','analyst','fan','model'])assert.equal(avatarFor(role,t,p).imageLibrary,79);
 assert.equal(new Set(['beat','analyst','fan'].map(role=>avatarFor(role,t,p).imageValue)).size,3);
 assert.deepEqual(avatarFor('official',t,p),{imageLibrary:0,imageValue:11});
 assert.equal(avatarFor('player',t,{...p,portrait:0}).uniformTeamLogo,undefined);
});
