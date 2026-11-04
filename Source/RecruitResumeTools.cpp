#include "RecruitResumeSource.h"
#include <fstream>
#include <iostream>
using namespace recruitingfog::resume;
#include "../Tests/RecruitResumeExpansionTests.h"
Json selfTest(){
    const char* positions[]={"QB","HB","FB","WR","TE","LT","LG","C","RG","RT","LE","RE","DT","LOLB","MLB","ROLB","CB","FS","SS","K","P","LS"};
    unsigned checked=0,zero=0;double strong=0,weak=0,tough=0,easy=0,class1=0,class6=0;unsigned count1=0,count6=0;
    for(const auto* pos:positions)for(unsigned i=0;i<1000;++i){
        Prospect p;p.identity=std::string("boundary-fixture:")+pos+":"+std::to_string(i);p.name="Controlled fixture";p.position=pos;p.stars=int(i%5)+1;p.stateRank=int(i%50)+1;p.development="Normal";
        // All relevant attributes take boundary values; fallback Overall is
        // intentional here, exercising every position without live game data.
        p.ratings["OverallRating"]=double(i%101);auto a=generate(p);validate(a.publicData);++checked;if(a.publicData.at("games")==0)++zero;
        if(a.publicData!=generate(p).publicData)throw std::runtime_error("Unstable controlled fixture");
        for(const auto* development:{"Normal","College_Impact","College_Star","College_Elite"}){p.development=development;if(a.publicData!=generate(p).publicData)throw std::runtime_error("Development changed public resume or wording");}
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
    recruitingfog::NotesProspect note;note.identity="catalog-check";note.progress=0;note.observations={{"Throw Power",99,99,true}};
    const auto unknown=scoutingSection(note);note.observations={{"Throw Power",1,1,true}};if(scoutingSection(note)!=unknown)throw std::runtime_error("Unscouted prose leaks ability");
    note.progress=40;note.observations={{"Throw Power",66,96,false}};if(scoutingSection(note).find("too wide")==std::string::npos)throw std::runtime_error("Unresolved range became a claim");
    note.observations={{"Throw Power",92,92,true},{"Medium Accuracy",79,79,true}};if(scoutingSection(note).find("Specific film")!=std::string::npos||scoutingSection(note).find_first_of("0123456789")!=std::string::npos)throw std::runtime_error("Qualitative report is missing or numeric");
    const auto testRoot=std::filesystem::current_path()/L"ResumePersistenceTests"/(std::to_string(GetCurrentProcessId())+"-"+std::to_string(GetTickCount64()));
    NativeClass c;c.league="123";c.season=2026;NativeEntry e;e.nativeId=100;e.first="Test";e.last="Prospect";e.identity="saved-prospect";e.highSchool=true;e.prospect.identity=e.identity;e.prospect.name="Test Prospect";e.prospect.position="LT";e.prospect.stars=3;e.prospect.stateRank=2;e.prospect.ratings["OverallRating"]=70;c.entries.emplace(100,e);
    persistClass(c,testRoot);const auto saved=c.entries.at(100).saved;e.prospect.ratings["OverallRating"]=99;c.entries.at(100)=e;persistClass(c,testRoot);
    if(c.entries.at(100).saved!=saved)throw std::runtime_error("Saved resume changed with ratings");
    c.season=2027;persistClass(c,testRoot);if(c.entries.at(100).saved!=saved)throw std::runtime_error("Year boundary lost the prior resume");
    const auto body=composeNotes(saved,note);if(body.size()>1500||body.find("pancakes")==std::string::npos||body.find('%')==std::string::npos)throw std::runtime_error("Combined native report is oversized or missing blocking context");
    return {{"expansion",expansionTests()},{"boundaryResumes",checked},{"zeroAppearanceResumes",zero},{"matchedQBPairs",8000},{"ability80Vs55YardageRatio",strong/weak},{"VermontVsFloridaYardageRatio",easy/tough},{"class1Vs6YardageRatio",(class1/count1)/(class6/count6)},{"developmentIsolation",true},{"qualitativePassages",prosePassages},{"journalPersistence",true}};
}
int main(int argc,char** argv){
    using namespace recruitingfog::resume;
    try{
        if(argc==2&&std::string(argv[1])=="--self-test"){std::cout<<selfTest().dump(2)<<'\n';return 0;}
        if(argc==4&&std::string(argv[1])=="--prepare-native"){
            std::ifstream in(argv[2]);Json raw;in>>raw;auto c=parseNativeClass(raw);persistClass(c,std::filesystem::path(argv[3]));unsigned count=0;for(const auto& [id,e]:c.entries){(void)id;if(e.highSchool)++count;}
            std::cout<<"Prepared "<<c.entries.size()<<" recruit backgrounds ("<<count<<" HS) for league "<<c.league<<", "<<c.season<<".\n";return 0;
        }
        if(argc==4&&std::string(argv[1])=="--native-parity"){
            std::ifstream a(argv[2]),b(argv[3]);Json raw,expected;a>>raw;b>>expected;const auto c=parseNativeClass(raw);std::map<std::string,Json> byId;for(const auto& v:expected.at("prospects"))byId.emplace(v.at("identity").get<std::string>(),v);
            unsigned matches=0;for(const auto& [id,e]:c.entries)if(e.highSchool){const auto& input=byId.at(e.identity);if(input.at("nativeRecruitId")!=id||generate(e.prospect).publicData!=generate(fromJson(input)).publicData)throw std::runtime_error("Native/JS source parity failed");++matches;}
            if(matches!=byId.size())throw std::runtime_error("Native class coverage mismatch");std::cout<<"Native source identity and generated resume match "<<matches<<" audited HS inputs.\n";return 0;
        }
        if(argc!=3){std::cerr<<"Usage: RecruitResumeTools input.json output.json\n";return 2;}
        std::ifstream in(argv[1]);if(!in)throw std::runtime_error("Missing resume inputs");Json input;in>>input;Json rows=Json::array();
        for(const auto& raw:input.at("prospects")){
        const auto p=fromJson(raw);const auto result=generate(p);validate(result.publicData);
            recruitingfog::NotesProspect notes;notes.identity=p.identity;notes.position=p.position;notes.progress=100;
            notes.observations={{"Speed",p.rating("SpeedRating"),p.rating("SpeedRating"),true},{"Strength",p.rating("StrengthRating"),p.rating("StrengthRating"),true}};
            if(composeNotes(result.publicData,notes).size()>1500)throw std::runtime_error("Composed resume exceeds native text budget");
            if(result.publicData!=generate(p).publicData)throw std::runtime_error("Unstable resume");
            auto changed=p;changed.development=p.development=="Normal"?"College_Elite":"Normal";const auto other=generate(changed);
            if(result.publicData!=other.publicData)throw std::runtime_error("Development changed public resume or wording");
            rows.push_back({{"identity",p.identity},{"name",p.name},{"position",p.position},{"stars",p.stars},{"public",result.publicData},{"evaluation",result.evaluation}});
        }
        std::ofstream out(argv[2]);out<<Json({{"format",1},{"modelVersion",2},{"rows",rows}}).dump();if(!out)throw std::runtime_error("Cannot write resume preview");
        std::cout<<"Generated and validated "<<rows.size()<<" resumes; deterministic and development-isolated.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;
}
