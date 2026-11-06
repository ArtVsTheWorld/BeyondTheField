#include "../Source/DraftResultsRuntime.h"
#include <cassert>
#include <iostream>
using namespace recruitingfog::draftresults;
Json sample(){
    Json result={{"format",2},{"sourceKind","runtime-draft-view"},{"league","4294954951"},{"season",2028},{"userTeam",1},{"actualRoundsOnly",true},{"rows",Json::array()},{"scopes",Json::array()}};
    result["scopes"].push_back({{"key","national"},{"label","National"},{"teams",{1,2}}});
    result["scopes"].push_back({{"key","conference:2:0"},{"label","Custom Conference"},{"teams",{1,2}}});
    for(int team=1;team<=2;++team)result["scopes"].push_back({{"key","team:"+std::to_string(team)},{"label","School "+std::to_string(team)},{"teams",{team}}});
    for(int i=0;i<224;++i)result["rows"].push_back({{"key","8:"+std::to_string(i)},{"name","Player "+std::to_string(i)},{"position","QB"},{"year","SR (RS)"},{"overall",85},{"team",i%2+1},{"school","School "+std::to_string(i%2+1)},{"conference","2:0"},{"round",i/32+1}});
    return result;
}
int main(){
    const Identity active{"4294954951",2028};auto data=sample();auto board=parse(data,active);assert(board.rows.size()==224&&board.scopes.size()==4&&board.wire.rfind("DE_DRAFT_2\t4294954951\t2028\t1\n",0)==0);
    assert(board.wire.find("P\t8:0\tPlayer 0\tQB\tSR (RS)\t85\t1\tSchool 1\t2:0\t1\n")!=std::string::npos);
    assert(board.wire.find("NFL")==std::string::npos);
    for(size_t i=1;i<board.rows.size();++i){const auto& a=board.rows[i-1];const auto& b=board.rows[i];assert(std::tie(a.round,a.school,a.name,a.key)<=std::tie(b.round,b.school,b.name,b.key));}
    Cache cache;assert(!cache.current(active));assert(cache.takeRequest());cache.publish(data,active);assert(cache.current(active));assert(!cache.current({active.league,2029}));
    unsigned setters=0;assert(cache.inject(active,123,[&](uintptr_t target,const char* field,const char* text){assert(target==123&&std::string(field)=="DEDraftBoard"&&std::string(text)==board.wire);++setters;}));assert(setters==1);
    auto reject=[&](Json bad,const Identity& id){bool rejected=false;try{parse(bad,id);}catch(const std::exception&){rejected=true;}assert(rejected);};
    reject(data,{"123",2028});reject(data,{active.league,2029});
    auto bad=data;bad["rows"][1]["key"]=bad["rows"][0]["key"];reject(bad,active);
    bad=data;bad["rows"][0]["name"]="Unexpected\nrow";reject(bad,active);
    bad=data;bad["rows"].erase(bad["rows"].begin());assert(parse(bad,active).rows.size()==223);
    bad=data;bad["rows"]=Json::array();assert(parse(bad,active).rows.empty());
    bad=data;bad["rows"][0]["round"]=8;reject(bad,active);
    bad=data;bad["format"]=1;reject(bad,active);
    bad=data;bad["actualRoundsOnly"]=false;reject(bad,active);
    bad=data;for(int i=224;i<1025;++i){auto row=data["rows"][0];row["key"]="8:"+std::to_string(i);bad["rows"].push_back(std::move(row));}reject(bad,active);
    bad=data;bad["rows"][0]["conference"]="2:1";reject(bad,active);
    bad=data;bad["rows"][0]["key"]="8:131072";reject(bad,active);
    cache.clear();assert(!cache.current(active));std::cout<<"Draft runtime validation and immutable cache pass\n";
}
