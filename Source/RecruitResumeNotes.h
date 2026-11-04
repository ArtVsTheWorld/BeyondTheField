#pragma once
#include "RecruitResume.h"
#include "RecruitNotes.h"
#include "RecruitNotesProse.h"
#include <iomanip>
#include <sstream>
#include <set>
namespace recruitingfog::resume {
inline std::string formatted(int value){auto s=std::to_string(value);for(int i=int(s.size())-3;i>0;i-=3)s.insert(size_t(i),",");return s;}
inline std::string stateLabel(const std::string& value){if(value=="NonUS")return "Outside US";std::string s;for(char c:value){if(!s.empty()&&c>='A'&&c<='Z')s+=' ';s+=c;}return s;}
inline std::string renderResume(const Json& v){
    validate(v);const auto& s=v.at("stats");auto n=[&](const char* k){return formatted(s.value(k,0));};
    std::string out="PREVIOUS HIGH SCHOOL SEASON\n"+v.value("hometown","")+", "+stateLabel(v.value("state",""))+" | "+v.at("competitionClass").get<std::string>()+"\n";
    out+=std::to_string(v.at("games").get<int>())+" appearances | "+std::to_string(v.at("starts").get<int>())+" starts\n";
    if(s.contains("passAttempts"))out+="Passing: "+n("passCompletions")+"/"+n("passAttempts")+", "+n("passingYards")+" yards, "+n("passingTD")+" TD, "+n("interceptionsThrown")+" INT\n";
    if(s.contains("carries"))out+="Rushing: "+n("carries")+" carries, "+n("rushingYards")+" yards, "+n("rushingTD")+" TD\n";
    if(s.contains("receptions"))out+="Receiving: "+n("receptions")+" catches, "+n("receivingYards")+" yards, "+n("receivingTD")+" TD\n";
    if(s.contains("passProtectionSnaps")){
        std::ostringstream rate;if(v.at("rates").at("sacksAllowedPercent").is_null())rate<<"--";else rate<<std::fixed<<std::setprecision(1)<<v.at("rates").at("sacksAllowedPercent").get<double>()<<'%';
        out+="Pass protection: "+n("sacksAllowed")+" sacks allowed / "+n("passProtectionSnaps")+" snaps ("+rate.str()+")\n";
    }
    if(s.contains("pancakes"))out+="Run blocking: "+n("pancakes")+" pancakes / "+n("runBlockingSnaps")+" snaps\n";
    if(s.contains("defensiveSnaps")){
        out+="Defense: "+n("tackles")+" tackles, "+n("tacklesForLoss")+" TFL, "+n("sacks")+" sacks\n";
        out+="Coverage/turnovers: "+n("interceptions")+" INT, "+n("passesDefended")+" breakups, "+n("forcedFumbles")+" forced fumbles\n";
    }
    if(s.contains("fieldGoalAttempts"))out+="Kicking: "+n("fieldGoalsMade")+"/"+n("fieldGoalAttempts")+" FG, long "+n("longestFieldGoal")+"; "+n("extraPointsMade")+"/"+n("extraPointAttempts")+" XP\n";
    if(s.contains("punts")){const auto punts=s.at("punts").get<int>();std::ostringstream avg;avg<<std::fixed<<std::setprecision(1)<<(punts?s.at("puntingYards").get<double>()/punts:0.);out+="Punting: "+n("punts")+" punts, "+avg.str()+" average, "+n("puntsInside20")+" inside the 20\n";}
    if(s.contains("specialTeamsSnaps"))out+="Long snapping: "+n("badSnaps")+" off-target snaps / "+n("specialTeamsSnaps")+" snaps\n";
    return out+"\n"+v.at("background").get<std::string>();
}
inline std::string scoutingSection(const NotesProspect& p){
    const auto progress=std::isfinite(p.progress)&&p.progress>=0&&p.progress<=100?p.progress:0;
    if(progress<25)return "SCOUTING NOTES\nSpecific film observations are not yet available.";
    struct Pick{uint64_t order;std::string text;};std::vector<Pick> bands[3];std::set<std::string> seen;
    for(const auto& o:p.observations){
        if(!std::isfinite(o.low)||!std::isfinite(o.high)||o.low<0||o.high>100||o.low>o.high)continue;
        auto key=notesKey(o.name);if(key=="tackling")key="tackle";if(!seen.insert(key).second)continue;
        const int band=o.low>=80?0:o.low>=70&&o.high<80?1:o.high<70?2:-1;if(band<0)continue;
        for(const auto& entry:prose)if(key==entry.attribute){const auto seed=notesHash(p.identity+"|"+key+"|"+std::to_string(band));bands[band].push_back({seed,entry.bands[band][seed%3]});break;}
    }
    for(auto& b:bands)std::sort(b.begin(),b.end(),[](const Pick& a,const Pick& b){return a.order<b.order;});
    std::string out="SCOUTING NOTES";unsigned used=0;const unsigned limit=progress>=75?4:progress>=50?3:2;
    // Take a balanced first observation from each supported band; additional
    // scouting adds to the report without rewriting already-selected phrases.
    for(size_t round=0;round<4&&used<limit;++round)for(auto& b:bands)if(round<b.size()&&used<limit){out+="\n"+b[round].text;++used;}
    if(!used)out+="\nThe available scouting still leaves too wide a range for a firm observation.";
    return out;
}
inline std::string composeNotes(const Json& saved,const NotesProspect& p){return renderResume(saved)+"\n\n"+scoutingSection(p);}
}
