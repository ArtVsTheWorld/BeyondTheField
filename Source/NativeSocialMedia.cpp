#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <atomic>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <deque>
#include <string>
#include <vector>
#include <map>
#include <charconv>
#include <string_view>
#include <algorithm>
#include "../Vendor/json.hpp"
#include "FeedData.h"
#include "CurrentBindings.h"
#include "NewsLayout.h"
#include "NewsStyle.h"
#include "NewsNavigation.h"
#include "NewsFlow.h"
#include "NewsScroll.h"
#include "NewsScopeInput.h"
#include "NewsDropdowns.h"
#include "NewsPolish.h"
#include "RuntimeFeed.h"
namespace {
using Json=nlohmann::json;
#ifdef SOCIAL_SCROLL_TEST
unsigned feedPostCount=12;
#else
unsigned feedPostCount=1;
#endif
#ifdef SOCIAL_LIST_FEED
constexpr bool listFeed=true;
#else
constexpr bool listFeed=false;
#endif
unsigned feedContainerCount=listFeed?1:feedPostCount;
std::mutex feedMutex;
std::shared_ptr<const social::Feed> latestFeed=social::statusFeed(feedPostCount),pageFeed=latestFeed;
void adoptFeed(){std::lock_guard<std::mutex> lock(feedMutex);pageFeed=latestFeed;feedPostCount=static_cast<unsigned>(pageFeed->posts.size());feedContainerCount=listFeed?1:feedPostCount;}
void publishFeed(const Json&);
void waitingFeed(){auto feed=social::statusFeed();std::lock_guard<std::mutex> lock(feedMutex);latestFeed=std::move(feed);}

#ifdef SOCIAL_READ_ONLY_FEED
constexpr bool selectablePosts=false;
#else
constexpr bool selectablePosts=true;
#endif
// Native coordinates are one-based; reject malformed and out-of-range input.
unsigned postNumber(std::string_view value){
    if(value.empty())return 0;
    unsigned number=0;
    auto result=std::from_chars(value.data(),value.data()+value.size(),number);
    return !value.empty()&&value.front()!='0'&&result.ec==std::errc()&&result.ptr==value.data()+value.size()&&number>=1&&number<=feedPostCount?number:0;
}
uintptr_t base=0;
HMODULE module=nullptr;
std::filesystem::path folder;
std::string buildId;
std::atomic<bool> disabled{false},opened{false};
std::atomic<unsigned> callbacks{0};
std::atomic<bool> preflightRunning{false},preflightReady{false},preflightAttempted{false};
std::atomic<bool> feedValidated{false};
void* preflightPanelData=nullptr; // UI-thread-owned retained notification value.
std::mutex logMutex;
std::deque<Json> messages;
void note(Json value) noexcept {try{value["tick"]=GetTickCount64();value["build"]=buildId;std::lock_guard<std::mutex> lock(logMutex);if(messages.size()<256)messages.push_back(std::move(value));}catch(...) {}}
bool read(uintptr_t p,void* out,size_t n) noexcept {SIZE_T got=0;return p>=0x10000&&n<=0x1000&&ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(p),out,n,&got)&&got==n;}
bool replace(void** slot,void* expected,void* desired) noexcept {DWORD old=0,unused=0;if(!VirtualProtect(slot,8,PAGE_READWRITE,&old))return false;void* before=InterlockedCompareExchangePointer(reinterpret_cast<PVOID volatile*>(slot),desired,expected);VirtualProtect(slot,8,old,&unused);return before==expected;}
uintptr_t newsLayout=0;
uintptr_t newsTemplate=0;
constexpr char focusClassName[]="VerticalFocusManager";
constexpr char scrollClassName[]="MountFocusInBounds";
std::array<unsigned char,726> focusedTemplate{};
std::mutex layoutMutex;
bool layoutOwned=false;
bool templateOwned=false;
uintptr_t newsHandle=0;
std::atomic<bool> handleOwned{false};
uintptr_t newsGrid=0,newsVerticalInput=0;
bool flowOwned=false;
uintptr_t newsScroll=0;
bool scrollOwned=false;
#ifdef SOCIAL_DUAL_DROPDOWN
const auto scopedScroll=social::newsScrollSmooth;
#else
const auto scopedScroll=social::scopedNewsScroll();
#endif
auto dropdownPatches=social::dropdown::patches();
uintptr_t newsModelBase=0,dropdownScreenBase=0;
bool dropdownModelOwned=false,dropdownScreenOwned=false;
bool configureNewsDropdowns(bool enable);
uintptr_t newsBodyStyle=0,newsViewport=0;
bool polishOwned=false;
const auto maskedViewport=social::polish::viewportMasked();
bool configureNewsPolish(bool enable);
bool locateNewsLayout(){
    // Installed APT streams have 64-KiB aligned native allocations. Check the
    // header and entire function, never accept a partial bytecode signature.
    uintptr_t match=0,templateMatch=0,frameworkMatch=0;unsigned matches=0,templateMatches=0,frameworkMatches=0,modelMatches=0,viewportMatches=0;const auto started=GetTickCount64();
    std::vector<unsigned char> block(0x100000+14);
    MEMORY_BASIC_INFORMATION region{};
    for(uintptr_t p=0x10000;p<0x7fffffff0000ull;){
        if(GetTickCount64()-started>10000)return false;
        if(!VirtualQuery(reinterpret_cast<void*>(p),&region,sizeof(region)))break;
        const auto end=reinterpret_cast<uintptr_t>(region.BaseAddress)+region.RegionSize;
        if(end<=p)return false;
        const DWORD access=region.Protect&0xff;
        if(region.State==MEM_COMMIT&&region.Type==MEM_PRIVATE&&!(region.Protect&(PAGE_GUARD|PAGE_NOACCESS))&&(access==PAGE_READONLY||access==PAGE_READWRITE||access==PAGE_WRITECOPY)){
            for(auto a=(p+0xffff)&~uintptr_t(0xffff);a<end;a+=0x10000){
                if(GetTickCount64()-started>10000)return false;
                char header[14]{};if(!read(a,header,sizeof(header))||(memcmp(header,"Apt Data:1:7:8",14)&&memcmp(header,"Apt Data:1:8:8",14)))continue;
                std::array<unsigned char,76> modelBytes{};
                if(read(a+0x24a58,modelBytes.data(),modelBytes.size())&&std::equal(modelBytes.begin(),modelBytes.end(),dropdownPatches[6].original.begin())&&read(a+0x24ae0,modelBytes.data(),modelBytes.size())&&std::equal(modelBytes.begin(),modelBytes.end(),dropdownPatches[7].original.begin())){newsModelBase=a;++modelMatches;}
                std::array<unsigned char,432> viewportBytes{};
                if(read(a+0x29398,viewportBytes.data(),viewportBytes.size())&&std::equal(viewportBytes.begin(),viewportBytes.end(),social::polish::viewportOriginal.begin())){newsViewport=a+0x29398;++viewportMatches;}
                std::array<unsigned char,107> bytes{};
                if(read(a+0x2c658,bytes.data(),bytes.size())&&bytes==social::newsLayoutOriginal){match=a+0x2c658;++matches;}
                std::array<unsigned char,61> grid{};std::array<unsigned char,7> input{};std::array<unsigned char,1432> scroll{};
                if(read(a+0xc3540,grid.data(),grid.size())&&grid==social::newsGridOriginal&&read(a+0x62d58,input.data(),input.size())&&input==social::newsVerticalInputOriginal&&read(a+0x630c8,scroll.data(),scroll.size())&&scroll==social::newsScrollOriginal){frameworkMatch=a;++frameworkMatches;}
            }
            // Small screen assets live inside pooled allocations rather than
            // at allocation boundaries. Search bounded committed regions for
            // their APT header, then require the entire News template gate.
            if(region.RegionSize<=8*1024*1024){
                constexpr unsigned char header[]="Apt Data:1:7:8";
                for(auto a=p;a<end;a+=0x100000){
                    if(GetTickCount64()-started>10000)return false;
                    SIZE_T size=static_cast<SIZE_T>((std::min)(uintptr_t(block.size()),end-a)),got=0;
                    if(!ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(a),block.data(),size,&got)||got!=size)continue;
                    auto first=block.begin(),last=first+got;
                    while(first!=last){
                        first=std::search(first,last,std::begin(header),std::end(header)-1);
                        if(first==last)break;
                        const auto offset=static_cast<uintptr_t>(first-block.begin());
                        if(offset<0x100000){std::array<unsigned char,726> candidate{};const auto address=a+offset+0x8a0;
                            if(read(address,candidate.data(),candidate.size())&&candidate==social::newsTemplateOriginal){templateMatch=address;++templateMatches;}}
                        ++first;
                    }
                }
            }
        }
        p=end;
    }
    if(matches!=1||templateMatches>1||frameworkMatches!=1||viewportMatches!=1)return false;
    newsLayout=match;newsTemplate=templateMatch;
    newsGrid=frameworkMatch+0xc3540;newsVerticalInput=frameworkMatch+0x62d58;
    newsScroll=frameworkMatch+0x630c8;
    std::array<unsigned char,56> handleBytes{};
    const auto handleAddress=match+(0x2ce11-0x2c658);
    if(read(handleAddress,handleBytes.data(),handleBytes.size())&&handleBytes==social::newsHandleOriginal)newsHandle=handleAddress;
    newsBodyStyle=match+(0x2ccd2-0x2c658);std::array<unsigned char,58> bodyStyle{};
    if(!read(newsBodyStyle,bodyStyle.data(),bodyStyle.size())||!std::equal(bodyStyle.begin(),bodyStyle.end(),social::polish::bodyOriginal.begin()))return false;
    focusedTemplate=social::focusedNewsTemplate(reinterpret_cast<uintptr_t>(focusClassName),reinterpret_cast<uintptr_t>(scrollClassName));
    if(modelMatches!=1)newsModelBase=0;
    note({{"event","news_layout_located"},{"address",match},{"template",templateMatch},{"framework",frameworkMatch},{"model",newsModelBase},{"modelMatches",modelMatches},{"viewport",newsViewport}});return true;
}
bool configureNewsPolish(bool enable){
    std::lock_guard<std::mutex> lock(layoutMutex);
    if(!enable&&!polishOwned)return true;
    const auto& oldBody=polishOwned?social::polish::bodyWide:social::polish::bodyOriginal;
    const auto& oldViewport=polishOwned?maskedViewport:social::polish::viewportOriginal;
    std::vector<unsigned char> body(oldBody.size()),viewport(oldViewport.size());
    if(!newsBodyStyle||!newsViewport||!read(newsBodyStyle,body.data(),body.size())||body!=oldBody||!read(newsViewport,viewport.data(),viewport.size())||viewport!=oldViewport){note({{"event","news_polish_rejected"},{"enable",enable}});return false;}
    if(enable==polishOwned)return true;
    auto write=[](uintptr_t address,const std::vector<unsigned char>& bytes){DWORD old=0,unused=0;if(!VirtualProtect(reinterpret_cast<void*>(address),bytes.size(),PAGE_READWRITE,&old))return false;memcpy(reinterpret_cast<void*>(address),bytes.data(),bytes.size());VirtualProtect(reinterpret_cast<void*>(address),bytes.size(),old,&unused);return true;};
    const auto& bodyBytes=enable?social::polish::bodyWide:social::polish::bodyOriginal;
    const auto& viewportBytes=enable?maskedViewport:social::polish::viewportOriginal;
    if(!write(newsBodyStyle,bodyBytes))return false;
    if(!write(newsViewport,viewportBytes)){write(newsBodyStyle,oldBody);return false;}
    polishOwned=enable;note({{"event",enable?"news_polish_enabled":"news_polish_restored"},{"bodyWidth",enable?1065:630},{"viewportMask",enable}});return true;
}
bool configureNewsFlow(bool enable){
    std::lock_guard<std::mutex> lock(layoutMutex);
    std::array<unsigned char,61> grid{};std::array<unsigned char,7> input{};
    const auto& expectedGrid=flowOwned?social::newsGridVertical:social::newsGridOriginal;
    const auto& expectedInput=flowOwned?social::newsVerticalInputEnabled:social::newsVerticalInputOriginal;
    if(!newsGrid||!newsVerticalInput||!read(newsGrid,grid.data(),grid.size())||grid!=expectedGrid||!read(newsVerticalInput,input.data(),input.size())||input!=expectedInput){note({{"event","news_flow_rejected"},{"enable",enable}});return false;}
    if(enable==flowOwned)return true;
    DWORD gridOld=0,inputOld=0,unused=0;
    if(!VirtualProtect(reinterpret_cast<void*>(newsGrid),grid.size(),PAGE_READWRITE,&gridOld))return false;
    if(!VirtualProtect(reinterpret_cast<void*>(newsVerticalInput),input.size(),PAGE_READWRITE,&inputOld)){VirtualProtect(reinterpret_cast<void*>(newsGrid),grid.size(),gridOld,&unused);return false;}
    const auto& desiredGrid=enable?social::newsGridVertical:social::newsGridOriginal;
    const auto& desiredInput=enable?social::newsVerticalInputEnabled:social::newsVerticalInputOriginal;
    for(size_t offset:{size_t(0x17),size_t(0x22)})*reinterpret_cast<volatile unsigned char*>(newsGrid+offset)=desiredGrid[offset];
    for(size_t offset:{size_t(4),size_t(5)})*reinterpret_cast<volatile unsigned char*>(newsVerticalInput+offset)=desiredInput[offset];
    VirtualProtect(reinterpret_cast<void*>(newsVerticalInput),input.size(),inputOld,&unused);
    VirtualProtect(reinterpret_cast<void*>(newsGrid),grid.size(),gridOld,&unused);
    flowOwned=enable;note({{"event",enable?"news_vertical_flow_enabled":"news_vertical_flow_restored"}});return true;
}
bool configureNewsScroll(bool enable){
    std::lock_guard<std::mutex> lock(layoutMutex);
    std::array<unsigned char,1432> current{};
    const auto& expected=scrollOwned?scopedScroll:social::newsScrollOriginal;
    if(!newsScroll||!read(newsScroll,current.data(),current.size())||current!=expected){note({{"event","news_scroll_rejected"},{"enable",enable}});return false;}
    if(enable==scrollOwned)return true;
    DWORD old=0,unused=0;if(!VirtualProtect(reinterpret_cast<void*>(newsScroll),current.size(),PAGE_READWRITE,&old))return false;
    const auto& desired=enable?scopedScroll:social::newsScrollOriginal;
    for(size_t offset:{size_t(0xe),size_t(0x141),size_t(0x199)})memcpy(reinterpret_cast<void*>(newsScroll+offset),desired.data()+offset,4);
    memcpy(reinterpret_cast<void*>(newsScroll+0xbc),desired.data()+0xbc,0x20);
    memcpy(reinterpret_cast<void*>(newsScroll+0x2f4),desired.data()+0x2f4,0x395-0x2f4);
    VirtualProtect(reinterpret_cast<void*>(newsScroll),current.size(),old,&unused);
    scrollOwned=enable;note({{"event",enable?"news_smooth_scroll_enabled":"news_smooth_scroll_restored"},{"dpadStepPixels",enable?164:853}});return true;
}
bool configureNewsDropdowns(bool enable){
#ifndef SOCIAL_DUAL_DROPDOWN
    (void)enable;return true;
#else
    std::lock_guard<std::mutex> lock(layoutMutex);
    auto matches=[&](const social::dropdown::Patch& p,uintptr_t address,bool changed){
        const auto& expected=changed?p.changed:p.original;std::vector<unsigned char> found(expected.size());
        return address&&read(address,found.data(),found.size())&&found==expected;
    };
    auto loadedScreen=[&](uintptr_t address){
        char header[14]{};unsigned dictionaryCount=0;uintptr_t dictionary=0;
        return read(address,header,sizeof(header))&&(!memcmp(header,"Apt Data:1:7:8",14)||!memcmp(header,"Apt Data:1:8:8",14))&&read(address+0x8a0-16,&dictionaryCount,4)&&dictionaryCount==180&&read(address+0x8a0-8,&dictionary,8)&&dictionary>=address&&dictionary<address+7321;
    };
    if(enable&&!dropdownScreenOwned){
        if(newsTemplate&&loadedScreen(newsTemplate-0x8a0)&&matches(dropdownPatches[0],newsTemplate,false))dropdownScreenBase=newsTemplate-0x8a0;
        else{
            uintptr_t found=0;unsigned count=0;const auto began=GetTickCount64();MEMORY_BASIC_INFORMATION m{};
            std::vector<unsigned char> buffer(0x100000+726);
            for(uintptr_t pos=0x10000;pos<0x7fffffff0000ull;){
                if(GetTickCount64()-began>5000)break;
                if(!VirtualQuery(reinterpret_cast<void*>(pos),&m,sizeof(m)))break;
                const auto end=reinterpret_cast<uintptr_t>(m.BaseAddress)+m.RegionSize;if(end<=pos)break;
                const auto access=m.Protect&0xff;
                if(m.State==MEM_COMMIT&&m.Type==MEM_PRIVATE&&m.RegionSize<=8*1024*1024&&!(m.Protect&(PAGE_GUARD|PAGE_NOACCESS))&&(access==PAGE_READONLY||access==PAGE_READWRITE||access==PAGE_WRITECOPY)){
                    for(auto a=pos;a<end;a+=0x100000){
                        SIZE_T got=0,n=static_cast<SIZE_T>((std::min)(uintptr_t(buffer.size()),end-a));
                        if(!ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(a),buffer.data(),n,&got)||got!=n)continue;
                        const auto& original=dropdownPatches[0].original;
                        auto first=buffer.begin(),last=first+got;
                        while((first=std::search(first,last,original.begin(),original.end()))!=last){
                            auto offset=static_cast<uintptr_t>(first-buffer.begin());const auto candidate=a+offset-0x8a0;if(offset<0x100000&&loadedScreen(candidate)){found=candidate;++count;}++first;
                        }
                    }
                }pos=end;
            }
            if(count!=1){note({{"event","social_dropdown_rejected"},{"reason","News screen is absent or ambiguous"},{"matches",count}});return false;}
            dropdownScreenBase=found;newsTemplate=found+0x8a0;
        }
    }
    // Validate the full batch before changing any function. Released screen
    // pools are never overwritten on exit; the stable model is gated separately.
    bool screenReleased=false;
    std::vector<const social::dropdown::Patch*> written;
    for(const auto& p:dropdownPatches){
        const bool owned=p.model?dropdownModelOwned:dropdownScreenOwned;
        if(!enable&&!owned)continue;
        if(!matches(p,(p.model?newsModelBase:dropdownScreenBase)+p.offset,owned)){
            if(!enable&&!p.model){screenReleased=true;continue;}
            note({{"event","social_dropdown_rejected"},{"offset",p.offset},{"enable",enable},{"model",p.model}});return false;
        }
    }
    for(const auto& p:dropdownPatches){
        const bool owned=p.model?dropdownModelOwned:dropdownScreenOwned;
        if(enable==owned||(!p.model&&screenReleased))continue;
        const auto address=(p.model?newsModelBase:dropdownScreenBase)+p.offset;
        const auto& bytes=enable?p.changed:p.original;DWORD old=0,unused=0;
        if(!VirtualProtect(reinterpret_cast<void*>(address),bytes.size(),PAGE_READWRITE,&old)){
            for(auto it=written.rbegin();it!=written.rend();++it){const auto& prior=**it;const auto target=(prior.model?newsModelBase:dropdownScreenBase)+prior.offset;const auto& original=enable?prior.original:prior.changed;DWORD protection=0;if(VirtualProtect(reinterpret_cast<void*>(target),original.size(),PAGE_READWRITE,&protection)){memcpy(reinterpret_cast<void*>(target),original.data(),original.size());VirtualProtect(reinterpret_cast<void*>(target),original.size(),protection,&unused);}}
            note({{"event","social_dropdown_rejected"},{"reason","Function write protection failed; rolled back batch"}});return false;
        }
        memcpy(reinterpret_cast<void*>(address),bytes.data(),bytes.size());
        VirtualProtect(reinterpret_cast<void*>(address),bytes.size(),old,&unused);
        written.push_back(&p);
    }
    dropdownModelOwned=enable;dropdownScreenOwned=enable;
    note({{"event",enable?"social_dropdowns_enabled":"social_dropdowns_restored"},{"screen",dropdownScreenBase},{"model",newsModelBase},{"screenReleased",screenReleased}});return true;
#endif
}
bool focusNewsPanel(bool enable){
    std::lock_guard<std::mutex> lock(layoutMutex);
    std::array<unsigned char,726> current{};
    if(enable==templateOwned)return !enable||(read(newsTemplate,current.data(),current.size())&&current==focusedTemplate);
    const auto& expected=enable?social::newsTemplateOriginal:focusedTemplate;
    const auto& desired=enable?focusedTemplate:social::newsTemplateOriginal;
    if(!newsTemplate||!read(newsTemplate,current.data(),current.size())||current!=expected){
        // The screen releases its APT allocation on Back. Never restore into
        // reused heap memory. On entry, reacquire the current allocation.
        if(!enable){templateOwned=false;note({{"event","news_template_released"}});return true;}
        uintptr_t found=0;unsigned matches=0;const auto started=GetTickCount64();
        std::vector<unsigned char> block(0x100000+14);
        uintptr_t lower=newsTemplate>0x800000?newsTemplate-0x800000:0x10000;
        uintptr_t upper=newsTemplate?newsTemplate+0x800000:0x7fffffff0000ull;
        for(unsigned pass=0;pass<2&&!found;++pass){
            if(pass){lower=0x10000;upper=0x7fffffff0000ull;}
            MEMORY_BASIC_INFORMATION region{};
            for(auto p=lower;p<upper;){
                if(GetTickCount64()-started>10000)return false;
                if(!VirtualQuery(reinterpret_cast<void*>(p),&region,sizeof(region)))break;
                auto end=reinterpret_cast<uintptr_t>(region.BaseAddress)+region.RegionSize;if(end<=p)return false;
                const auto access=region.Protect&0xff;
                if(region.State==MEM_COMMIT&&region.Type==MEM_PRIVATE&&region.RegionSize<=8*1024*1024&&!(region.Protect&(PAGE_GUARD|PAGE_NOACCESS))&&(access==PAGE_READONLY||access==PAGE_READWRITE||access==PAGE_WRITECOPY)){
                    constexpr unsigned char header[]="Apt Data:1:7:8";
                    for(auto a=p;a<end;a+=0x100000){
                        if(GetTickCount64()-started>10000)return false;
                        SIZE_T size=static_cast<SIZE_T>((std::min)(uintptr_t(block.size()),end-a)),got=0;
                        if(!ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(a),block.data(),size,&got)||got!=size)continue;
                        auto first=block.begin(),last=first+got;
                        while(first!=last){
                            first=std::search(first,last,std::begin(header),std::end(header)-1);if(first==last)break;
                            auto offset=static_cast<uintptr_t>(first-block.begin());auto address=a+offset+0x8a0;
                            if(offset<0x100000&&read(address,current.data(),current.size())&&current==social::newsTemplateOriginal){found=address;++matches;}
                            ++first;
                        }
                    }
                }
                p=end;
            }
        }
        if(matches!=1)return false;
        newsTemplate=found;note({{"event","news_template_reacquired"},{"address",found},{"milliseconds",GetTickCount64()-started}});
    }
    if(!read(newsTemplate,current.data(),current.size())||current!=expected)return false;
    DWORD old=0,unused=0;if(!VirtualProtect(reinterpret_cast<void*>(newsTemplate),current.size(),PAGE_READWRITE,&old))return false;
    memcpy(reinterpret_cast<void*>(newsTemplate),desired.data(),desired.size());
    VirtualProtect(reinterpret_cast<void*>(newsTemplate),current.size(),old,&unused);
    templateOwned=enable;note({{"event",enable?"news_focus_enabled":"news_focus_restored"}});return true;
}
bool alignNewsHandle(bool enable){
    std::lock_guard<std::mutex> lock(layoutMutex);
    if(!newsHandle)return false;
    std::array<unsigned char,56> current{};
    const bool owned=handleOwned.load();
    const auto& expected=owned?social::newsHandleAligned:social::newsHandleOriginal;
    if(!read(newsHandle,current.data(),current.size())||current!=expected){handleOwned=false;note({{"event","news_handle_layout_rejected"},{"enable",enable}});return false;}
    if(enable==owned)return true;
    DWORD old=0,unused=0;
    if(!VirtualProtect(reinterpret_cast<void*>(newsHandle),current.size(),PAGE_READWRITE,&old))return false;
    *reinterpret_cast<volatile unsigned char*>(newsHandle+0x2e)=enable?16:24;
    VirtualProtect(reinterpret_cast<void*>(newsHandle),current.size(),old,&unused);
    handleOwned=enable;note({{"event",enable?"news_handle_aligned":"news_handle_restored"}});return true;
}
bool alignNewsFrame(bool enable){
    if(!enable)focusNewsPanel(false);
    // A missing handle gate falls back to a combined account/handle label.
    // It must never block page entry or change unsupported script data.
    alignNewsHandle(enable);
    std::lock_guard<std::mutex> lock(layoutMutex);
    std::array<unsigned char,107> current{};
    if(enable==layoutOwned)return !enable||(newsLayout&&read(newsLayout,current.data(),current.size())&&current==social::newsLayoutAligned);
    const auto& expected=enable?social::newsLayoutOriginal:social::newsLayoutAligned;
    const auto& desired=enable?social::newsLayoutAligned:social::newsLayoutOriginal;
    if(!newsLayout||!read(newsLayout,current.data(),current.size())||current!=expected){note({{"event","news_layout_rejected"},{"enable",enable}});return false;}
    DWORD old=0,unused=0;if(!VirtualProtect(reinterpret_cast<void*>(newsLayout),current.size(),PAGE_READWRITE,&old))return false;
    auto bytes=reinterpret_cast<volatile unsigned char*>(newsLayout);
    for(size_t offset:{size_t(0x45),size_t(0x4e)}){bytes[offset+1]=desired[offset+1];bytes[offset]=desired[offset];}
    VirtualProtect(reinterpret_cast<void*>(newsLayout),current.size(),old,&unused);
    layoutOwned=enable;note({{"event",enable?"news_layout_aligned":"news_layout_restored"}});return true;
}
struct Guard {Guard(){++callbacks;}~Guard(){--callbacks;}};
struct Alias {void** vt;const char* value;};
extern void* aliasVt[];
std::string argument(void* p) {
    uintptr_t vt=0,fn=0;
    if(!read(reinterpret_cast<uintptr_t>(p),&vt,8))return {};
    if(vt==reinterpret_cast<uintptr_t>(aliasVt))return static_cast<Alias*>(p)->value;
    if(vt!=base+0xb575928||!read(vt+0x30,&fn,8)||fn!=base+0x3f07c50)return {};
    char text[128]{};reinterpret_cast<void(__fastcall*)(void*,char*,unsigned)>(fn)(p,text,sizeof(text));text[127]=0;return text;
}
void __fastcall aliasRead(Alias* a,char* out,unsigned n){if(n)strncpy_s(out,n,a->value,_TRUNCATE);}
void* aliasVt[]={nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,reinterpret_cast<void*>(aliasRead)};
using Tiles=void*(__fastcall*)(void*,void**,void*,void*);
using Containers=void(__fastcall*)(void*,void*,void*);
using NavInfo=void(__fastcall*)(void*,void*,void*);
using NavRequest=void(__fastcall*)(void*,unsigned,const char*,void*);
using RequestPanel=bool(__fastcall*)(void*,void*,void*);
using FilterData=void(__fastcall*)(void*,void*,void*,void*);
using PanelReady=void(__fastcall*)(void*,const char*,void*);
using FilterChanged=void(__fastcall*)(void*,const char*,const char*,void*);
Tiles tiles=nullptr;Containers containers=nullptr;NavInfo navInfo=nullptr;NavRequest navRequest=nullptr;
RequestPanel requestPanel=nullptr;
PanelReady panelReady=nullptr;
FilterData filterData=nullptr;
FilterChanged filterChanged=nullptr;
void tileText(void* tile,const char* name,const char* value){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(tile,name,value);}
void tileInt(void* tile,const char* name,int value){reinterpret_cast<void(__fastcall*)(void*,const char*,int)>(base+0x2b075c0)(tile,name,value);}
void tileBool(void* tile,const char* name,bool value){reinterpret_cast<void(__fastcall*)(void*,const char*,bool)>(base+0x2b07670)(tile,name,value);}
void releaseValue(void* value);
void* makeObject(){void* result=nullptr;auto manager=reinterpret_cast<void*(__fastcall*)()>(base+0x3f0a1d0)();reinterpret_cast<void*(__fastcall*)(void*,void**)>(base+0x8aec980)(manager,&result);return result;}
void objectValue(void* target,const char* name,void* value){
    // The captured native string/int setters both acquire a map node through
    // this helper, retain the replacement, release node+0x10, then assign it.
    void* iterator[2]{};reinterpret_cast<void*(__fastcall*)(void*,void*,const char*)>(base+0x8aed560)(target,iterator,name);
    auto slot=reinterpret_cast<void**>(reinterpret_cast<uintptr_t>(iterator[0])+0x10);
    if(value)InterlockedIncrement(reinterpret_cast<volatile LONG*>(reinterpret_cast<uintptr_t>(value)+0x14));
    releaseValue(*slot);*slot=value;
}
void objectText(void* out,const char* name,const char* value){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>((*reinterpret_cast<void***>(out))[4])(out,name,value);}
template<class T>void rowSet(void* out,unsigned row,const char* name,T value,size_t slot){reinterpret_cast<void(__fastcall*)(void*,unsigned,const char*,T)>((*reinterpret_cast<void***>(out))[slot])(out,row,name,value);}
void rowText(void* out,unsigned row,const char* name,const char* value){rowSet(out,row,name,value,6);}
struct ContainerProxy {void** vt;void* target;std::map<unsigned,Json> captured;bool discard=false;};
template<class T>void forwardRow(ContainerProxy* p,unsigned row,const char* name,T value,size_t slot){if(!p->discard)rowSet(p->target,row,name,value,slot);p->captured[row][name]=value;}
void __fastcall containerBool(ContainerProxy* p,unsigned row,const char* name,bool v){forwardRow(p,row,name,v,3);}
void __fastcall containerInt(ContainerProxy* p,unsigned row,const char* name,int v){forwardRow(p,row,name,v,4);}
void __fastcall containerFloat(ContainerProxy* p,unsigned row,const char* name,float v){forwardRow(p,row,name,v,5);}
void __fastcall containerString(ContainerProxy* p,unsigned row,const char* name,const char* v){
    forwardRow(p,row,name,v,6);
}
void __fastcall unmapped(){/* The verified collector uses only typed slots 3..6. */}
void* containerVt[]={reinterpret_cast<void*>(unmapped),reinterpret_cast<void*>(unmapped),reinterpret_cast<void*>(unmapped),reinterpret_cast<void*>(containerBool),reinterpret_cast<void*>(containerInt),reinterpret_cast<void*>(containerFloat),reinterpret_cast<void*>(containerString)};
bool appendContainer(ContainerProxy& proxy){
    if(proxy.captured.empty())return false;
    for(const auto& [row,fields]:proxy.captured){
        if(fields.value("tileCoords",std::string())!="7")continue;
        unsigned added=proxy.captured.rbegin()->first+1;
        for(const auto& [name,value]:fields.items()){
            if(value.is_boolean())rowSet(proxy.target,added,name.c_str(),value.get<bool>(),3);
            else if(value.is_number_integer())rowSet(proxy.target,added,name.c_str(),value.get<int>(),4);
            else if(value.is_number_float())rowSet(proxy.target,added,name.c_str(),value.get<float>(),5);
            else if(value.is_string())rowText(proxy.target,added,name.c_str(),name=="tileCoords"?"12":value.get_ref<const std::string&>().c_str());
        }
        note({{"event","cfb_container_added"},{"donorRow",row},{"addedRow",added},{"coordinate","12"}});return true;
    }
    note({{"event","cfb_donor_missing"},{"rows",proxy.captured}});return false;
}
void __fastcall containerHook(void* self,void* panel,void* out){
    Guard guard;auto name=argument(panel);
    if(!disabled&&!preflightRunning&&name=="CM_NEWSTAB"){configureNewsDropdowns(false);configureNewsPolish(false);}
    if(!disabled&&opened&&!preflightRunning&&name=="CM_NEWSTAB"){opened=false;configureNewsScroll(false);configureNewsFlow(false);alignNewsFrame(false);}
    if(!disabled&&opened&&name=="CM_NEWSSUB"){
        Alias donor{aliasVt,"CM_NEWSTAB"};ContainerProxy proxy{containerVt,out,{},true};containers(self,&donor,&proxy);
        if(!proxy.captured.empty())for(unsigned row=0;row<feedContainerCount;++row){auto coords=std::to_string(row+1);for(const auto& [key,value]:proxy.captured.begin()->second.items()){
            if(value.is_boolean())rowSet(out,row,key.c_str(),key=="useTileDimensions"||key=="UseTileDimensions"?true:key=="UseFrame"?false:value.get<bool>(),3);
            else if(value.is_number_integer())rowSet(out,row,key.c_str(),value.get<int>(),4);
            else if(value.is_number_float())rowSet(out,row,key.c_str(),value.get<float>(),5);
            else if(value.is_string())rowText(out,row,key.c_str(),key=="tileCoords"?coords.c_str():key=="panelId"?"CM_NEWSSUB":value.get_ref<const std::string&>().c_str());
        }
            if constexpr(listFeed){rowText(out,row,"linkage","art_control.group.PanelListContainer");rowSet(out,row,"Width",1200,4);rowSet(out,row,"Height",600,4);rowSet(out,row,"ScrollByMount",false,3);rowSet(out,row,"UseScrollArrows",false,3);rowSet(out,row,"ShowScroller",true,3);rowSet(out,row,"WrapList",false,3);}
        }note({{"event","social_feed_containers"},{"donor",proxy.captured},{"listFeed",listFeed}});return;
    }
    if(disabled||name!="CM_NEWSTAB"){containers(self,panel,out);return;}ContainerProxy proxy{containerVt,out,{}};containers(self,panel,&proxy);appendContainer(proxy);
}
void populatePost(void* tile,unsigned number){
    const auto c=std::to_string(number);
            const auto& post=pageFeed->posts.at(number-1);auto author=post.author+" ("+post.handle+")";
            tileText(tile,"Id",("SOCIAL_POST_"+c).c_str());tileText(tile,"Coordinates",c.c_str());tileText(tile,"Linkage","art_control.paneltile.NewsStoryTile");tileText(tile,"Text0",author.c_str());tileText(tile,"Text1",post.body.c_str());tileText(tile,"Text2",post.handle.c_str());tileText(tile,"Tweet1Text0",author.c_str());tileText(tile,"Tweet1Text1",post.body.c_str());tileText(tile,"Tweet1Image0","");tileText(tile,"Tweet2Text0","");tileText(tile,"NavigationId","DO_NOTHING");
            // Modern News consumes WidgetData directly. Legacy CFB list tiles
            // use capitalized Linkage/Text0 and do their own formatting.
            // News needs a focusable input target to keep native panning active.
            // AllowFocus controls the card accent separately; DO_NOTHING keeps
            // the posts read-only even though the input route remains enabled.
            tileText(tile,"linkage","art_control.paneltile.NewsStoryTile");tileText(tile,"display",handleOwned.load()?post.author.c_str():author.c_str());tileInt(tile,"Width",1200);tileInt(tile,"Height",social::postHeight(post.body));tileBool(tile,"isFocusable",true);tileBool(tile,"isInteractive",true);tileBool(tile,"ForceContainer",listFeed);
            void* extra=makeObject();tileText(extra,"SubText",post.body.c_str());auto stamp=post.stamp+" | "+c+"/"+std::to_string(feedPostCount);tileText(extra,"DateText",stamp.c_str());tileText(extra,"TertiaryText",handleOwned.load()?post.handle.c_str():"");tileInt(extra,"ImageLibrary",post.imageLibrary);tileInt(extra,"ImageValue",post.imageValue);tileText(extra,"ImageRenderType","SwappableImage");tileInt(extra,"VisualStyle",2);tileBool(extra,"UseFrame",false);tileBool(extra,"AllowFocus",selectablePosts);tileBool(extra,"ShowDisableOverlay",false);tileInt(extra,"DisableButtonAlpha",0);tileInt(extra,"FillFocusAlpha",100);tileInt(extra,"FillUnFocusAlpha",100);tileInt(extra,"FillUnfocusAlpha",100);tileBool(extra,"StrokeEnabled",false);tileBool(extra,"SendAsData",true);tileBool(extra,"ImmediateUpdate",true);tileInt(tile,"VisualStyle",2);
            objectValue(tile,"ExtraInfo",extra);releaseValue(extra);
            note({{"event","weekly_post_tile"},{"post",c},{"author",author}});
}
void* makeArray(){void* value=nullptr;auto manager=reinterpret_cast<void*(__fastcall*)()>(base+0x3f0a1d0)();reinterpret_cast<void*(__fastcall*)(void*,void**)>(base+0x8ae99d0)(manager,&value);return value;}
void appendArray(void* array,void* value){
    // The native vector copies a pointer without retaining. Transfer one
    // explicit reference to the array, whose destructor releases its items.
    InterlockedIncrement(reinterpret_cast<volatile LONG*>(reinterpret_cast<uintptr_t>(value)+0x14));
    reinterpret_cast<void(__fastcall*)(void*,void**)>(base+0x8aed930)(reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(array)+0x18),&value);
}
void* __fastcall tileHook(void* self,void** out,void* panel,void* coords){
    Guard guard;const auto p=argument(panel),c=argument(coords);void* result=nullptr;
    if constexpr(listFeed){
        if(!disabled&&opened&&p=="CM_NEWSSUB"&&c=="1"&&out){
            void* array=makeArray();if(!array){*out=nullptr;return out;}
            for(unsigned number=1;number<=feedPostCount;++number){
                Alias donorPanel{aliasVt,"CM_NEWSTAB"},donorCoords{aliasVt,"7"};void* donor=nullptr;tiles(self,&donor,&donorPanel,&donorCoords);
                uintptr_t span[2]{};void* tile=nullptr;
                if(donor&&read(reinterpret_cast<uintptr_t>(donor)+0x18,span,16)&&span[1]-span[0]==8&&read(span[0],&tile,8)&&tile){populatePost(tile,number);appendArray(array,tile);}
                releaseValue(donor);
            }
            *out=array;return out;
        }
    }
    if(!listFeed&&!disabled&&opened&&p=="CM_NEWSSUB"&&postNumber(c)){
        Alias donorPanel{aliasVt,"CM_NEWSTAB"},donorCoords{aliasVt,"7"};result=tiles(self,out,&donorPanel,&donorCoords);
        uintptr_t span[2]{};if(out&&*out&&read(reinterpret_cast<uintptr_t>(*out)+0x18,span,16)&&span[1]-span[0]==8){void* tile=nullptr;if(read(span[0],&tile,8)&&tile){
            populatePost(tile,postNumber(c));
        }}return result;
    }
    if(!disabled&&p=="CM_NEWSTAB"&&c=="12"){
        Alias alias{aliasVt,"7"};result=tiles(self,out,panel,&alias);
        uintptr_t span[2]{};unsigned kind=0;
        if(out&&*out&&read(reinterpret_cast<uintptr_t>(*out)+0x10,&kind,4)&&kind==4&&read(reinterpret_cast<uintptr_t>(*out)+0x18,span,16)&&span[1]>=span[0]&&span[1]-span[0]<=128){
            for(uintptr_t a=span[0];a<span[1];a+=8){void* tile=nullptr;if(!read(a,&tile,8)||!tile)continue;
                tileText(tile,"Coordinates",c.c_str());
                tileText(tile,"Id","SOCIAL_MEDIA");tileText(tile,"Text0","Social Media");tileText(tile,"Text1","See what everyone is saying around college football");tileText(tile,"NavigationId","NEWS_MENU");note({{"event","social_button_added"}});
            }
        }
    }else result=tiles(self,out,panel,coords);
    if(!disabled&&p=="CM_NEWSSUB")note({{"event","news_tiles"},{"container",c}});
    return result;
}
// The native category binding reads indexed display/key/isDefault/icon fields.
std::string nativeString(const char* p);
std::string filterArgument(void* value){uintptr_t vt=0;if(read(reinterpret_cast<uintptr_t>(value),&vt,8)&&(vt==reinterpret_cast<uintptr_t>(aliasVt)||vt==base+0xb575928))return argument(value);return nativeString(static_cast<const char*>(value));}
void __fastcall filterDataHook(void* self,void* out,void* panel,void* kind){
    Guard guard;
    const auto panelName=filterArgument(panel),filterKind=filterArgument(kind);
    // Stock News passes an unset panel ID to its category binding. The active
    // Social Media scope also ends when native CFB containers are requested.
    if(!disabled&&opened&&(panelName=="CM_NEWSSUB"||panelName.empty())){
        if(pageFeed->catalog){
#ifdef SOCIAL_DUAL_DROPDOWN
            if(_stricmp(filterKind.c_str(),"filter_one")==0){
                for(unsigned i=0;i<social::scopeLabels.size();++i){rowText(out,i,"display",social::scopeLabels[i]);rowText(out,i,"icon","");rowSet(out,i,"key",static_cast<int>(i+1),4);rowSet(out,i,"isDefault",i==pageFeed->scope,3);}
                note({{"event","social_scope_filter_supplied"},{"scope",pageFeed->scope}});return;
            }
#endif
            for(unsigned i=0;i<pageFeed->catalog->weeks.size();++i){const auto& e=pageFeed->catalog->weeks[i];rowText(out,i,"display",e.label.c_str());rowText(out,i,"icon","");rowSet(out,i,"key",static_cast<int>(i+1),4);rowSet(out,i,"isDefault",i==pageFeed->edition,3);}
        }else{rowText(out,0,"display","All Posts");rowText(out,0,"icon","");rowSet(out,0,"key",0,4);rowSet(out,0,"isDefault",true,3);}
        note({{"event","social_filter_supplied"},{"kind",filterKind}});return;
    }
    filterData(self,out,panel,kind);
}
std::string nativeString(const char* p){char b[128]{};return p&&read(reinterpret_cast<uintptr_t>(p),b,sizeof(b))&&memchr(b,0,sizeof(b))?b:"";}
enum class SocialFilter {unknown,scope,week,scopeDropdown};
SocialFilter socialFilter(const std::string& kind){
    if(_stricmp(kind.c_str(),"SOCIAL_SCOPE")==0)return SocialFilter::scope;
    if(_stricmp(kind.c_str(),"NEWS_CATEGORY")==0)return SocialFilter::week;
#ifdef SOCIAL_DUAL_DROPDOWN
    if(_stricmp(kind.c_str(),"filter_one")==0)return SocialFilter::scopeDropdown;
#endif
    return SocialFilter::unknown;
}
bool changingSelection=false;
void __fastcall filterChangedHook(void* self,const char* panel,const char* kind,void* value){
    Guard guard;const auto p=nativeString(panel),k=nativeString(kind);
    if(!disabled&&opened&&pageFeed->catalog&&(p.empty()||p=="CM_NEWSSUB"||p=="CM_NEWSTAB")){
        // Native FilterGeneric dispatches lowercase news_category, whereas the
        // panel definition and our LT action use uppercase identifiers. Never
        // send our synthetic panel to the stock manager's null panel lookup.
        const auto selectedFilter=socialFilter(k);
        if(selectedFilter==SocialFilter::unknown){note({{"event","social_filter_ignored"},{"panel",p},{"kind",k}});return;}
        if(changingSelection)return;
        try{
            auto week=pageFeed->edition;auto scope=pageFeed->scope;
            if(selectedFilter==SocialFilter::scope)scope=(scope+1)%4;
            else{
                uintptr_t vt=0,fn=0;if(!read(reinterpret_cast<uintptr_t>(value),&vt,8)||!read(vt+0x18,&fn,8)||fn<base||fn>=base+0x11ffe000)throw std::runtime_error("Unsupported week filter value");
                const int key=reinterpret_cast<int(__fastcall*)(void*)>(fn)(value);
                if(selectedFilter==SocialFilter::scopeDropdown){if(key<1||key>4)return;scope=static_cast<unsigned>(key-1);}
                else{if(key<1||static_cast<size_t>(key)>pageFeed->catalog->weeks.size())return;week=static_cast<size_t>(key-1);}
            }
            if(week==pageFeed->edition&&scope==pageFeed->scope)return;
            pageFeed=social::selectFeed(pageFeed->catalog,week,scope);feedPostCount=static_cast<unsigned>(pageFeed->posts.size());feedContainerCount=listFeed?1:feedPostCount;
            note({{"event","social_selection_changed"},{"week",pageFeed->key},{"scope",social::scopeKeys[scope]},{"posts",feedPostCount}});
            changingSelection=true;void* params=makeObject();Alias donor{aliasVt,"CM_NEWSTAB"};const bool requested=requestPanel(self,&donor,params);releaseValue(params);changingSelection=false;
            note({{"event","social_selection_refresh"},{"requested",requested}});
        }catch(const std::exception& e){changingSelection=false;note({{"event","social_selection_failed"},{"error",e.what()}});}
        return;
    }
    filterChanged(self,panel,kind,value);
}
// Typed forwarding preserves the native navigation collector contract while
// recording whether the retained NEWS_MENU destination exists on this build.
struct InfoProxy {void** vt;void* target;};
template<class T>void infoValue(InfoProxy* p,const char* key,T v,size_t slot){reinterpret_cast<void(__fastcall*)(void*,const char*,T)>((*reinterpret_cast<void***>(p->target))[slot])(p->target,key,v);note({{"event","news_navigation_info"},{"key",key},{"value",v}});}
void __fastcall infoBool(InfoProxy* p,const char* k,bool v){infoValue(p,k,v,1);}
void __fastcall infoInt(InfoProxy* p,const char* k,int v){infoValue(p,k,v,2);}
void __fastcall infoFloat(InfoProxy* p,const char* k,float v){infoValue(p,k,v,3);}
void __fastcall infoString(InfoProxy* p,const char* k,const char* v){infoValue(p,k,v,4);}
void* infoVt[]={reinterpret_cast<void*>(unmapped),reinterpret_cast<void*>(infoBool),reinterpret_cast<void*>(infoInt),reinterpret_cast<void*>(infoFloat),reinterpret_cast<void*>(infoString)};
bool runPreflight();
void __fastcall navInfoHook(void* self,void* arg,void* out){Guard guard;auto name=argument(arg);if(!disabled&&name=="NEWS_MENU"){Alias alias{aliasVt,"NEWS"};InfoProxy proxy{infoVt,out};navInfo(self,&alias,&proxy);objectText(out,"Id","NEWS_MENU");}else navInfo(self,arg,out);
    if(!disabled&&name=="HEISMAN_WATCH"&&!preflightAttempted.exchange(true))runPreflight();
}
void __fastcall navRequestHook(void* self,unsigned user,const char* name,void* params){Guard guard;bool selected=!disabled&&name&&strcmp(name,"NEWS_MENU")==0;
#ifdef SOCIAL_PREFLIGHT_ONLY
    if(selected){note({{"event","news_navigation_blocked"},{"reason","Panel initialization preflight only"}});return;}
#else
    if(selected){adoptFeed();note({{"event","weekly_feed_adopted"},{"key",pageFeed->key},{"posts",feedPostCount}});}
    if(selected&&!feedValidated&&!runPreflight()){note({{"event","news_navigation_blocked"},{"reason","Native feed preflight failed"}});return;}
#endif
    if(!disabled){
        if(!alignNewsFrame(selected)&&selected){note({{"event","news_navigation_blocked"},{"reason","Native frame layout gate failed"}});return;}
        if(!configureNewsFlow(selected)&&selected){alignNewsFrame(false);note({{"event","news_navigation_blocked"},{"reason","Native vertical flow gate failed"}});return;}
        if(!configureNewsScroll(selected)&&selected){configureNewsFlow(false);alignNewsFrame(false);note({{"event","news_navigation_blocked"},{"reason","Native scroll gate failed"}});return;}
        if(!configureNewsPolish(selected)&&selected){configureNewsScroll(false);configureNewsFlow(false);alignNewsFrame(false);note({{"event","news_navigation_blocked"},{"reason","Native text/viewport gate failed"}});return;}
        opened=selected;note({{"event","navigation_request"},{"name",name?name:""}});
    }navRequest(self,user,selected?"NEWS":name,params);}
bool __fastcall requestPanelHook(void* self,void* arg,void* params){Guard guard;auto name=argument(arg);if(!disabled&&opened){note({{"event","social_panel_request_argument"},{"name",name}});if(name=="CM_NEWSSUB"){
    if(!configureNewsDropdowns(true)){note({{"event","news_navigation_blocked"},{"reason","Native dropdown gates failed"}});return false;}
#ifdef SOCIAL_EXPERIMENTAL_FOCUS
    if(!preflightRunning&&!focusNewsPanel(true)){note({{"event","news_focus_unavailable"}});return false;}
#endif
    Alias donor{aliasVt,"CM_NEWSTAB"};bool result=requestPanel(self,&donor,params);note({{"event","news_panel_requested"},{"result",result}});return result;}}return requestPanel(self,arg,params);}
void __fastcall panelReadyHook(void* self,const char* name,void* data){
    Guard guard;
    if(preflightRunning){unsigned kind=0;bool valid=name&&strcmp(name,"CM_NEWSTAB")==0&&data&&read(reinterpret_cast<uintptr_t>(data)+0x10,&kind,4)&&kind==5;preflightReady=valid;if(valid&&!preflightPanelData){InterlockedIncrement(reinterpret_cast<volatile LONG*>(reinterpret_cast<uintptr_t>(data)+0x14));preflightPanelData=data;}note({{"event","preflight_panel_ready"},{"name",name?name:""},{"kind",kind},{"valid",valid}});return;}
    if(!disabled&&opened&&name&&strcmp(name,"CM_NEWSTAB")==0){
        unsigned kind=0;
        if(data&&read(reinterpret_cast<uintptr_t>(data)+0x10,&kind,4)&&kind==5){tileText(data,"id","CM_NEWSSUB");tileText(data,"name",pageFeed->label.c_str());tileInt(data,"numRows",static_cast<int>(feedContainerCount));tileInt(data,"numColumns",1);tileText(data,"FilterTypeA","NEWS_CATEGORY");tileText(data,"PositionOffset","0,0");}
        note({{"event","social_panel_ready"}});panelReady(self,"CM_NEWSSUB",data);return;
    }
    panelReady(self,name,data);
}
struct CheckCollector {void** vt;std::map<unsigned,Json> rows;};
void __fastcall checkBool(CheckCollector* c,unsigned r,const char* k,bool v){c->rows[r][k]=v;}
void __fastcall checkInt(CheckCollector* c,unsigned r,const char* k,int v){c->rows[r][k]=v;}
void __fastcall checkFloat(CheckCollector* c,unsigned r,const char* k,float v){c->rows[r][k]=v;}
void __fastcall checkString(CheckCollector* c,unsigned r,const char* k,const char* v){c->rows[r][k]=v;}
void* checkVt[]={nullptr,nullptr,nullptr,reinterpret_cast<void*>(checkBool),reinterpret_cast<void*>(checkInt),reinterpret_cast<void*>(checkFloat),reinterpret_cast<void*>(checkString)};
void releaseValue(void* value){if(value&&InterlockedDecrement(reinterpret_cast<volatile LONG*>(reinterpret_cast<uintptr_t>(value)+0x14))==0)reinterpret_cast<void(__fastcall*)(void*)>(base+0x8aeb1f0)(value);}
bool runPreflight(){
    // Called only from the genuine UI navigation-info callback. Suppress the
    // synthetic ready notification so no live screen is entered or rebound.
    void* adapter=nullptr;void* params=nullptr;unsigned tilesChecked=0;bool requested=false;
    preflightRunning=true;preflightReady=false;
    try {
        if(!read(base+0xfa5a290,&adapter,8)||!adapter)throw std::runtime_error("Panel adapter is unavailable");
        auto manager=reinterpret_cast<void*(__fastcall*)()>(base+0x3f0a1d0)();
        reinterpret_cast<void*(__fastcall*)(void*,void**)>(base+0x8aec980)(manager,&params);
        if(!params)throw std::runtime_error("Native parameter object is unavailable");
        Alias donor{aliasVt,"CM_NEWSTAB"};requested=requestPanel(adapter,&donor,params);
        releaseValue(params);params=nullptr;
        opened=true;CheckCollector output{checkVt,{}};Alias socialPanel{aliasVt,"CM_NEWSSUB"};containerHook(adapter,&socialPanel,&output);
        if(output.rows.size()!=feedContainerCount)throw std::runtime_error("Feed container count does not match the selected content");
        for(unsigned i=0;i<feedContainerCount;++i){auto coordinate=std::to_string(i+1);Alias arg{aliasVt,coordinate.c_str()};void* array=nullptr;tileHook(adapter,&array,&socialPanel,&arg);
            uintptr_t span[2]{};unsigned kind=0;bool valid=array&&read(reinterpret_cast<uintptr_t>(array)+0x10,&kind,4)&&kind==4&&read(reinterpret_cast<uintptr_t>(array)+0x18,span,16)&&span[1]-span[0]==8*(listFeed?feedPostCount:1);
            releaseValue(array);if(!valid)throw std::runtime_error("Feed did not supply the expected post count per container");tilesChecked+=listFeed?feedPostCount:1;
        }
        opened=false;preflightRunning=false;bool passed=requested&&preflightReady&&tilesChecked==feedPostCount;
        feedValidated=passed;
        note({{"event","native_feed_preflight"},{"passed",passed},{"requestSucceeded",requested},{"readyNotification",preflightReady.load()},{"containers",output.rows},{"tiles",tilesChecked},{"thread",GetCurrentThreadId()},{"screenEntered",false}});
#ifndef SOCIAL_PREFLIGHT_ONLY
        if(passed&&preflightPanelData){panelReady(adapter,"CM_NEWSTAB",preflightPanelData);note({{"event","hub_refresh_published"}});}
#endif
        releaseValue(preflightPanelData);preflightPanelData=nullptr;return passed;
    }catch(const std::exception& e){releaseValue(params);releaseValue(preflightPanelData);preflightPanelData=nullptr;opened=false;preflightRunning=false;feedValidated=false;note({{"event","native_feed_preflight"},{"passed",false},{"error",e.what()},{"tiles",tilesChecked},{"screenEntered",false}});return false;}
}
struct Binding{uintptr_t vt,offset,rva;void* hook;bool installed=false;};
Binding bindings[]={
    {0xbac63a8,0xa0,0x7a1af50,reinterpret_cast<void*>(containerHook)},
    {0xbac63a8,0xb0,0x7a1b4c0,reinterpret_cast<void*>(tileHook)},
    {0xbac8c40,0x50,0x7a1c8e0,reinterpret_cast<void*>(navInfoHook)},
    {0xbac8c40,0x40,0x7a2cca0,reinterpret_cast<void*>(navRequestHook)},
    {0xbac63a8,0x88,0x7a2cdd0,reinterpret_cast<void*>(requestPanelHook)},
    {0xbac63a8,0x40,0x7a27f10,reinterpret_cast<void*>(panelReadyHook)},
    {0xbac63a8,0xc8,0x7a19370,reinterpret_cast<void*>(filterDataHook)},
    {0xbac63a8,0xd0,0x7a2def0,reinterpret_cast<void*>(filterChangedHook)}
};
void stop(){disabled=true;opened=false;configureNewsPolish(false);configureNewsDropdowns(false);configureNewsScroll(false);configureNewsFlow(false);alignNewsFrame(false);for(auto& b:bindings)if(b.installed)replace(reinterpret_cast<void**>(base+b.vt+b.offset),b.hook,reinterpret_cast<void*>(base+b.rva));}
void publishFeed(const Json& data){auto feed=social::decodeFeed(data);std::lock_guard<std::mutex> lock(feedMutex);latestFeed=std::move(feed);}
void flush(){std::deque<Json> batch;{std::lock_guard<std::mutex> lock(logMutex);batch.swap(messages);}if(batch.empty())return;std::ofstream out(folder/L"social-media.jsonl",std::ios::app);for(const auto& x:batch)out<<x.dump()<<'\n';}
DWORD WINAPI worker(void*){
    wchar_t path[32768]{};GetModuleFileNameW(module,path,32768);folder=std::filesystem::path(path).parent_path();buildId=std::filesystem::path(path).filename().u8string();base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
    try{
        dynasty::live::FeedWorker refresh;refresh.configure(folder,base);waitingFeed();adoptFeed();
        for(const auto& g:socialGates){unsigned char bytes[32]{};if(!read(base+g.rva,bytes,32)||memcmp(bytes,g.bytes,32))throw std::runtime_error("Unsupported game code at "+std::to_string(g.rva));}
        for(const auto& b:bindings){uintptr_t pointer=0;if(!read(base+b.vt+b.offset,&pointer,8)||pointer!=base+b.rva)throw std::runtime_error("Native UI slot is owned or unsupported");}
        if(!locateNewsLayout())throw std::runtime_error("Native NewsStory layout is absent, ambiguous, or unsupported");
#ifdef SOCIAL_DUAL_DROPDOWN
        if(!newsModelBase)throw std::runtime_error("Native Dynasty filter model is absent or ambiguous");
#endif
        tiles=reinterpret_cast<Tiles>(base+0x7a1b4c0);containers=reinterpret_cast<Containers>(base+0x7a1af50);navInfo=reinterpret_cast<NavInfo>(base+0x7a1c8e0);navRequest=reinterpret_cast<NavRequest>(base+0x7a2cca0);
        requestPanel=reinterpret_cast<RequestPanel>(base+0x7a2cdd0);
        panelReady=reinterpret_cast<PanelReady>(base+0x7a27f10);
        filterData=reinterpret_cast<FilterData>(base+0x7a19370);
        filterChanged=reinterpret_cast<FilterChanged>(base+0x7a2def0);
        HMODULE pinned=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&tileHook),&pinned))throw std::runtime_error("Cannot pin runtime");
        for(auto& b:bindings){if(!replace(reinterpret_cast<void**>(base+b.vt+b.offset),reinterpret_cast<void*>(base+b.rva),b.hook))throw std::runtime_error("UI hook ownership changed during activation");b.installed=true;}
        note({{"event","active"},{"pid",GetCurrentProcessId()},{"scope","Dynasty Enhancer active-Dynasty weekly and midweek feed"},{"posts",feedPostCount},{"listFeed",listFeed},{"selectablePosts",selectablePosts}});
        while(!disabled){flush();if(auto feed=refresh.tick([]{return disabled.load();},[](Json j){note(std::move(j));},[]{waitingFeed();}))publishFeed(*feed);Sleep(200);}note({{"event","stopped"},{"callbacks",callbacks.load()}});flush();
    }catch(const std::exception& e){stop();note({{"event","activation_failed"},{"error",e.what()}});flush();}
    return 0;
}
}
// Scope switching executes inside native APT input. Exit the page first so a
// development stop cannot replace that bytecode underneath an active input call.
extern "C" __declspec(dllexport) DWORD WINAPI WeeklyEventsStop(void*){if(opened)return ERROR_BUSY;stop();return 0;}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){if(opened)return ERROR_BUSY;stop();return 0;}
extern "C" __declspec(dllexport) DWORD WINAPI SocialMediaStop(void*){if(opened)return ERROR_BUSY;stop();return 0;}
BOOL WINAPI DllMain(HMODULE self,DWORD why,void*){if(why==DLL_PROCESS_ATTACH){module=self;DisableThreadLibraryCalls(self);HANDLE thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
