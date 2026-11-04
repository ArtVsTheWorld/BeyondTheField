// Offline A/B/A comparison. Neither game memory nor source archives are changed.
import fs from 'node:fs/promises';
import {isDeepStrictEqual} from 'node:util';
import {performance} from 'node:perf_hooks';
import {readRuntime} from './read_runtime.mjs';
import {readHistory} from './runtime_archive.mjs';
import {buildFeed} from './feed_engine.mjs';
const [rawFile,historyFile,output]=process.argv.slice(2);if(!output)throw Error('Usage: benchmark_templates.mjs raw.json history.json output.json');
const s=await readRuntime(JSON.parse(await fs.readFile(rawFile,'utf8'))),state=await readHistory(historyFile,{archiveOnly:true});
const history=(state?.editions??[]).filter(e=>e.week<s.season.CurrentWeek).map(e=>e.feed),options={history,authors:state?.authors??{}},runs=[];let reference;
for(const mode of ['eager','lazy','eager']){
 let candidates=0;const began=performance.now(),feed=buildFeed(s,null,{...options,...(mode==='eager'?{onTemplates:r=>{candidates+=r.candidates.length;}}:{})}),ms=performance.now()-began;
 if(reference&&!isDeepStrictEqual(feed,reference))throw Error('Template optimization changed the feed');reference??=feed;
 runs.push({mode,ms:Math.round(ms),stories:feed.stories.length,posts:feed.posts.length,auditedEligibleCandidates:candidates});
}
const report={edition:reference.key,exactlyEqual:true,runs,note:'Eager diagnostic renders all candidates; lazy formats only candidates needed for the identical selection. Frozen live data; not game frame-time measurement.'};
await fs.writeFile(output,JSON.stringify(report,null,2));console.log(JSON.stringify(report));
