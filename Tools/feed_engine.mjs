// Approved prewritten voices applied only to verified Dynasty event facts.
import {scopeCatalog} from './social_discovery.mjs';
import {publishWeek} from './feed_selection.mjs';
import {detectEvents,weekKey} from './story_events.mjs';
import {renderStories,CONTENT_REVISION} from './story_renderer.mjs';
import {PUBLICATION_POLICY_VERSION} from './publication_policy.mjs';
export {detectEvents,weekKey};
export const ENGINE_VERSION=2;
export function trackOffers(s,sameWeek=null,previous=null){
  const valid=(x,w)=>x&&x.leagueId===s.leagueId&&x.season.CurrentSeasonYear===s.season.CurrentSeasonYear&&x.season.CurrentWeekType===s.season.CurrentWeekType&&x.season.CurrentWeek===w;
  const same=valid(sameWeek,s.season.CurrentWeek)?sameWeek:null;
  const prior=valid(previous,s.season.CurrentWeek-1)?previous:null;
  const baseline=Array.isArray(same?.offers)?same:Array.isArray(prior?.offers)?prior:null;
  const key=o=>`${o.team}:${o.player}`,current=new Set(s.offers.map(key));
  // A rewind or withdrawn offer cannot leave a fact in this week's feed that
  // is absent from the currently loaded snapshot.
  const events=new Map((same?.offerEvents??[]).filter(o=>current.has(key(o))).map(o=>[key(o),o]));
  if(baseline){const known=new Set(baseline.offers.map(key));for(const o of s.offers)if(!known.has(key(o)))events.set(key(o),o);}
  return [...events.values()];
}
export function buildFeed(s,previous=null,options={}){
  const events=detectEvents(s,previous),key=weekKey(s);
  const rendered=renderStories(s,events,{authors:options.authors??{},history:options.history??[],sameWeek:options.sameWeek??null});
  options.onAuthors?.(rendered.authors);
  const publication={key,season:s.season.CurrentSeasonYear,phase:s.season.CurrentWeekType,week:s.season.CurrentWeek};
  return publishWeek({format:1,engineVersion:ENGINE_VERSION,key,leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,
    season:publication.season,week:publication.week,phase:publication.phase,source:s.source,sourceKind:s.sourceKind??'save',sha256:s.sha256,sourceUnchanged:true,
    conference:s.teams.find(t=>t.id===s.userTeamIndex)?.conferenceName??null,contentStatus:'generated',contentRevision:CONTENT_REVISION,publicationPolicyVersion:PUBLICATION_POLICY_VERSION,
    scopeOptions:scopeCatalog(s),events:events.map(e=>({...e,publication})),dialogueEventOrder:rendered.dialogueEventOrder,stories:rendered.stories});
}
