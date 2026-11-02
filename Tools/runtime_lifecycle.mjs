import {projectLine,rosterStrengths} from './betting_model.mjs';
import {buildFeed,trackOffers,weekKey} from './feed_engine.mjs';
import {buildCatalog} from './feed_selection.mjs';
import {publicPoll} from './public_polls.mjs';
export function scopeKey(s){return `${s.leagueId}/${s.userTeamIndex}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}`;}
const pair=o=>`${o.team}:${o.player}`;
export function updateRuntime(s,state={format:1,editions:[]},{archives=[]}={}){
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
  const status=new Map((s.recruitStatuses??[]).map(x=>[x.player,x.stage])),nowCommits=new Map(s.commitments.filter(c=>c.stage==='HardCommitted').map(c=>[c.player,c]));
  const changes=new Map();
  for(const c of same?.snapshot?.commitmentChanges??[]){const now=nowCommits.get(c.player);if(now&&now.team!==c.from)changes.set(c.player,{...c,to:now.team});else if(!now&&['Top10','Top5','Top3','Battle'].includes(status.get(c.player)))changes.set(c.player,{...c,to:null});}
  for(const old of baseline?.commitments??[]){if(old.stage!=='HardCommitted')continue;const now=nowCommits.get(old.player);if(now&&now.team!==old.team)changes.set(old.player,{player:old.player,from:old.team,to:now.team});else if(!now&&['Top10','Top5','Top3','Battle'].includes(status.get(old.player)))changes.set(old.player,{player:old.player,from:old.team,to:null});}
  s.commitmentChanges=[...changes.values()];s.recordBaseline=same?.snapshot?.recordBaselineVersion===1?same.snapshot.recordBaseline:baseline?.records??s.records??[];
  s.pregameGames={...(baseline?.pregameGames??{})};const strengths=rosterStrengths(s),poll=publicPoll(s,previous?.snapshot);
  for(const g of s.games)if(g.week===week&&g.phase===s.season.CurrentWeekType&&g.status==='Unplayed'&&!s.pregameGames[g.id]){const line=projectLine(s,g,strengths);s.pregameGames[g.id]={...(line??{}),poll:poll.key,ranks:Object.fromEntries([g.home,g.away].map(id=>[id,poll.ranks[id]??null]))};}
  // Remember observed injury episodes, so a midweek injury followed by recovery
  // can publish recovery news throughout this edition. Native episode metadata
  // prevents a restore from before the injury from masquerading as recovery.
  const injured=new Map((same?.snapshot?.midweekBaseline?.players??same?.snapshot?.players??[]).filter(p=>p.injury&&p.injury!=='Uninjured').map(p=>[p.id,p]));
  for(const p of s.players)if(p.team!==255&&p.injury&&p.injury!=='Uninjured')injured.set(p.id,p);
  const currentPlayers=new Map(s.players.map(p=>[p.id,p]));
  for(const [id,old] of injured){const now=currentPlayers.get(id);if(!now||(now.injury==='Uninjured'&&['injuryYear','injuryWeek','injuryType'].some(k=>old[k]!==now[k])))injured.delete(id);}
  const midweekBaseline=injured.size?{players:[...injured.values()]}:null;
  if(midweekBaseline)s.midweekBaseline=midweekBaseline;
  let authors=state.authors??{};
  const feed=buildFeed(s,previous?.snapshot??null,{authors,history:editions.filter(e=>e.week<week).map(e=>e.feed),sameWeek:same?.feed??null,onAuthors:value=>{authors=value;}});
  const snapshot={format:2,sourceKind:'runtime',leagueId:s.leagueId,season:s.season,userTeamIndex:s.userTeamIndex,sha256:s.sha256,
    publicPoll:{key:poll.key,ranks:poll.ranks},players:s.players.filter(p=>p.team!==255).map(p=>({id:p.id,team:p.team,injury:p.injury,injuryYear:p.injuryYear,injuryWeek:p.injuryWeek,injuryType:p.injuryType})),records:s.records??[],recordBaseline:s.recordBaseline,recordBaselineVersion:1,pregameGames:s.pregameGames,commitmentChanges:s.commitmentChanges,commitments:s.commitments,offers:s.offers,offerEvents:s.newOffers,commitmentEvents:s.newCommitments,midweekBaseline};
  const entry={scope,week,key:weekKey(s),snapshot,feed};
  const updated=[...editions.filter(e=>e.week!==week),entry].sort((a,b)=>a.week-b.week);
  return {state:{format:1,editions:updated,authors},catalog:buildCatalog(feed,[...archives,...updated.map(e=>e.feed)])};
}
