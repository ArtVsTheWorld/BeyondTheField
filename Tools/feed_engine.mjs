import {transactionObservation} from './transaction_events.mjs';
import {applyWeeklyCoverage} from './weekly_coverage.mjs';
// Approved prewritten voices applied only to verified Dynasty event facts.
import {scopeCatalog} from './social_discovery.mjs';
import {publishWeek} from './feed_selection.mjs';
import {detectEvents,weekKey} from './story_events.mjs';
import {renderStories,CONTENT_REVISION} from './story_renderer.mjs';
import {PUBLICATION_POLICY_VERSION} from './publication_policy.mjs';
import {freshEditorialEvents,EDITORIAL_POLICY_VERSION} from './editorial_policy.mjs';
import {deduplicateConversations} from './conversation_topics.mjs';
export {detectEvents,weekKey};
export const ENGINE_VERSION=2;
export function trackOffers(s,sameWeek=null,previous=null,earlier=null){
  const valid=(x,w)=>x&&x.leagueId===s.leagueId&&x.season.CurrentSeasonYear===s.season.CurrentSeasonYear&&x.season.CurrentWeekType===s.season.CurrentWeekType&&x.season.CurrentWeek===w;
  const same=valid(sameWeek,s.season.CurrentWeek)?sameWeek:null;
  const prior=valid(previous,s.season.CurrentWeek-1)?previous:earlier&&valid(earlier,earlier.season.CurrentWeek)&&Number.isInteger(earlier.season.CurrentWeek)&&earlier.season.CurrentWeek<s.season.CurrentWeek-1?earlier:null;
  const baseline=Array.isArray(same?.offers)?same:Array.isArray(prior?.offers)?prior:null;
  const key=o=>`${o.team}:${o.player}`,current=new Set(s.offers.map(key));
  // A rewind or withdrawn offer cannot leave a fact in this week's feed that
  // is absent from the currently loaded snapshot.
  const events=new Map((same?.offerEvents??[]).filter(o=>current.has(key(o))).map(o=>[key(o),o]));
  if(baseline){const known=new Set(baseline.offers.map(key));for(const o of s.offers)if(!known.has(key(o)))events.set(key(o),o);}
  return [...events.values()];
}
export function buildFeed(s,previous=null,options={}){
  const publication={key:weekKey(s),leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,season:s.season.CurrentSeasonYear,phase:s.season.CurrentWeekType,week:s.season.CurrentWeek};
  const events=freshEditorialEvents(detectEvents(s,previous),publication,options.history??[]),key=weekKey(s);
  const rendered=renderStories(s,events,{authors:options.authors??{},history:options.history??[],sameWeek:options.sameWeek??null,onTemplates:options.onTemplates??null});
  options.onAuthors?.(rendered.authors);
  return publishWeek({format:1,engineVersion:ENGINE_VERSION,key,leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,
    offseasonStage:s.season.CurrentOffseasonStage,championshipWeek:s.season.RegularSeasonWeekConferenceChampionship,season:publication.season,week:publication.week,phase:publication.phase,source:s.source,sourceKind:s.sourceKind??'save',sha256:s.sha256,sourceUnchanged:true,
    conference:s.teams.find(t=>t.id===s.userTeamIndex)?.conferenceName??null,contentStatus:'generated',contentRevision:CONTENT_REVISION,publicationPolicyVersion:PUBLICATION_POLICY_VERSION,
    editorialPolicyVersion:EDITORIAL_POLICY_VERSION,presentationVersion:3,scopeOptions:scopeCatalog(s),events:events.map(e=>({...e,publication})),dialogueEventOrder:rendered.dialogueEventOrder,transactionObservation:transactionObservation(s),coverageVersion:1,stories:applyWeeklyCoverage(deduplicateConversations(rendered.stories,events),s)});
}
