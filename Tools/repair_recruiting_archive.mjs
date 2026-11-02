// Explicit repair from a retained native observation, never today's recruit state.
import {updateRuntime,scopeKey} from './runtime_lifecycle.mjs';
import {publishWeek} from './feed_selection.mjs';
const recruiting=p=>['recruiting','offers'].includes(p.category);
const pairs=a=>JSON.stringify(a.map(x=>[x.team,x.player,x.rank??null,x.stage??null,x.week??null]).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b))));
export function repairRecruitingArchive(s,state){
 const scope=scopeKey(s),week=s.season.CurrentWeek,entry=state.editions.find(e=>e.scope===scope&&e.week===week&&!e.reconstructed);
 if(!entry?.snapshot||entry.snapshot.leagueId!==s.leagueId||entry.snapshot.userTeamIndex!==s.userTeamIndex||pairs(entry.snapshot.commitments)!==pairs(s.commitments)||pairs(entry.snapshot.offers)!==pairs(s.offers))throw Error('Historical recruiting capture does not match the stored observed edition');
 if(entry.snapshot.recruitingObservationVersion===1)return {state,added:0};
 const rebuilt=updateRuntime(structuredClone(s),state),next=rebuilt.state.editions.find(e=>e.week===week),original=entry.feed,ids=new Set(original.stories.map(p=>p.id));
 const coveredEvents=new Set(original.stories.filter(recruiting).map(p=>p.eventId));
 const additions=next.feed.stories.filter(p=>recruiting(p)&&!ids.has(p.id)&&!coveredEvents.has(p.eventId)),eventMap=new Map(original.events.map(e=>[e.id,e]));for(const e of next.feed.events.filter(recruiting))eventMap.set(e.id,e);
 const feed=publishWeek({...original,stories:[...original.stories,...additions],events:[...eventMap.values()]});
 const repaired={...entry,feed,snapshot:{...entry.snapshot,offerEvents:next.snapshot.offerEvents,commitmentEvents:next.snapshot.commitmentEvents,recruitingObservationVersion:1,recruitingCatchup:next.snapshot.recruitingCatchup}};
 return {state:{...state,authors:rebuilt.state.authors,editions:state.editions.map(e=>e===entry?repaired:e)},added:additions.length};
}
