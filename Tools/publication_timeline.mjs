// Native SeasonWeekType values in chronological order, not dictionary order.
export const PUBLICATION_PHASES=['PreSeason','RegularSeason','BowlSeason1','BowlSeason2','BowlSeason3','NationalChampionship','OffSeason'];
export const phaseIndex=phase=>PUBLICATION_PHASES.indexOf(phase);
export const comparePublication=(a,b)=>phaseIndex(a.phase)-phaseIndex(b.phase)||a.week-b.week;
export function visibleEdition(active,entry){
 return phaseIndex(active.phase)>=0&&phaseIndex(entry.phase)>=0&&entry.engineVersion===2&&entry.leagueId===active.leagueId&&entry.userTeamIndex===active.userTeamIndex&&entry.season===active.season&&comparePublication(entry,active)<=0;
}
