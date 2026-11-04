#include "../Source/RecruitingFog.cpp"
#include <iostream>
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
unsigned forwarded=0;
void* __fastcall fakeGetter(void*,void** out){++forwarded;return out;}
struct FixtureView {
    std::map<uintptr_t,std::vector<uintptr_t>> arrays;
    std::map<uintptr_t,std::map<std::string,uintptr_t>> maps;
    std::map<uintptr_t,double> numbers;std::map<uintptr_t,bool> booleans;
    bool array(uintptr_t at,std::vector<uintptr_t>& out,size_t max){if(!arrays.count(at)||arrays.at(at).size()>max)return false;out=arrays.at(at);return true;}
    bool members(uintptr_t at,std::map<std::string,uintptr_t>& out){if(!maps.count(at))return false;out=maps.at(at);return true;}
    bool number(uintptr_t at,double& out){if(!numbers.count(at))return false;out=numbers.at(at);return true;}
    bool boolean(uintptr_t at,bool& out){if(!booleans.count(at))return false;out=booleans.at(at);return true;}
};
int main(){try{
    using namespace recruitingfog;
    for(int rating=0;rating<=100;++rating){const char expected=rating<60?'F':rating<70?'D':rating<80?'C':rating<90?'B':'A';require(display(Visibility::Revealed,rating)==std::string(1,expected),"Incorrect revealed grade");require(display(Visibility::Unknown,rating)=="?","Unknown rating leaked");}
    for(int low=0;low<=100;++low)for(int high=low;high<=100;++high){const auto label=display(Visibility::Range,99,low,high);require(label.find_first_of("0123456789")==std::string::npos,"Range exposed numerical precision");require(label==display(Visibility::Range,0,low,high),"Range depends on hidden true rating");}
    require(display(Visibility::Range,99,75,85)==u8"C–B","C-B range incorrect");require(display(Visibility::Range,99,80,89)=="B","Same-band range must collapse");require(display(Visibility::Range,99,89,90)==u8"B–A","Boundary-crossing range incorrect");
    require(display(Visibility::Revealed,-1)=="?"&&display(Visibility::Revealed,101)=="?"&&display(Visibility::Revealed,79.5)=="?","Malformed rating was accepted");
    require(display(Visibility::Range,90,80,70)=="?"&&display(Visibility::Range,90,-1,90)=="?","Malformed range was accepted");
    {
        FixtureView view;view.arrays[1]={2};view.maps[2]={{"PercentageScouted",3},{"ScoutingAttributes",4}};view.numbers[3]=40;
        // Actual visible bounds captured from the reference QB, followed by an
        // unknown sentinel. The hidden true ratings are deliberately absent.
        const double lows[]={66,92,70,79,58,66,64,48,67,50,0};
        const double highs[]={96,92,100,79,88,81,79,63,82,80,0};
        const std::string expected[]={u8"D–A","A",u8"C–A","C",u8"F–B",u8"D–B",u8"D–C",u8"F–D",u8"D–B",u8"F–B"};
        for(unsigned i=0;i<11;++i){const uintptr_t at=100+i*10;view.arrays[4].push_back(at);view.maps[at]={{"HaveSlider",at+1},{"SliderStart",at+2},{"SliderEnd",at+3}};view.booleans[at+1]=lows[i]!=highs[i];view.numbers[at+2]=lows[i];view.numbers[at+3]=highs[i];}
        std::map<uintptr_t,std::map<std::string,std::string>> writes;unsigned flags=0;
        const auto before=view.numbers;
        auto strings=[&](uintptr_t at,const char* key,const char* value){writes[at][key]=value;};
        auto booleans=[&](uintptr_t,const char* key,bool value){require(std::string(key)=="HaveSlider"&&!value,"Unexpected non-display property mutation");++flags;};
        auto stats=convertRecruitingResponse(view,1,strings,booleans);
        require(stats.recruits==1&&stats.attributes==10&&stats.revealed==2&&stats.ranges==8&&stats.unknown==1&&!stats.unsupported,"Reference scouting conversion counts differ");
        for(unsigned i=0;i<10;++i){const auto at=100+i*10;require(writes[at]["SliderStart"]==expected[i]&&writes[at]["SliderEnd"]==expected[i],"Reference grade/range differs");require(writes[at].size()==2,"Conversion modified unrelated text");}
        require(!writes.count(200)&&flags==10,"Unknown sentinel was converted or bar not disabled");require(view.numbers==before,"Native observations/progress changed");
        view.numbers[3]=100;writes.clear();flags=0;stats=convertRecruitingResponse(view,1,strings,booleans);require(writes[200]["SliderStart"]=="F"&&stats.attributes==11,"Legitimately revealed zero must be distinguishable from unknown zero");
        view.numbers[3]=0;view.booleans[201]=true;view.numbers[203]=100;writes.clear();flags=0;stats=convertRecruitingResponse(view,1,strings,booleans);require(writes[200]["SliderStart"]=="?","Entirely unknown range exposed a grade");
        writes.clear();stats=convertRecruitingResponse(view,999,strings,booleans);require(stats.unsupported==1&&writes.empty(),"Unsupported response was mutated");
    }
    {
        std::array<unsigned char,48> value{};std::array<unsigned char,16> text{};memcpy(text.data(),"Luke",4);text[15]=11;
        unsigned kind=3;memcpy(value.data()+0x10,&kind,4);const auto at=reinterpret_cast<uintptr_t>(text.data());memcpy(value.data()+0x20,&at,8);
        require(runtime::snapshot(reinterpret_cast<uintptr_t>(value.data()))=="Luke","Interned UI string must use +0x20, not allocator context +0x18");
    }
    runtime::original=fakeGetter;void* value=reinterpret_cast<void*>(0x1234);auto out=&value;
    require(runtime::getterHook(nullptr,out)==out&&value==reinterpret_cast<void*>(0x1234)&&forwarded==1,"Probe changed the native return or output");
    runtime::disabled=true;require(runtime::getterHook(nullptr,out)==out&&forwarded==2,"Stopped probe did not pass through");
    std::cout<<"Passed: grade boundaries, hidden states, 5151 range pairs, hidden-rating independence, live-response fixtures, interned-string layout, malformed values and native pass-through ABI.\n";
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}return 0;}
