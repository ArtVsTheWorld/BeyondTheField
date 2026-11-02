import {phaseIndex} from './publication_timeline.mjs';
// Native weeks are global season weeks: CCG 15, waiting week 16, selections 17
// in the verified league. Respect a customized native championship week.
export function postseasonTiming(s){
 const cc=Number.isInteger(s.season.RegularSeasonWeekConferenceChampionship)?s.season.RegularSeasonWeekConferenceChampionship:15;
 const phase=s.season.CurrentWeekType,week=s.season.CurrentWeek,active=s.season.CurrentStage==='NFLSeason';
 return {championshipWeek:cc,selectionWeek:cc+2,waiting:active&&phase==='RegularSeason'&&week===cc+1,
  locked:active&&phaseIndex(phase)>=phaseIndex('BowlSeason1')&&week>=cc+2,
  standings:active&&phase==='RegularSeason'&&week<=cc};
}
