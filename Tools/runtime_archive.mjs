import path from 'node:path';
import {PUBLICATION_PHASES,phaseIndex} from './publication_timeline.mjs';
import {scopeKey} from './runtime_lifecycle.mjs';
import {buildCatalog} from './feed_selection.mjs';
import {CONTENT_REVISION} from './story_renderer.mjs';
import {refreshAccountPresentation} from './account_presentation.mjs';
import {EDITORIAL_POLICY_VERSION} from './editorial_policy.mjs';
import {currentPublicationPolicy} from './publication_policy.mjs';
import {readEditionHistory,writeEditionHistory,atomicJsonFile} from './history_store.mjs';
export const readHistory=readEditionHistory,writeHistory=writeEditionHistory;
export async function loadArchives(folder,s){
 const seasonFolder=path.join(folder,'RuntimeHistory',String(s.leagueId),String(s.userTeamIndex),String(s.season.CurrentSeasonYear)),archives=[];
 for(const phase of PUBLICATION_PHASES){if(phaseIndex(phase)>=phaseIndex(s.season.CurrentWeekType))continue;
  const state=await readHistory(path.join(seasonFolder,phase,'history.json'),{archiveOnly:true});if(state)archives.push(...state.editions.map(e=>({...e.feed,milestoneObservation:e.snapshot?.milestoneTotals,seasonEndPublications:e.snapshot?.seasonEndPublications,postseasonPublications:e.snapshot?.postseasonPublications})));
 }
 return archives;
}
export function resumeEdition(s,state,archives=[]){
 if(!state)return null;const scope=scopeKey(s),week=s.season.CurrentWeek;
 const entries=state.editions.filter(e=>e.scope===scope),same=entries.find(e=>e.week===week);
 // Rewinds follow normal reconciliation so future observations are pruned.
 if(!same||entries.some(e=>e.week>week)||same.snapshot?.sha256!==s.sha256)return null;
 const f=same.feed;if(f?.editorialPolicyVersion!==EDITORIAL_POLICY_VERSION)return null;if(f?.sourceKind!=='runtime'||f.key!==`${s.leagueId}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}/${week}`||f.leagueId!==s.leagueId||f.userTeamIndex!==s.userTeamIndex||f.season!==s.season.CurrentSeasonYear||f.phase!==s.season.CurrentWeekType||f.week!==week||f.sha256!==s.sha256||f.contentRevision!==CONTENT_REVISION||!currentPublicationPolicy(f))return null;
 return buildCatalog(refreshAccountPresentation(f,s),[...archives,...entries.map(e=>e.feed)].map(old=>refreshAccountPresentation(old,s)));
}
export const atomicJson=atomicJsonFile;
