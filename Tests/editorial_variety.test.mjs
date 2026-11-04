import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {personalVoice,finishPersonalText} from '../Tools/voice_style.mjs';
import {chooseTemplate,contentPack} from '../Tools/story_templates.mjs';
import {renderStories} from '../Tools/story_renderer.mjs';
import {seasonStorylines} from '../Tools/season_storylines.mjs';
import {freshEditorialEvents} from '../Tools/editorial_policy.mjs';
import {cleanLanguage} from '../Tools/clean_language.mjs';
const pack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/editorial-variety-pack.json',import.meta.url),'utf8'));
const actual=()=>JSON.parse(fs.readFileSync(new URL('./Fixtures/ulm-close-games-2026.json',import.meta.url),'utf8'));
const pub={leagueId:1,userTeamIndex:1,season:2027,phase:'OffSeason',week:0};
test('personal style persists for a handle and gives trained quarterbacks a restrained voice',()=>{
 const a={handle:'@Person',styleSeed:10};assert.equal(personalVoice(a,{position:'WR',personality:'Neutral'}),personalVoice({...a},{position:'WR',personality:'Neutral'}));
 for(let i=0;i<50;i++)assert.equal(personalVoice({styleSeed:i},{position:'QB',personality:'Intense'}),'measured');
 assert.equal(personalVoice({styleSeed:2},{position:'QB',personality:'Unpredictable'}),'expressive');
 assert.equal(finishPersonalText('Good work','measured'),'Good work.');assert.equal(finishPersonalText('Good work.','conversational'),'Good work');assert.equal(finishPersonalText('Good work!!','expressive'),'Good work!!');
});
test('style selects matching language while another body is preferred within an edition',()=>{
 const values={school:'Harbor'},a=chooseTemplate('recruit.offer.Neutral',values,'same',{style:'measured'}),b=chooseTemplate('recruit.offer.Neutral',values,'same',{style:'measured',avoidBodies:new Set([a.body])});
 assert.equal(contentPack.families['recruit.offer.Neutral'].find(t=>t.id===a.templateId).style,'measured');assert.notEqual(a.body,b.body);
});
test('exhausted wording never hides a factual story and same-week wording remains frozen',()=>{
 const values={school:'Harbor'},all=new Set(pack.families['recruit.offer.Neutral'].map(t=>t.body.replace('{school}','Harbor'))),a=chooseTemplate('recruit.offer.Neutral',values,'same',{avoidBodies:all});assert.ok(a);
 const frozen={...a,contentRevision:contentPack.revision,renderKey:'frozen'},b=chooseTemplate('recruit.offer.Neutral',values,'other',{sameStory:frozen,renderKey:'frozen',style:'expressive',avoidBodies:new Set([a.body])});assert.deepEqual(b,a);
});
test('template cooldown crosses the championship to offseason week-number reset',()=>{
 const values={school:'Harbor',nickname:'Hawks'},a=chooseTemplate('fan.win',values,'same'),history=[{...pub,phase:'NationalChampionship',week:20,stories:[{...a,handle:'@fan'}]}],b=chooseTemplate('fan.win',values,'same',{publication:pub,week:0,handle:'@fan',history});assert.notEqual(a.templateId,b.templateId);
 const foreign=history.map(f=>({...f,leagueId:2}));assert.equal(chooseTemplate('fan.win',values,'same',{publication:pub,week:0,handle:'@fan',history:foreign}).templateId,a.templateId);
});
test('cold wording is preferred over the only matching style when that phrase was recently used',()=>{
 const values={school:'Harbor'},a=chooseTemplate('recruit.offer.Neutral',values,'same',{style:'measured'}),preferred=contentPack.families['recruit.offer.Neutral'].filter(t=>t.style==='measured'),history=[{...pub,phase:'NationalChampionship',week:20,stories:preferred.map(t=>({templateId:t.id,handle:'@prospect'}))}];
 const b=chooseTemplate('recruit.offer.Neutral',values,'same',{style:'measured',publication:pub,week:0,handle:'@prospect',history});
 assert.ok(!preferred.some(t=>t.id===b.templateId));assert.equal(b.cooldownFallback,false);
});
test('new wording is clean and all eligible variants respect both native text budgets',()=>{
 const values=Object.fromEntries([...JSON.stringify(pack).matchAll(/\{([A-Za-z][A-Za-z0-9]*)\}/g)].map(m=>[m[1],'12']));Object.assign(values,{school:'Harbor State',nickname:'Captains',playerName:'Evan Moss',position:'QB',prospectType:'high school ',starDescription:'4-star ',opponent:'Red Mesa',record:'3–9',recentLine:'200 passing yards, 100 rushing yards, 3 passing/rushing TD, 0 INT',seasonLine:'2000 passing yards, 600 rushing yards, 20 passing/rushing TD, 3 INT',interpretation:'Little separation in those efficiency averages.'});
 for(const [family,variants] of Object.entries(pack.families))for(const t of variants){assert.equal(cleanLanguage(t.body),t.body,t.id);assert.ok(!/\b(?:OVR|overall|rating|skill tree)\b|[\u{1F000}-\u{1FAFF}\u2600-\u27BF]/iu.test(t.body),t.id);const body=chooseTemplate(family,values,t.id);assert.ok(body,t.id);assert.ok([...body.body].length<=280&&Buffer.byteLength(body.body)<=512,t.id);}
});
test('mechanical analysis endings are absent from the complete loaded pack',()=>{
 for(const variants of Object.values(contentPack.families))for(const t of variants)assert.ok(!/The whole stat line belongs|Worth keeping alongside|A profile worth following as the evaluation develops|A useful unit comparison before kickoff/.test(t.body),t.id);
});
test('actual ULM results support three wins by a combined five points, with no invented decisive wins',()=>{
 const s=actual();s.season.CurrentWeek=14;const e=seasonStorylines(s).find(e=>e.options.team===63&&e.facts.family==='editorial.close-wins');assert.ok(e);assert.equal(e.facts.record,'3–9');assert.equal(e.facts.wins,3);assert.equal(e.facts.maxMargin,2);assert.equal(e.facts.totalMargin,5);
 const body=chooseTemplate(e.facts.family,e.facts,'ULM').body;assert.ok(body.includes('5')&&body.includes('3')&&body.includes('2'));
});
test('season narratives reject contradictory records, stale games and reconstructed weeks',()=>{
 const s=actual();s.season.CurrentWeek=14;s.teams.find(t=>t.id===63).wins=4;assert.ok(!seasonStorylines(s).some(e=>e.options.team===63));
 s.teams.find(t=>t.id===63).wins=3;s.season.CurrentWeek=16;assert.ok(!seasonStorylines(s).some(e=>e.options.team===63));s.season.CurrentWeek=14;s.reconstructed=true;assert.deepEqual(seasonStorylines(s),[]);
});
test('a changed season pattern is news; an unchanged pattern is not republished',()=>{
 const s=actual();s.season.CurrentWeek=14;const raw=seasonStorylines(s).find(e=>e.options.team===63),e={...raw,teamIds:[63]},previous={...pub,phase:'RegularSeason',week:14,events:[e],stories:[{eventId:e.id}]},active={...pub,phase:'RegularSeason',week:15};assert.deepEqual(freshEditorialEvents([e],active,[previous]),[]);assert.equal(freshEditorialEvents([{...e,facts:{...e.facts,count:99}}],active,[previous]).length,1);
});
const heismanFixture=()=>({leagueId:1,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2027,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason',CurrentWeek:8},teams:[{id:1,name:'Harbor',mediaRank:1},{id:2,name:'Valley'}],players:[{id:'p',name:'Evan Moss',team:1,position:'QB'}],games:[{id:'g',year:0,phase:'RegularSeason',week:7,home:1,away:2,homeScore:31,awayScore:10,status:'HomeWon',published:true}],performances:[{player:'p',team:1,game:'g',type:'GameOffensiveStats',stats:{PASSYARDS:200,PASSTDS:2,PASSINTS:0,RUSHYARDS:100,RUSHTDS:1}}],offers:[],commitments:[],heisman:[]});
test('a Heisman drop after a strong dual-threat win keeps the whole performance without inventing a voting cause',()=>{
 const s=heismanFixture(),e={id:'heisman:p',category:'heisman',playerId:'p',teamIds:[1],scopes:['national','team'],priority:100,thread:'h',facts:{school:'Harbor',playerName:'Evan Moss',rank:3,previousRank:2}},a=renderStories(s,[e]),p=a.stories.find(p=>p.category==='heisman');assert.ok(p.templateId.startsWith('editorial.heisman-slip'));for(const fact of ['200 passing','100 rushing','3 passing/rushing TD','0 INT','No. 2','No. 3'])assert.ok(p.body.includes(fact),p.body);assert.ok(!/voters|because|lost|poor performance/i.test(p.body));assert.deepEqual(renderStories(s,[e],{authors:a.authors,sameWeek:{stories:a.stories,dialogueEventOrder:a.dialogueEventOrder}}).stories,a.stories);
});
test('negative Heisman production does not receive the strong-performance contrast',()=>{
 const s=heismanFixture();s.performances[0].stats.PASSINTS=3;const e={id:'heisman:p',category:'heisman',playerId:'p',teamIds:[1],scopes:['national'],priority:100,thread:'h',facts:{school:'Harbor',playerName:'Evan Moss',rank:3,previousRank:2}},p=renderStories(s,[e]).stories[0];assert.ok(p.templateId.startsWith('editorial.heisman-movement'));assert.ok(p.body.includes('3 INT'));assert.ok(!/strong game|productive game/.test(p.body));
});
