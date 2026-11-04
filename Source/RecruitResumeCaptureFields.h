#pragma once
namespace dynasty::live {
inline std::set<std::string> resumeCaptureFields(const std::string& name){
    if(name=="Franchise")return {"LeagueID"};
    if(name=="SeasonInfo")return {"CurrentSeasonYear","CurrentYear","CurrentWeek","CurrentWeekType","CurrentStage","CurrentOffseasonStage"};
    if(name=="FranchiseServer_CareerFlow")return {"IsStageActive","IsStageAdvancing"};
    if(name=="Team")return {"TeamIndex","DisplayName","LongName","ShortName"};
    if(name=="Recruit")return {"Class","Player"};
    if(name=="Player")return {"FirstName","LastName","Position","TeamIndex","SeasonStats","CareerStats","PresentationId","ProspectStarRating","TraitDevelopment","PLYR_HOME_STATE","PLYR_HOME_TOWN","PLYR_BIRTHDATE","OverallRating","SpeedRating","AccelerationRating","AgilityRating","StrengthRating","AwarenessRating","BCVisionRating","ThrowPowerRating","ThrowAccuracyShortRating","ThrowAccuracyMidRating","ThrowAccuracyDeepRating","CatchingRating","CatchInTrafficRating","ShortRouteRunningRating","MediumRouteRunningRating","DeepRouteRunningRating","BreakTackleRating","CarryingRating","RunBlockRating","PassBlockRating","BlockSheddingRating","FinesseMovesRating","PowerMovesRating","TackleRating","PlayRecognitionRating","ManCoverageRating","ZoneCoverageRating","KickPowerRating","KickAccuracyRating","ChangeOfDirectionRating","ImpactBlockingRating","LongSnapRating","ReleaseRating"};
    if(name=="SeasonStats[]")return {};
    if((name.rfind("Season",0)==0||name.rfind("Career",0)==0)&&name.size()>=5&&name.substr(name.size()-5)=="Stats")return {"SEAS_YEAR","YEARBYYEARTEAMINDEX","GAMESPLAYED","GAMESSTARTED","DOWNSPLAYED","PASSATTEMPTS","PASSCOMPLETED","PASSYARDS","PASSTDS","PASSINTS","RUSHATTEMPTS","RUSHYARDS","RUSHTDS","RECEIVECATCHES","RECEIVEYARDS","RECEIVETDS","DEFTACKLES","ASSDEFTACKLES","DEFTACKLESFORLOSS","DLINESACKS","DLINEHALFSACK","DSECINTS","DEFPASSDEFLECTIONS","DLINEFORCEDFUMBLES","OLINEPANCAKES","OLINESACKSALLOWED","KICKFGATTEMPTS","KICKFGMADE","KICKFGLONGEST","KICKEPATTEMPTS","KICKEPMADE","PUNTATTEMPTS","PUNTYARDS","PUNTIN20"};
    return {"__no_resume_fields__"};
}
}
