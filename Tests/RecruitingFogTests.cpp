#include "../Source/RecruitingFog.cpp"
#include <iostream>
#include "../Source/RecruitNotes.h"
#include "../Source/PlayerAbilityDescriptions.h"
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
unsigned forwarded=0;
void* __fastcall fakeGetter(void*,void** out){++forwarded;return out;}
std::array<uintptr_t,2> detailArguments{};
void* __fastcall fakeDetailGetter(void*,void** out,uintptr_t first,uintptr_t second){++forwarded;detailArguments={first,second};return out;}
#if defined(RECRUIT_NOTES_UI)
std::array<uintptr_t,5> setupArguments{};
unsigned __fastcall fakeColorLength(void*){return 148;}
unsigned abilityForwarded=0;bool abilityMentals=false;
void* __fastcall fakeAbilities(void*,void** out,bool mentals){++abilityForwarded;abilityMentals=mentals;return out;}
unsigned awardForwarded=0;void* awardKey=nullptr;
void* __fastcall fakeAward(void*,void** out,void* key){++awardForwarded;awardKey=key;return out;}
uintptr_t __fastcall fakeScriptSetup(void* object,void* saved,uintptr_t receiver,uintptr_t parent,uintptr_t super){setupArguments={reinterpret_cast<uintptr_t>(object),reinterpret_cast<uintptr_t>(saved),receiver,parent,super};return 0xabcdef;}
#endif
#if defined(RECRUIT_NOTES_UI)
struct GridTestOutput{void** vtable;nlohmann::json values=nlohmann::json::array();};
void __fastcall gridTestReserve(GridTestOutput* o,unsigned n){o->values.push_back({{"reserve",n}});}
template<class T>void gridTestField(GridTestOutput* o,unsigned row,const char* key,T value){o->values.push_back({{"row",row},{"key",key},{"value",value}});}
void __fastcall gridTestBool(GridTestOutput* o,unsigned r,const char* k,bool v){gridTestField(o,r,k,v);}
void __fastcall gridTestInt(GridTestOutput* o,unsigned r,const char* k,int v){gridTestField(o,r,k,v);}
void __fastcall gridTestFloat(GridTestOutput* o,unsigned r,const char* k,float v){gridTestField(o,r,k,v);}
void __fastcall gridTestString(GridTestOutput* o,unsigned r,const char* k,const char* v){gridTestField(o,r,k,v);}
void* gridTestTable[]={nullptr,reinterpret_cast<void*>(gridTestReserve),nullptr,reinterpret_cast<void*>(gridTestBool),reinterpret_cast<void*>(gridTestInt),reinterpret_cast<void*>(gridTestFloat),reinterpret_cast<void*>(gridTestString)};
std::string gridTestLabel(void* source,int form,int row,const char*){return source==reinterpret_cast<void*>(123)&&form==0&&row==7?"FCS (SO)":"";}
struct GridTestColumns{void** vtable;int column;};
int __fastcall gridTestCount(void*){return 1;}
int __fastcall gridTestColumn(GridTestColumns* columns,int){return columns->column;}
void* gridTestColumnsTable[]={nullptr,reinterpret_cast<void*>(gridTestCount),reinterpret_cast<void*>(gridTestColumn)};
struct MapTestOutput{void** vtable;nlohmann::json values=nlohmann::json::object();};
void __fastcall mapTestBool(MapTestOutput* o,const char* k,bool v){o->values[k]=v;}
void __fastcall mapTestInt(MapTestOutput* o,const char* k,int v){o->values[k]=v;}
void __fastcall mapTestFloat(MapTestOutput* o,const char* k,float v){o->values[k]=v;}
void __fastcall mapTestString(MapTestOutput* o,const char* k,const char* v){o->values[k]=v?v:"";}
void __fastcall mapTestUndefined(MapTestOutput* o,const char* k){o->values[k]=nullptr;}
void __fastcall mapTestOpaque(MapTestOutput* o,const char* k,void* v){o->values[k]=reinterpret_cast<uintptr_t>(v);}
void* mapTestTable[]={nullptr,reinterpret_cast<void*>(mapTestBool),reinterpret_cast<void*>(mapTestInt),reinterpret_cast<void*>(mapTestFloat),reinterpret_cast<void*>(mapTestString),reinterpret_cast<void*>(mapTestUndefined),reinterpret_cast<void*>(mapTestOpaque)};
std::array<uintptr_t,5> gridTestArgs{};
void __fastcall fakeClassRows(void* s,void* out,int form,int row,void* cols){gridTestArgs={reinterpret_cast<uintptr_t>(s),reinterpret_cast<uintptr_t>(out),static_cast<uintptr_t>(form),static_cast<uintptr_t>(row),reinterpret_cast<uintptr_t>(cols)};}
#endif
struct FixtureView {
    std::map<uintptr_t,std::vector<uintptr_t>> arrays;
    std::map<uintptr_t,std::map<std::string,uintptr_t>> maps;
    std::map<uintptr_t,double> numbers;std::map<uintptr_t,bool> booleans;
    std::map<uintptr_t,std::string> strings;
    unsigned kind(uintptr_t at){return arrays.count(at)?4:maps.count(at)?5:strings.count(at)?3:numbers.count(at)?2:booleans.count(at)?1:0;}
    bool string(uintptr_t at,std::string& out){if(!strings.count(at))return false;out=strings.at(at);return true;}
    bool array(uintptr_t at,std::vector<uintptr_t>& out,size_t max){if(!arrays.count(at)||arrays.at(at).size()>max)return false;out=arrays.at(at);return true;}
    bool members(uintptr_t at,std::map<std::string,uintptr_t>& out){if(!maps.count(at))return false;out=maps.at(at);return true;}
    bool number(uintptr_t at,double& out){if(!numbers.count(at))return false;out=numbers.at(at);return true;}
    bool boolean(uintptr_t at,bool& out){if(!booleans.count(at))return false;out=booleans.at(at);return true;}
};
int main(){try{
    using namespace recruitingfog;
    {
        using namespace playerfog;
        require(abilityDescriptionGrades("Bronze Requires: 84 Pass Block Power (75 Currently)")=="Bronze Requires: B Pass Block Power (C Currently)","Ability paired attribute ratings leaked");
        require(abilityDescriptionGrades("Bronze Requires: 82 Acceleration (73 Currently) \nand 68 Speed (61 Currently)")=="Bronze Requires: B Acceleration (C Currently) \nand D Speed (D Currently)","Two-attribute ability wording/newline failed");
        require(abilityDescriptionGrades("Costs 2 points. Gold Requires: 90 Speed (? Currently), jersey99, 25% boost")=="Costs 2 points. Gold Requires: A Speed (? Currently), jersey99, 25% boost","Ability costs/unknown/stat numbers changed");
        for(const auto* untouched:{"Costs 84 points. 75 Currently","Requires: 84 Skill Points (75 Currently)","Requires: 84 Pass Block Powerful (75 Currently)","Requires: 84 Pass Block Powerhouse (75 Currently)","Requires: 5 Speed Boosts (3 Currently)","Requires: -84 Speed (-75 Currently)","Requires: 84.5 Speed (75 Currently)","Requires: 101 Speed (75 Currently)","Requires: 84% Speed (75 Currently)","Requires: +84 Speed (75 Currently)","Requires: 84 Speediness (75 Currently)","Requires: 90 Passing Yards (80 Currently)"})
            require(abilityDescriptionGrades(untouched)==untouched,"Unrecognized/ordinary/invalid ability number was changed");
        for(int rating=0;rating<=100;++rating)for(auto name:abilityAttributeNames()){
            const auto input="Bronze Requires: "+std::to_string(rating)+" "+std::string(name)+" ("+std::to_string(rating)+" Currently)";
            const auto grade=display(Visibility::Revealed,rating);
            require(abilityDescriptionGrades(input)=="Bronze Requires: "+grade+" "+std::string(name)+" ("+grade+" Currently)","Ability rating boundary or longest attribute name failed");
        }
    }
    using namespace recruitingfog;
    for(int rating=0;rating<=100;++rating){const char expected=rating<60?'F':rating<70?'D':rating<80?'C':rating<90?'B':'A';require(display(Visibility::Revealed,rating)==std::string(1,expected),"Incorrect revealed grade");require(display(Visibility::Unknown,rating)=="?","Unknown rating leaked");}
    for(int low=0;low<=100;++low)for(int high=low;high<=100;++high){const auto label=display(Visibility::Range,99,low,high);require(label.find_first_of("0123456789")==std::string::npos,"Range exposed numerical precision");require(label==display(Visibility::Range,0,low,high),"Range depends on hidden true rating");}
    require(display(Visibility::Range,99,75,85)==u8"C–B","C-B range incorrect");require(display(Visibility::Range,99,80,89)=="B","Same-band range must collapse");require(display(Visibility::Range,99,89,90)==u8"B–A","Boundary-crossing range incorrect");
    require(display(Visibility::Revealed,-1)=="?"&&display(Visibility::Revealed,101)=="?"&&display(Visibility::Revealed,79.5)=="?","Malformed rating was accepted");
    require(display(Visibility::Range,90,80,70)=="?"&&display(Visibility::Range,90,-1,90)=="?","Malformed range was accepted");
    {
        NotesProspect p;p.identity="Luke|Callen|Buffalo|New York|561120980";p.position="QB";p.tendency="Pocket Passer";
        const auto broad=makeRecruitNotes(p);p.observations={{"Throw Power",99,99,true},{"Medium Accuracy",40,40,true}};
        require(makeRecruitNotes(p)==broad,"Unscouted notes leaked unrevealed attributes");
        p.progress=std::numeric_limits<double>::quiet_NaN();require(makeRecruitNotes(p)==broad,"Malformed scouting progress exposed detailed notes");
        p.progress=40;p.observations={{"Throw Power",92,92,true},{"Medium Accuracy",79,79,true},{"Speed",67,82,false}};
        const auto detailed=makeRecruitNotes(p);require(detailed.find("real zip")!=std::string::npos&&detailed.find("Intermediate placement")!=std::string::npos,"Revealed scouting facts did not produce qualitative notes");
        require(detailed.find_first_of("0123456789")==std::string::npos&&detailed.find("overall")==std::string::npos&&detailed.find("92")==std::string::npos,"Notes exposed numerical metrics");
        require(detailed==makeRecruitNotes(p)&&detailed.size()<=1500,"Notes are unstable or exceed the display budget");
        p.observations={{"Throw Power",0,100,false},{"Speed",67,82,false}};require(makeRecruitNotes(p).find("real zip")==std::string::npos,"An unresolved public range became a strength");
        p.observations={{"Throw Power",80,100,false}};require(makeRecruitNotes(p).find("real zip")!=std::string::npos,"A public strong range lost its qualitative hint");
        for(const auto* position:{"QB","HB","FB","WR","TE","LT","LG","C","RG","RT","LEDG","REDG","DT","SAM","MIKE","WILL","CB","FS","SS","K","P","LS"}){p.position=position;p.progress=0;require(!makeRecruitNotes(p).empty()&&makeRecruitNotes(p).find_first_of("0123456789")==std::string::npos,"Position note failed or exposed a rating");}
    }
#if defined(RECRUIT_NOTES_UI)
    {
        using namespace notesui;
        std::array<unsigned char,48> h{};std::vector<unsigned char> original={0x59,0x17,0x76,0x3e};
        auto put=[&](size_t at,const auto& value){memcpy(h.data()+at,&value,sizeof(value));};
        put(8,unsigned(1));put(12,static_cast<unsigned short>(3));put(14,static_cast<unsigned short>(41));put(24,unsigned(4));put(32,unsigned(5));put(40,uintptr_t(0x20000));
        Program p{0,1,3,41,4,bodyHash(original),10,8,4,std::vector<unsigned char>(16,0)};
        const auto cloned=makeDefinition(p,h,original);
        require(field<unsigned>(cloned.data(),24)==16&&field<unsigned short>(cloned.data(),12)==10&&std::equal(original.begin(),original.end(),cloned.begin()+56),"Notes definition header/body copy differs");
        require(std::equal(h.begin()+32,h.end(),cloned.begin()+32),"Notes clone changed the native constant pool");
        original[0]^=1;bool rejected=false;try{makeDefinition(p,h,original);}catch(const std::exception&){rejected=true;}require(rejected,"Changed native method body bypassed the Notes gate");
        std::vector<unsigned char> callback(64,0);const uintptr_t name=0x120,params=0x128,sourcePool=0x12345678;const unsigned sourceCount=0x98765432;
        memcpy(callback.data(),&name,8);memcpy(callback.data()+16,&params,8);memcpy(callback.data()+32,&sourceCount,4);memcpy(callback.data()+40,&sourcePool,8);callback[55]=0x59;
        Program nested{0,1,3,41,64,bodyHash(callback),3,0,64,std::vector<unsigned char>(66,0)};nested.nestedDefinitions.push_back({0,name,params});put(24,unsigned(64));
        require(sourceBodyHash(nested,h,callback,0x100000)==nested.hash,"Lazy callback source metadata was rejected");
        const uintptr_t liveName=0x100000+name,liveParams=0x100000+params,livePool=0x20000;const unsigned liveCount=5;
        memcpy(callback.data(),&liveName,8);memcpy(callback.data()+16,&liveParams,8);memcpy(callback.data()+32,&liveCount,4);memcpy(callback.data()+40,&livePool,8);
        require(sourceBodyHash(nested,h,callback,0x100000)==nested.hash,"Verified loader relocations changed the semantic callback hash");
        const auto retained=makeDefinition(nested,h,callback,0x100000);require(std::equal(callback.begin(),callback.end(),retained.begin()+48),"Normalized metadata replaced live callback pointers");
        callback[55]^=1;rejected=false;try{makeDefinition(nested,h,callback,0x100000);}catch(const std::exception&){rejected=true;}require(rejected,"Changed callback instruction escaped the full body gate");
        callback[55]^=1;callback[40]^=1;rejected=false;try{sourceBodyHash(nested,h,callback,0x100000);}catch(const std::exception&){rejected=true;}require(rejected,"Foreign nested pool accepted");callback[40]^=1;callback[0]^=1;
        rejected=false;try{sourceBodyHash(nested,h,callback,0x100000);}catch(const std::exception&){rejected=true;}require(rejected,"Unknown nested pointer relocation accepted");
        put(24,unsigned(4));
        const std::vector<OwnedDefinition> definitions={{0x10000,0x20000},{0x30000,0x40000}};
        PVOID volatile location=reinterpret_cast<void*>(0x30000);
        require(redirectDefinition(&location,definitions)==1&&location==reinterpret_cast<void*>(0x40000),"Live invocation did not attach its matching definition");
        require(redirectDefinition(&location,definitions)==-1&&location==reinterpret_cast<void*>(0x40000),"Already-patched clone was changed twice");
        location=reinterpret_cast<void*>(0x50000);
        require(redirectDefinition(&location,definitions)==-1&&location==reinterpret_cast<void*>(0x50000),"Recycled owner or unrelated script was changed");
        // The fifth native setup argument lives on the stack; forwarding only
        // register arguments would corrupt super-binding on other UI scripts.
        runtime::originalScriptSetup=fakeScriptSetup;
        for(bool stopped:{false,true}){runtime::disabled=stopped;
            require(runtime::notesSetupHook(reinterpret_cast<void*>(1),reinterpret_cast<void*>(2),3,4,5)==0xabcdef&&setupArguments==std::array<uintptr_t,5>{1,2,3,4,5},"Notes setup hook changed native ABI or pass-through return");}
        runtime::disabled=false;
        std::array<unsigned char,4096> asset{};std::array<uintptr_t,6> pool{};memcpy(asset.data(),"Apt Data:1:",11);
        original[0]^=1;p.offset=256;auto second=p;second.offset=512;second.argc=0;
        const auto assetBase=reinterpret_cast<uintptr_t>(asset.data());const auto poolAddress=reinterpret_cast<uintptr_t>(pool.data());
        put(40,poolAddress);
        memcpy(asset.data()+p.offset,h.data(),48);memcpy(asset.data()+p.offset+48,original.data(),original.size());
        put(8,unsigned(0));memcpy(asset.data()+second.offset,h.data(),48);memcpy(asset.data()+second.offset+48,original.data(),original.size());
        Runtime live({p,second});live.prepare();std::array<uintptr_t,12> object{};object[11]=assetBase+p.offset;
        asset[second.offset+48]^=1;rejected=false;
        try{live.beforeInvoke(object.data(),runtime::read);}catch(const std::exception&){rejected=true;}
        require(rejected&&object[11]==assetBase+p.offset&&live.ownerCount()==0,"Notes attached before every method body passed its gate");
        asset[second.offset+48]^=1;
        require(live.beforeInvoke(object.data(),runtime::read)==0&&object[11]!=assetBase+p.offset&&live.ownerCount()==1,"Notes failed to attach to a newly-created live script");
        const auto owned=object[11];object[11]=assetBase+p.offset;
        require(live.beforeInvoke(object.data(),runtime::read,true)==-1&&object[11]==assetBase+p.offset,"Late color hook changed a method requiring more registers");
        auto fixed=p;fixed.newRegisters=fixed.registers;Runtime safe({fixed});safe.prepare();
        require(safe.beforeInvoke(object.data(),runtime::read,true)==0,"Frame-preserving method was rejected by late gate");
        object[11]=assetBase+p.offset;
        runtime::originalColorLength=fakeColorLength;
        for(bool stopped:{false,true}){runtime::disabled=stopped;require(runtime::colorLengthHook(object.data())==148,"Color accessor changed the native return");}runtime::disabled=false;
        require(live.beforeInvoke(object.data(),runtime::read)==0&&object[11]==owned,"Fresh receiver failed to reuse verified script generation");
        // Same source allocation may be reused after leaving Recruiting. A
        // changed pool pointer must generate fresh headers, never stale ones.
        LARGE_INTEGER frequency{},started{},finished{};QueryPerformanceFrequency(&frequency);QueryPerformanceCounter(&started);
        unsigned total=0;for(unsigned i=0;i<1000000;++i)total+=runtime::colorLengthHook(object.data());QueryPerformanceCounter(&finished);
        require(total==148000000,"Color fast path did not preserve native lengths");
        std::cout<<"Color accessor fast path: "<<double(finished.QuadPart-started.QuadPart)*1e9/frequency.QuadPart/1000000<<" ns/call (standalone mock; not a game frame-time measurement).\n";
        const auto nextPool=reinterpret_cast<uintptr_t>(pool.data()+1);memcpy(asset.data()+p.offset+40,&nextPool,8);
        object[11]=assetBase+p.offset;
        require(live.beforeInvoke(object.data(),runtime::read)==0&&object[11]!=owned,"Reloaded source reused a stale constant-pool header");
        require(field<uintptr_t>(reinterpret_cast<const unsigned char*>(object[11]),40)==nextPool,"Reloaded definition lost its current pool");
    }
#endif
#if defined(RECRUIT_NOTES_UI)
    {
        using namespace playerfog;
        for(int n=0;n<=100;++n){const auto expected=display(Visibility::Revealed,n);for(const auto* suffix:{"",",TrendUp",",TrendDown",",TrendNone"})require(ratingLabel((std::to_string(n)+suffix).c_str())==expected,"Roster rating/trend converted incorrectly");}
        for(const auto* hidden:{"?","--","", "Hidden","-1","101","79.5","92 yards"})require(ratingLabel(hidden)==hidden,"Roster transformed hidden or non-rating text");
        std::array<std::string,90> names{};names[1]="RS";names[2]="Name";names[3]="Year";names[4]="POS";names[5]="OVR";names[6]="NIL";names[7]="DEV";names[8]="SPD";names[9]="ACC";
        for(unsigned col=10;col<62;++col)names[col]="LSP";
        require(rosterSchema(names,62),"Roster schema rejected");names[5]="Yards";require(!rosterSchema(names,62),"Statistics schema accepted as ratings");names[5]="OVR";
        names[8]="THP";names[9]="SAC";names[10]="MAC";require(rosterSchema(names,11),"Position-specific attribute subset rejected");
        names[10]="Passing Yards";require(!rosterSchema(names,11),"Position schema admitted a statistic");names[10]="MAC";names[7]="GAMES";require(!rosterSchema(names,11),"Stats identity fields accepted as roster");
        GridTestOutput output{gridTestTable};GridSink cells{gridTable,&output};cells.count=5;cells.columns={6,61,5,8,2};
        gridString(&cells,0,"display","92");gridString(&cells,1,"display","59");gridString(&cells,2,"display","83,TrendUp");gridString(&cells,3,"tooltip","90");gridString(&cells,4,"display","91");
        require(output.values[0]["value"]=="92"&&output.values[1]["value"]=="F"&&output.values[4]["value"]=="B"&&output.values[7]["value"]=="90"&&output.values[8]["value"]=="91","Subset/reordered roster columns changed NIL, names or tooltip unexpectedly");
        require(output.values[2]["key"]=="DEPlayerRating"&&output.values[2]["value"]==true&&output.values[3]["value"]==0xF04444&&output.values[6]["value"]==0xA8D943,"Roster color markers lost grade palette");
        ColumnSink columns{columnTable};columnReserve(&columns,62);columnString(&columns,5,"display","OVR");columnInt(&columns,5,"formatType",4);columnBool(&columns,5,"isTrend",true);columnInt(&columns,6,"formatType",4);columnFloat(&columns,5,"width",42.5f);
        output.values=nlohmann::json::array();replayColumns(columns,&output,true);
        require(output.values[2]["value"]==0&&output.values[3]["value"]==false&&output.values[4]["value"]==4&&output.values[5]["value"]==42.5,"Roster columns changed unrelated metadata");
        output.values=nlohmann::json::array();replayColumns(columns,&output,false);require(output.values[2]["value"]==4&&output.values[3]["value"]==true,"Unknown schema changed formats");
        std::array<std::string,90> depthNames{};const char* depthHeaders[]={"","POS","#","RS","Name","Year","POS","OVR","NIL","MOR","SPD","ACC","AGI","COD","STR","AWR","THP","SAC","MAC","DAC","RUN","TUP","BSK","PAC","CAR","BCV","JKM","SPM","BTK","SFA","TRK","IBL","STA","TGH","INJ"};
        for(size_t i=0;i<std::size(depthHeaders);++i)depthNames[i]=depthHeaders[i];
        require(classifyGrid(depthNames,35)==GridSchema::DepthChart&&!rosterSchema(depthNames,35),"Captured native depth schema misclassified");
        for(int form:{0,1,999,2147483647})for(auto schema:{GridSchema::Roster,GridSchema::DepthChart,GridSchema::Redshirts,GridSchema::InjuryReport,GridSchema::PositionAth,GridSchema::PlayersLeaving,GridSchema::Training,GridSchema::EncourageTransfers}){
            const auto state=gridState(form,schema);require(gridStateForm(state)==form&&gridStateSchema(state)==schema,"Atomic form/schema snapshot lost identity");
        }
        require(gridState(-1,GridSchema::Roster)==0&&gridState(0,GridSchema::None)==0&&gridStateForm(0)==-1,"Inactive grid state admitted a row");
        depthNames[16]="Passing Yards";require(classifyGrid(depthNames,35)==GridSchema::None,"Depth schema admitted a statistic");depthNames[16]="THP";
        depthNames[2]="Jersey";require(classifyGrid(depthNames,35)==GridSchema::None,"Depth identity prefix accepted another table");depthNames[2]="#";
        output.values=nlohmann::json::array();GridSink depthCells{gridTable,&output};depthCells.schema=GridSchema::DepthChart;depthCells.count=7;depthCells.columns={2,7,8,9,10,63,4};
        for(unsigned i=0;i<7;++i)gridString(&depthCells,i,"display",std::array<const char*,7>{"1","66,TrendUp","10","76","92","59","Whitaker"}[i]);
        gridInt(&depthCells,1,"intValue",66);
        require(output.values[0]["value"]=="1"&&output.values[1]["value"]=="D"&&output.values[4]["value"]=="10"&&output.values[5]["value"]=="76"&&output.values[6]["value"]=="A"&&output.values[9]["value"]=="F"&&output.values[12]["value"]=="Whitaker"&&output.values[13]["value"]==66,"Depth cells changed depth/NIL/morale/name/sort value or missed rating subset");
        ColumnSink depthColumns{columnTable};columnString(&depthColumns,7,"display","OVR");columnInt(&depthColumns,7,"formatType",15);columnBool(&depthColumns,7,"isTrend",true);columnInt(&depthColumns,8,"formatType",49);columnInt(&depthColumns,2,"formatType",13);
        output.values=nlohmann::json::array();replayColumns(depthColumns,&output,true,GridSchema::DepthChart);
        require(output.values[1]["value"]==0&&output.values[2]["value"]==false&&output.values[3]["value"]==49&&output.values[4]["value"]==13,"Depth rating format change affected NIL or ordinal formatter");
        std::array<std::string,90> redshirtNames{};
        const char* redshirtHeaders[]={"RS","Name","POS","Year","OVR","NIL","GP","SPD","ACC","AGI","COD","STR","AWR","CAR","BCV","BTK","TRK","SFA","SPM","JKM","CTH","CIT","SPC","SRR","MRR","DRR","RLS","JMP","THP","SAC","MAC","DAC","RUN","TUP","BSK","PAC","PBK","PBP","PBF","RBK","RBP","RBF","LBK","IBL","PRC","TAK","POW","BSH","FMV","PMV","PUR","MCV","ZCV","PRS","RET","KPW","KAC","STA","TGH","INJ","Last Name"};
        for(size_t i=0;i<std::size(redshirtHeaders);++i)redshirtNames[i]=redshirtHeaders[i];
        require(classifyGrid(redshirtNames,61)==GridSchema::Redshirts,"Captured Redshirts schema not recognized");
        redshirtNames[60]="Last Name Rating";require(classifyGrid(redshirtNames,61)==GridSchema::None,"Redshirts trailing identity field not gated");redshirtNames[60]="Last Name";
        redshirtNames[7]="Yards";require(classifyGrid(redshirtNames,61)==GridSchema::None,"Redshirts accepted statistics in attribute columns");redshirtNames[7]="SPD";
        require(classifyGrid(redshirtNames,60)==GridSchema::None,"Unverified compact Redshirts schema accepted");
        output.values=nlohmann::json::array();GridSink redshirtCells{gridTable,&output};redshirtCells.schema=GridSchema::Redshirts;redshirtCells.count=6;redshirtCells.columns={4,5,6,7,59,60};
        for(unsigned i=0;i<6;++i)gridString(&redshirtCells,i,"display",std::array<const char*,6>{"83,TrendUp","45","4","90","59","88"}[i]);
        gridInt(&redshirtCells,0,"intValue",83);
        require(output.values[0]["value"]=="B"&&output.values[3]["value"]=="45"&&output.values[4]["value"]=="4"&&output.values[5]["value"]=="A"&&output.values[8]["value"]=="F"&&output.values[11]["value"]=="88"&&output.values[12]["value"]==83,"Redshirts conversion touched NIL, games played, last name or sorting");
        std::array<std::string,90> injuryNames{};const char* injuryHeaders[]={"","POS","Name","POS","OVR","Injury","Length","IR","Return","Status"};
        for(size_t i=0;i<std::size(injuryHeaders);++i)injuryNames[i]=injuryHeaders[i];
        require(classifyGrid(injuryNames,10)==GridSchema::InjuryReport,"Captured Injury Report schema not recognized");
        require(classifyGrid(injuryNames,9)==GridSchema::None,"Injury Report lost its hidden leading column");
        injuryNames[8]="Yards";require(classifyGrid(injuryNames,10)==GridSchema::None,"Injury Report accepted an unrelated schema");
        output.values=nlohmann::json::array();GridSink injuryCells{gridTable,&output};injuryCells.schema=GridSchema::InjuryReport;injuryCells.count=6;injuryCells.columns={2,4,5,6,8,9};
        for(unsigned i=0;i<6;++i)gridString(&injuryCells,i,"display",std::array<const char*,6>{"McNeal","78","Dislocated Hip","2","33","Injured"}[i]);
        gridInt(&injuryCells,1,"intValue",78);
        require(output.values[0]["value"]=="McNeal"&&output.values[1]["value"]=="C"&&output.values[4]["value"]=="Dislocated Hip"&&output.values[5]["value"]=="2"&&output.values[6]["value"]=="33"&&output.values[7]["value"]=="Injured"&&output.values[8]["value"]==78,"Injury conversion changed injury text, length, return/status or sorting");
        std::array<std::string,90> athNames{};const char* athHeaders[]={"","RS","Name","Year","POS","OVR","DEV","SPD","ACC","AGI","COD","STR","AWR","THP","SAC","MAC","DAC","RUN","TUP","BSK","PAC","CAR","BCV","JKM","SPM","BTK","SFA","TRK","IBL","STA","TGH","INJ"};
        for(size_t i=0;i<std::size(athHeaders);++i)athNames[i]=athHeaders[i];
        require(classifyGrid(athNames,32)==GridSchema::PositionAth,"Captured ATH position-change schema not recognized");
        athNames[31]="Passing Yards";require(classifyGrid(athNames,32)==GridSchema::None,"ATH schema admitted ordinary stats");athNames[31]="INJ";
        require(classifyGrid(athNames,31)==GridSchema::None,"Unverified compact ATH schema admitted");
        output.values=nlohmann::json::array();GridSink athCells{gridTable,&output};athCells.schema=GridSchema::PositionAth;athCells.count=5;athCells.columns={5,6,7,31,2};
        for(unsigned i=0;i<5;++i)gridString(&athCells,i,"display",std::array<const char*,5>{"73,TrendNone","2","86","59","73"}[i]);
        gridInt(&athCells,0,"intValue",73);
        require(output.values[0]["value"]=="C"&&output.values[3]["value"]=="2"&&output.values[4]["value"]=="B"&&output.values[7]["value"]=="F"&&output.values[10]["value"]=="73"&&output.values[11]["value"]==73,"ATH conversion touched hiddenDEV/name/sort or missed ratings");
        std::array<std::string,90> leavingNames{};const char* leavingHeaders[]={"Name","","POS","Year","OVR","Reason","Persuasion Chance","RS"};
        for(size_t i=0;i<std::size(leavingHeaders);++i)leavingNames[i]=leavingHeaders[i];
        require(classifyGrid(leavingNames,8)==GridSchema::PlayersLeaving,"Captured Players Leaving schema not recognized");
        leavingNames[6]="Transfer Stats";require(classifyGrid(leavingNames,8)==GridSchema::None,"Leaving schema accepted unrelated table");
        output.values=nlohmann::json::array();GridSink leavingCells{gridTable,&output};leavingCells.schema=GridSchema::PlayersLeaving;leavingCells.count=5;leavingCells.columns={4,5,6,7,0};
        for(unsigned i=0;i<5;++i)gridString(&leavingCells,i,"display",std::array<const char*,5>{"80","Transfer (NIL)","Medium","1","Toothman"}[i]);
        gridInt(&leavingCells,0,"intValue",80);
        require(output.values[0]["value"]=="B"&&output.values[3]["value"]=="Transfer (NIL)"&&output.values[4]["value"]=="Medium"&&output.values[5]["value"]=="1"&&output.values[6]["value"]=="Toothman"&&output.values[7]["value"]==80,"Leaving conversion changed reasons, persuasion, redshirt, name or sort value");
        std::array<std::string,90> trainingNames{};const char* trainingIdentity[]={"","RS","Name","Year","POS","OVR","NIL"};
        for(size_t i=0;i<std::size(trainingIdentity);++i)trainingNames[i]=trainingIdentity[i];
        for(unsigned i=7;i<60;++i)trainingNames[i]=redshirtHeaders[i];trainingNames[60]="LSP";
        require(classifyGrid(trainingNames,61)==GridSchema::Training,"Captured Training Results schema not recognized");
        require(classifyGrid(trainingNames,9)==GridSchema::Training,"Known training position subset rejected");
        trainingNames[7]="Yards";require(classifyGrid(trainingNames,61)==GridSchema::None,"Training schema admitted statistics");trainingNames[7]="SPD";
        for(int current=0;current<=100;++current){
            const auto expected=display(Visibility::Revealed,current);
            require(trainingRatingLabel(std::to_string(current).c_str())==expected,"Training zero delta base failed");
            for(int previous=0;previous<=100;++previous)if(previous!=current){
                const auto delta=current-previous;const auto suffix=",TrendWithDelta,("+std::string(delta>0?"+":"")+std::to_string(delta)+")";
                require(trainingRatingLabel((std::to_string(current)+suffix).c_str())==expected+suffix,"Training base changed its native adjustment/trend suffix");
            }
        }
        for(const auto* invalid:{"?","-1","101","079","79.5","97,TrendWithDelta,2","97,TrendWithDelta,(+0)","97,TrendWithDelta,(+101)","97,TrendWithDelta,(+02)","97,TrendWithDelta,(+2) yards","97,TrendWithDelta,(+2),other"})require(trainingRatingLabel(invalid)==invalid,"Malformed training delta was converted");
        output.values=nlohmann::json::array();GridSink trainingCells{gridTable,&output};trainingCells.schema=GridSchema::Training;trainingCells.count=5;trainingCells.columns={5,6,7,60,2};
        for(unsigned i=0;i<5;++i)gridString(&trainingCells,i,"display",std::array<const char*,5>{"97,TrendWithDelta,(+2)","10","75,TrendWithDelta,(-3)","88","97"}[i]);
        gridInt(&trainingCells,0,"intValue",97);
        require(output.values[0]["value"]=="A,TrendWithDelta,(+2)"&&output.values[3]["value"]=="10"&&output.values[4]["value"]=="C,TrendWithDelta,(-3)"&&output.values[7]["value"]=="B"&&output.values[10]["value"]=="97"&&output.values[11]["value"]==97,"Training cells changed delta, NIL, name or numeric sort metadata");
        ColumnSink trainingColumns{columnTable};columnInt(&trainingColumns,5,"formatType",35);columnBool(&trainingColumns,5,"isTrend",true);columnInt(&trainingColumns,6,"formatType",49);columnInt(&trainingColumns,7,"formatType",35);
        output.values=nlohmann::json::array();replayColumns(trainingColumns,&output,true,GridSchema::Training);
        require(output.values[0]["value"]==35&&output.values[1]["value"]==true&&output.values[2]["value"]==49&&output.values[3]["value"]==35,"Training removed the native delta renderer or changed NIL format");
        std::array<std::string,90> encourageNames{};const char* encourageHeaders[]={"","Name","Year","POS","OVR","NIL","DEV","SPD","STR","ACC","AGI","AWR","BCV","BSH","BSK","CAR","CTH","COD","FMV","POW","INJ","JKM","JMP","KAC","KPW","RET","LBK","MCV","PBF","PBP","PBK","PAC","PRC","PMV","PRS","PUR","RLS","DRR","MRR","SRR","RBF","RBP","RBK","SPC","SPD","SPM","STA","SFA","STR","TAK","DAC","MAC","SAC","RUN","THP","TUP","TGH","TRK","ZCV","IBL","LSP"};
        for(size_t i=0;i<std::size(encourageHeaders);++i)encourageNames[i]=encourageHeaders[i];
        require(classifyGrid(encourageNames,61)==GridSchema::EncourageTransfers,"Captured Encourage Transfers schema not recognized");
        encourageNames[60]="Games Played";require(classifyGrid(encourageNames,61)==GridSchema::None,"Encourage schema admitted statistics");encourageNames[60]="LSP";
        output.values=nlohmann::json::array();GridSink encourageCells{gridTable,&output};encourageCells.schema=GridSchema::EncourageTransfers;encourageCells.count=6;encourageCells.columns={4,5,6,7,60,1};
        for(unsigned i=0;i<6;++i)gridString(&encourageCells,i,"display",std::array<const char*,6>{"57,TrendNone","10","2","71","88","Joseph"}[i]);
        gridInt(&encourageCells,0,"intValue",57);
        require(output.values[0]["value"]=="F"&&output.values[3]["value"]=="10"&&output.values[4]["value"]=="2"&&output.values[5]["value"]=="C"&&output.values[8]["value"]=="B"&&output.values[11]["value"]=="Joseph"&&output.values[12]["value"]==57,"Encourage conversion changed NIL,DEV,name or numeric sort value");
        FixtureView view;view.maps[1]={{"overall",2},{"teamOverall",3},{"jersey",4}};view.numbers={{2,82},{3,64},{4,1}};std::string changed;
        require(selectedOverall(view,1,[&](uintptr_t root,const char* key,const char* value){require(root==1,"Selected player root changed");changed=std::string(key)+"="+value;})&&changed=="overall=B","Selected overall not scoped to player field");
        view.numbers[2]=-1;require(!selectedOverall(view,1,[&](uintptr_t,const char*,const char*){throw std::runtime_error("Invalid selected rating exposed");}),"Invalid player overall changed");
        view.arrays[10]={11};view.maps[11]={{"PlayerA",12},{"PlayerB",13},{"StatLine",14}};view.maps[12]={{"Overall",15},{"Jersey",16}};view.maps[13]={{"Overall",17},{"RecordList",18}};view.numbers[15]=90;view.numbers[17]=59;
        std::vector<std::string> edits;auto capture=[&](uintptr_t root,const char* key,const char* value){edits.push_back(std::to_string(root)+":"+key+"="+value);};
        require(convert(view,10,Surface::Comparison,capture)==2&&edits==std::vector<std::string>{"12:Overall=A","13:Overall=F"},"Comparison touched statistics or failed to hide player overalls");
        // Current native comparison stores one Overall per role in RecordList.
        view.maps[12]={{"RecordList",60},{"Jersey",16}};view.maps[13]={{"RecordList",61},{"Name",18}};view.arrays[60]={62,63};view.arrays[61]={64};
        view.maps[62]={{"Overall",65},{"PlayerTypeName",66}};view.maps[63]={{"Overall",67},{"Jersey",16}};view.maps[64]={{"Overall",68},{"PlayerTypeName",69}};view.maps[14]={{"Overall",70},{"Yards",71}};
        view.numbers[65]=90;view.numbers[67]=79;view.numbers[68]=59;view.numbers[70]=90;view.numbers[71]=450;edits.clear();
        require(convert(view,10,Surface::Comparison,capture)==3&&edits==std::vector<std::string>{"62:Overall=A","63:Overall=C","64:Overall=F"},"Native comparison role Overall path missed or StatLine/identity values changed");
        edits.clear();view.maps[11]={{"Name",14},{"Value",15},{"GroupColor",16}};
        require(convert(view,10,Surface::TopAttributes,capture)==1&&edits==std::vector<std::string>{"11:Value=A"},"Top attributes changed group color/name");
        view.maps[20]={{"OVR",21},{"Jersey",22},{"PrimaryPositionDepth",23}};view.strings[21]="80";edits.clear();
        require(convert(view,20,Surface::PlaycallSubstitution,capture)==1&&edits==std::vector<std::string>{"20:OVR=B"},"Playcall substitution touched jersey or depth");
        view.strings[21]="?";require(convert(view,20,Surface::PlaycallSubstitution,capture)==0,"Hidden playcall rating became a grade");
        view.maps[30]={{"overall",31},{"attributesSubpanelInfo",32},{"NILCompensation",33},{"skillPoints",34}};view.numbers[31]=88;view.numbers[33]=90;view.numbers[34]=70;
        view.arrays[32]={35,36,37};view.maps[35]={{"ratingValue",38},{"isFullyScouted",39}};view.maps[36]={{"ratingValue",40},{"isFullyScouted",41}};view.maps[37]={{"ratingValue",42},{"isFullyScouted",43}};
        view.numbers[38]=92;view.booleans[39]=true;view.numbers[40]=80;view.booleans[41]=false;view.numbers[42]=90.5;view.booleans[43]=true;edits.clear();
        require(convert(view,30,Surface::RosterNIL,capture)==2&&edits==std::vector<std::string>{"30:overall=B","35:ratingValue=A"},"Roster NIL changed compensation/points or uncertain/invalid attributes");
        view.maps[30]["injuryLength"]=45;view.maps[30]["injuryRisk"]=46;view.maps[30]["age"]=47;view.maps[30]["injuryName"]=48;view.maps[30]["seasonStats"]=49;
        view.numbers[45]=33;view.numbers[46]=78;view.numbers[47]=21;view.strings[48]="Torn Pectoral";view.maps[49]={{"Yards",70}};view.numbers[70]=450;edits.clear();
        require(convert(view,30,Surface::RosterNIL,capture)==2&&edits==std::vector<std::string>{"30:overall=B","35:ratingValue=A"},"Injury sidebar touched duration/risk/age/injury name/season statistics");
        view.maps[30]["careerStats"]=80;view.maps[80]={{"Overall",81},{"Yards",82},{"Rank",83},{"CompletionPercentage",84}};
        view.numbers[81]=90;view.numbers[82]=9500;view.numbers[83]=75;view.numbers[84]=70;
        const auto statisticsNumbers=view.numbers;edits.clear();
        require(convert(view,30,Surface::RosterNIL,capture)==2&&edits==std::vector<std::string>{"30:overall=B","35:ratingValue=A"}&&view.numbers==statisticsNumbers,"Stats sidebar changed career/season totals, ranks, percentages or numeric source fields");
        view.maps[30]["isCoach"]=44;view.booleans[44]=false;edits.clear();
        require(convert(view,30,Surface::AnnualAwardsPlayer,capture)==2&&edits==std::vector<std::string>{"30:overall=B","35:ratingValue=A"},"Annual award player fields missed");
        view.booleans[44]=true;edits.clear();
        require(convert(view,30,Surface::AnnualAwardsPlayer,capture)==0&&edits.empty(),"Annual coach prestige/attributes changed");
        view.booleans.erase(44);view.numbers[44]=0;
        require(convert(view,30,Surface::AnnualAwardsPlayer,capture)==0&&edits.empty(),"Nonboolean award discriminator accepted");
        view.maps[30].erase("isCoach");
        require(convert(view,30,Surface::AnnualAwardsPlayer,capture)==0&&edits.empty(),"Missing player discriminator admitted annual award");
        view.maps[50]={{"ovr",51},{"Height",52},{"Weight",53},{"PlayerId",54},{"Stats",55}};view.numbers[51]=59;view.numbers[52]=73;view.numbers[53]=200;view.numbers[54]=88;edits.clear();
        require(convert(view,50,Surface::ContextPlayer,capture)==1&&edits==std::vector<std::string>{"50:ovr=F"},"Context player panel touched physical/identity/statistical fields");
        view.arrays[70]={71};view.maps[71]={{"Description",72},{"UpgradeDescription",73},{"Cost",74},{"CurrentRank",75},{"HasMetRequirements",76}};
        view.strings[72]="Improved pass blocking";view.strings[73]="Bronze Requires: 84 Pass Block Power (75 Currently)";view.numbers[74]=2;view.numbers[75]=1;view.booleans[76]=false;edits.clear();
        const auto beforeAbilityNumbers=view.numbers;const auto beforeAbilityFlags=view.booleans;
        require(convertAbilityDescriptions(view,70,capture)==1&&edits==std::vector<std::string>{"71:UpgradeDescription=Bronze Requires: B Pass Block Power (C Currently)"}&&view.numbers==beforeAbilityNumbers&&view.booleans==beforeAbilityFlags,"Ability UI conversion changed cost/rank/eligibility or another field");
        runtime::originalAbilities=fakeAbilities;void* abilityValue=reinterpret_cast<void*>(0x1234);
        runtime::disabled=true;require(runtime::playerAbilitiesHook(nullptr,&abilityValue,true)==&abilityValue&&abilityMentals&&abilityForwarded==1&&abilityValue==reinterpret_cast<void*>(0x1234),"Stopped ability getter changed bool argument/native return");runtime::disabled=false;
        for(size_t i=0;i<runtime::keyedPlayerBindingCount;++i)runtime::keyedPlayerOriginal[i]=fakeAward;
        runtime::disabled=true;
        for(const auto hook:runtime::keyedPlayerHooks)require(hook(nullptr,&abilityValue,reinterpret_cast<void*>(0x4567))==&abilityValue&&awardKey==reinterpret_cast<void*>(0x4567)&&abilityValue==reinterpret_cast<void*>(0x1234),"Award getter changed opaque key/output/native return");
        require(awardForwarded==runtime::keyedPlayerBindingCount,"Award getter did not invoke native exactly once");runtime::disabled=false;
        MapTestOutput mapOutput{mapTestTable};MapSink map{mapTable,&mapOutput,"overall"};mapInt(&map,"overall",66);mapInt(&map,"Overall",83);mapInt(&map,"jersey",92);mapFloat(&map,"height",74.5f);mapBool(&map,"redshirt",true);mapString(&map,"lastName","Branham");mapUndefined(&map,"injury");mapOpaque(&map,"nested",reinterpret_cast<void*>(123));
        require(mapOutput.values==nlohmann::json({{"overall","D"},{"Overall",83},{"jersey",92},{"height",74.5},{"redshirt",true},{"lastName","Branham"},{"injury",nullptr},{"nested",123}})&&map.changed==1,"Native map collector changed another property's type or value");
        mapInt(&map,"overall",-1);require(mapOutput.values["overall"]==-1&&map.changed==1,"Map collector converted hidden overall sentinel");
        map.key="Overall";map.labelKey="DEOverallGrade";mapInt(&map,"Overall",83);
        require(mapOutput.values["Overall"]==83&&mapOutput.values["DEOverallGrade"]=="B","Shared progression Overall became a string");
    }
    {
        GridTestOutput output{gridTestTable};ClassGridSink sink{classGridTable,&output,reinterpret_cast<void*>(123),0,7,gridTestLabel};
        classGridReserve(&sink,2);classGridBool(&sink,0,"isTrend",true);classGridInt(&sink,0,"value",42);classGridFloat(&sink,0,"trend",1.5f);
        classGridString(&sink,0,"display","JC (SO)");classGridString(&sink,0,"tooltip","JC (SO)");classGridString(&sink,1,"display","HS");require(sink.count==1&&output.values.size()==6,"Class cell was not deferred until the native getter returned");classGridFlush(&sink);
        require(output.values[1]["value"]==true&&output.values[2]["value"]==42&&output.values[3]["value"]==1.5,"Class grid changed another cell property type");
        require(output.values[6]["value"]=="FCS (SO)"&&output.values[4]["value"]=="JC (SO)"&&output.values[5]["value"]=="HS","Class grid edited an unrelated label");
        sink.row=8;classGridString(&sink,0,"display","JC (SO)");classGridFlush(&sink);require(output.values.back()["value"]=="JC (SO)","Unmatched record received another recruit's class");
        runtime::originalClassRows=fakeClassRows;GridTestColumns columns{gridTestColumnsTable,15};
        require(classGridColumns(&columns),"Recruit Class column not recognized");columns.column=14;require(!classGridColumns(&columns),"Non-Class columns missed the passthrough fast path");columns.column=15;
        for(bool stopped:{false,true}){runtime::disabled=stopped;runtime::classRowsHook(reinterpret_cast<void*>(1),&output,2,3,&columns);
            require(gridTestArgs[0]==1&&gridTestArgs[2]==2&&gridTestArgs[3]==3&&gridTestArgs[4]==reinterpret_cast<uintptr_t>(&columns),"Class grid getter changed native argument registers or fifth stack argument");
            if(stopped)require(gridTestArgs[1]==reinterpret_cast<uintptr_t>(&output),"Stopped class grid failed to pass through");}
        runtime::disabled=false;
    }
#endif
    {
        FixtureView view;view.arrays[1]={10,20};
        view.maps[10]={{"MotivationString",11},{"Grade",12},{"IntelStatus",13},{"IsDealbreakerViolated",14}};
        view.maps[20]={{"MotivationString",21},{"Grade",22}};
        view.strings={{11,"Playing Time"},{12,"A+"},{21,"Playing Style"},{22,"C"}};view.numbers[13]=2;view.booleans[14]=true;
        std::map<uintptr_t,std::map<std::string,std::string>> texts;std::map<uintptr_t,std::map<std::string,unsigned>> numbers;
        auto setText=[&](uintptr_t at,const char* key,const char* value){texts[at][key]=value;};
        auto setNumber=[&](uintptr_t at,const char* key,unsigned value){numbers[at][key]=value;};
        {
            FixtureView preview;preview.maps[1]={{"dealBreakerSubpanelInfo",2},{"attributesSubpanelInfo",9}};
            preview.maps[2]={{"playingTime",3},{"hasGradeText",4},{"neededGradeText",5},{"hasGrade",6},{"neededGrade",7}};
            preview.strings={{3,"Playing Time"},{4,"A+"},{5,"C-"}};preview.numbers={{6,0},{7,8}};
            auto result=maskPlayingTime(preview,1,PlayingTimeSurface::ProspectEntry,0,{},setText,setNumber);
            require(result.grades==2&&texts[2]["hasGradeText"]=="?"&&texts[2]["neededGradeText"]=="?"&&numbers[2]["hasGrade"]==0&&numbers[2]["neededGrade"]==0,"Prospect List Playing Time grades or arrow comparison leaked");
            texts.clear();numbers.clear();preview.strings[3]="Playing Style";result=maskPlayingTime(preview,1,PlayingTimeSurface::ProspectEntry,0,{},setText,setNumber);
            require(!result.grades&&texts.empty()&&numbers.empty(),"Prospect List mask hid another motivation");
        }
        const auto beforeNumbers=view.numbers;const auto beforeFlags=view.booleans;
        for(const auto* grade:{"A+","A","B+","B","C+","C","D","F"}){
            view.strings[12]=grade;texts.clear();auto stats=maskPlayingTime(view,1,PlayingTimeSurface::Motivations,0,{},setText,setNumber);
            require(stats.grades==1&&texts[10]["Grade"]=="?"&&!texts.count(20),"Playing Time mask depends on the hidden grade or changes another motivation");
        }
        require(view.numbers==beforeNumbers&&view.booleans==beforeFlags&&numbers.empty(),"Interest or native eligibility was changed");
        view.maps[10]={{"RecruitingMotivation",11},{"DealbreakerTeamGrade",12},{"DealbreakerTeamLevel",13},{"Locked",14}};
        view.maps[20]={{"RecruitingMotivation",21},{"DealbreakerTeamGrade",22}};texts.clear();numbers.clear();
        auto stats=maskPlayingTime(view,1,PlayingTimeSurface::RecruitList,0,{},setText,setNumber);
        require(stats.dealbreakers==2&&numbers[10]["DealbreakerTeamGrade"]==255&&numbers[10]["DealbreakerTeamLevel"]==255&&!numbers.count(20),"Dealbreaker mask is not scoped to Playing Time");
        require(!numbers[10].count("Locked"),"Dealbreaker eligibility was changed");
        // My School's board-comparison grade must be hidden too.
        view.maps[10]={{"Grade",12}};view.maps[20]={{"Grade",22}};texts.clear();numbers.clear();
        stats=maskPlayingTime(view,1,PlayingTimeSurface::SchoolModule,playingTimeSchoolTile,{},setText,setNumber);
        require(stats.grades==2&&texts[10]["Grade"]=="?"&&texts[20]["Grade"]=="?","My School comparison leaked Playing Time grades");
        texts.clear();stats=maskPlayingTime(view,1,PlayingTimeSurface::SchoolModule,0,{},setText,setNumber);require(texts.empty(),"Other My School categories were changed");
        // Only bundle 2 contains Playing Time. Preserve other aggregate grades
        // and individual non-Playing-Time grades within the same pitch.
        view.maps[10]={{"PitchTypeID",15},{"Grade",12},{"Gain",16},{"Motivations",2}};view.numbers[15]=2;view.arrays[2]={30,40};
        view.maps[20]={{"PitchTypeID",25},{"Grade",22}};view.numbers[25]=0;
        view.maps[30]={{"Name",31},{"Grade",32}};view.strings[31]="Playing Time";view.strings[32]="A+";
        view.maps[40]={{"Name",41},{"Grade",42}};view.strings[41]="Brand Exposure";view.strings[42]="C";
        texts.clear();stats=maskPlayingTime(view,1,PlayingTimeSurface::Pitches,0,{2},setText,setNumber);
        require(texts[10]["Grade"]=="?"&&texts[10]["Gain"]=="?"&&texts[30]["Grade"]=="?"&&!texts.count(20)&&!texts.count(40),"Pitch aggregate or nested motivation masking is incorrect");
        view.maps[30]={{"Motivation",33},{"Grade",32},{"ActivityId",34},{"Triangles",35},{"MaxInfluenceTriangles",36}};view.numbers[33]=9;view.numbers[34]=123;
        texts.clear();numbers.clear();stats=maskPlayingTime(view,2,PlayingTimeSurface::VisitActivities,0,{},setText,setNumber);
        require(texts[30]["Grade"]=="?"&&numbers[30]["Triangles"]==0&&numbers[30]["MaxInfluenceTriangles"]==0&&!numbers[30].count("ActivityId")&&!texts.count(40),"Visit preview leaked grade or changed the action ID");
        stats=maskPlayingTime(view,999,PlayingTimeSurface::Motivations,0,{},setText,setNumber);require(stats.unsupported==1,"Invalid Playing Time root was not reported");
    }
    {
        // Exercise the guarded reader against a synthetic native pitch config,
        // not a hard-coded list of the six stock bundles.
        std::array<unsigned char,0x430> object{};std::array<unsigned char,0x150> context{};std::array<unsigned char,0x470> config{};
        std::array<unsigned char,0x40> entry{};std::array<unsigned char,3> motives={2,9,12};
        auto pointer=[](auto& bytes,size_t at,uintptr_t value){memcpy(bytes.data()+at,&value,8);};
        const auto entryPointer=reinterpret_cast<uintptr_t>(entry.data());
        const auto begin=reinterpret_cast<uintptr_t>(&entryPointer);
        pointer(object,0x420,reinterpret_cast<uintptr_t>(context.data()));pointer(context,0x148,reinterpret_cast<uintptr_t>(config.data()));
        pointer(config,0x460,begin);pointer(config,0x468,begin+8);entry[0x10]=17;
        pointer(entry,0x30,reinterpret_cast<uintptr_t>(motives.data()));pointer(entry,0x38,reinterpret_cast<uintptr_t>(motives.data())+3);
        auto result=runtime::pitchMask(reinterpret_cast<uintptr_t>(object.data()));require(result==std::set<unsigned>{17},"Pitch membership was not read from verified native configuration");
        motives[1]=10;result=runtime::pitchMask(reinterpret_cast<uintptr_t>(object.data()));require(result.empty(),"Non-Playing-Time bundle was masked");
        pointer(config,0x468,begin+9);result=runtime::pitchMask(reinterpret_cast<uintptr_t>(object.data()));require(result.size()==256,"Invalid pitch configuration must not expose aggregate grades");
    }
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
    runtime::detailOriginal[0]=fakeDetailGetter;runtime::disabled=false;
    require(runtime::detailHook<0>(nullptr,out,0xabcdef,0x123456)==out&&forwarded==3&&detailArguments==std::array<uintptr_t,2>{0xabcdef,0x123456},"Detail getter changed native arguments or return");
    runtime::disabled=true;require(runtime::detailHook<0>(nullptr,out,5,6)==out&&forwarded==4&&detailArguments==std::array<uintptr_t,2>{5,6},"Stopped detail hook did not pass through");
    std::cout<<"Passed: grade boundaries, hidden states, 5151 ranges, Playing Time/dealbreaker/bundle/visit/My School masks, native pitch configuration, malformed values and native getter ABIs.\n";
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}return 0;}
