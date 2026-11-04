#pragma once
namespace dynasty::live {
inline std::set<std::string> resumeCaptureFields(const std::string& name){
    if(name=="Franchise")return {"LeagueID"};
    if(name=="SeasonInfo")return {"CurrentSeasonYear","CurrentYear","CurrentWeek","CurrentWeekType","CurrentStage","CurrentOffseasonStage"};
    if(name=="FranchiseServer_CareerFlow")return {"IsStageActive","IsStageAdvancing"};
    if(name=="Recruit")return {"Class","Player"};
    if(name=="Player")return {"FirstName","LastName","Position","PresentationId","ProspectStarRating","TraitDevelopment","PLYR_HOME_STATE","PLYR_HOME_TOWN","PLYR_BIRTHDATE","OverallRating","SpeedRating","AccelerationRating","AgilityRating","StrengthRating","AwarenessRating","BCVisionRating","ThrowPowerRating","ThrowAccuracyShortRating","ThrowAccuracyMidRating","ThrowAccuracyDeepRating","CatchingRating","CatchInTrafficRating","ShortRouteRunningRating","MediumRouteRunningRating","DeepRouteRunningRating","BreakTackleRating","CarryingRating","RunBlockRating","PassBlockRating","BlockSheddingRating","FinesseMovesRating","PowerMovesRating","TackleRating","PlayRecognitionRating","ManCoverageRating","ZoneCoverageRating","KickPowerRating","KickAccuracyRating","ChangeOfDirectionRating","ImpactBlockingRating","LongSnapRating","ReleaseRating"};
    return {"__no_resume_fields__"};
}
}
