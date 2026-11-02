import {buildFeed,trackOffers,weekKey} from './feed_engine.mjs';
import {buildCatalog} from './feed_selection.mjs';
export function scopeKey(s){return `${s.leagueId}/${s.userTeamIndex}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}`;}
const pair=o=>`${o.team}:${o.player}`;
export function updateRuntime(s,state={format:1,editions:[]}){
  if(s.sourceKind!=='runtime')throw Error('Expected active-Dynasty snapshot');
  if(state.format!==1||!Array.isArray(state.editions))throw Error('Invalid runtime history');
  const scope=scopeKey(s),week=s.season.CurrentWeek;
  const editions=state.editions.filter(e=>e.scope===scope&&e.week<=week);
  const same=editions.find(e=>e.week===week),previous=editions.find(e=>e.week===week-1);
  const baseline=same?.snapshot??previous?.snapshot;
  s.newOffers=trackOffers(s,same?.snapshot,previous?.snapshot);
  const current=new Set(s.commitments.map(pair));
  const events=new Map((same?.snapshot?.commitmentEvents??[]).filter(c=>current.has(pair(c))).map(c=>[pair(c),c]));
  if(baseline){const known=new Set(baseline.commitments.map(pair));for(const c of s.commitments)if(!known.has(pair(c)))events.set(pair(c),c);}
  s.newCommitments=[...events.values()];
  // Remember observed injury episodes, so a midweek injury followed by recovery
  // can publish recovery news throughout this edition. Native episode metadata
  // prevents a restore from before the injury from masquerading as recovery.
  const injured=new Map((same?.snapshot?.midweekBaseline?.players??same?.snapshot?.players??[]).filter(p=>p.injury&&p.injury!=='Uninjured').map(p=>[p.id,p]));
  for(const p of s.players)if(p.team===s.userTeamIndex&&p.injury&&p.injury!=='Uninjured')injured.set(p.id,p);
  const currentPlayers=new Map(s.players.map(p=>[p.id,p]));
  for(const [id,old] of injured){const now=currentPlayers.get(id);if(!now||(now.injury==='Uninjured'&&['injuryYear','injuryWeek','injuryType'].some(k=>old[k]!==now[k])))injured.delete(id);}
  const midweekBaseline=injured.size?{players:[...injured.values()]}:null;
  if(midweekBaseline)s.midweekBaseline=midweekBaseline;
  let authors=state.authors??{};
  const feed=buildFeed(s,previous?.snapshot??null,{authors,history:editions.filter(e=>e.week<week).map(e=>e.feed),sameWeek:same?.feed??null,onAuthors:value=>{authors=value;}});
  const snapshot={format:2,sourceKind:'runtime',leagueId:s.leagueId,season:s.season,userTeamIndex:s.userTeamIndex,sha256:s.sha256,
    players:s.players.filter(p=>p.team===s.userTeamIndex),commitments:s.commitments,offers:s.offers,offerEvents:s.newOffers,commitmentEvents:s.newCommitments,midweekBaseline};
  const entry={scope,week,key:weekKey(s),snapshot,feed};
  const updated=[...editions.filter(e=>e.week!==week),entry].sort((a,b)=>a.week-b.week);
  return {state:{format:1,editions:updated,authors},catalog:buildCatalog(feed,updated.map(e=>e.feed))};
}
