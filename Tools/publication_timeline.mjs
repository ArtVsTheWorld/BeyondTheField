// Native SeasonWeekType values in chronological order, not dictionary order.
export const PUBLICATION_PHASES=['PreSeason','RegularSeason','BowlSeason1','BowlSeason2','BowlSeason3','NationalChampionship','OffSeason'];
export const phaseIndex=phase=>PUBLICATION_PHASES.indexOf(phase);
export const comparePublication=(a,b)=>phaseIndex(a.phase)-phaseIndex(b.phase)||a.week-b.week;
export function visibleEdition(active,entry){
 return phaseIndex(active.phase)>=0&&phaseIndex(entry.phase)>=0&&entry.engineVersion===2&&entry.leagueId===active.leagueId&&entry.userTeamIndex===active.userTeamIndex&&entry.season===active.season&&comparePublication(entry,active)<=0;
}

export function publicationLabel(f){
 const year=', '+f.season;
 if(f.phase==='PreSeason')return 'Preseason'+year;
 if(f.phase==='RegularSeason')return (f.week===(f.championshipWeek??15)?'Conference Championship':'Week '+f.week)+year;
 const phases={BowlSeason1:'Bowl Week 1',BowlSeason2:'Bowl Week 2',BowlSeason3:'Bowl Week 3',NationalChampionship:'National Championship'};
 if(phases[f.phase])return phases[f.phase]+year;
 const stage=f.offseasonStage??Math.min(f.week+1,9),labels={1:'End of Season Recap',2:'Players Leaving',3:'Offseason Recruiting - Week 1',4:'Offseason Recruiting - Week 2',5:'Offseason Recruiting - Week 3',6:'Offseason Recruiting - Week 4',7:'National Signing Day / Position Changes',8:'Training Results',9:'Encourage Transfers / Conference Realignment'};
 return (labels[stage]??'Offseason')+year;
}
