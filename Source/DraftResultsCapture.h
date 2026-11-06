#pragma once
#include "LiveTables.h"
namespace recruitingfog::draftresults {
// Explicit request only. DraftClass references select the drafted players;
// neither the entire player pool nor any season/career stat tables are roots.
inline bool captureRoot(const std::string& name){
    return name=="SeasonInfo"||name=="Franchise"||name=="FranchiseServer_CareerFlow"||name=="FranchiseUser"||name=="Team"||name=="Conference"||name=="PlayersLeavingEval";
}
inline std::set<std::string> captureFields(const std::string& name){
    if(name=="SeasonInfo")return {"CurrentSeasonYear","CurrentYear","CurrentWeek","CurrentWeekType","CurrentStage","CurrentOffseasonStage"};
    if(name=="Franchise")return {"LeagueID"};
    if(name=="FranchiseServer_CareerFlow")return {"IsStageActive","IsStageAdvancing"};
    if(name=="FranchiseUser")return {"IsRetired","AdminLevel","Team","UserEntity"};
    if(name=="Team")return {"TeamIndex","DisplayName","LongName","ShortName"};
    if(name=="Conference")return {"Name","ConferenceEnum","TeamSlots","Divisions"};
    if(name=="Division")return {"Teams"};
    if(name=="PlayersLeavingEval")return {"DraftClass"};
    if(name=="LeavingPlayer")return {"Player","ProjectRound","LeaveType"};
    if(name=="Player")return {"FirstName","LastName","Position","TeamIndex","OverallRating","SchoolYear","RedshirtStatus"};
    return {"__no_draft_fields__"};
}
}
