import fs from 'node:fs/promises';
import path from 'node:path';
import {readDynasty} from './read_dynasty.mjs';
import {buildFeed,weekKey,trackOffers} from './feed_engine.mjs';
import {buildCatalog} from './feed_selection.mjs';

const [configPath,output]=process.argv.slice(2);
if(!configPath||!output)throw Error('Usage: node export_feed.mjs social-refresh.json feed.json');
const c=JSON.parse(await fs.readFile(configPath,'utf8'));
const snapshot=await readDynasty(c.save,c.schema,c.parser);
if(snapshot.leagueId!==c.leagueId||snapshot.userTeamIndex!==c.userTeamIndex)throw Error('Configured save identity changed; refusing another Dynasty');
const dir=path.resolve(path.dirname(configPath),'History',String(snapshot.leagueId),String(snapshot.season.CurrentSeasonYear),snapshot.season.CurrentWeekType);
await fs.mkdir(dir,{recursive:true});
let previous=null;
try{previous=JSON.parse(await fs.readFile(path.join(dir,`${snapshot.season.CurrentWeek-1}.snapshot.json`),'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
let sameWeek=null;
try{sameWeek=JSON.parse(await fs.readFile(path.join(dir,`${snapshot.season.CurrentWeek}.snapshot.json`),'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
snapshot.newOffers=trackOffers(snapshot,sameWeek,previous);
const feed=buildFeed(snapshot,previous);
feed.sourceModifiedMs=(await fs.stat(c.save)).mtimeMs;
// Retain each observed save version; reloading a week neither rerolls templates
// nor appends duplicate posts. Week files are the latest verified snapshot.
async function atomic(file,value){const tmp=`${file}.${process.pid}.tmp`;try{await fs.writeFile(tmp,JSON.stringify(value));await fs.rename(tmp,file);}finally{await fs.rm(tmp,{force:true}).catch(()=>{});}}
const archive=path.join(dir,`${snapshot.season.CurrentWeek}.${snapshot.sha256}.feed.json`);
await atomic(archive,feed);
await atomic(path.join(dir,`${snapshot.season.CurrentWeek}.snapshot.json`),{
  format:snapshot.format,leagueId:snapshot.leagueId,season:snapshot.season,sha256:snapshot.sha256,
  players:snapshot.players.filter(p=>p.team===snapshot.userTeamIndex),commitments:snapshot.commitments,
  offers:snapshot.offers,offerEvents:snapshot.newOffers});
const history=[];
for(const file of await fs.readdir(dir))if(file.endsWith('.feed.json')){
  const f=JSON.parse(await fs.readFile(path.join(dir,file),'utf8'));if(f.engineVersion===2)history.push(f);
}
const catalog=buildCatalog(feed,history);
await atomic(path.resolve(output),catalog);
console.log(JSON.stringify({event:'feed_exported',key:weekKey(snapshot),posts:feed.posts.length,
  categories:[...new Set(feed.posts.map(p=>p.category))],sha256:snapshot.sha256,sourceUnchanged:true,
  previousWeekBaseline:previous!==null,teams:snapshot.teams.length,players:snapshot.players.length,
  games:snapshot.games.length,performances:snapshot.performances.length,heisman:snapshot.heisman.length,
  commitments:snapshot.commitments.length,stories:feed.stories.length,weeks:catalog.weeks.map(w=>w.week),scopeCounts:Object.fromEntries(Object.entries(feed.views).map(([k,v])=>[k,v.length]))}));
