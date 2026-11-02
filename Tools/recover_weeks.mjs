// Reconstruct only completed-game facts. No historical poll, recruit, injury,
// award or coaching state is inferred from the active week's snapshot.
import {createHash} from 'node:crypto';
import {detectEvents,weekKey} from './story_events.mjs';
import {renderStories,CONTENT_REVISION} from './story_renderer.mjs';
import {publishWeek} from './feed_selection.mjs';
import {scopeCatalog} from './social_discovery.mjs';
import {PUBLICATION_POLICY_VERSION} from './publication_policy.mjs';
export function recoverWeek(current,week,authors={}){
 if(current.season.CurrentWeekType!=='RegularSeason'||!Number.isInteger(week)||week<1||week>=current.season.CurrentWeek)return null;
 const s=structuredClone(current);s.season.CurrentWeek=week;s.reconstructed=true;
 s.games=s.games.filter(g=>g.week===week-1&&g.year===s.season.CurrentYear&&g.phase==='RegularSeason'&&g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status));
 if(!s.games.length)return null;
 s.teams=s.teams.map(t=>({...t,mediaRank:null,mediaLastRank:null,coachesRank:null,coachesLastRank:null,cfpRank:null,cfpLastRank:null,seasonStats:null}));
 s.commitments=[];s.offers=[];s.newOffers=[];s.newCommitments=[];s.heisman=[];s.weeklyAwards=[];s.records=[];s.preseasonHonors=[];s.recruitStatuses=[];
 s.players=s.players.map(p=>({...p,injury:'Uninjured',seasonStats:[]}));
 const events=detectEvents(s).filter(e=>['results','team-stats','player-stats'].includes(e.category)).map(e=>e.category==='results'?{...e,scopes:[...new Set([...e.scopes,'national'])]}:e);
 const rendered=renderStories(s,events,{authors}),key=weekKey(s),publication={key,season:s.season.CurrentSeasonYear,phase:'RegularSeason',week};
 const sha256=createHash('sha256').update(JSON.stringify(events)).digest('hex');
 const feed=publishWeek({format:1,engineVersion:2,key,leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,season:publication.season,phase:publication.phase,week,sourceKind:'runtime',source:'recovered:published-games',sourceUnchanged:true,sha256,reconstructed:true,contentStatus:'recovered',contentRevision:CONTENT_REVISION,publicationPolicyVersion:PUBLICATION_POLICY_VERSION,scopeOptions:scopeCatalog(s),events:events.map(e=>({...e,publication})),stories:rendered.stories});
 return {feed,authors:rendered.authors};
}
