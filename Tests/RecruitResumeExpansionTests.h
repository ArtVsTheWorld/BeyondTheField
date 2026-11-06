#pragma once
#include "RecruitTransferClassTests.h"
inline nlohmann::json expansionTests(){
    using namespace recruitingfog::resume;
    transferClassLabelTests();
    Prospect p;p.identity="expansion";p.position="QB";p.stars=3;p.state="NorthCarolina";p.ratings={{"OverallRating",70},{"AwarenessRating",70}};
    double gpaTotal=0;int middle=0,edges=0,nearby=0,assigned=0;std::set<std::string> levels;
    const std::set<std::string> active={schoolKey("Elon University"),schoolKey("North Dakota State"),schoolKey("Mount Union")};
    for(int i=0;i<6000;++i){
        p.identity="academic-pair-"+std::to_string(i);const auto academic=academicGpa(p.identity);gpaTotal+=academic;
        if(academic>=2.75&&academic<=3.75)++middle;if(academic<=2.25||academic>=4.25)++edges;
        auto changed=p;changed.stars=1;changed.ratings={{"OverallRating",1},{"AwarenessRating",1}};changed.development="College_Elite";
        const auto weakGpa=generate(changed).publicData.at("gpa");changed.stars=5;changed.ratings={{"OverallRating",99},{"AwarenessRating",99}};changed.development="Normal";
        if(weakGpa!=academic||generate(changed).publicData.at("gpa")!=academic)throw std::runtime_error("Academic background depends on football ability");
        const auto* school=chooseCollege(p,active);if(!school||schoolCollision(*school,active))throw std::runtime_error("Prior school collides with Dynasty");
        ++assigned;if(schoolRegion(school->state)==schoolRegion(p.state))++nearby;
        p.collegeLevel=school->level;p.collegeSchool=school->name;levels.insert(p.collegeLevel);auto resume=generate(p).publicData;validate(resume);
        if(resume.at("heading")!="Previous College Season"||resume.at("background").get<std::string>().find("varsity")!=std::string::npos)throw std::runtime_error("JUCO profile still uses a high school background");
        p.collegeLevel.clear();p.collegeSchool.clear();
        if(resume.at("gpa").get<double>()<2||resume.at("gpa").get<double>()>4.5)throw std::runtime_error("GPA outside range");
    }
    if(levels.size()!=3||middle<6000*.65||middle>6000*.85||edges>6000*.02||edges<6000*.002||std::abs(gpaTotal/6000-3.25)>.03||nearby<assigned*.40)throw std::runtime_error("Academic/college background balance failed");
    p.identity="zero-opportunity";auto legacy=generate(p).publicData;legacy["modelVersion"]=2;legacy["gpa"]=2.01;legacy.erase("academicModelVersion");legacy["rates"].erase("completionPercent");
    const auto originalStats=legacy.at("stats"),originalClass=legacy.at("competitionClass");addResumeDetails(legacy,p);validate(legacy);
    if(legacy.at("stats")!=originalStats||legacy.at("competitionClass")!=originalClass||legacy.at("gpa")!=academicGpa(p.identity)||legacy.at("academicModelVersion")!=2)throw std::runtime_error("Migration rerolled the prior season");
    const auto migrated=legacy;addResumeDetails(legacy,p);if(legacy!=migrated)throw std::runtime_error("Academic migration is not idempotent");
    Json transfer={{"modelVersion",3},{"kind","transfer"},{"gpa",4.5}};addAcademicBackground(transfer,p.identity);
    if(transfer.at("gpa")!=academicGpa(p.identity)||transfer.at("kind")!="transfer")throw std::runtime_error("Existing transfer GPA kept its awareness linkage");
    const auto gpa=legacy.at("gpa");p.ratings["AwarenessRating"]=10;addResumeDetails(legacy,p);if(legacy.at("gpa")!=gpa)throw std::runtime_error("Stored GPA changed with awareness");
    legacy["stats"]["passAttempts"]=0;legacy["stats"]["passCompletions"]=0;legacy["stats"]["passingTD"]=0;legacy["stats"]["interceptionsThrown"]=0;addResumeDetails(legacy,p);validate(legacy);if(!legacy.at("rates").at("completionPercent").is_null())throw std::runtime_error("Zero attempts produced a percentage");
    for(const auto* position:{"QB","LT","WR","HB","CB","K","ATH"}){
        recruitingfog::NotesProspect notes;notes.identity="football-intelligence";notes.position=position;notes.progress=0;notes.observations={{"Awareness",90,90,true}};
        const auto hidden=scoutingSection(notes);notes.observations={{"Awareness",30,30,true}};if(scoutingSection(notes)!=hidden)throw std::runtime_error("Unscouted football intelligence leaked");
        notes.progress=40;notes.observations={{"Awareness",60,95,false}};if(scoutingSection(notes).find("too wide")==std::string::npos)throw std::runtime_error("Uncertain awareness range became a football claim");
        for(const auto rating:{55,75,90}){
            notes.observations={{"Awareness",double(rating),double(rating),true}};const auto text=scoutingSection(notes);
            if(text.find("too wide")!=std::string::npos||text.find("GPA")!=std::string::npos||text.find_first_of("0123456789")!=std::string::npos)throw std::runtime_error("Football intelligence report is missing or exposes an academic/numeric value");
        }
    }
    Json records={{"array",{{"v",{{"Member0","old"},{"Member1","current"},{"Member2","future"}}}}},
        {"old",{{"type","SeasonOffensiveStats"},{"v",{{"SEAS_YEAR",0},{"GAMESPLAYED",12},{"PASSATTEMPTS",300},{"PASSCOMPLETED",180}}}}},
        {"current",{{"type","SeasonOffensiveStats"},{"v",{{"SEAS_YEAR",1},{"YEARBYYEARTEAMINDEX",15},{"GAMESPLAYED",10},{"GAMESSTARTED",8},{"PASSATTEMPTS",200},{"PASSCOMPLETED",130},{"PASSYARDS",1800},{"PASSTDS",15},{"PASSINTS",4},{"RUSHATTEMPTS",70},{"RUSHYARDS",450},{"RUSHTDS",5}}}}},
        {"future",{{"type","SeasonOffensiveStats"},{"v",{{"SEAS_YEAR",2},{"GAMESPLAYED",12},{"PASSYARDS",9999}}}}}};
    const std::map<int,std::string> teams={{15,"BYU"}};Json player={{"SeasonStats","array"},{"TeamIndex",15}};
    const auto actual=transferSeason(records,player,1,teams);const auto report=renderTransfer(actual,3.2,2027,1);
    if(actual.at("rows").size()!=1||report.find("130/200 (65.0%)")==std::string::npos||report.find("450 yards")==std::string::npos||report.find("BYU")==std::string::npos||report.find("9999")!=std::string::npos)throw std::runtime_error("Transfer did not use the latest actual dual-threat line");
    const auto missing=transferSeason(records,Json::object(),1,teams);if(renderTransfer(missing,3.2,2027,1).find("No recorded college statistics")==std::string::npos)throw std::runtime_error("Transfer fallback invented statistics");
    records["career"]={{"type","CareerOffensiveStats"},{"v",{{"GAMESPLAYED",20},{"PASSATTEMPTS",400},{"PASSCOMPLETED",250}}}};player={{"CareerStats","career"},{"TeamIndex",15}};
    if(!transferSeason(records,player,1,teams).at("career").get<bool>())throw std::runtime_error("Actual career fallback was ignored");
    // Raymond Liggins screenshot regression. Return specialists use a derived
    // native class, not SeasonOffensiveStats, while retaining receiving fields.
    Json liggins={{"array",{{"type","SeasonStats[]"},{"v",{{"Member0","line"}}}}},
        {"line",{{"type","SeasonOffensiveKPReturnStats"},{"v",{{"SEAS_YEAR",2},{"YEARBYYEARTEAMINDEX",98},{"GAMESPLAYED",13},{"GAMESSTARTED",13},{"RECEIVECATCHES",54},{"RECEIVEYARDS",896},{"RECEIVETDS",8},{"RECEIVEYARDSAFTER",218},{"RECEIVELONGEST",75},{"PRETATTEMPTS",4},{"PRETYARDS",39},{"PRETTDS",0}}}}}};
    const Json ligginsPlayer={{"SeasonStats","array"},{"TeamIndex",255}};const std::map<int,std::string> schools={{98,"UConn"}};
    const auto recordedLiggins=transferSeason(liggins,ligginsPlayer,3,schools);const auto ligginsBefore=liggins;
    const auto receiving=renderTransfer(recordedLiggins,3.8,2029,3);
    for(const auto* expected:{"2028","UConn","13 games played","54 catches, 896 yards, 8 TD","218 YAC","75 long","Punt returns: 4 returns, 39 yards, 0 TD"})if(receiving.find(expected)==std::string::npos)throw std::runtime_error(std::string("Return-specialist transfer missing recorded field: ")+expected);
    if(receiving.find("starts")!=std::string::npos||liggins!=ligginsBefore)throw std::runtime_error("Transfer report published starts or changed native stats");
    liggins["line"]["v"].erase("GAMESPLAYED");liggins["line"]["v"].erase("RECEIVETDS");
    auto sparse=renderTransfer(transferSeason(liggins,ligginsPlayer,3,schools),3.8,2029,3);
    if(sparse.find("54 catches, 896 yards")==std::string::npos||sparse.find("games played")!=std::string::npos||sparse.find("Receiving: 54 catches, 896 yards, 0 TD")!=std::string::npos)throw std::runtime_error("Missing transfer fields were dropped with valid production or invented as zero");
    liggins["career"]={{"type","CareerOffensiveKPReturnStats"},{"v",{{"RECEIVECATCHES",95},{"RECEIVEYARDS",1420},{"RECEIVETDS",12}}}};
    auto totals=renderTransfer(transferSeason(liggins,Json{{"CareerStats","career"}},3,schools),3.8,2029,3);
    if(totals.find("COLLEGE CAREER RECORD")==std::string::npos||totals.find("95 catches, 1,420 yards, 12 TD")==std::string::npos||totals.find("games played")!=std::string::npos)throw std::runtime_error("Career returner totals require an unavailable games-played field");
    liggins["line"]["type"]="SeasonDefensiveKPReturnStats";liggins["line"]["v"]={{"SEAS_YEAR",2},{"DEFTACKLES",42},{"ASSDEFTACKLES",15},{"DLINESACKS",2},{"DLINEHALFSACK",1},{"DSECINTS",3},{"PRETATTEMPTS",8},{"PRETYARDS",121},{"PRETTDS",1}};
    const auto defender=renderTransfer(transferSeason(liggins,ligginsPlayer,3,schools),3.8,2029,3);
    if(defender.find("Tackles: 57")==std::string::npos||defender.find("Sacks: 2.5")==std::string::npos||defender.find("Punt returns: 8 returns, 121 yards, 1 TD")==std::string::npos||defender.find("starts")!=std::string::npos)throw std::runtime_error("Defensive return specialist was omitted or reported fabricated fields");
    auto sparseDefense=liggins;sparseDefense["line"]["v"]={{"SEAS_YEAR",2},{"DLINEFORCEDFUMBLES",2},{"DLINEFUMBLERECOVERIES",1}};
    const auto fumbles=renderTransfer(transferSeason(sparseDefense,ligginsPlayer,3,schools),3.8,2029,3);
    if(fumbles.find("2 forced fumbles, 1 fumble recoveries")==std::string::npos||fumbles.find("games played")!=std::string::npos)throw std::runtime_error("Partial recorded defense was omitted or given invented games");
    NativeEntry portal;portal.classYear="JR";portal.redshirt=true;
    if(nativeTransferClass(portal)!="TR (JR RS)"||nativeRecruitClassLabel(portal,"Transfer (JR)")!="TR (JR RS)"||!nativeRecruitClassLabel(portal,"Transfer (SO)").empty())throw std::runtime_error("Transfer redshirt class labeling lost its year gate");
    portal.redshirt=false;if(nativeTransferClass(portal)!="TR (JR)"||nativeRecruitClassLabel(portal,"Transfer (JR)")!="TR (JR)")throw std::runtime_error("An eligible/ineligible transfer received an incorrect compact class");
    portal.redshirt=true;portal.juniorCollege=true;portal.saved={{"competitionClass","FCS"}};
    if(!nativeTransferClass(portal).empty()||nativeRecruitClassLabel(portal,"JC (JR)")!="FCS (JR)")throw std::runtime_error("Transfer redshirt handling changed the generated JUCO association");
    if(nativeClassYear("Transfer_Freshman")!="FR"||nativeClassYear("Senior")!="SR"||!nativeClassYear("Unknown").empty())throw std::runtime_error("Native transfer class year mapping differs");
    // A native transfer's actual RedshirtStatus, not its age/class label,
    // controls the RS tag. High-school/JUCO generation stays on its own path.
    Json native={{"format",1},{"sourceKind","runtime"},{"status",{{"league",123},{"season",{{"CurrentSeasonYear",2029},{"CurrentYear",3}}}}},{"records",Json::object()}};
    native["records"]["1:0"]={{"key","1:0"},{"type","Recruit"},{"capacity",10},{"v",{{"Class","Transfer_Junior"},{"Player","2:0"}}}};
    native["records"]["2:0"]={{"type","Player"},{"v",{{"FirstName","Raymond"},{"LastName","Liggins"},{"PresentationId",100},{"Position","WR"},{"TraitDevelopment","Normal"},{"PLYR_HOME_STATE","Connecticut"},{"PLYR_HOME_TOWN","Hartford"},{"SchoolYear","Junior"},{"RedshirtStatus","Previous"},{"SeasonStats","array"}}}};
    native["records"]["array"]=liggins.at("array");native["records"]["line"]=ligginsBefore.at("line");
    const auto parsedPortal=parseNativeClass(native);const auto& parsedEntry=parsedPortal.entries.at(131072);
    if(!parsedEntry.redshirt||parsedEntry.classYear!="JR"||parsedEntry.actual.at("rows").size()!=1)throw std::runtime_error("Native transfer source lost its redshirt status or returner stats");
    native["records"]["2:0"]["v"]["RedshirtStatus"]="Eligible";
    if(parseNativeClass(native).entries.at(131072).redshirt)throw std::runtime_error("Native eligible transfer was inferred to be redshirted");
    native["records"]["1:0"]["v"]["Class"]="HighSchool";
    const auto parsedHighSchool=parseNativeClass(native).entries.at(131072);
    if(!parsedHighSchool.highSchool||parsedHighSchool.redshirt||!parsedHighSchool.actual.is_null())throw std::runtime_error("High-school prospect was changed to a transfer college record");
    return {{"academicPairs",6000},{"academicIndependence",true},{"gpaMean",gpaTotal/6000},{"middleGpaShare",double(middle)/6000},{"edgeGpaShare",double(edges)/6000},{"nearbyCollegeShare",double(nearby)/assigned},{"collegeLevels",levels},{"additiveMigration",true},{"actualTransferStats",true},{"returnSpecialistTransferStats",true},{"missingTransferFieldsNotInvented",true},{"transferRedshirtClass",true}};
}
