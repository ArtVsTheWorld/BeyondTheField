import fs from 'node:fs/promises';
import path from 'node:path';
import {readRuntime} from './read_runtime.mjs';
import {updateRuntime,scopeKey} from './runtime_lifecycle.mjs';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw Error('Usage: node export_runtime.mjs runtime-raw.json output.json');
const s=await readRuntime(JSON.parse(await fs.readFile(input,'utf8')));
const directory=path.join(path.dirname(input),'RuntimeHistory',scopeKey(s)),file=path.join(directory,'history.json');
let state;try{state=JSON.parse(await fs.readFile(file,'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
const result=updateRuntime(s,state);
async function atomic(file,data){const tmp=`${file}.${process.pid}.tmp`;try{await fs.writeFile(tmp,JSON.stringify(data));await fs.rename(tmp,file);}finally{await fs.rm(tmp,{force:true}).catch(()=>{});}}
await fs.mkdir(directory,{recursive:true});await atomic(file,result.state);await atomic(output,result.catalog);
console.log(JSON.stringify({event:'runtime_feed_ready',league:s.leagueId,team:s.userTeamIndex,week:s.season.CurrentWeek,stories:result.catalog.stories.length,posts:result.catalog.posts.length,newOffers:s.newOffers.length,newCommitments:s.newCommitments.length,sha256:s.sha256}));
