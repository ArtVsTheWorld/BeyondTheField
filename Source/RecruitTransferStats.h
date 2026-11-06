#pragma once
#include "RecruitResumeNotes.h"
namespace recruitingfog::resume {
inline const Json* nativeReference(const Json& records,const Json& owner,const char* field){
    if(!owner.contains(field)||!owner.at(field).is_string())return nullptr;
    const auto found=records.find(owner.at(field).get<std::string>());return found==records.end()?nullptr:&*found;
}
inline bool actualCollegeStat(const Json& row,const char* key,int64_t& value){
    const auto field=row.find(key);if(field==row.end()||!field->is_number_integer())return false;
    value=field->get<int64_t>();return true;
}
inline std::string formattedCollegeStat(int64_t value){
    auto text=std::to_string(value);for(int i=int(text.size())-3;i>(value<0?1:0);i-=3)text.insert(size_t(i),",");return text;
}
inline bool hasCollegeProduction(const Json& row){
    for(const auto* key:{"GAMESPLAYED","DOWNSPLAYED","PASSATTEMPTS","PASSCOMPLETED","PASSYARDS","PASSTDS","PASSINTS","RUSHATTEMPTS","RUSHYARDS","RUSHTDS","RECEIVECATCHES","RECEIVEYARDS","RECEIVETDS","RECEIVEYARDSAFTER","RECEIVELONGEST","DEFTACKLES","ASSDEFTACKLES","DEFTACKLESFORLOSS","DLINESACKS","DLINEHALFSACK","DSECINTS","DEFPASSDEFLECTIONS","DLINEFORCEDFUMBLES","DLINEFUMBLERECOVERIES","OLINEPANCAKES","OLINESACKSALLOWED","KICKFGATTEMPTS","KICKFGMADE","KICKFGLONGEST","KICKEPATTEMPTS","KICKEPMADE","PUNTATTEMPTS","PUNTYARDS","PUNTIN20","KRETATTEMPTS","KRETYARDS","KRETTDS","PRETATTEMPTS","PRETYARDS","PRETTDS"}){
        int64_t value=0;if(actualCollegeStat(row,key,value)&&value!=0)return true;
    }return false;
}
inline bool collegeOffenseType(const std::string& type){return type=="SeasonOffensiveStats"||type=="CareerOffensiveStats"||type=="SeasonOffensiveKPReturnStats"||type=="CareerOffensiveKPReturnStats";}
inline bool collegeDefenseType(const std::string& type){return type=="SeasonDefensiveStats"||type=="CareerDefensiveStats"||type=="SeasonDefensiveKPReturnStats"||type=="CareerDefensiveKPReturnStats";}
inline bool collegeStatType(const std::string& type){return collegeOffenseType(type)||collegeDefenseType(type)||type=="SeasonOLineStats"||type=="CareerOLineStats"||type=="SeasonKickingStats"||type=="CareerKickingStats";}
// Read actual player-linked season rows, never infer a college line from ability.
// SEAS_YEAR is a Dynasty-relative year, not a calendar year.
inline Json transferSeason(const Json& records,const Json& player,int currentYear,const std::map<int,std::string>& teams){
    Json rows=Json::array();int newest=-1;
    if(const auto* array=nativeReference(records,player,"SeasonStats"))for(const auto& ref:array->at("v")){
        if(!ref.is_string())continue;const auto found=records.find(ref.get<std::string>());if(found==records.end())continue;
        const auto& row=*found;const auto& v=row.at("v");const int year=v.value("SEAS_YEAR",-1);
        if(year<0||year>currentYear||!collegeStatType(row.at("type"))||!hasCollegeProduction(v))continue;
        if(year>newest){newest=year;rows=Json::array();}if(year==newest)rows.push_back(row);
    }
    bool career=false;if(rows.empty()){
        if(const auto* row=nativeReference(records,player,"CareerStats"))if(collegeStatType(row->at("type"))&&hasCollegeProduction(row->at("v"))){rows.push_back(*row);career=true;}
    }
    Json out={{"source","dynasty"},{"career",career},{"relativeYear",newest},{"rows",rows}};
    std::set<std::string> names;for(const auto& row:rows){const int index=row.at("v").value("YEARBYYEARTEAMINDEX",-1);const auto team=teams.find(index);if(team!=teams.end()&&!team->second.empty())names.insert(team->second);}
    if(names.empty()){const auto team=teams.find(player.value("TeamIndex",-1));if(team!=teams.end()&&!team->second.empty())names.insert(team->second);}
    out["schools"]=names;return out;
}
inline std::string renderTransfer(const Json& actual,double gpa,int calendarYear,int relativeYear){
    std::ostringstream academic;academic<<std::fixed<<std::setprecision(2)<<gpa;
    const bool career=actual.value("career",false);std::string out=career?"COLLEGE CAREER RECORD":"LATEST RECORDED COLLEGE SEASON";
    if(!career&&actual.value("relativeYear",-1)>=0)out+=" | "+std::to_string(calendarYear-relativeYear+actual.at("relativeYear").get<int>());
    out+="\n";bool first=true;for(const auto& name:actual.at("schools")){if(!first)out+=" / ";out+=name.get<std::string>();first=false;}
    if(!first)out+=" | ";out+="GPA: "+academic.str()+"\n";
    if(actual.at("rows").empty())return out+"No recorded college statistics are available.\n";
    auto percent=[](double n,double d){std::ostringstream s;if(!d)return std::string("--");s<<std::fixed<<std::setprecision(1)<<100*n/d<<'%';return s.str();};
    // GP is published only when recorded. Starts are omitted: they are not
    // presented by the game's Career Stats view and must never be inferred.
    int64_t games=-1;for(const auto& row:actual.at("rows")){int64_t value=0;if(actualCollegeStat(row.at("v"),"GAMESPLAYED",value)&&value>=0)games=(std::max)(games,value);}
    if(games>=0)out+=formattedCollegeStat(games)+" games played\n";
    for(const auto& row:actual.at("rows")){
        const auto& s=row.at("v");const auto type=row.at("type").get<std::string>();auto n=[&](const char* key){return formattedCollegeStat(s.at(key).get<int64_t>());};
        auto has=[&](const char* key){int64_t value=0;return actualCollegeStat(s,key,value);};
        auto line=[&](const std::string& heading,const std::vector<std::pair<const char*,const char*>>& fields){std::string text;for(const auto& [key,suffix]:fields)if(has(key)){if(!text.empty())text+=", ";text+=n(key)+suffix;}if(!text.empty())out+=heading+text+"\n";};
        if(collegeOffenseType(type)){
            if(s.value("PASSATTEMPTS",0)||s.value("PASSYARDS",0)||s.value("PASSTDS",0)){
                std::string passing;if(has("PASSCOMPLETED")&&has("PASSATTEMPTS"))passing=n("PASSCOMPLETED")+"/"+n("PASSATTEMPTS")+" ("+percent(s.at("PASSCOMPLETED"),s.at("PASSATTEMPTS"))+")";
                for(const auto& [key,suffix]:std::vector<std::pair<const char*,const char*>>{{"PASSYARDS"," yards"},{"PASSTDS"," TD"},{"PASSINTS"," INT"}})if(has(key)){if(!passing.empty())passing+=", ";passing+=n(key)+suffix;}
                if(!passing.empty())out+="Passing: "+passing+"\n";
            }
            if(s.value("RUSHATTEMPTS",0)||s.value("RUSHYARDS",0)||s.value("RUSHTDS",0))line("Rushing: ",{{"RUSHATTEMPTS"," carries"},{"RUSHYARDS"," yards"},{"RUSHTDS"," TD"}});
            if(s.value("RECEIVECATCHES",0)||s.value("RECEIVEYARDS",0)||s.value("RECEIVETDS",0))line("Receiving: ",{{"RECEIVECATCHES"," catches"},{"RECEIVEYARDS"," yards"},{"RECEIVETDS"," TD"},{"RECEIVEYARDSAFTER"," YAC"},{"RECEIVELONGEST"," long"}});
        }else if(collegeDefenseType(type)){
            if(has("DEFTACKLES")&&has("ASSDEFTACKLES"))out+="Tackles: "+formattedCollegeStat(s.at("DEFTACKLES").get<int64_t>()+s.at("ASSDEFTACKLES").get<int64_t>())+"\n";
            else line("Tackles: ",{{"DEFTACKLES"," solo"},{"ASSDEFTACKLES"," assisted"}});
            if(has("DLINESACKS")&&has("DLINEHALFSACK")){std::ostringstream sacks;sacks<<s.at("DLINESACKS").get<int64_t>()+.5*s.at("DLINEHALFSACK").get<int64_t>();out+="Sacks: "+sacks.str()+"\n";}
            line("Defense: ",{{"DEFTACKLESFORLOSS"," TFL"},{"DSECINTS"," INT"},{"DEFPASSDEFLECTIONS"," breakups"},{"DLINEFORCEDFUMBLES"," forced fumbles"},{"DLINEFUMBLERECOVERIES"," fumble recoveries"}});
        }else if(type.find("OLineStats")!=std::string::npos){
            line("Blocking: ",{{"OLINESACKSALLOWED"," sacks allowed"},{"OLINEPANCAKES"," pancakes"},{"DOWNSPLAYED"," total snaps"}});
            out+="Pass/run snap splits are not recorded; blocking rates unavailable.\n";
        }else if(type.find("KickingStats")!=std::string::npos){
            if(s.value("KICKFGATTEMPTS",0)||s.value("KICKEPATTEMPTS",0))line("Kicking: ",{{"KICKFGMADE"," field goals made"},{"KICKFGATTEMPTS"," field-goal attempts"},{"KICKFGLONGEST"," longest"},{"KICKEPMADE"," extra points made"},{"KICKEPATTEMPTS"," extra-point attempts"}});
            if(s.value("PUNTATTEMPTS",0)){std::string punting=n("PUNTATTEMPTS")+" punts";if(has("PUNTYARDS")){std::ostringstream avg;avg<<std::fixed<<std::setprecision(1)<<double(s.at("PUNTYARDS").get<int64_t>())/s.at("PUNTATTEMPTS").get<int64_t>();punting+=", "+avg.str()+" average";}if(has("PUNTIN20"))punting+=", "+n("PUNTIN20")+" inside the 20";out+="Punting: "+punting+"\n";}
        }
        if(s.value("KRETATTEMPTS",0)||s.value("KRETYARDS",0)||s.value("KRETTDS",0))line("Kick returns: ",{{"KRETATTEMPTS"," returns"},{"KRETYARDS"," yards"},{"KRETTDS"," TD"}});
        if(s.value("PRETATTEMPTS",0)||s.value("PRETYARDS",0)||s.value("PRETTDS",0))line("Punt returns: ",{{"PRETATTEMPTS"," returns"},{"PRETYARDS"," yards"},{"PRETTDS"," TD"}});
    }
    return out;
}
}
