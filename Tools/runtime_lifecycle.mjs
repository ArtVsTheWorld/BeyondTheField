import {draftBoard,undraftedBoard} from './draft_results.mjs';
import {transactionObservation,blueprintNILChanges} from './transaction_events.mjs';
import {observedStaffMoves} from './season_review_events.mjs';
import {seedPostseasonPublications} from './postseason_events.mjs';
import {seedSeasonEndPublications} from './season_ending_events.mjs';
import {milestoneTotals} from './history_milestones.mjs';
import {projectLine,rosterStrengths} from './betting_model.mjs';
import {buildFeed,trackOffers,weekKey} from './feed_engine.mjs';
import {buildCatalog} from './feed_selection.mjs';
import {refreshAccountPresentation} from './account_presentation.mjs';
import {recoverWeek} from './recover_weeks.mjs';
import {publicPoll} from './public_polls.mjs';
export function scopeKey(s){return `${s.leagueId}/${s.userTeamIndex}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}`;}
const pair=o=>`${o.team}:${o.player}`;
export function updateRuntime(s,state={format:1,editions:[]},{archives=[]}={}){
  if(s.sourceKind!=='runtime')throw Error('Expected active-Dynasty snapshot');
  if(state.format!==1||!Array.isArray(state.editions))throw Error('Invalid runtime history');
  const scope=scopeKey(s),week=s.season.CurrentWeek;
  const editions=state.editions.filter(e=>e.scope===scope&&e.week<=week);
  let authors=state.authors??{};
  const lastObserved=editions.filter(e=>!e.reconstructed&&e.snapshot&&e.week<week).sort((a,b)=>b.week-a.week)[0];
  if(lastObserved)for(let missing=lastObserved.week+1;missing<week;++missing)if(!editions.some(e=>e.week===missing)){const r=recoverWeek(s,missing,authors);if(r){authors=r.authors;editions.push({scope,week:missing,key:r.feed.key,reconstructed:true,feed:r.feed});}}
  const same=editions.find(e=>e.week===week&&!e.reconstructed),previous=editions.find(e=>e.week===week-1&&!e.reconstructed);
  const baseline=same?.snapshot??previous?.snapshot;
  seedPostseasonPublications(s,same?.snapshot?.postseasonPublications??previous?.snapshot?.postseasonPublications??lastObserved?.snapshot?.postseasonPublications??[...archives].reverse().find(f=>f.postseasonPublications)?.postseasonPublications??{});
  seedSeasonEndPublications(s,same?.snapshot?.seasonEndPublications??previous?.snapshot?.seasonEndPublications??lastObserved?.snapshot?.seasonEndPublications??[...archives].reverse().find(f=>f.seasonEndPublications)?.seasonEndPublications??{});
  const totals=milestoneTotals(s);
  const archiveMilestones=[...archives].reverse().find(f=>f.milestoneObservation?.version===1&&f.milestoneObservation.year===s.season.CurrentSeasonYear)?.milestoneObservation;
  s.milestoneBaseline=same?.snapshot?.milestoneBaseline??previous?.snapshot?.milestoneTotals??lastObserved?.snapshot?.milestoneTotals??archiveMilestones??totals;
  const gap=!previous&&lastObserved&&lastObserved.week<week-1;
  const seedGap=gap&&(!same||same.snapshot.recruitingObservationVersion!==1);
  const recruitingBaseline=seedGap?lastObserved.snapshot:baseline;
  s.newOffers=trackOffers(s,seedGap?null:same?.snapshot,previous?.snapshot,gap?lastObserved.snapshot:null);
  const current=new Set(s.commitments.map(pair));
  const events=new Map((same?.snapshot?.commitmentEvents??[]).filter(c=>current.has(pair(c))).map(c=>[pair(c),c]));
  if(recruitingBaseline){const known=new Set(recruitingBaseline.commitments.map(pair));for(const c of s.commitments)if(!known.has(pair(c)))events.set(pair(c),c);}
  s.newCommitments=[...events.values()];
  s.recruitingCatchup=same?.snapshot?.recruitingCatchup??(seedGap?{fromWeek:lastObserved.week,commitments:s.newCommitments.map(pair),offers:s.newOffers.map(pair)}:null);
  const status=new Map((s.recruitStatuses??[]).map(x=>[x.player,x.stage])),nowCommits=new Map(s.commitments.filter(c=>c.stage==='HardCommitted').map(c=>[c.player,c]));
  const changes=new Map();
  for(const c of same?.snapshot?.commitmentChanges??[]){const now=nowCommits.get(c.player);if(now&&now.team!==c.from)changes.set(c.player,{...c,to:now.team});else if(!now&&['Top10','Top5','Top3','Battle'].includes(status.get(c.player)))changes.set(c.player,{...c,to:null});}
  for(const old of recruitingBaseline?.commitments??[]){if(old.stage!=='HardCommitted')continue;const now=nowCommits.get(old.player);if(now&&now.team!==old.team)changes.set(old.player,{player:old.player,from:old.team,to:now.team});else if(!now&&['Top10','Top5','Top3','Battle'].includes(status.get(old.player)))changes.set(old.player,{player:old.player,from:old.team,to:null});}
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
  const priorTransactions=previous?.snapshot?.transactionObservation??lastObserved?.snapshot?.transactionObservation??[...archives].reverse().find(f=>f.transactionObservation?.version===1&&f.transactionObservation.year===s.season.CurrentSeasonYear)?.transactionObservation;
  s.transactionBaseline=same?.snapshot?.transactionBaseline??priorTransactions??transactionObservation(s);
  // Upgrade old NIL baselines with a quiet, identity-checked position baseline.
  const positionSeed=new Map((same?.snapshot?.transactionObservation?.players??transactionObservation(s).players).map(p=>[p.id,p]));
  s.transactionBaseline={...s.transactionBaseline,players:s.transactionBaseline.players.map(p=>{const v=positionSeed.get(p.id);return p.position||!v||v.team!==p.team?p:{...p,name:v.name,position:v.position,presentationId:v.presentationId};})};
  const offseason=s.season.CurrentStage==='OffSeason'&&s.season.CurrentWeekType==='OffSeason';
  s.delayedNILChanges=offseason&&week===1?(same?.snapshot?.delayedNILChanges??blueprintNILChanges(previous?.snapshot?.transactionBaseline,previous?.snapshot?.transactionObservation)):[];
  const originFeeds=[...archives,...editions.map(e=>e.feed)];
  s.portalOrigins=Object.fromEntries(originFeeds.flatMap(f=>(f.transactionObservation?.players??[]).filter(p=>p.team!==255).map(p=>[p.id,p.team])));
  s.draftBoard=draftBoard(s,same?.snapshot?.draftBoard??[]);
  s.undraftedSignings=undraftedBoard(s,same?.snapshot?.undraftedSignings??[]);
  const officialPicks=feed=>(feed?.events??[]).filter(e=>e.category==='draft'&&Number.isInteger(e.facts?.draftPick)&&e.facts.draftPick>=1&&e.facts.draftPick<=224);
  const priorDraft=[...editions].filter(e=>e.week<=week).reverse().find(e=>e.snapshot?.recentDraftClass?.length===224||officialPicks(e.feed).length===224);
  s.recentDraftClass=s.draftBoard.length===224?s.draftBoard.map(d=>{const p=s.players.find(p=>p.id===d.player);return {...d,teamId:p?.team,playerName:p?.name,position:p?.position};}):priorDraft?.snapshot?.recentDraftClass?.length===224?priorDraft.snapshot.recentDraftClass:officialPicks(priorDraft?.feed).map(e=>({player:e.playerId,teamId:e.teamIds[0],playerName:e.facts.playerName,position:e.facts.position,pick:e.facts.draftPick,round:e.facts.draftRound,nflTeam:e.facts.nflTeam}));
  s.seasonStaffMoves=observedStaffMoves([...archives,...editions.filter(e=>e.week<week).map(e=>e.feed)],s.season.CurrentSeasonYear);
  const feed=buildFeed(s,previous?.snapshot??null,{authors,history:[...archives,...editions.filter(e=>e.week<week).map(e=>e.feed)],sameWeek:same?.feed??null,onAuthors:value=>{authors=value;}});
  const snapshot={format:2,sourceKind:'runtime',leagueId:s.leagueId,season:s.season,userTeamIndex:s.userTeamIndex,sha256:s.sha256,
    draftBoard:s.draftBoard,undraftedSignings:s.undraftedSignings,recentDraftClass:s.recentDraftClass,transactionObservation:transactionObservation(s),transactionBaseline:s.transactionBaseline,delayedNILChanges:s.delayedNILChanges,postseasonPublications:s.postseasonPublications,seasonEndPublications:s.seasonEndPublications,milestoneTotals:totals,milestoneBaseline:s.milestoneBaseline,publicPoll:{key:poll.key,ranks:poll.ranks},players:s.players.filter(p=>p.team!==255).map(p=>({id:p.id,team:p.team,injury:p.injury,injuryYear:p.injuryYear,injuryWeek:p.injuryWeek,injuryType:p.injuryType,minInjury:p.minInjury,maxInjury:p.maxInjury,injurySeverity:p.injurySeverity})),records:s.records??[],recordBaseline:s.recordBaseline,recordBaselineVersion:1,pregameGames:s.pregameGames,commitmentChanges:s.commitmentChanges,commitments:s.commitments,offers:s.offers,offerEvents:s.newOffers,commitmentEvents:s.newCommitments,recruitingObservationVersion:1,recruitingCatchup:s.recruitingCatchup,midweekBaseline};
  const entry={scope,week,key:weekKey(s),snapshot,feed};
  const updated=[...editions.filter(e=>e.week!==week).map(e=>({...e,feed:refreshAccountPresentation(e.feed,s)})),entry].sort((a,b)=>a.week-b.week);
  return {state:{format:1,editions:updated,authors},catalog:buildCatalog(feed,[...archives.map(f=>refreshAccountPresentation(f,s)),...updated.map(e=>e.feed)])};
}
