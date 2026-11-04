#pragma once
#include "RecruitResumeNotes.h"
namespace recruitingfog::resume {
inline const Json* nativeReference(const Json& records,const Json& owner,const char* field){
    if(!owner.contains(field)||!owner.at(field).is_string())return nullptr;
    const auto found=records.find(owner.at(field).get<std::string>());return found==records.end()?nullptr:&*found;
}
// Read actual player-linked season rows, never infer a college line from ability.
// SEAS_YEAR is a Dynasty-relative year, not a calendar year.
inline Json transferSeason(const Json& records,const Json& player,int currentYear,const std::map<int,std::string>& teams){
    Json rows=Json::array();int newest=-1;
    if(const auto* array=nativeReference(records,player,"SeasonStats"))for(const auto& ref:array->at("v")){
        if(!ref.is_string())continue;const auto found=records.find(ref.get<std::string>());if(found==records.end())continue;
        const auto& row=*found;const auto& v=row.at("v");const int year=v.value("SEAS_YEAR",-1);
        if(year<0||year>currentYear||v.value("GAMESPLAYED",0)<=0)continue;
        if(year>newest){newest=year;rows=Json::array();}if(year==newest)rows.push_back(row);
    }
    bool career=false;if(rows.empty()){
        if(const auto* row=nativeReference(records,player,"CareerStats"))if(row->at("v").value("GAMESPLAYED",0)>0){rows.push_back(*row);career=true;}
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
    int games=0,starts=0;for(const auto& row:actual.at("rows")){games=(std::max)(games,row.at("v").value("GAMESPLAYED",0));starts=(std::max)(starts,row.at("v").value("GAMESSTARTED",0));}
    out+=std::to_string(games)+" appearances | "+std::to_string(starts)+" starts\n";
    for(const auto& row:actual.at("rows")){
        const auto& s=row.at("v");const auto type=row.at("type").get<std::string>();auto n=[&](const char* key){return formatted(s.value(key,0));};
        if(type.find("OffensiveStats")!=std::string::npos){
            if(s.value("PASSATTEMPTS",0))out+="Passing: "+n("PASSCOMPLETED")+"/"+n("PASSATTEMPTS")+" ("+percent(s.value("PASSCOMPLETED",0),s.value("PASSATTEMPTS",0))+"), "+n("PASSYARDS")+" yards, "+n("PASSTDS")+" TD, "+n("PASSINTS")+" INT\n";
            if(s.value("RUSHATTEMPTS",0))out+="Rushing: "+n("RUSHATTEMPTS")+" carries, "+n("RUSHYARDS")+" yards, "+n("RUSHTDS")+" TD\n";
            if(s.value("RECEIVECATCHES",0))out+="Receiving: "+n("RECEIVECATCHES")+" catches, "+n("RECEIVEYARDS")+" yards, "+n("RECEIVETDS")+" TD\n";
        }else if(type.find("DefensiveStats")!=std::string::npos){
            std::ostringstream sacks;sacks<<s.value("DLINESACKS",0)+.5*s.value("DLINEHALFSACK",0);
            out+="Defense: "+formatted(s.value("DEFTACKLES",0)+s.value("ASSDEFTACKLES",0))+" tackles, "+n("DEFTACKLESFORLOSS")+" TFL, "+sacks.str()+" sacks\n";
            out+="Coverage/turnovers: "+n("DSECINTS")+" INT, "+n("DEFPASSDEFLECTIONS")+" breakups, "+n("DLINEFORCEDFUMBLES")+" forced fumbles\n";
        }else if(type.find("OLineStats")!=std::string::npos){
            out+="Blocking: "+n("OLINESACKSALLOWED")+" sacks allowed, "+n("OLINEPANCAKES")+" pancakes / "+n("DOWNSPLAYED")+" total snaps\n";
            out+="Pass/run snap splits are not recorded; blocking rates unavailable.\n";
        }else if(type.find("KickingStats")!=std::string::npos){
            if(s.value("KICKFGATTEMPTS",0)||s.value("KICKEPATTEMPTS",0))out+="Kicking: "+n("KICKFGMADE")+"/"+n("KICKFGATTEMPTS")+" FG, long "+n("KICKFGLONGEST")+"; "+n("KICKEPMADE")+"/"+n("KICKEPATTEMPTS")+" XP\n";
            if(s.value("PUNTATTEMPTS",0)){std::ostringstream avg;avg<<std::fixed<<std::setprecision(1)<<double(s.value("PUNTYARDS",0))/s.at("PUNTATTEMPTS").get<int>();out+="Punting: "+n("PUNTATTEMPTS")+" punts, "+avg.str()+" average, "+n("PUNTIN20")+" inside the 20\n";}
        }
    }
    return out;
}
}
