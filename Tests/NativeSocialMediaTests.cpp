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
void __fastcall donorRows(void*,void*,void* out){
    rowText(out,0,"panelId","CM_NEWSTAB");rowText(out,0,"tileCoords","1");
    rowSet(out,0,"UseTileDimensions",false,3);rowSet(out,0,"UseFrame",true,3);
    rowSet(out,0,"Priority",0,4);
}
unsigned filterForwardCalls=0;
void __fastcall originalFilter(void*,void* out,void*,void*){++filterForwardCalls;rowText(out,0,"display","Original category");}
unsigned changedForwardCalls=0;
void __fastcall originalChanged(void*,const char*,const char*,void*){++changedForwardCalls;}
struct FilterValue {void** vt;int key;};
int __fastcall filterKey(FilterValue* value){return value->key;}
void require(bool result,const char* detail){if(!result)throw std::runtime_error(detail);}
}
int main(int argc,char** argv){
    using namespace fixture;
    try {
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
        require(postNumber("1")==1,"First post must be addressable");
        require(postNumber(std::to_string(feedPostCount))==feedPostCount,"Last post must be addressable");
        for(const auto& invalid:{"","0","01","-1","1x","999999999999999999999"})require(postNumber(invalid)==0,"Invalid coordinate accepted");
        require(postNumber(std::to_string(feedPostCount+1))==0,"Out-of-range post accepted");
        containers=donorRows;opened=true;
        Collector feed{vt,{}};Alias panel{aliasVt,"CM_NEWSSUB"};containerHook(nullptr,&panel,&feed);
        require(feed.rows.size()==feedContainerCount,"Feed count differs from native containers");
        for(unsigned row=0;row<feedContainerCount;++row){
            require(feed.rows.at(row).at("tileCoords")==std::to_string(row+1),"Feed coordinate sequence changed");
            require(feed.rows.at(row).at("panelId")=="CM_NEWSSUB","Feed leaked donor panel identity");
            require(feed.rows.at(row).at("UseTileDimensions")==true,"Feed must size from post widgets");
        }
        if constexpr(listFeed)require(feed.rows.at(0).at("linkage")=="art_control.group.PanelListContainer","List feed must use the native list control");
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
            validate(data,config);auto wrong=data;wrong["leagueId"]=99;bool rejected=false;try{validate(wrong,config);}catch(...){rejected=true;}require(rejected,"Another Dynasty was accepted");
            wrong=data;wrong["weeks"][0]["stories"][1]["id"]="0";rejected=false;try{validate(wrong,config);}catch(...){rejected=true;}require(rejected,"Duplicate posts were accepted");
            auto catalog=social::decodeFeed(data)->catalog;
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
            edition.stories.emplace("parent",parent);edition.stories.emplace("reply",reply);edition.stories.emplace("recruit",recruit);
            for(unsigned i=0;i<151;++i){const auto key=i?"team:"+std::to_string(i):"all";catalog->scopes.push_back({key,"Scope "+std::to_string(i)});edition.views[key]={"parent","reply","recruit"};}catalog->weeks.push_back(edition);
            auto view=social::selectFeed(catalog,0,150,7);require(view->posts.size()==2&&view->posts[1].voice=="fan","Native account filter detached a reply from its parent");
            require(view->label=="Social Media - Team Accounts","Category is not visible in the native header");
            require(social::selectFeed(catalog,0,150,9)->posts[0].stamp=="News","A reply must not appear without its parent when filtering Fans");
            require(social::selectFeed(catalog,0,150,1)->posts.size()==1,"Recruiting filter included another root category");
            bool bad=false;try{social::selectFeed(catalog,0,151);}catch(...){bad=true;}require(bad,"Dynamic scope boundary was not enforced");
        }
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
            modelBytes[0x24ae0]^=1;require(!configureNewsDropdowns(false)&&dropdownModelOwned,"Dropdown restore must preserve foreign model changes");modelBytes[0x24ae0]^=1;
            require(configureNewsDropdowns(false)&&!dropdownScreenOwned&&!dropdownModelOwned,"Dropdown restore failed");
            for(const auto& p:dropdownPatches)require(memcmp((p.model?modelBytes:screenBytes)+p.offset,p.original.data(),p.original.size())==0,"Dropdown function failed exact restoration");
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
        auto status=social::statusFeed();
        require(status->posts.size()==1&&status->key=="runtime-waiting","Startup must expose only a system status row");
        require(status->posts[0].author=="Dynasty Enhancer"&&status->posts[0].stamp=="Status","Startup fallback must not masquerade as a social account");
        // An unsupported process must refuse activation before installing slots.
        if(argc==3){auto config=social::refresh::readJson(argv[1]),data=social::refresh::readJson(argv[2]);social::refresh::validate(data,config);auto decoded=social::decodeFeed(data);require(decoded->catalog&&decoded->posts.size()<=20,"Actual catalog did not decode as a curated single-week feed");for(size_t week=0;week<decoded->catalog->weeks.size();++week)for(unsigned scope=0;scope<social::scopesFor(*decoded->catalog).size();++scope){auto view=social::selectFeed(decoded->catalog,week,scope);require(!view->posts.empty(),"Actual scope has no renderable native row");}std::cout<<"Actual catalog validated: "<<decoded->catalog->weeks.size()<<" publication weeks; every dynamic scope validated.\n";}
        std::cout<<"Passed: filtered CFB identity/order and typed ABI, missing-donor preservation, system-status fallback, "<<feedPostCount<<" posts in "<<feedContainerCount<<" feed containers, coordinate boundaries, scoped native category, exact layout correction/restoration and foreign ownership rejection.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
    return 0;
}
