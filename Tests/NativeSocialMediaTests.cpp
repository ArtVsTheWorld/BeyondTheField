#include "../Source/NativeSocialMedia.cpp"
#include <iostream>
#include <map>
#include <set>
namespace fixture {
struct Collector {void** vt;std::map<unsigned,Json> rows;};
void __fastcall b(Collector* c,unsigned r,const char* k,bool v){c->rows[r][k]=v;}
void __fastcall i(Collector* c,unsigned r,const char* k,int v){c->rows[r][k]=v;}
void __fastcall f(Collector* c,unsigned r,const char* k,float v){c->rows[r][k]=v;}
void __fastcall s(Collector* c,unsigned r,const char* k,const char* v){c->rows[r][k]=v;}
void* vt[]={nullptr,nullptr,nullptr,reinterpret_cast<void*>(b),reinterpret_cast<void*>(i),reinterpret_cast<void*>(f),reinterpret_cast<void*>(s)};
std::string lastDonorPanel;
void* expectedRequestSelf=nullptr;
void* expectedRequestParams=nullptr;
unsigned requestCalls=0;
const unsigned char* executingBody=nullptr;
const unsigned char* __fastcall originalScriptBody(void*){return executingBody;}
bool requestResult=true;
bool __fastcall originalRequest(void* self,void* panel,void* params){lastDonorPanel=argument(panel);++requestCalls;return requestResult&&self==expectedRequestSelf&&params==expectedRequestParams;}
void __fastcall donorRows(void*,void* panel,void* out){
    lastDonorPanel=argument(panel);
    rowText(out,0,"panelId",lastDonorPanel.c_str());rowText(out,0,"tileCoords",lastDonorPanel=="cm_team"?"3":"5");
    rowSet(out,0,"UseTileDimensions",false,3);rowSet(out,0,"UseFrame",true,3);
    rowSet(out,0,"Priority",0,4);
}
unsigned filterForwardCalls=0;
void __fastcall originalFilter(void*,void* out,void*,void*){++filterForwardCalls;rowText(out,0,"display","Original category");}
unsigned changedForwardCalls=0;
unsigned navForwardCalls=0;
std::string navForwardName;
void __fastcall originalNav(void*,unsigned,const char* name,void*){++navForwardCalls;navForwardName=name?name:"";}
void __fastcall originalChanged(void*,const char*,const char*,void*){++changedForwardCalls;}
struct FilterValue {void** vt;int key;};
int __fastcall filterKey(FilterValue* value){return value->key;}
void require(bool result,const char* detail){if(!result)throw std::runtime_error(detail);}
}
int main(int argc,char** argv){
    using namespace fixture;
    try {
        {
            const auto savedContainers=containers;const auto savedNav=navRequest;
            containers=donorRows;navRequest=originalNav;enhancements::currentOptions=38;
            opened=false;uiReady=false;disabled=false;admittedHubEntries[teamEntry.panel]=true;
            Collector out{vt,{}};Alias team{aliasVt,teamEntry.panel};containerHook(nullptr,&team,&out);
            require(out.rows.size()==1&&!admittedHubEntries[teamEntry.panel],"Social Off altered native hub rows or retained its shortcut admission");
            const auto calls=navForwardCalls;navRequestHook(nullptr,0,"NEWS_MENU",nullptr);
            require(navForwardCalls==calls+1&&navForwardName=="DO_NOTHING"&&!opened,"Social Off opened a stale cached feed button or stranded navigation");
            containers=savedContainers;navRequest=savedNav;enhancements::currentOptions=39;
        }
        {
            dynasty::live::PackedChangeWatch watch;std::vector<unsigned char> memory(0x4000,7);constexpr uintptr_t start=0x100000;
            watch.record(start+4,{1,2,3,4});watch.record(start+6,{3,4,5});watch.record(start+0x800,{9});
            const auto count=watch.bytes();watch.record(start+4,{1,2,3,4});require(watch.bytes()==count,"Repeated packed reads were retained twice");
            auto put=[&](uintptr_t at,const std::vector<unsigned char>& bytes){memcpy(memory.data()+at-start,bytes.data(),bytes.size());};put(start+4,{1,2,3,4,5});put(start+0x800,{9});
            unsigned calls=0;auto q=[&](uintptr_t at,void* out,size_t size){++calls;if(at<start||at-start+size>memory.size())return false;memcpy(out,memory.data()+at-start,size);return true;};
            require(watch.unchanged(q)&&calls==1,"Same-page observation ranges did not coalesce");
            memory[0x200]=55;require(watch.unchanged(q),"Unconsumed UI bytes caused a false change");
            for(size_t at:{size_t(4),size_t(7),size_t(0x800)}){auto old=memory[at];memory[at]^=1;require(!watch.unchanged(q),"Consumed midweek byte change was missed");memory[at]=old;}
            require(!watch.unchanged([](uintptr_t,void*,size_t){return false;}),"Failed/cancelled observation was reported unchanged");
            bool conflict=false;try{watch.record(start+6,{33});}catch(...){conflict=true;}require(conflict,"Changing overlapping capture reads were accepted");
            dynasty::live::PackedChangeWatch empty;require(!empty.available()&&!empty.unchanged(q),"An uninitialized observer suppressed capture");
            dynasty::live::PackedChangeWatch large;std::vector<unsigned char> data(2*1024*1024+3,42);large.record(start,data);size_t maximumRead=0,reads=0;
            auto largeRead=[&](uintptr_t at,void* out,size_t n){maximumRead=(std::max)(maximumRead,n);++reads;if(at<start||at-start+n>data.size())return false;memcpy(out,data.data()+at-start,n);return true;};
            require(large.unchanged(largeRead)&&reads==3&&maximumRead<=dynasty::live::PackedChangeWatch::chunkBytes,"Large probes escaped their bounded chunk size");data.back()^=1;require(!large.unchanged(largeRead),"A changed final chunk was ignored");
        }
        {
            dynasty::live::PackedChangeWatch watch;unsigned char byte=1;const auto at=reinterpret_cast<uintptr_t>(&byte);
            auto read=[](uintptr_t p,void* out,size_t n){memcpy(out,reinterpret_cast<const void*>(p),n);return true;};
            watch.recordMasked(at,{1},{1});byte=65;require(watch.unchanged(read),"Unselected packed bits triggered a refresh");
            byte=64;uintptr_t changed=0;require(!watch.unchanged(read,&changed)&&changed==at,"Selected packed bit change was missed");
            byte=3;watch.recordMasked(at,{2},{2});require(watch.unchanged(read),"Disjoint selected bits were not merged");
            bool conflict=false;try{watch.recordMasked(at,{0},{2});}catch(...){conflict=true;}require(conflict,"Conflicting selected bits were accepted");
        }
        {
            dynasty::live::Memory reader;dynasty::live::PackedChangeWatch textWatch;reader.observation=&textWatch;
            std::array<unsigned char,64> text{};memcpy(text.data(),"Hello",5);const auto at=reinterpret_cast<uintptr_t>(text.data());
            auto read=[](uintptr_t p,void* out,size_t n){memcpy(out,reinterpret_cast<const void*>(p),n);return true;};
            require(reader.text(at)=="Hello","String fixture decoding changed");text[20]=77;require(textWatch.unchanged(read),"Bytes after NUL caused a false refresh");
            text[5]='!';require(!textWatch.unchanged(read),"String growth beyond a former NUL was missed");text[5]=0;text[0]='J';require(!textWatch.unchanged(read),"String content change was missed");
            dynasty::live::PackedChangeWatch ssoWatch;reader.observation=&ssoWatch;std::array<unsigned char,16> small{};memcpy(small.data(),"Coach",5);small[15]=10;const auto sso=reinterpret_cast<uintptr_t>(small.data());
            require(reader.sso(sso)=="Coach","SSO fixture decoding changed");small[9]=90;require(ssoWatch.unchanged(read),"Unused SSO capacity caused a false refresh");small[15]=9;require(!ssoWatch.unchanged(read),"SSO length change was missed");
        }
        {
            std::vector<unsigned char> assets(0x43000),replacement;const auto a=reinterpret_cast<uintptr_t>(assets.data());
            auto mount=[&](uintptr_t root){newsLayout=root+0x2c658;newsBodyStyle=root+0x2ccd2;newsGrid=root+0x40000;newsVerticalInput=root+0x40100;newsScroll=root+0x41000;newsViewport=root+0x42000;};mount(a);
            auto put=[](uintptr_t target,const auto& bytes){memcpy(reinterpret_cast<void*>(target),bytes.data(),bytes.size());};
            put(newsLayout,social::newsLayoutOriginal);put(newsBodyStyle,social::polish::bodyOriginal);put(newsGrid,social::newsGridOriginal);put(newsVerticalInput,social::newsVerticalInputOriginal);put(newsScroll,social::newsScrollOriginal);put(newsViewport,social::polish::viewportOriginal);
            require(newsLayoutUsable(),"Complete original layout cache was rejected");replacement=assets;
            for(const auto at:{newsLayout,newsBodyStyle,newsGrid,newsVerticalInput,newsScroll,newsViewport}){layoutDiscoveryNeeded=false;*reinterpret_cast<unsigned char*>(at)^=1;require(!newsLayoutUsable()&&layoutDiscoveryNeeded,"A replaced layout component did not request background rediscovery");*reinterpret_cast<unsigned char*>(at)^=1;}
            assets[0x2c658]^=1;require(!newsLayoutUsable(),"Released layout cache was still ready");mount(reinterpret_cast<uintptr_t>(replacement.data()));require(newsLayoutUsable(),"Replacement asset bundle did not restore readiness");
            require(replacement[0x2c658]==social::newsLayoutOriginal[0],"Readiness checks modified native bytecode");newsLayout=1;require(!newsLayoutUsable(),"Unreadable cached layout was accepted");
            newsLayout=newsBodyStyle=newsGrid=newsVerticalInput=newsScroll=newsViewport=0;layoutDiscoveryNeeded=false;
        }
        {
            std::vector<unsigned char> screenData(0x3000),modelData(0x30000);
            const auto screenAt=reinterpret_cast<uintptr_t>(screenData.data()),modelAt=reinterpret_cast<uintptr_t>(modelData.data());
            memcpy(screenData.data(),"Apt Data:1:7:8",14);memcpy(modelData.data(),"Apt Data:1:7:8",14);
            auto put=[&](uintptr_t at,auto value){memcpy(reinterpret_cast<void*>(at),&value,sizeof(value));};
            put(screenAt+0x8a0-16,unsigned(180));put(screenAt+0x8a0-8,screenAt+0x100);
            put(modelAt+0x24970-16,unsigned(41));put(modelAt+0x24970-8,modelAt+0x2000);
            memcpy(screenData.data()+0x8a0,dropdownPatches[0].original.data(),dropdownPatches[0].original.size());
            for(const auto& patch:dropdownPatches)if(patch.model)memcpy(modelData.data()+patch.offset,patch.original.data(),patch.original.size());
            auto q=[&](uintptr_t at,void* out,size_t n){for(const auto& span:std::vector<std::pair<uintptr_t,size_t>>{{screenAt,screenData.size()},{modelAt,modelData.size()}})if(at>=span.first&&at-span.first<=span.second&&n<=span.second-(at-span.first)){memcpy(out,reinterpret_cast<void*>(at),n);return true;}return false;};
            require(social::assets::screen(screenAt+0x8a0,726,dropdownPatches,q)==screenAt,"Actual News body did not resolve its own asset");
            require(social::assets::model(modelAt+0x24970,91,dropdownPatches,q)==modelAt,"Actual News Init body did not resolve its own model");
            require(!social::assets::screen(screenAt+0x8a0,725,dropdownPatches,q)&&!social::assets::model(modelAt+0x24970,90,dropdownPatches,q),"Foreign action length passed asset discovery");
            screenData[0x8a0]^=1;require(!social::assets::screen(screenAt+0x8a0,726,dropdownPatches,q),"Modified foreign template passed discovery");screenData[0x8a0]^=1;
            put(screenAt+0x8a0-8,modelAt);require(!social::assets::screen(screenAt+0x8a0,726,dropdownPatches,q),"External template constant pool passed discovery");
            put(modelAt+0x24970-16,unsigned(42));require(!social::assets::model(modelAt+0x24970,91,dropdownPatches,q),"Foreign News model constant pool passed discovery");
        }
        for(const auto& binding:bindings)require(binding.vt!=0xbac63a8||binding.offset!=0x20,"Recovery build must leave native MenuPanelsReady unhooked");
        {
            auto c=std::make_shared<social::Catalog>();c->scopes={{"all","For You"},{"team:1","Team"}};social::Edition e;e.key="paged";
            for(int n=0;n<38;++n){auto id=std::to_string(n);social::FeedPost parent{"Beat","@Beat","Report","Recruiting"};parent.category="recruiting";e.stories.emplace(id,parent);auto reply=parent;reply.replyTo=id;reply.voice="fan";e.stories.emplace(id+"r",reply);e.views["team:1"].push_back(id);e.views["team:1"].push_back(id+"r");}c->weeks.push_back(e);
            auto all=social::selectFeed(c,0,1,1);require(all->posts.size()==76&&all->total==76,"Filtered teams must expose every qualified post without page navigation");
            for(size_t n=0;n<all->posts.size();n+=2)require(all->posts[n+1].replyTo==std::to_string(n/2),"Full category view detached a reply from its parent");
            require(all->label=="Social Media - Recruiting","Category header still exposes page controls");

        }
        {
            Collector original{vt,{}};ContainerProxy p{containerVt,&original,{},true};containerString(&p,3,"tileCoords","3");containerString(&p,8,"tileCoords","5");containerString(&p,9,"tileCoords","11");containerBool(&p,3,"AllowFocus",true);containerFloat(&p,3,"Opacity",0.5f);
            require(appendContainer(p,teamEntry)&&original.rows.size()==4&&original.rows[0]["tileCoords"]=="12"&&original.rows[1]["tileCoords"]=="3"&&original.rows[2]["tileCoords"]=="5"&&original.rows[3]["tileCoords"]=="11"&&original.rows[0]["Opacity"]==0.5f,"Prominent shortcut must precede stock settings/retirement without changing their identities");
        }
        uiReady=true;waitingFeed();require(!feedReady()&&!adoptReadyFeed(),"UI readiness alone must never admit a preparing feed");{auto saved=navRequest;navRequest=originalNav;navRequestHook(nullptr,0,"NEWS_MENU",nullptr);require(navForwardName=="DO_NOTHING"&&!opened,"A ready UI must still block a preparing edition at click time");navRequest=saved;navForwardCalls=0;}uiReady=false;opened=false;auto savedNav=navRequest;navRequest=originalNav;require(std::string(socialDestination())=="DO_NOTHING","Preparing navigation info must not promise a News screen");navRequestHook(nullptr,0,"NEWS_MENU",nullptr);require(!opened&&navForwardCalls==1&&navForwardName=="DO_NOTHING","Preparing UI must complete the native navigation transaction with its inert action");navRequest=savedNav;navForwardCalls=0;uiReady=true;{auto ready=std::make_shared<social::Feed>();ready->catalog=std::make_shared<social::Catalog>();latestFeed=ready;}require(std::string(socialDestination())=="DO_NOTHING","A ready feed must not bypass native model ownership checks");
        {auto savedChanged=filterChanged;filterChanged=originalChanged;opened=true;for(const char* kind:{"news_category","filter_one","SOCIAL_TYPE","SOCIAL_TYPE_PREV"})filterChangedHook(nullptr,"CM_NEWSSUB",kind,nullptr);require(changedForwardCalls==0,"Preparing-page filters escaped to the stock custom-panel lookup");filterChanged=savedChanged;opened=false;}
        {
            using dynasty::live::Address;const Address image=0x140000000,svc=0x100000,career=0x110000,ui=0x120000,owner=0x130000,db=0x140000;
            std::map<Address,Address> cells={{image+0xfa519b8,svc},{svc,image+0xbaa8998},{svc+0x468,career},{svc+0x470,ui},{svc+0x460,owner},{svc+0x7b1,1},{career,image+0xbce9b08},{ui,image+0xbd7a538},{career+0x20,owner},{career+0x238,db},{db,image+0xbd0d2d8}};
            auto q=[&](Address a){return cells.at(a);};const auto bound=dynasty::live::activeSession(image,q);require(bound.career==career&&bound.database==db,"Canonical CareerManager ownership did not resolve the shared database");cells[db]=image+0xbd0d378;require(dynasty::live::activeSession(image,q).database==db,"Direct active child context was rejected");
            for(const auto& fault:std::vector<std::pair<Address,Address>>{{svc+0x7b1,0},{svc+0x468,0},{career,0},{ui,0},{career+0x20,0},{db,0}}){const auto old=cells.at(fault.first);cells[fault.first]=fault.second;bool rejected=false;try{dynasty::live::activeSession(image,q);}catch(...){rejected=true;}require(rejected,"Inactive or foreign career ownership was accepted");cells[fault.first]=old;}
            require(dynasty::live::supportedRecordLayout(true,1,8100,9)&&!dynasty::live::supportedRecordLayout(false,1,8100,9)&&!dynasty::live::supportedRecordLayout(true,1,16385,9),"Award-array capacity exception escaped its array-only bounds");
            const Address child=0x150000;cells[child]=image+0xbd0d378;cells[child+0x1a8]=db;
            const Address viewOwner=0x160000,binding=0x170000,nextChild=0x180000;
            cells[career+0x230]=viewOwner;cells[career+0x240]=binding;cells[viewOwner]=image+0xb4dbb18;cells[binding]=viewOwner;cells[binding+8]=child;
            require(dynasty::live::ownedCareerContext(image,bound,q)==child,"Career-owned live view was not resolved");
            cells[nextChild]=image+0xbd0d378;cells[nextChild+0x1a8]=db;cells[binding+8]=nextChild;
            require(dynasty::live::ownedCareerContext(image,bound,q)==nextChild,"Postgame replacement did not supersede the still-valid old view");
            for(const auto& fault:std::vector<std::pair<Address,Address>>{{binding,viewOwner+8},{binding+8,0},{nextChild,0},{nextChild+0x1a8,db+8}}){const auto old=cells.at(fault.first);cells[fault.first]=fault.second;bool rejected=false;try{dynasty::live::ownedCareerContext(image,bound,q);}catch(...){rejected=true;}require(rejected,"Changing/foreign owned view was accepted or silently fell back");cells[fault.first]=old;}
            cells[viewOwner]=0;require(!dynasty::live::ownedCareerContext(image,bound,q),"Unknown binding layout must use validated fallback");cells[viewOwner]=image+0xb4dbb18;cells[binding+8]=child;
            const dynasty::live::SessionContextHint hint{career,db,child};
            require(dynasty::live::verifiedContextHint(image,bound,hint,q)==child,"Verified same-session context hint was not accepted");
            auto foreign=hint;foreign.career+=8;require(!dynasty::live::verifiedContextHint(image,bound,foreign,q),"Hint from another CareerManager was accepted");
            foreign=hint;foreign.database+=8;require(!dynasty::live::verifiedContextHint(image,bound,foreign,q),"Hint from another database was accepted");
            cells[child+0x1a8]=db+8;require(!dynasty::live::verifiedContextHint(image,bound,hint,q),"Hint with a foreign parent was accepted");cells[child+0x1a8]=db;
            cells[child]=0;require(!dynasty::live::verifiedContextHint(image,bound,hint,q),"Hint with a foreign vtable was accepted");cells.erase(child);
            require(!dynasty::live::verifiedContextHint(image,bound,hint,q),"Unreadable hint was accepted");
        }
        {
            unsigned probes=0,pauses=0,reports=0;bool cancel=false;
            const bool ready=social::awaitStartup([&]{return cancel;},[&]{++probes;return probes<=2?std::string("Title screen"):probes==3?std::string("Dynasty assets loading"):std::string();},[&](const std::string&){++reports;},[&]{++pauses;});
            require(ready&&probes==4&&pauses==3&&reports==2,"Cold startup did not wait through title/loading states or deduplicate status");
            probes=0;cancel=false;const bool stopped=social::awaitStartup([&]{return cancel;},[&]{++probes;return std::string("Loading");},[](const std::string&){},[&]{cancel=true;});
            require(!stopped&&probes==1,"Startup cancellation still allowed UI activation");
        }
        require(social::compactCount(999)=="999"&&social::compactCount(1000)=="1K"&&social::compactCount(1950000)=="2M"&&social::compactCount(999950)=="1M","Engagement K/M formatting boundaries changed");
        require(social::storyLabel(Json{{"category","recruiting"}})=="Recruiting","Recruiting category label changed");
        require(social::storyLabel(Json{{"category","recruiting"},{"replyTo","real-parent"}})=="Reply","Native reply label is missing");
        {
            std::vector<unsigned char> packed(48);uint32_t first=0xfedcba98u,second=0x12345678u;
            memcpy(packed.data()+32,&first,4);memcpy(packed.data()+36,&second,4);
            require(dynasty::live::bits(packed,1,8,0,0,32)==first,"Live 32-bit fields were truncated");
            require(dynasty::live::bits(packed,1,8,1,4,8)==0x67,"Live row stride/bit offset changed");
            bool rejected=false;try{dynasty::live::bits(packed,1,8,0,31,2);}catch(const std::exception&){rejected=true;}
            require(rejected,"Unverified packed layout was accepted");
            dynasty::live::Memory memory;require(memory.at<uint32_t>(reinterpret_cast<uintptr_t>(&first))==first,"Read-only native memory accessor changed");
            rejected=false;try{memory.at<uint32_t>(0);}catch(const std::exception&){rejected=true;}
            require(rejected,"Unavailable native memory did not fail closed");
        }
        Collector out{vt,{}};ContainerProxy proxy{containerVt,&out,{}};
        const char* coordinates[]={"1","2","3","5","6","7"};
        for(unsigned row=0;row<6;++row){containerString(&proxy,row,"tileCoords",coordinates[row]);containerInt(&proxy,row,"Priority",0);containerFloat(&proxy,row,"Opacity",0.875f);containerBool(&proxy,row,"AllowFocus",true);}
        require(appendContainer(proxy),"Filtered CFB rows lost the Heisman donor");
        require(out.rows.size()==7,"Expected six visible containers plus Social Media");
        for(unsigned row=0;row<7;++row){require(out.rows.at(row).at("tileCoords")==std::string(row<6?coordinates[row]:"12"),"Original coordinates changed");require(out.rows.at(row).at("Priority")==0,"Native priorities changed");require(out.rows.at(row).at("Opacity")==0.875f,"Float collector ABI changed");require(out.rows.at(row).at("AllowFocus")==true,"Focus state lost");}
        Collector absent{vt,{}};ContainerProxy noDonor{containerVt,&absent,{}};containerString(&noDonor,0,"tileCoords","1");require(!appendContainer(noDonor)&&absent.rows.size()==1,"Missing donor must preserve the original menu");
        {
            require(hubEntry("cm_team")==&teamEntry&&!hubEntry("DynastyCentral")&&!hubEntry("CM_NEWSTAB")&&!hubEntry("CM_LEAGUE"),"Social shortcut must be restricted to Team");
            {const auto savedRequest=requestPanel;requestPanel=originalRequest;expectedRequestSelf=&out;expectedRequestParams=&proxy;requestCalls=0;
             require(requestSocialPanel(&out,&proxy)&&requestCalls==1&&lastDonorPanel=="DynastyCentral","Category refresh must request the persistent panel and preserve its native self/params");
             requestResult=false;require(!requestSocialPanel(&out,&proxy)&&requestCalls==2,"A failed native refresh must not report success");requestResult=true;requestPanel=savedRequest;}
            Collector central{vt,{}};ContainerProxy cp{containerVt,&central,{}};
            containerString(&cp,2,"tileCoords","2");containerString(&cp,9,"tileCoords","5");containerString(&cp,9,"panelId","DynastyCentral");containerBool(&cp,9,"AllowFocus",true);containerInt(&cp,9,"Priority",0);containerFloat(&cp,9,"Opacity",0.5f);
            require(appendContainer(cp,centralEntry)&&central.rows.size()==3,"Sparse Dynasty Central rows lost the User Settings donor");
            require(central.rows.at(10).at("tileCoords")=="12"&&central.rows.at(10).at("panelId")=="DynastyCentral"&&central.rows.at(10).at("AllowFocus")==true&&central.rows.at(10).at("Opacity")==0.5f&&central.rows.at(9).at("tileCoords")=="5","Persistent shortcut changed stock identities or typed fields");
            Collector occupied{vt,{}};ContainerProxy collision{containerVt,&occupied,{}};containerString(&collision,0,"tileCoords","5");containerString(&collision,1,"tileCoords","12");
            require(!appendContainer(collision,centralEntry)&&occupied.rows.size()==2,"An existing foreign coordinate must not be overwritten");
            Collector unavailable{vt,{}};ContainerProxy missing{containerVt,&unavailable,{}};containerString(&missing,0,"tileCoords","7");require(!appendContainer(missing,centralEntry)&&unavailable.rows.size()==1,"Persistent donor absence must leave native menu intact");
        }
        require(postNumber("1")==1,"First post must be addressable");
        require(postNumber(std::to_string(feedPostCount))==feedPostCount,"Last post must be addressable");
        for(const auto& invalid:{"","0","01","-1","1x","999999999999999999999"})require(postNumber(invalid)==0,"Invalid coordinate accepted");
        require(postNumber(std::to_string(feedPostCount+1))==0,"Out-of-range post accepted");
        containers=donorRows;opened=true;
        Collector feed{vt,{}};Alias panel{aliasVt,"CM_NEWSSUB"};containerHook(nullptr,&panel,&feed);
        require(lastDonorPanel=="DynastyCentral","Offseason feed still depends on the hidden CFB panel");
        require(feed.rows.size()==feedContainerCount,"Feed count differs from native containers");
        for(unsigned row=0;row<feedContainerCount;++row){
            require(feed.rows.at(row).at("tileCoords")==std::to_string(row+1),"Feed coordinate sequence changed");
            require(feed.rows.at(row).at("panelId")=="CM_NEWSSUB","Feed leaked donor panel identity");
            require(feed.rows.at(row).at("UseTileDimensions")==true,"Feed must size from post widgets");
        }
        if constexpr(listFeed)require(feed.rows.at(0).at("linkage")=="art_control.group.PanelListContainer","List feed must use the native list control");
        {opened=false;Collector central{vt,{}};Alias hub{aliasVt,"cm_team"};containerHook(nullptr,&hub,&central);require(central.rows.size()==2&&admittedHubEntries["cm_team"],"Persistent hub did not admit a separate Social Media row");Collector other{vt,{}};Alias untouched{aliasVt,"OTHER_PANEL"};containerHook(nullptr,&untouched,&other);require(other.rows.size()==1&&!admittedHubEntries.count("OTHER_PANEL"),"Unrelated menus received the Social Media shortcut");opened=true;}
        filterData=originalFilter;
        Collector filter{vt,{}};Alias kind{aliasVt,"NEWS_CATEGORY"};filterDataHook(nullptr,&filter,&panel,&kind);
        require(filter.rows.size()==1&&filter.rows.at(0).at("display")=="For You"&&filter.rows.at(0).at("isDefault")==true,"Native category must have one labeled default");
        require(filterForwardCalls==0,"Custom category queried unrelated native filters");
        Alias unsetPanel{aliasVt,""};Collector stockNewsCategory{vt,{}};filterDataHook(nullptr,&stockNewsCategory,&unsetPanel,&kind);
        require(stockNewsCategory.rows.at(0).at("display")=="For You","Stock News unset panel ID lost the category");
        Alias otherPanel{aliasVt,"OTHER_PANEL"};Collector otherCategory{vt,{}};filterDataHook(nullptr,&otherCategory,&otherPanel,&kind);
        require(filterForwardCalls==1&&otherCategory.rows.at(0).at("display")=="Original category","Other panel category was replaced");
        opened=false;Collector ordinary{vt,{}};filterDataHook(nullptr,&ordinary,&panel,&kind);
        require(filterForwardCalls==2&&ordinary.rows.at(0).at("display")=="Original category","Unrelated category behavior changed");
        {
            using namespace social::refresh;
            Watch watch;Stamp a{100,200,300,1},b=a;b.modified=201;
            require(!watch.ready(a,0)&&!watch.ready(a,1499)&&watch.ready(a,1500),"Save debounce failed");
            watch.success(a);require(!watch.ready(a,5000),"Completed save reread unnecessarily");
            require(!watch.ready(b,5000)&&watch.ready(b,6500),"Same-size save was ignored");
            watch.failure(6500);require(!watch.ready(b,11499)&&watch.ready(b,11500),"Failed read retry policy failed");
            b.identity=301;require(!watch.ready(b,12000)&&watch.ready(b,13500),"Atomic replacement was ignored");
            Json config{{"leagueId",10},{"userTeamIndex",1},{"save","C:/saves/TEST"}};
            Json data{{"format",1},{"engineVersion",2},{"sourceUnchanged",true},{"leagueId",10},{"userTeamIndex",1},{"source","C:/saves/TEST"},{"key","10/2027/RegularSeason/7"},{"week",7},{"posts",Json::array()}};
            for(unsigned n=0;n<5;++n)data["posts"].push_back({{"id",std::to_string(n)},{"author","Beat"},{"handle","@Beat"},{"body","Verified result"},{"stamp","Week 6"},{"imageLibrary",0},{"imageValue",76}});
            data["season"]=2027;data["phase"]="RegularSeason";data["activeWeekKey"]=data["key"];
            Json edition=data;edition["stories"]=data["posts"];edition["views"]=Json::object();
            for(auto& post:edition["stories"])post["publication"]={{"key",data["key"]},{"week",7}};
            for(const char* scope:{"all","national","conference","team"}){edition["views"][scope]=Json::array();for(const auto& post:edition["stories"])edition["views"][scope].push_back(post["id"]);}
            data["weeks"]=Json::array({edition});
            {
                const auto savedBase=base;const auto savedLatest=latestFeed,savedPage=pageFeed;
                const auto savedIdentity=nativeFeedIdentity;const auto savedLeague=nativeFeedLeague;
                const auto savedCount=feedPostCount,savedContainers=feedContainerCount;
                uint32_t activeLeague=2930100523u;base=reinterpret_cast<uintptr_t>(&activeLeague)-0xf55c998;
                auto native=data;native["sourceKind"]="runtime";native["leagueId"]=-1364866773;
                publishFeed(native);require(feedReady()&&adoptReadyFeed(),"Signed native LeagueID did not match its unsigned profile identity");
                activeLeague=1234;
                require(!feedReady()&&!adoptReadyFeed(),"Cached feed from another Dynasty remained eligible for entry");
                activeLeague=2930100523u;
                for(const Json invalid:std::vector<Json>{1.5,true,Json(uint64_t(UINT32_MAX)+1),Json(int64_t(INT32_MIN)-1),nullptr,"2930100523"}){
                    auto malformed=native;malformed["leagueId"]=invalid;bool refused=false;
                    try{publishFeed(malformed);}catch(const std::exception&){refused=true;}
                    require(refused&&feedReady(),"Invalid runtime identity was coerced or replaced the last valid feed");
                }
                {std::lock_guard<std::mutex> guard(feedMutex);latestFeed=savedLatest;pageFeed=savedPage;nativeFeedIdentity=savedIdentity;nativeFeedLeague=savedLeague;}
                base=savedBase;feedPostCount=savedCount;feedContainerCount=savedContainers;
            }
            validate(data,config);auto wrong=data;wrong["leagueId"]=99;bool rejected=false;try{validate(wrong,config);}catch(...){rejected=true;}require(rejected,"Another Dynasty was accepted");
            wrong=data;wrong["weeks"][0]["stories"][1]["id"]="0";rejected=false;try{validate(wrong,config);}catch(...){rejected=true;}require(rejected,"Duplicate posts were accepted");
            auto catalog=social::decodeFeed(data)->catalog;
            {
                Json large=data;auto& largeEdition=large["weeks"][0];largeEdition["stories"]=Json::array();largeEdition["views"]=Json::object();for(const char* scope:{"all","national","conference","team"})largeEdition["views"][scope]=Json::array();
                for(unsigned n=0;n<9300;++n){const auto id="offer-"+std::to_string(n);largeEdition["stories"].push_back({{"id",id},{"author","Recruit"},{"handle","@Recruit"},{"body","Verified scholarship announcement"},{"stamp","Recruiting"},{"category","offers"},{"voice","recruit"},{"likes",n},{"imageLibrary",79},{"imageValue",598},{"publication",{{"key",large["key"]},{"week",7}}}});for(const char* scope:{"national","conference","team"})largeEdition["views"][scope].push_back(id);if(n<30)largeEdition["views"]["all"].push_back(id);}
                validate(large,config);auto many=social::decodeFeed(large);require(many->posts.size()==30&&social::selectFeed(many->catalog,0,1)->posts.size()==100&&social::selectFeed(many->catalog,0,2)->posts.size()==60&&social::selectFeed(many->catalog,0,3)->posts.size()==25,"Large candidate catalog changed the 30/100/60/25 display caps");
                auto recruiting=social::selectFeed(many->catalog,0,1,1);require(recruiting->posts.size()==9300&&recruiting->posts[0].likes==0,"Large recruiting category lost editorial order or its National cap");
                auto excessive=large;excessive["weeks"][0]["stories"].get_ref<Json::array_t&>().resize(32769,largeEdition["stories"][0]);bool bounded=false;try{validate(excessive,config);}catch(const std::exception& e){bounded=std::string(e.what()).find("exceeds catalogue limit")!=std::string::npos;}require(bounded,"Unbounded weekly catalog was accepted");
            }
            {
                Json mixed=data;mixed["catalogVersion"]=2;mixed["week"]=0;mixed["key"]="10/2027/RegularSeason/0";mixed["activeWeekKey"]=mixed["key"];
                auto current=mixed["weeks"][0];current["week"]=0;current["key"]=mixed["key"];for(auto& p:current["stories"]){p["body"]="Regular season story";p["publication"]={{"key",current["key"]},{"week",0},{"season",2027},{"phase","RegularSeason"}};}
                auto preseason=current;preseason["phase"]="PreSeason";preseason["key"]="10/2027/PreSeason/0";for(auto& p:preseason["stories"]){p["body"]="Frozen preseason story";p["publication"]["key"]=preseason["key"];p["publication"]["phase"]="PreSeason";}
                mixed["weeks"]=Json::array({current,preseason});validate(mixed,config);auto selected=social::decodeFeed(mixed);
                require(selected->catalog->weeks.size()==2&&selected->edition==1&&selected->catalog->weeks[0].phase=="PreSeason","Cross-phase picker did not order preseason before regular Week 0 and default to active");
                require(selected->catalog->weeks[0].label=="Preseason, 2027"&&selected->catalog->weeks[1].label=="Week 0, 2027","Preseason and Week 0 labels collided");
                require(social::selectFeed(selected->catalog,0,3)->posts[0].body=="Frozen preseason story"&&selected->posts[0].body=="Regular season story","Archive selection borrowed the active edition's stories");
                auto recovered=mixed;recovered["weeks"][0]["reconstructed"]=true;require(social::decodeFeed(recovered)->catalog->weeks[1].label=="Week 0, 2027 (recovered)","Recovered-week provenance missing from native label");
                auto invalid=mixed;invalid["weeks"][1]["phase"]="BowlSeason1";bool refused=false;try{validate(invalid,config);}catch(...){refused=true;}require(refused,"A future phase with Week 0 escaped chronology validation");
                invalid=mixed;invalid["weeks"][1]["stories"][0]["publication"]["phase"]="RegularSeason";refused=false;try{validate(invalid,config);}catch(...){refused=true;}require(refused,"Publication phase mismatch was accepted");
                Json runtimeIdentity{{"sourceKind","runtime"},{"leagueId",10},{"season",2027},{"phase","RegularSeason"},{"week",0}},status{{"league",10},{"season",{{"CurrentSeasonYear",2027},{"CurrentWeekType","RegularSeason"},{"CurrentWeek",0}}}};
                dynasty::live::validateRuntimeIdentity(runtimeIdentity,status);runtimeIdentity["leagueId"]=11;refused=false;try{dynasty::live::validateRuntimeIdentity(runtimeIdentity,status);}catch(...){refused=true;}require(refused,"A cached edition from a different live Dynasty was accepted");
            }
            auto teamView=social::selectFeed(catalog,0,3);require(teamView->scope==3&&teamView->key==data["key"],"Scope changed the selected publication week");
            bool badWeek=false;try{social::selectFeed(catalog,99,0);}catch(...){badWeek=true;}require(badWeek,"Invalid single-week selection accepted");
            auto empty=std::make_shared<social::Catalog>(*catalog);empty->weeks[0].views["conference"].clear();require(social::selectFeed(empty,0,2)->posts.size()==1,"Empty scope must provide a readable native placeholder");
            auto original=pageFeed;publishFeed(data);require(pageFeed==original,"Background refresh changed the visible page");adoptFeed();
            require(feedPostCount==5&&postNumber("5")==5&&postNumber("6")==0,"Dynamic feed count is not applied on entry");
            opened=true;Collector dynamic{vt,{}};containerHook(nullptr,&panel,&dynamic);require(dynamic.rows.size()==(listFeed?1u:5u),"Dynamic feed omitted native containers");
#ifdef SOCIAL_DUAL_DROPDOWN
            Collector scopes{vt,{}};filterDataHook(nullptr,&scopes,const_cast<char*>("CM_NEWSSUB"),const_cast<char*>("filter_one"));
            require(scopes.rows.size()==4&&scopes.rows.at(0).at("display")=="For You"&&scopes.rows.at(3).at("display")=="My Team","Raw native LT scope binding did not return four independent choices");
            require(scopes.rows.at(0).at("isDefault")==true,"Scope dropdown lost its selected default");
            require(socialFilter("filter_one")==SocialFilter::scopeDropdown,"Native LT selection must select rather than cycle scopes");
#endif
            filterChanged=originalChanged;
            require(socialFilter("news_category")==SocialFilter::week&&socialFilter("NEWS_CATEGORY")==SocialFilter::week,"Native week filter casing is not accepted");
            require(socialFilter("SOCIAL_SCOPE")==SocialFilter::scope,"LT scope callback is not recognized");
            // Replay the crashing callback spelling. Bad values are rejected
            // here rather than forwarded to the stock synthetic-panel lookup.
            filterChangedHook(nullptr,"CM_NEWSSUB","news_category",nullptr);
            require(changedForwardCalls==0,"Lowercase week callback escaped into the stock panel lookup");
            void* valueVt[]={nullptr,nullptr,nullptr,reinterpret_cast<void*>(filterKey)};
            FilterValue value{valueVt,1};const auto oldBase=base;base=reinterpret_cast<uintptr_t>(filterKey);
            const auto beforeSelection=pageFeed;filterChangedHook(nullptr,"CM_NEWSSUB","news_category",&value);
            require(pageFeed==beforeSelection&&changedForwardCalls==0,"Existing week callback must preserve selection without native refresh");
            value.key=99;filterChangedHook(nullptr,"CM_NEWSSUB","news_category",&value);
            require(pageFeed==beforeSelection&&changedForwardCalls==0,"Invalid week must not reach the stock lookup");base=oldBase;
            filterChangedHook(nullptr,"CM_NEWSSUB","unknown_filter",nullptr);
            require(changedForwardCalls==0,"Unknown custom filter escaped into the stock panel lookup");
            filterChangedHook(nullptr,"OTHER_PANEL","news_category",nullptr);
            require(changedForwardCalls==1,"Another native panel's filter callback was intercepted");
            {std::lock_guard<std::mutex> lock(feedMutex);latestFeed=original;}adoptFeed();opened=false;
        }
        {
            auto catalog=std::make_shared<social::Catalog>();social::Edition edition;edition.key="one";
            social::FeedPost parent{"Team","@team","Result","Recap"};parent.category="results";parent.voice="official";
            social::FeedPost reply{"Fan","@fan","Reply","Reply"};reply.category="results";reply.voice="fan";reply.replyTo="parent";
            social::FeedPost recruit{"Recruit","@recruit","Offer","Recruiting"};recruit.category="offers";recruit.voice="recruit";
            social::FeedPost injury{"Beat","@beat","Estimated return: 1-2 weeks.","Injury Report"};injury.category="injuries";injury.voice="beat";
            auto injuryReply=reply;injuryReply.category="other";injuryReply.replyTo="injury";edition.stories.emplace("injury",injury);edition.stories.emplace("injury-reply",injuryReply);
            social::FeedPost playoff{"CFP","@CFBPlayoff","Rankings","Playoff Watch"};playoff.voice="cfp";playoff.category="cfp";require(social::matchesType(playoff,7)&&social::matchesType(playoff,4),"CFP official account is missing its official/rankings categories");
            edition.stories.emplace("parent",parent);edition.stories.emplace("reply",reply);edition.stories.emplace("recruit",recruit);
            for(unsigned i=0;i<151;++i){const auto key=i?"team:"+std::to_string(i):"all";catalog->scopes.push_back({key,"Scope "+std::to_string(i)});edition.views[key]={"parent","reply","recruit","injury","injury-reply"};}catalog->weeks.push_back(edition);
            auto view=social::selectFeed(catalog,0,150,7);require(view->posts.size()==2&&view->posts[1].voice=="fan","Native account filter detached a reply from its parent");
            require(view->label=="Social Media - Official Accounts","Category is not visible in the native header");
            require(social::selectFeed(catalog,0,150,10)->posts[0].stamp=="News","A reply must not appear without its parent when filtering Fans");
            require(social::selectFeed(catalog,0,150,9)->posts.size()==2&&social::selectFeed(catalog,0,150,9)->posts[1].voice=="fan","Injury filter failed to keep its category-agnostic reply");
            require(social::selectFeed(catalog,0,150,8)->posts[0].stamp=="News","Player filter included a recruit root");
            require(social::selectFeed(catalog,0,150,1)->posts.size()==1,"Recruiting filter included another root category");
            bool bad=false;try{social::selectFeed(catalog,0,151);}catch(...){bad=true;}require(bad,"Dynamic scope boundary was not enforced");
        }
        {
            auto catalog=std::make_shared<social::Catalog>();social::Edition e;e.key="limits";
            catalog->scopes={{"all","For You"},{"national","National"},{"conference:c","Conference"},{"team:1","Team"}};
            std::vector<std::string> ids;
            for(int i=0;i<140;++i)for(int type=0;type<2;++type){const auto id=std::to_string(type)+":"+std::to_string(i);social::FeedPost p{id,"@account",id,"News"};p.likes=(type?500:1000)-i;p.category=type?"analytics":"results";p.voice=type?"analyst":"official";e.stories.emplace(id,p);ids.push_back(id);}
            social::FeedPost reply{"attached","@fan","reply","Reply"};reply.replyTo="0:0";reply.likes=200;reply.voice="fan";e.stories.emplace("reply",reply);ids.insert(ids.begin(),"reply");
            for(const auto& scope:catalog->scopes)e.views[scope.key]=ids;catalog->weeks.push_back(e);
            auto national=social::selectFeed(catalog,0,1);require(national->posts.size()==100,"National cap failed");
            require(national->posts[0].author=="0:0"&&national->posts[1].author=="attached"&&national->posts[2].author=="1:0","Editorial ordering split a conversation or followed likes");
            require(social::selectFeed(catalog,0,0)->posts.size()==30,"For You cap failed");require(social::selectFeed(catalog,0,2)->posts.size()==60,"Conference cap failed");require(social::selectFeed(catalog,0,3)->posts.size()==25,"Team feed card budget failed");
            auto analysts=social::selectFeed(catalog,0,1,5);require(analysts->posts.size()==140&&analysts->posts[0].author=="1:0","National cap was applied before the category filter");
            require(social::selectFeed(catalog,0,2,5)->posts.size()==140,"Filtered conference cap failed");
        }
        {
            auto c=std::make_shared<social::Catalog>();c->scopes={{"all","For You"},{"national","National"}};social::Edition e;e.key="draft";
            for(int pick=224;pick>=1;--pick){auto id=std::to_string(pick);social::FeedPost p{"NFL Draft","@NFLDraft","Selection","Draft"};p.category="draft";p.voice="nflDraft";p.transaction=true;p.draftPick=pick;p.draftRound=(pick-1)/32+1;e.stories.emplace(id,p);e.views["national"].push_back(id);}
            c->weeks.push_back(e);auto f=social::selectFeed(c,0,1,11);require(f->posts.size()==224,"Draft Transactions must expose the whole board");int seen=0;for(const auto& post:f->posts)require(post.draftPick==++seen,"Full draft view lost pick order");require(seen==224,"Full draft view lost a pick");require(social::selectFeed(c,0,1)->posts.size()==100,"The ordinary National cap must stay at 100");require(social::matchesType(f->posts.front(),7),"NFL Draft must also count as an official account");
        }
        {social::FeedPost p{"reporter","@reporter","terms","Signing"};p.voice="beat";p.category="signings";require(social::matchesType(p,11)&&social::matchesType(p,1),"Reported signatures must appear in Transactions and Recruiting");p.category="coaching";p.voice="fan";require(!social::matchesType(p,11),"Speculative fan roots must not become transaction reports");p.voice="analyst";require(social::matchesType(p,11),"Coaching reports must appear in Transactions");}
        require(socialFilter("SOCIAL_TYPE_PREV")==SocialFilter::typePrev,"RB reverse category callback is not recognized");
        unsigned changed=0;
        {
            using social::storyLabel;
            require(storyLabel(Json{{"category","results"}})=="Recap"&&storyLabel(Json{{"category","player-stats"}})=="Recap","Previous-week results/stats must display Recap");
            require(storyLabel(Json{{"category","offers"}})=="Recruiting"&&storyLabel(Json{{"category","recruiting"}})=="Recruiting","Offers and commitments must share Recruiting");
            require(storyLabel(Json{{"category","schedule"}})=="Upcoming"&&storyLabel(Json{{"category","polls"}})=="Rankings","Current-week story labels are incorrect");
            require(storyLabel(Json{{"category","future-type"}})=="News","Unknown story types need a readable fallback");
            require(social::postHeight("A short post.")==160,"Short posts must keep compact cards");
            require(social::postHeight(std::string(380,'W'))>160,"Wide long text requires a taller card");
            require(social::postHeight("One\nTwo\nThree\nFour\nFive\nSix")>=288,"Explicit lines were omitted from card sizing");
            auto* allocation=static_cast<unsigned char*>(VirtualAlloc(nullptr,8192,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));require(allocation!=nullptr,"Polish fixture allocation failed");auto* memory=allocation+128;
            newsBodyStyle=reinterpret_cast<uintptr_t>(memory);newsViewport=newsBodyStyle+4096;newsLayout=newsBodyStyle-(0x2ccd2-0x2c658);for(const auto& patch:discoveryPatches)memcpy(reinterpret_cast<void*>(newsLayout-0x2c658+patch.offset),patch.original.data(),patch.original.size());
            memcpy(memory,social::polish::bodyOriginal.data(),social::polish::bodyOriginal.size());memcpy(memory+4096,social::polish::viewportOriginal.data(),social::polish::viewportOriginal.size());
            memory[4096]^=1;require(!configureNewsPolish(true)&&!polishOwned,"Polish must reject the complete mismatched batch");require(memcmp(memory,social::polish::bodyOriginal.data(),58)==0,"Failed viewport gate changed body style");memory[4096]^=1;
            require(configureNewsPolish(true)&&polishOwned&&configureNewsPolish(true),"Text/viewport activation or idempotence failed");
            require(memcmp(memory,social::polish::bodyWide.data(),58)==0&&memcmp(memory+4096,maskedViewport.data(),432)==0,"Polish bytes do not match the candidate");
            memory[4096]^=1;require(!configureNewsPolish(false)&&polishOwned,"Polish must preserve foreign viewport changes");memory[4096]^=1;
            require(configureNewsPolish(false)&&!polishOwned&&memcmp(memory,social::polish::bodyOriginal.data(),58)==0&&memcmp(memory+4096,social::polish::viewportOriginal.data(),432)==0,"Polish did not restore the original functions");
            VirtualFree(allocation,0,MEM_RELEASE);newsBodyStyle=0;newsViewport=0;newsLayout=0;
        }
#ifdef SOCIAL_DUAL_DROPDOWN
        {
            auto* screenBytes=static_cast<unsigned char*>(VirtualAlloc(nullptr,0x2000,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
            auto* modelBytes=static_cast<unsigned char*>(VirtualAlloc(nullptr,0x30000,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
            require(screenBytes&&modelBytes,"Dropdown fixture allocation failed");dropdownScreenBase=reinterpret_cast<uintptr_t>(screenBytes);newsTemplate=dropdownScreenBase+0x8a0;newsModelBase=reinterpret_cast<uintptr_t>(modelBytes);
            memcpy(screenBytes,"Apt Data:1:7:8",14);const unsigned dictionaryCount=180;const auto dictionary=dropdownScreenBase+0x1300;memcpy(screenBytes+0x8a0-16,&dictionaryCount,4);memcpy(screenBytes+0x8a0-8,&dictionary,8);
            for(const auto& p:dropdownPatches)memcpy((p.model?modelBytes:screenBytes)+p.offset,p.original.data(),p.original.size());
            modelBytes[0x24ae0]^=1;require(!configureNewsDropdowns(true)&&!dropdownScreenOwned,"Dropdown activation must reject the entire mismatched batch");
            require(memcmp(screenBytes+0x8a0,dropdownPatches[0].original.data(),726)==0,"A failed dropdown gate partially changed the screen");modelBytes[0x24ae0]^=1;
            require(configureNewsDropdowns(true)&&dropdownScreenOwned&&dropdownModelOwned&&configureNewsDropdowns(true),"Dropdown activation or idempotence failed");
            for(const auto& p:dropdownPatches)require(memcmp((p.model?modelBytes:screenBytes)+p.offset,p.changed.data(),p.changed.size())==0,"Dropdown bytes differ from the bounded candidate");
            {auto handoffNav=navRequest;const bool handoffReady=uiReady.load();uiReady=true;opened=true;navRequest=originalNav;navForwardCalls=0;navRequestHook(nullptr,0,"CFP_BRACKET",nullptr);
             require(navForwardCalls==1&&navForwardName=="CFP_BRACKET"&&!opened&&!dropdownModelOwned&&!dropdownScreenOwned,"Stock CFP handoff must forward unchanged and restore Social Media dropdowns");navRequest=handoffNav;uiReady=handoffReady;navForwardCalls=0;require(configureNewsDropdowns(true),"Dropdown fixture did not reenable after the stock handoff");}
            modelBytes[0x24ae0]^=1;require(!configureNewsDropdowns(false)&&dropdownModelOwned,"Dropdown restore must preserve foreign model changes");
            savedNav=navRequest;navRequest=originalNav;const bool previousValidated=feedValidated;feedValidated=true;opened=false;navRequestHook(nullptr,0,"NEWS_MENU",nullptr);require(!opened&&navForwardCalls==1&&navForwardName=="DO_NOTHING","A failed dropdown model gate must complete through native no-action navigation");navForwardCalls=0;feedValidated=previousValidated;navRequest=savedNav;modelBytes[0x24ae0]^=1;
            require(configureNewsDropdowns(false)&&!dropdownScreenOwned&&!dropdownModelOwned,"Dropdown restore failed");
            for(const auto& p:dropdownPatches)require(memcmp((p.model?modelBytes:screenBytes)+p.offset,p.original.data(),p.original.size())==0,"Dropdown function failed exact restoration");
            newsTemplate=0;require(!configureNewsDropdowns(true)&&!dropdownScreenOwned,"Unknown News asset must not trigger a UI-thread search");
            const auto savedBody=scriptBody;const bool wasOpened=opened.load();scriptBody=originalScriptBody;executingBody=screenBytes+0x8a0;const unsigned actionSize=726;memcpy(screenBytes+0x8a0-24,&actionSize,4);
            opened=false;require(scriptBodyHook(nullptr)==executingBody&&!dropdownScreenOwned,"Unrelated stock template execution was modified");
            opened=true;require(scriptBodyHook(nullptr)==executingBody&&dropdownScreenOwned&&newsTemplate==reinterpret_cast<uintptr_t>(executingBody),"Observed template was not prepared before its body executed");
            require(configureNewsDropdowns(false),"Observed screen did not restore exactly");
            auto* replacementModel=static_cast<unsigned char*>(VirtualAlloc(nullptr,0x30000,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));require(replacementModel!=nullptr,"Replacement model fixture allocation failed");
            memcpy(replacementModel,"Apt Data:1:7:8",14);for(const auto& p:dropdownPatches)if(p.model)memcpy(replacementModel+p.offset,p.original.data(),p.original.size());
            modelBytes[0x24a58]^=1;require(!ensureNewsModel()&&modelDiscoveryNeeded,"Missing model did not defer discovery off the UI thread");
            const unsigned modelSize=91,modelPoolSize=41;const auto modelPool=reinterpret_cast<uintptr_t>(replacementModel)+0x23000;memcpy(replacementModel+0x24970-24,&modelSize,4);memcpy(replacementModel+0x24970-16,&modelPoolSize,4);memcpy(replacementModel+0x24970-8,&modelPool,8);
            executingBody=replacementModel+0x24970;require(scriptBodyHook(nullptr)==executingBody&&ensureNewsModel()&&newsModelBase==reinterpret_cast<uintptr_t>(replacementModel),"Executing replacement model was not reacquired");scriptBody=savedBody;opened=wasOpened;
            require(configureNewsDropdowns(true)&&configureNewsDropdowns(false),"Replaced model did not support entry and exit");
            require(modelBytes[0x24a58]!=(dropdownPatches[6].original[0]),"Stale model allocation was overwritten");
            VirtualFree(replacementModel,0,MEM_RELEASE);
            VirtualFree(screenBytes,0,MEM_RELEASE);VirtualFree(modelBytes,0,MEM_RELEASE);newsTemplate=0;newsModelBase=0;dropdownScreenBase=0;
        }
#endif
        {
            auto* memory=static_cast<unsigned char*>(VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
            require(memory!=nullptr,"Scroll fixture allocation failed");newsScroll=reinterpret_cast<uintptr_t>(memory);memcpy(memory,social::newsScrollOriginal.data(),1432);
            require(configureNewsScroll(true)&&scrollOwned&&configureNewsScroll(true),"Smooth scrolling activation failed");
            for(size_t n=0;n<1432;++n)if(memory[n]!=social::newsScrollOriginal[n])require((n>=0xe&&n<0x12)||(n>=0x141&&n<0x145)||(n>=0x199&&n<0x19d)||(n>=0xbc&&n<0xdc)||(n>=0x2f4&&n<0x395),"Scrolling changed a native branch, opcode or input contract");
            float step=0,analog=0;memcpy(&step,memory+0xe,4);memcpy(&analog,memory+0x141,4);
            require(step*5686>163.9f&&step*5686<164.1f,"D-pad step must be one card plus its spacing");require(analog<-.00999f&&analog>-.01001f,"Analog polling scale must be one-third of the original");
            memory[0]^=1;require(!configureNewsScroll(false)&&scrollOwned&&memory[0]!=social::newsScrollOriginal[0],"Scrolling must preserve foreign changes");memory[0]^=1;
            require(configureNewsScroll(false)&&!scrollOwned&&memcmp(memory,social::newsScrollOriginal.data(),1432)==0,"Native scrolling did not fully restore");
            VirtualFree(memory,0,MEM_RELEASE);newsScroll=0;
        }
        {
            auto* memory=static_cast<unsigned char*>(VirtualAlloc(nullptr,8192,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
            require(memory!=nullptr,"Flow fixture allocation failed");newsGrid=reinterpret_cast<uintptr_t>(memory);newsVerticalInput=newsGrid+4096;
            memcpy(memory,social::newsGridOriginal.data(),social::newsGridOriginal.size());memcpy(memory+4096,social::newsVerticalInputOriginal.data(),social::newsVerticalInputOriginal.size());
            require(configureNewsFlow(true)&&flowOwned&&configureNewsFlow(true),"Vertical flow activation or idempotence failed");
            require(memcmp(memory,social::newsGridVertical.data(),61)==0&&memcmp(memory+4096,social::newsVerticalInputEnabled.data(),7)==0,"Vertical flow bytes differ from expected native instructions");
            unsigned delta=0;for(size_t n=0;n<61;++n)if(social::newsGridOriginal[n]!=memory[n]){++delta;require(n==0x17||n==0x22,"Flow changed a non-direction operand");}
            for(size_t n=0;n<7;++n)if(social::newsVerticalInputOriginal[n]!=memory[4096+n]){++delta;require(n==4||n==5,"Flow changed the native setter contract");}
            require(delta==4,"Vertical flow must change exactly four bytes");
            memory[0]^=1;require(!configureNewsFlow(false)&&flowOwned&&memory[0]!=social::newsGridVertical[0],"Flow must preserve foreign changes");memory[0]^=1;
            require(configureNewsFlow(false)&&!flowOwned&&memcmp(memory,social::newsGridOriginal.data(),61)==0&&memcmp(memory+4096,social::newsVerticalInputOriginal.data(),7)==0,"Flow did not fully restore on exit");
            memory[4096]^=1;require(!configureNewsFlow(true)&&!flowOwned&&memcmp(memory,social::newsGridOriginal.data(),61)==0,"Flow activation wrote partially with a mismatched input gate");
            VirtualFree(memory,0,MEM_RELEASE);newsGrid=0;newsVerticalInput=0;
        }
        for(size_t i=0;i<social::newsLayoutOriginal.size();++i)if(social::newsLayoutOriginal[i]!=social::newsLayoutAligned[i]){++changed;require(i==0x45||i==0x46||i==0x4e||i==0x4f,"Layout changed an unrelated instruction");}
        require(changed==4,"Layout correction must change exactly two APT push instructions");
        void* layoutFixture=VirtualAlloc(nullptr,12288,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
        require(layoutFixture!=nullptr,"Layout fixture allocation failed");
        memcpy(layoutFixture,social::newsLayoutOriginal.data(),social::newsLayoutOriginal.size());
        newsLayout=reinterpret_cast<uintptr_t>(layoutFixture);
        newsTemplate=newsLayout+4096;
        newsHandle=newsLayout+8192;
        memcpy(reinterpret_cast<void*>(newsHandle),social::newsHandleOriginal.data(),social::newsHandleOriginal.size());
        focusedTemplate=social::focusedNewsTemplate(reinterpret_cast<uintptr_t>(focusClassName),reinterpret_cast<uintptr_t>(scrollClassName));
        memcpy(reinterpret_cast<void*>(newsTemplate),social::newsTemplateOriginal.data(),social::newsTemplateOriginal.size());
        for(size_t i=0;i<focusedTemplate.size();++i)if(focusedTemplate[i]!=social::newsTemplateOriginal[i])require((i>=0xf6&&i<0x128)||(i>=0x142&&i<0x186),"Navigation changed code outside the reserved constructors");
        require(alignNewsFrame(true)&&layoutOwned&&focusNewsPanel(true),"Checked layout activation failed");
        require(memcmp(layoutFixture,social::newsLayoutAligned.data(),social::newsLayoutAligned.size())==0,"Frame origin correction differs from expected APT");
        require(memcmp(reinterpret_cast<void*>(newsTemplate),focusedTemplate.data(),focusedTemplate.size())==0,"Native focus manager template was not activated");
        require(handleOwned&&memcmp(reinterpret_cast<void*>(newsHandle),social::newsHandleAligned.data(),social::newsHandleAligned.size())==0,"Handle vertical alignment was not applied");
        require(alignNewsFrame(true),"Repeated activation must be harmless");
        static_cast<unsigned char*>(layoutFixture)[0]^=1;
        require(!alignNewsFrame(true),"Repeated activation must recheck ownership");
        require(!alignNewsFrame(false)&&static_cast<unsigned char*>(layoutFixture)[0]!=(social::newsLayoutAligned[0]),"Stop must preserve foreign bytecode changes");
        static_cast<unsigned char*>(layoutFixture)[0]^=1;
        require(alignNewsFrame(false)&&!layoutOwned,"Owned layout must restore");
        require(memcmp(layoutFixture,social::newsLayoutOriginal.data(),social::newsLayoutOriginal.size())==0,"Original layout was not restored");
        require(memcmp(reinterpret_cast<void*>(newsTemplate),social::newsTemplateOriginal.data(),social::newsTemplateOriginal.size())==0,"Native News template was not restored");
        require(focusNewsPanel(true)&&focusNewsPanel(true)&&templateOwned,"Repeated focus activation must preserve the owned template");
        auto* templateBytes=reinterpret_cast<unsigned char*>(newsTemplate);
        templateBytes[0]^=1;
        require(!focusNewsPanel(true),"Focus activation must reject a changed live template");
        std::array<unsigned char,726> reusedTemplate{};
        memcpy(reusedTemplate.data(),templateBytes,reusedTemplate.size());
        require(focusNewsPanel(false)&&!templateOwned,"Released template must clear ownership");
        require(memcmp(templateBytes,reusedTemplate.data(),reusedTemplate.size())==0,"Restore must not overwrite a released or reused template allocation");
        memcpy(templateBytes,social::newsTemplateOriginal.data(),social::newsTemplateOriginal.size());
        require(!handleOwned&&memcmp(reinterpret_cast<void*>(newsHandle),social::newsHandleOriginal.data(),social::newsHandleOriginal.size())==0,"Handle alignment was not restored");
        require(alignNewsHandle(true),"Handle alignment reactivation failed");
        auto* handleBytes=reinterpret_cast<unsigned char*>(newsHandle);handleBytes[0]^=1;
        const auto foreignHandle=handleBytes[0];
        require(!alignNewsHandle(false)&&!handleOwned&&handleBytes[0]==foreignHandle,"Handle stop must preserve foreign changes");
        memcpy(handleBytes,social::newsHandleOriginal.data(),social::newsHandleOriginal.size());
        require(alignNewsHandle(true)&&alignNewsHandle(false),"Handle gate did not recover after fixture repair");
        std::ofstream("news-navigation-fixture.bin",std::ios::binary).write(reinterpret_cast<const char*>(focusedTemplate.data()),focusedTemplate.size());
        static_cast<unsigned char*>(layoutFixture)[0]^=1;
        require(!alignNewsFrame(true)&&!layoutOwned,"Foreign bytecode must be rejected");
        VirtualFree(layoutFixture,0,MEM_RELEASE);newsLayout=0;newsTemplate=0;newsHandle=0;
        for(const auto* category:{"history","championship","bowls"}){social::FeedPost p{"a","@a","body","News"};p.category=category;require(social::matchesType(p,4),"History/title/bowl stories must appear in Rankings & Awards");}
        {social::FeedPost p{"a","@a","body","News"};p.category="season-end";require(social::matchesType(p,2),"Season reviews must appear in Recaps");p.category="matchup-recap";require(social::matchesType(p,2),"Matchup recaps must appear in Recaps");p.category="matchup-preview";require(social::matchesType(p,3),"Matchup previews must appear in Upcoming");}
        require(dynasty::live::decodedEnum("TeamHistoricSeriesYear","FirstRoundCFPBowlPresentationId",999,{}).is_null(),"Unknown optional history art must not block the entire feed");
        require(dynasty::live::decodedEnum("TeamHistoricSeriesYear","FirstRoundCFPBowlPresentationId",1,{{1,"CFPFirstRound"}})=="CFPFirstRound","Known history identifiers must remain intact");
        {bool rejected=false;try{(void)dynasty::live::decodedEnum("Recruit","RecruitStage",999,{});}catch(const std::exception&){rejected=true;}require(rejected,"Unknown identity/event enums must still fail closed");}
        {auto c=std::make_shared<social::Catalog>();c->scopes={{"all","For You"}};social::Edition e;e.key="required-draft";
         for(int i=0;i<36;++i){auto id=std::to_string(i);social::FeedPost p{"NFL Draft","@NFLDraft",id,"Draft"};p.voice="nflDraft";p.category="draft";p.draftPick=i+1;e.stories.emplace(id,p);e.views["all:default"].push_back(id);e.views["all:required"].push_back(id);}c->weeks.push_back(e);
         require(social::selectFeed(c,0,0)->posts.size()==36,"For You lost guaranteed user draft coverage beyond 30");c->weeks[0].views.erase("all:required");require(social::selectFeed(c,0,0)->posts.size()==30,"Ordinary For You cap changed");}
        {auto c=std::make_shared<social::Catalog>();c->scopes={{"team:1","Team"}};social::Edition e;e.key="required-signings";
         for(int i=0;i<32;++i){auto id=std::to_string(i);social::FeedPost p{"Beat","@Beat",id,"Signing"};e.stories.emplace(id,p);e.views["team:1"].push_back(id);e.views["team:1:required"].push_back(id);}c->weeks.push_back(e);
         require(social::selectFeed(c,0,0)->posts.size()==32,"Team view lost required signings beyond routine cap");c->weeks[0].views.erase("team:1:required");require(social::selectFeed(c,0,0)->posts.size()==25,"Routine team cap must be 25");}
        auto status=social::statusFeed();
        require(status->posts.size()==1&&status->key=="runtime-waiting","Startup must expose only a system status row");
        require(status->posts[0].author=="Dynasty Enhancer"&&status->posts[0].stamp=="Status","Startup fallback must not masquerade as a social account");
        // An unsupported process must refuse activation before installing slots.
        if(argc==3){auto config=social::refresh::readJson(argv[1]),data=social::refresh::readJson(argv[2]);social::refresh::validate(data,config);auto decoded=social::decodeFeed(data);require(decoded->catalog&&decoded->posts.size()<=30,"Actual catalog did not decode as a curated single-week feed");for(size_t week=0;week<decoded->catalog->weeks.size();++week)for(unsigned scope=0;scope<social::scopesFor(*decoded->catalog).size();++scope){auto view=social::selectFeed(decoded->catalog,week,scope);require(!view->posts.empty(),"Actual scope has no renderable native row");}std::cout<<"Actual catalog validated: "<<decoded->catalog->weeks.size()<<" publication weeks; every dynamic scope validated.\n";}
        std::cout<<"Passed: filtered CFB identity/order and typed ABI, missing-donor preservation, system-status fallback, "<<feedPostCount<<" posts in "<<feedContainerCount<<" feed containers, coordinate boundaries, scoped native category, exact layout correction/restoration and foreign ownership rejection.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
    return 0;
}
