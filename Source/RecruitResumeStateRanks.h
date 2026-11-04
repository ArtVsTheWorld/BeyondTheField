// Generated from Config/high-school-state-strength.json.
#pragma once
#include <string>
namespace recruitingfog::resume {
inline int stateRank(const std::string& state){
if(state=="DistrictOfColumbia"||state=="WashingtonDC"||state=="DC")return 21;
static constexpr const char* states[]={"Florida","Texas","Georgia","California","Louisiana","Ohio","Tennessee","Alabama","NorthCarolina","Pennsylvania","NewJersey","Indiana","SouthCarolina","Mississippi","Arizona","Utah","Illinois","Missouri","Virginia","Arkansas","Maryland","Michigan","Oklahoma","Massachusetts","Kentucky","Colorado","Nevada","Hawaii","Nebraska","NewYork","Washington","Wisconsin","Oregon","Idaho","Minnesota","NewMexico","Kansas","WestVirginia","Iowa","Delaware","Connecticut","RhodeIsland","Wyoming","Alaska","SouthDakota","NorthDakota","Montana","Maine","NewHampshire","Vermont"};
for(int i=0;i<50;++i)if(state==states[i])return i+1;return 0;
}
}
