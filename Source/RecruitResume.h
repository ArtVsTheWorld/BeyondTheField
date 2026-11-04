#pragma once
#include "../Vendor/json.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <map>
#include <stdexcept>
#include <string>

namespace recruitingfog::resume {
using Json=nlohmann::json;
inline double clamp(double v,double low,double high){return (std::max)(low,(std::min)(high,v));}
inline uint64_t hash(const std::string& value){uint64_t h=14695981039346656037ull;for(unsigned char c:value){h^=c;h*=1099511628211ull;}return h;}
struct Random {
    uint64_t state;
    explicit Random(const std::string& seed):state(hash(seed)){}
    double unit(){uint64_t z=(state+=0x9e3779b97f4a7c15ull);z=(z^(z>>30))*0xbf58476d1ce4e5b9ull;z=(z^(z>>27))*0x94d049bb133111ebull;return double((z^(z>>31))>>11)/9007199254740992.;}
    double between(double low,double high){return low+(high-low)*unit();}
    double noise(){double z=0;for(int i=0;i<12;++i)z+=unit();return z-6;}
    int integer(int low,int high){return low+int(unit()*(high-low+1));}
};
inline int count(double value){return int(std::lround((std::max)(0.,value)));}
struct Prospect {
    std::string identity,name,position,state,town,development,collegeLevel,collegeSchool;int stars=0,stateRank=0;
    std::map<std::string,double> ratings;
    double rating(const char* key)const{auto it=ratings.find(key);if(it!=ratings.end())return it->second;auto overall=ratings.find("OverallRating");return overall==ratings.end()?60:overall->second;}
};
inline Prospect fromJson(const Json& input){
    Prospect p;p.identity=input.at("identity");p.name=input.at("name");p.position=input.at("position");p.state=input.value("state","");p.town=input.value("town","");p.development=input.value("development","");
    p.stars=input.contains("stars")&&!input["stars"].is_null()?input.at("stars").get<int>():0;p.stateRank=input.contains("stateRank")&&!input["stateRank"].is_null()?input.at("stateRank").get<int>():0;
    p.ratings=input.at("ratings").get<std::map<std::string,double>>();
    if(p.identity.empty()||!p.ratings.count("OverallRating"))throw std::runtime_error("Incomplete resume identity/ability");
    if(p.stars<1||p.stars>5||p.stateRank<0||p.stateRank>50)throw std::runtime_error("Invalid resume stars/state rank");
    const std::string positions="|QB|HB|RB|FB|WR|TE|LT|LG|C|RG|RT|LE|RE|DT|LEDG|REDG|LOLB|MLB|ROLB|SAM|MIKE|WILL|CB|FS|SS|K|P|LS|";
    if(p.position.empty()||positions.find("|"+p.position+"|")==std::string::npos)throw std::runtime_error("Unsupported resume position");
    for(const auto& [key,value]:p.ratings){(void)key;if(!std::isfinite(value)||value<0||value>100)throw std::runtime_error("Invalid underlying resume attribute");}
    return p;
}
inline double skill(const Prospect& p){
    const auto& pos=p.position;auto r=[&](const char* k){return p.rating(k);};
    if(pos=="QB")return .15*r("ThrowPowerRating")+.25*r("ThrowAccuracyShortRating")+.25*r("ThrowAccuracyMidRating")+.15*r("ThrowAccuracyDeepRating")+.20*r("AwarenessRating");
    if(pos=="HB"||pos=="RB"||pos=="FB")return .20*r("SpeedRating")+.15*r("AccelerationRating")+.20*r("BCVisionRating")+.20*r("BreakTackleRating")+.10*r("ChangeOfDirectionRating")+.15*r("CarryingRating");
    if(pos=="WR"||pos=="TE")return .20*r("SpeedRating")+.25*r("CatchingRating")+.20*r("ShortRouteRunningRating")+.20*r("MediumRouteRunningRating")+.15*r("ReleaseRating");
    if(pos=="LT"||pos=="LG"||pos=="C"||pos=="RG"||pos=="RT")return .35*r("PassBlockRating")+.35*r("RunBlockRating")+.20*r("StrengthRating")+.10*r("AwarenessRating");
    if(pos=="K"||pos=="P")return .45*r("KickPowerRating")+.55*r("KickAccuracyRating");
    if(pos=="LS")return .7*r("LongSnapRating")+.3*r("AwarenessRating");
    if(pos=="CB"||pos=="FS"||pos=="SS")return .25*r("ManCoverageRating")+.25*r("ZoneCoverageRating")+.2*r("SpeedRating")+.15*r("PlayRecognitionRating")+.15*r("CatchingRating");
    if(pos=="LE"||pos=="RE"||pos=="DT"||pos=="LEDG"||pos=="REDG")return .3*r("BlockSheddingRating")+.2*r("FinesseMovesRating")+.2*r("PowerMovesRating")+.2*r("TackleRating")+.1*r("StrengthRating");
    return .3*r("TackleRating")+.25*r("PlayRecognitionRating")+.2*r("BlockSheddingRating")+.15*r("SpeedRating")+.1*r("ZoneCoverageRating");
}
inline double academicGpa(const std::string& identity){
    // The API accepts identity alone: football ability, stars, development,
    // competition level and position cannot influence academic background.
    Random random(identity+"|academic-gpa-v2");
    const auto middleWeighted=(random.unit()+random.unit()+random.unit())/3.;
    return std::round((2.+2.5*middleWeighted)*100.)/100.;
}
inline void addAcademicBackground(Json& data,const std::string& identity){
    // One-time migration retires the old awareness-correlated GPA. Other
    // persisted biography and production fields remain untouched.
    if(!data.contains("gpa")||data.value("academicModelVersion",0)!=2)data["gpa"]=academicGpa(identity);
    data["academicModelVersion"]=2;
}
inline void addResumeDetails(Json& data,const Prospect& p){
    addAcademicBackground(data,p.identity);
    const auto& s=data.at("stats");auto& rates=data["rates"];if(!rates.is_object())rates=Json::object();
    auto rate=[&](const char* key,const char* numerator,const char* denominator){if(!s.contains(denominator))return;const auto n=s.value(numerator,0),d=s.at(denominator).get<int>();rates[key]=d?Json(std::round(1000.*n/d)/10.):Json(nullptr);};
    rate("completionPercent","passCompletions","passAttempts");rate("pancakePercent","pancakes","runBlockingSnaps");rate("sacksAllowedPercent","sacksAllowed","passProtectionSnaps");
    data["modelVersion"]=3;
}
struct Result {Json publicData;Json evaluation;};
inline Result generate(const Prospect& p){
    Random competition(p.identity+"|competition-v1"),opportunity(p.identity+"|opportunity-v1"),production(p.identity+"|production-v1"),blocking(p.identity+"|blocking-v1");
    const auto ability=skill(p);
    const int classification=competition.integer(1,6);
    // Rank is ordinal: soft bands avoid claiming measured gaps between states.
    const double state=p.stateRank==0?.5:p.stateRank<=5?.90:p.stateRank<=15?.75:p.stateRank<=30?.55:p.stateRank<=40?.38:.22;
    const double schedule=competition.between(0,1),level=p.collegeLevel.empty()?.50*state+.32*(classification-1)/5.+.18*schedule:p.collegeLevel=="FCS"?.78+.15*schedule:p.collegeLevel=="D2"?.48+.22*schedule:.22+.25*schedule;
    const int schoolGames=10+competition.integer(0,p.collegeLevel.empty()?5:2);
    const double roleRoll=opportunity.unit();std::string role;
    if(roleRoll<(p.stars>=4?.002:.025))role="No varsity appearances";
    else if(roleRoll<(p.stars>=4?.045:.13))role="Reserve";
    else {
        const double r=opportunity.unit()+.12*(ability-65)/20.+.04*(p.stars-3)-.10*(level-.5);
        role=r<.17?"Late-season starter":r<.37?"Shared role":"Regular starter";
    }
    int games=schoolGames,starts=schoolGames;double workload=1;
    if(role=="No varsity appearances"){games=0;starts=0;workload=0;}
    else if(role=="Reserve"){games=opportunity.integer(2,schoolGames);starts=0;workload=.10;}
    else if(role=="Late-season starter"){starts=opportunity.integer(2,(std::max)(2,schoolGames/2));workload=(starts+.12*(games-starts))/games;}
    else if(role=="Shared role"){starts=opportunity.integer(2,schoolGames);workload=opportunity.between(.43,.70);}
    // Separate per-position workload and efficiency; adjusted production never
    // becomes a direct algebraic encoding of ability or development.
    const double effective=games*workload,environment=.5-level;
    auto r=[&](const char* k){return p.rating(k);};Json stats=Json::object();
    auto put=[&](const char* key,double n){stats[key]=count(n);};
    const auto& pos=p.position;
    if(pos=="QB"){
        const auto attempts=count(effective*production.between(19,41));
        const auto accuracy=(r("ThrowAccuracyShortRating")+r("ThrowAccuracyMidRating")+r("ThrowAccuracyDeepRating"))/3;
        const auto completions=count(attempts*clamp(.58+.0032*(accuracy-65)+.10*environment+.045*production.noise(),.35,.84));
        const auto yards=count(completions*clamp(11.8+.045*(r("ThrowPowerRating")-65)+3.8*environment+1.6*production.noise(),7,20));
        put("passAttempts",attempts);put("passCompletions",completions);put("passingYards",yards);
        put("passingTD",(std::min)(completions,count(attempts*clamp(.055+.0013*(ability-65)+.055*environment+.02*production.noise(),.01,.20))));
        put("interceptionsThrown",(std::min)(attempts-completions,count(attempts*clamp(.035-.00065*(accuracy-65)-.02*environment+.012*production.noise(),.002,.10))));
        const auto carries=count(effective*clamp(3+(r("SpeedRating")-60)*.23+production.between(-2,5),1,15));put("carries",carries);
        const auto rushYards=count(carries*clamp(3.4+.085*(r("SpeedRating")-65)+2*environment+production.noise(),.5,11));put("rushingYards",rushYards);put("rushingTD",(std::min)(carries,count(rushYards/production.between(65,180))));
    }else if(pos=="HB"||pos=="RB"||pos=="FB"){
        const auto carries=count(effective*production.between(pos=="FB"?2:10,pos=="FB"?9:25));
        const auto yards=count(carries*clamp(5+.07*(ability-65)+3*environment+1.1*production.noise(),1.5,13));put("carries",carries);put("rushingYards",yards);put("rushingTD",(std::min)(carries,count(yards/production.between(65,160))));
        const auto catches=count(effective*production.between(.2,4.2)*clamp(r("CatchingRating")/65.,.3,1.4));put("receptions",catches);const auto recYards=count(catches*production.between(7,15));put("receivingYards",recYards);put("receivingTD",(std::min)(catches,count(recYards/production.between(110,240))));
    }else if(pos=="WR"||pos=="TE"){
        const auto targets=count(effective*production.between(pos=="TE"?2:4,pos=="TE"?8:12));
        const auto catches=count(targets*clamp(.57+.003*(r("CatchingRating")-65)+.09*environment+.06*production.noise(),.30,.90));
        const auto yards=count(catches*clamp(14+.09*(r("SpeedRating")-65)+4*environment+2*production.noise(),6,27));
        put("targets",targets);put("receptions",catches);put("receivingYards",yards);put("receivingTD",(std::min)(catches,count(yards/production.between(90,210))));
    }else if(pos=="LT"||pos=="LG"||pos=="C"||pos=="RG"||pos=="RT"){
        const auto snaps=count(effective*production.between(48,72)),passSnaps=count(snaps*production.between(.30,.65));put("offensiveSnaps",snaps);put("passProtectionSnaps",passSnaps);
        put("sacksAllowed",(std::min)(passSnaps,count(passSnaps*clamp(.027-.00075*(r("PassBlockRating")-65)-.025*environment+.009*production.noise(),.001,.10))));
    }else if(pos=="K"){
        const auto attempts=count(effective*production.between(.5,2.5)),made=count(attempts*clamp(.64+.008*(r("KickAccuracyRating")-65)+.065*production.noise(),.25,.98));
        put("fieldGoalAttempts",attempts);put("fieldGoalsMade",made);put("longestFieldGoal",made?clamp(39+.4*(r("KickPowerRating")-65)+production.between(-3,8),25,63):0);
        const auto xp=count(effective*production.between(2,6));put("extraPointAttempts",xp);put("extraPointsMade",xp-count(xp*clamp(.06-.0013*(r("KickAccuracyRating")-65)+.015*production.noise(),0,.14)));
    }else if(pos=="P"){
        const auto punts=count(effective*production.between(2,6));put("punts",punts);put("puntingYards",punts*clamp(37+.25*(r("KickPowerRating")-65)+2*production.noise(),25,52));put("puntsInside20",punts*production.between(.1,.5));
    }else if(pos=="LS"){
        const auto snaps=count(effective*production.between(5,12));put("specialTeamsSnaps",snaps);put("badSnaps",snaps*clamp(.025-.0008*(ability-65)+.01*production.noise(),0,.10));
    }else{
        const bool db=pos=="CB"||pos=="FS"||pos=="SS",line=pos=="LE"||pos=="RE"||pos=="DT"||pos=="LEDG"||pos=="REDG";
        const auto snaps=count(effective*production.between(40,65));const auto tackles=count(snaps*clamp((line?.08:db?.09:.14)+.0015*(r("TackleRating")-65)+.02*environment+.022*production.noise(),.025,.25));
        put("defensiveSnaps",snaps);put("tackles",tackles);
        const auto tfl=(std::min)(tackles,count(tackles*production.between(db?.01:.12,db?.12:.35)));put("tacklesForLoss",tfl);
        put("sacks",(std::min)(tfl,count(effective*clamp((db?.07:line?.65:.28)+.014*(ability-65)+.35*environment+.15*production.noise(),0,2))));
        put("forcedFumbles",(std::min)(tackles,count(tackles*production.between(.003,.035))));
        if(db){const auto coverage=(r("ManCoverageRating")+r("ZoneCoverageRating"))/2;const auto targets=count(effective*clamp(5-.06*(coverage-65)+production.noise(),1,9));put("coverageTargets",targets);const auto ints=count(targets*clamp(.07+.002*(r("CatchingRating")-65)+.04*environment+.025*production.noise(),.01,.22));put("interceptions",ints);put("passesDefended",(std::min)(targets-ints,count(targets*production.between(.1,.35))));}
        else{put("interceptions",effective*production.between(0,.25));put("passesDefended",effective*production.between(0,.6));}
    }
    Json rates=Json::object();
    const bool offensiveLine=pos=="LT"||pos=="LG"||pos=="C"||pos=="RG"||pos=="RT";
    if(offensiveLine||pos=="TE"||pos=="FB"){
        const auto snaps=offensiveLine?stats.at("offensiveSnaps").get<int>():count(effective*blocking.between(40,67));
        const auto runSnaps=offensiveLine?snaps-stats.at("passProtectionSnaps").get<int>():count(snaps*blocking.between(pos=="FB"?.48:.35,pos=="FB"?.78:.65));
        put("offensiveSnaps",snaps);put("runBlockingSnaps",runSnaps);
        const auto blockingSkill=.45*r("RunBlockRating")+.30*r("ImpactBlockingRating")+.25*r("StrengthRating");
        put("pancakes",runSnaps*clamp(.045+.0016*(blockingSkill-65)+.05*environment+.022*blocking.noise(),.001,.20));
        if(offensiveLine){const auto passSnaps=stats.at("passProtectionSnaps").get<int>();
            rates["sacksAllowedPercent"]=passSnaps?Json(std::round(1000.*stats.at("sacksAllowed").get<int>()/passSnaps)/10.):Json(nullptr);}
    }
    // Development is deliberately absent from every public output, including
    // background wording. The previous positional-settling hint is retired.
    std::string context;
    if(role=="No varsity appearances")context="Did not appear in a varsity game; spent the season behind an established starter.";
    else if(role=="Reserve")context="Most of his work came in a reserve role behind older players.";
    else if(role=="Late-season starter")context="Took over a starting role during the second half of the season.";
    else if(role=="Shared role")context="Shared the workload rather than playing every available series.";
    else context=schedule>.75?"The schedule included several opponents above the school's usual competition level.":schedule<.25?"Most opponents came from the same small regional pool.":"Played a full role against a mixed schedule of regional opponents.";
    Json publicData={{"modelVersion",2},{"heading","Previous High School Season"},{"state",p.state},{"hometown",p.town},{"competitionClass",std::to_string(classification)+"A"},{"games",games},{"starts",starts},{"role",role},{"stats",stats},{"rates",rates},{"background",context}};
    if(!p.collegeLevel.empty()){
        publicData["heading"]="Previous College Season";publicData["competitionClass"]=p.collegeLevel;publicData["collegeSchool"]=p.collegeSchool;
        if(role=="No varsity appearances"){publicData["role"]="No appearances";publicData["background"]="Did not appear in a game; spent the season behind an established starter.";}
        else if(role=="Reserve")publicData["background"]="Most of his work came in a reserve role.";
        else if(role=="Regular starter")publicData["background"]="Played a full role against the program's schedule.";
    }
    addResumeDetails(publicData,p);
    return {publicData,{{"overall",r("OverallRating")},{"positionSkill",ability},{"development",p.development},{"competition",level},{"stateRank",p.stateRank},{"schedule",schedule}}};
}
inline void validate(const Json& v){
    if(v.contains("gpa")&&(!v.at("gpa").is_number()||v.at("gpa").get<double>()<2||v.at("gpa").get<double>()>4.5))throw std::runtime_error("Invalid GPA");
    const int games=v.at("games"),starts=v.at("starts");if(games<0||games>15||starts<0||starts>games)throw std::runtime_error("Invalid playing opportunity");
    const auto& s=v.at("stats");for(auto it=s.begin();it!=s.end();++it)if(!it.value().is_number_integer()||it.value().get<int>()<0||(games==0&&it.value().get<int>()!=0))throw std::runtime_error("Invalid high-school statistic");
    auto bound=[&](const char* a,const char* b){if(s.contains(a)&&s.contains(b)&&s[a].get<int>()>s[b].get<int>())throw std::runtime_error(std::string("Invalid stat relationship: ")+a);};
    bound("passCompletions","passAttempts");bound("passingTD","passCompletions");bound("interceptionsThrown","passAttempts");bound("receptions","targets");bound("receivingTD","receptions");bound("rushingTD","carries");bound("sacks","tacklesForLoss");bound("tacklesForLoss","tackles");bound("forcedFumbles","tackles");bound("fieldGoalsMade","fieldGoalAttempts");bound("extraPointsMade","extraPointAttempts");bound("puntsInside20","punts");bound("passProtectionSnaps","offensiveSnaps");bound("sacksAllowed","passProtectionSnaps");bound("badSnaps","specialTeamsSnaps");
    bound("tackles","defensiveSnaps");
    bound("runBlockingSnaps","offensiveSnaps");bound("pancakes","runBlockingSnaps");
    if(v.contains("rates")&&v.at("rates").contains("sacksAllowedPercent")){
        const int attempts=s.at("passProtectionSnaps"),sacks=s.at("sacksAllowed");const auto& rate=v.at("rates").at("sacksAllowedPercent");
        if(attempts==0){if(!rate.is_null())throw std::runtime_error("Zero pass snaps must have no sack rate");}
        else if(!rate.is_number()||std::abs(rate.get<double>()-std::round(1000.*sacks/attempts)/10.)>.00001)throw std::runtime_error("Incorrect sacks-allowed percentage");
    }
    for(const auto& triple:{std::array<const char*,3>{"completionPercent","passCompletions","passAttempts"},std::array<const char*,3>{"pancakePercent","pancakes","runBlockingSnaps"}}){
        if(!s.contains(triple[2])||!v.contains("rates")||!v.at("rates").contains(triple[0]))continue;
        const int n=s.at(triple[1]),d=s.at(triple[2]);const auto& rate=v.at("rates").at(triple[0]);
        if(!d){if(!rate.is_null())throw std::runtime_error("Rate for zero opportunities");}
        else if(!rate.is_number()||std::abs(rate.get<double>()-std::round(1000.*n/d)/10.)>.00001)throw std::runtime_error("Incorrect derived percentage");
    }
    if(s.contains("coverageTargets")&&s.value("interceptions",0)+s.value("passesDefended",0)>s["coverageTargets"].get<int>())throw std::runtime_error("Coverage events exceed targets");
    if(s.contains("passCompletions")&&s.value("passCompletions",0)+s.value("interceptionsThrown",0)>s.value("passAttempts",0))throw std::runtime_error("Pass outcomes exceed attempts");
    for(const auto* hidden:{"overall","ratings","development","positionSkill","competition","stateRank"})if(v.contains(hidden))throw std::runtime_error("Hidden evaluation leaked into public resume");
}
}
