import fs from 'node:fs/promises';
import path from 'node:path';
import {PUBLICATION_PHASES,phaseIndex} from './publication_timeline.mjs';
import {scopeKey} from './runtime_lifecycle.mjs';
import {buildCatalog} from './feed_selection.mjs';
import {CONTENT_REVISION} from './story_renderer.mjs';
export async function readHistory(file){
 let value;try{value=JSON.parse(await fs.readFile(file,'utf8'));}catch(e){if(e.code==='ENOENT')return null;throw e;}
 if(value.format!==1||!Array.isArray(value.editions))throw Error('Invalid runtime history');return value;
}
export async function loadArchives(folder,s){
 const seasonFolder=path.join(folder,'RuntimeHistory',String(s.leagueId),String(s.userTeamIndex),String(s.season.CurrentSeasonYear)),archives=[];
 for(const phase of PUBLICATION_PHASES){if(phaseIndex(phase)>=phaseIndex(s.season.CurrentWeekType))continue;
  const state=await readHistory(path.join(seasonFolder,phase,'history.json'));if(state)archives.push(...state.editions.map(e=>e.feed));
 }
 return archives;
}
export function resumeEdition(s,state,archives=[]){
 if(!state)return null;const scope=scopeKey(s),week=s.season.CurrentWeek;
 const entries=state.editions.filter(e=>e.scope===scope),same=entries.find(e=>e.week===week);
 // Rewinds follow normal reconciliation so future observations are pruned.
 if(!same||entries.some(e=>e.week>week)||same.snapshot?.sha256!==s.sha256)return null;
 const f=same.feed;if(f?.sourceKind!=='runtime'||f.key!==`${s.leagueId}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}/${week}`||f.leagueId!==s.leagueId||f.userTeamIndex!==s.userTeamIndex||f.season!==s.season.CurrentSeasonYear||f.phase!==s.season.CurrentWeekType||f.week!==week||f.sha256!==s.sha256||f.contentRevision!==CONTENT_REVISION)return null;
 return buildCatalog(f,[...archives,...entries.map(e=>e.feed)]);
}
export async function atomicJson(file,data){const tmp=`${file}.${process.pid}.tmp`;try{await fs.writeFile(tmp,JSON.stringify(data));await fs.rename(tmp,file);}finally{await fs.rm(tmp,{force:true}).catch(()=>{});}}
