#pragma once
inline nlohmann::json expansionTests(){
    using namespace recruitingfog::resume;
    Prospect p;p.identity="expansion";p.position="QB";p.stars=3;p.state="NorthCarolina";p.ratings={{"OverallRating",70},{"AwarenessRating",70}};
    double low=0,high=0;int nearby=0,assigned=0;std::set<std::string> levels;
    const std::set<std::string> active={schoolKey("Elon University"),schoolKey("North Dakota State"),schoolKey("Mount Union")};
    for(int i=0;i<6000;++i){
        p.identity="academic-pair-"+std::to_string(i);p.ratings["AwarenessRating"]=40;low+=academicGpa(p);p.ratings["AwarenessRating"]=90;high+=academicGpa(p);
        const auto* school=chooseCollege(p,active);if(!school||schoolCollision(*school,active))throw std::runtime_error("Prior school collides with Dynasty");
        ++assigned;if(schoolRegion(school->state)==schoolRegion(p.state))++nearby;
        p.collegeLevel=school->level;p.collegeSchool=school->name;levels.insert(p.collegeLevel);auto resume=generate(p).publicData;validate(resume);
        if(resume.at("heading")!="Previous College Season"||resume.at("background").get<std::string>().find("varsity")!=std::string::npos)throw std::runtime_error("JUCO profile still uses a high school background");
        p.collegeLevel.clear();p.collegeSchool.clear();
        if(resume.at("gpa").get<double>()<2||resume.at("gpa").get<double>()>4.5)throw std::runtime_error("GPA outside range");
    }
    if(levels.size()!=3||high-low<6000*.4||nearby<assigned*.40)throw std::runtime_error("Academic/college background balance failed");
    p.identity="zero-opportunity";auto legacy=generate(p).publicData;legacy["modelVersion"]=2;legacy.erase("gpa");legacy["rates"].erase("completionPercent");
    const auto originalStats=legacy.at("stats"),originalClass=legacy.at("competitionClass");addResumeDetails(legacy,p);validate(legacy);
    if(legacy.at("stats")!=originalStats||legacy.at("competitionClass")!=originalClass)throw std::runtime_error("Migration rerolled the prior season");
    const auto gpa=legacy.at("gpa");p.ratings["AwarenessRating"]=10;addResumeDetails(legacy,p);if(legacy.at("gpa")!=gpa)throw std::runtime_error("Stored GPA changed with awareness");
    legacy["stats"]["passAttempts"]=0;legacy["stats"]["passCompletions"]=0;legacy["stats"]["passingTD"]=0;legacy["stats"]["interceptionsThrown"]=0;addResumeDetails(legacy,p);validate(legacy);if(!legacy.at("rates").at("completionPercent").is_null())throw std::runtime_error("Zero attempts produced a percentage");
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
    return {{"academicPairs",6000},{"higherVsLowerAwarenessMeanGpaGap",(high-low)/6000},{"nearbyCollegeShare",double(nearby)/assigned},{"collegeLevels",levels},{"additiveMigration",true},{"actualTransferStats",true}};
}
