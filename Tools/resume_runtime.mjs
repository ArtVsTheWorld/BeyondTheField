// Restore only an edition whose normalized native facts match exactly.
// No event generation or history writes; missing/changed editions use exit 3.
import fs from 'node:fs/promises';
import path from 'node:path';
import {readRuntime} from './read_runtime.mjs';
import {scopeKey} from './runtime_lifecycle.mjs';
import {readHistory,loadArchives,resumeEdition,atomicJson} from './runtime_archive.mjs';
const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Usage: node resume_runtime.mjs runtime-raw.json output.json');
const s=await readRuntime(JSON.parse(await fs.readFile(input,'utf8'))),folder=path.dirname(input);
const state=await readHistory(path.join(folder,'RuntimeHistory',scopeKey(s),'history.json'));
const feed=resumeEdition(s,state,await loadArchives(folder,s));
if(!feed){process.exitCode=3;}else{await atomicJson(output,feed);console.log(JSON.stringify({event:'runtime_feed_resumed',league:s.leagueId,team:s.userTeamIndex,phase:feed.phase,week:feed.week,stories:feed.stories.length,sha256:s.sha256}));}
