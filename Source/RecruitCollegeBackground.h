#pragma once
#include "RecruitResume.h"
#include "RecruitCollegeSchools.h"
#include <set>
#include <cctype>
namespace recruitingfog::resume {
inline std::string schoolKey(const std::string& name){
    std::string words,word;auto finish=[&](){if(word!="university"&&word!="college"&&word!="of"&&word!="the"&&word!="at")words+=word;word.clear();};
    for(unsigned char c:name){if(std::isalnum(c))word+=static_cast<char>(std::tolower(c));else finish();}finish();return words;
}
inline int schoolRegion(const std::string& state){
    const std::string groups[]={"|Maine|Vermont|NewHampshire|Massachusetts|RhodeIsland|Connecticut|NewYork|NewJersey|Pennsylvania|",
        "|Maryland|DistrictOfColumbia|Delaware|Virginia|WestVirginia|NorthCarolina|SouthCarolina|Georgia|Florida|",
        "|Ohio|Michigan|Indiana|Illinois|Wisconsin|Minnesota|Iowa|Missouri|",
        "|Kentucky|Tennessee|Alabama|Mississippi|Louisiana|Arkansas|",
        "|Texas|Oklahoma|Kansas|Nebraska|SouthDakota|NorthDakota|",
        "|Montana|Wyoming|Colorado|NewMexico|Arizona|Utah|Idaho|Nevada|",
        "|California|Oregon|Washington|Alaska|Hawaii|"};
    for(int i=0;i<7;++i)if(groups[i].find("|"+state+"|")!=std::string::npos)return i;return -1;
}
inline bool schoolCollision(const CollegeSchool& school,const std::set<std::string>& active){
    return active.count(schoolKey(school.name))||active.count(schoolKey(school.institution));
}
inline const CollegeSchool* chooseCollege(const Prospect& p,const std::set<std::string>& active){
    Random random(p.identity+"|college-school-v1");
    // A weak tendency, with broad overlap: level is not a rating conversion.
    const double roll=random.unit()+clamp((skill(p)-65)/200.,-.12,.12);
    const std::string level=!p.collegeLevel.empty()?p.collegeLevel:roll<.30?"D3":roll<.65?"D2":"FCS";
    const bool nationwide=random.unit()<.18;const auto region=schoolRegion(p.state);
    double total=0;for(const auto& s:collegeSchools)if(s.level==level&&!schoolCollision(s,active))
        total+=nationwide?1.:p.state==s.state?55.:region>=0&&region==schoolRegion(s.state)?5.:.35;
    if(!total)return nullptr;double choice=random.unit()*total;
    for(const auto& s:collegeSchools)if(s.level==level&&!schoolCollision(s,active)){
        choice-=nationwide?1.:p.state==s.state?55.:region>=0&&region==schoolRegion(s.state)?5.:.35;if(choice<=0)return &s;
    }
    return nullptr;
}
}
