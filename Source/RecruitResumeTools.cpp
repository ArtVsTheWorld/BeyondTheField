#include "RecruitResume.h"
#include <fstream>
#include <iostream>
using namespace recruitingfog::resume;
Json selfTest(){
    const char* positions[]={"QB","HB","FB","WR","TE","LT","LG","C","RG","RT","LE","RE","DT","LOLB","MLB","ROLB","CB","FS","SS","K","P","LS"};
    unsigned checked=0,zero=0;double strong=0,weak=0,tough=0,easy=0,class1=0,class6=0;unsigned count1=0,count6=0;
    for(const auto* pos:positions)for(unsigned i=0;i<1000;++i){
        Prospect p;p.identity=std::string("boundary-fixture:")+pos+":"+std::to_string(i);p.name="Controlled fixture";p.position=pos;p.stars=int(i%5)+1;p.stateRank=int(i%50)+1;p.development="Normal";
        // All relevant attributes take boundary values; fallback Overall is
        // intentional here, exercising every position without live game data.
        p.ratings["OverallRating"]=double(i%101);auto a=generate(p);validate(a.publicData);++checked;if(a.publicData.at("games")==0)++zero;
        if(a.publicData!=generate(p).publicData)throw std::runtime_error("Unstable controlled fixture");
        p.development="College_Elite";auto b=generate(p);auto x=a.publicData,y=b.publicData;x.erase("background");y.erase("background");if(x!=y)throw std::runtime_error("Development revealed by production/opportunity");
    }
    for(unsigned i=0;i<8000;++i){
        Prospect p;p.identity="matched-qb:"+std::to_string(i);p.name="Matched QB";p.position="QB";p.stars=3;p.stateRank=2;p.development="Normal";p.ratings["OverallRating"]=55;
        weak+=generate(p).publicData.at("stats").at("passingYards").get<int>();p.ratings["OverallRating"]=80;strong+=generate(p).publicData.at("stats").at("passingYards").get<int>();
        p.ratings["OverallRating"]=70;p.stateRank=1;auto a=generate(p);tough+=a.publicData.at("stats").at("passingYards").get<int>();
        if(a.publicData.at("competitionClass")=="1A"){class1+=a.publicData.at("stats").at("passingYards").get<int>();++count1;}
        if(a.publicData.at("competitionClass")=="6A"){class6+=a.publicData.at("stats").at("passingYards").get<int>();++count6;}
        p.stateRank=50;easy+=generate(p).publicData.at("stats").at("passingYards").get<int>();
    }
    if(!zero||strong<=weak*1.15||easy<=tough*1.04||class1/count1<=class6/count6*1.04)throw std::runtime_error("Competition/ability calibration lost its expected population direction");
    bool rejected=false;try{fromJson({{"identity","x"},{"name","x"},{"position","QB"},{"stars",3},{"stateRank",2},{"ratings",{{"OverallRating",101}}}});}catch(const std::exception& e){rejected=std::string(e.what())=="Invalid underlying resume attribute";}if(!rejected)throw std::runtime_error("Malformed hidden ratings accepted");
    return {{"boundaryResumes",checked},{"zeroAppearanceResumes",zero},{"matchedQBPairs",8000},{"ability80Vs55YardageRatio",strong/weak},{"VermontVsFloridaYardageRatio",easy/tough},{"class1Vs6YardageRatio",(class1/count1)/(class6/count6)},{"developmentIsolation",true}};
}
int main(int argc,char** argv){
    using namespace recruitingfog::resume;
    try{
        if(argc==2&&std::string(argv[1])=="--self-test"){std::cout<<selfTest().dump(2)<<'\n';return 0;}
        if(argc!=3){std::cerr<<"Usage: RecruitResumeTools input.json output.json\n";return 2;}
        std::ifstream in(argv[1]);if(!in)throw std::runtime_error("Missing resume inputs");Json input;in>>input;Json rows=Json::array();
        for(const auto& raw:input.at("prospects")){
            const auto p=fromJson(raw);const auto result=generate(p);validate(result.publicData);
            if(result.publicData!=generate(p).publicData)throw std::runtime_error("Unstable resume");
            auto changed=p;changed.development=p.development=="Normal"?"College_Elite":"Normal";const auto other=generate(changed);
            for(const auto* key:{"stats","games","starts","role","competitionClass"})if(result.publicData.at(key)!=other.publicData.at(key))throw std::runtime_error("Development became a statistical tell");
            rows.push_back({{"identity",p.identity},{"name",p.name},{"position",p.position},{"stars",p.stars},{"public",result.publicData},{"evaluation",result.evaluation}});
        }
        std::ofstream out(argv[2]);out<<Json({{"format",1},{"modelVersion",1},{"rows",rows}}).dump();if(!out)throw std::runtime_error("Cannot write resume preview");
        std::cout<<"Generated and validated "<<rows.size()<<" resumes; deterministic and development-isolated.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;
}
