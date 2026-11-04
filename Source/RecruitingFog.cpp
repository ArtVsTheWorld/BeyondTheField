#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <atomic>
#include <array>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <set>
#include "../Vendor/json.hpp"
#include "RecruitingGradePolicy.h"
#include "RecruitingUiResponse.h"
#include "RecruitingUiGates.h"
#include "PlayingTimeGates.h"
#include "PlayingTimePolicy.h"
#if defined(RECRUIT_NOTES_PROBE) || defined(RECRUIT_NOTES_UI)
#include "RecruitNotes.h"
#include "RecruitNotesUiPrograms.h"
#endif
#if defined(RECRUIT_NOTES_UI)
#include "RecruitNotesUiRuntime.h"
#include "RecruitResumeRuntime.h"
#endif

namespace recruitingfog::runtime {
using Json=nlohmann::json;
using Getter=void*(__fastcall*)(void*,void**);
HMODULE self=nullptr;uintptr_t base=0;
Getter original=nullptr;
using DetailGetter=void*(__fastcall*)(void*,void**,uintptr_t,uintptr_t);
constexpr size_t detailCount=sizeof(playingTimeGates)/sizeof(playingTimeGates[0]);
std::array<DetailGetter,detailCount> detailOriginal{};
std::array<bool,detailCount> detailInstalled{};
std::array<std::atomic<unsigned>,detailCount> detailCalls{};
constexpr PlayingTimeSurface detailSurfaces[]={PlayingTimeSurface::Motivations,PlayingTimeSurface::SchoolPitch,PlayingTimeSurface::Pitches,PlayingTimeSurface::PitchGrid,PlayingTimeSurface::VisitActivities,PlayingTimeSurface::VisitSummary,PlayingTimeSurface::SchoolModule};
static_assert(sizeof(detailSurfaces)/sizeof(detailSurfaces[0])==detailCount);
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0},calls{0};bool installed=false;
std::mutex queueMutex;std::deque<Json> pending;
#if defined(RECRUIT_NOTES_UI)
notesui::Runtime notesUi;
resume::Cache resumeCache;
using ScriptSetup=uintptr_t(__fastcall*)(void*,void*,uintptr_t,uintptr_t,uintptr_t);
ScriptSetup originalScriptSetup=nullptr;bool notesSetupInstalled=false;
std::atomic<unsigned> notesAttachedMethods{0};
std::atomic<bool> notesAttachmentFailed{false};
constexpr uintptr_t scriptSetupRva=0x7c36850,scriptTableRva=0xbc42fe8,scriptSetupSlot=0xc8;
constexpr std::array<unsigned char,24> scriptSetupPrefix={0x48,0x89,0x5c,0x24,0x10,0x48,0x89,0x6c,0x24,0x18,0x48,0x89,0x74,0x24,0x20,0x57,0x41,0x56,0x41,0x57,0x48,0x83,0xec,0x20};
#endif
constexpr uintptr_t vtableRva=0xc752bc8,slot=0x40,getterRva=0xa0e91a0;
constexpr std::array<unsigned char,32> prefix={0x48,0x89,0x54,0x24,0x10,0x48,0x89,0x4c,0x24,0x08,0x55,0x53,0x41,0x56,0x48,0x8d,0xac,0x24,0xd0,0xfc,0xff,0xff,0x48,0x81,0xec,0x30,0x04,0x00,0x00,0x48,0x8b,0xda};
bool read(uintptr_t at,void* out,size_t size){SIZE_T got=0;return at>=0x10000&&ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<const void*>(at),out,size,&got)&&got==size;}
void note(Json value)noexcept{try{std::lock_guard<std::mutex> lock(queueMutex);if(pending.size()<16)pending.push_back(std::move(value));}catch(...){}}
#if defined(RECRUIT_NOTES_PROBE)
using ScriptLength=unsigned(__fastcall*)(void*);
ScriptLength originalScriptLength=nullptr;bool notesProbeInstalled=false;
std::atomic<uintptr_t> notesObservedAsset{0};
std::atomic<uintptr_t> notesObservedOwner{0};
const auto notesPrograms=notesui::programs();
uint64_t notesBodyHash(const std::vector<unsigned char>& bytes){uint64_t h=14695981039346656037ull;for(auto b:bytes){h^=b;h*=1099511628211ull;}return h;}
unsigned __fastcall notesLengthHook(void* object){
    const auto length=originalScriptLength(object);
    if(disabled||notesObservedAsset)return length;
    if(std::none_of(notesPrograms.begin(),notesPrograms.end(),[&](const auto& p){return p.size==length;}))return length;
    uintptr_t definition=0;if(!read(reinterpret_cast<uintptr_t>(object)+0x58,&definition,8))return length;
    for(const auto& p:notesPrograms)if(p.size==length&&definition>p.offset+0x10000){
        const auto asset=definition-p.offset;char magic[14]{};if(!read(asset,magic,14)||memcmp(magic,"Apt Data:1:",11))continue;
        std::vector<unsigned char> bytes(length);if(!read(definition+0x30,bytes.data(),bytes.size())||notesBodyHash(bytes)!=p.hash)continue;
        notesObservedOwner=reinterpret_cast<uintptr_t>(object);notesObservedAsset=asset;note({{"event","notes_asset_observed"},{"asset",asset},{"owner",notesObservedOwner.load()}});break;
    }
    return length;
}
#endif
bool replace(void* expected,void* wanted,uintptr_t table=vtableRva,uintptr_t offset=slot){
    auto address=reinterpret_cast<PVOID volatile*>(base+table+offset);DWORD old=0,unused=0;
    if(!VirtualProtect(const_cast<PVOID*>(address),8,PAGE_READWRITE,&old))return false;
    const auto previous=InterlockedCompareExchangePointer(address,wanted,expected);
    VirtualProtect(const_cast<PVOID*>(address),8,old,&unused);return previous==expected;
}
Json header(uintptr_t at){
    std::array<uint64_t,10> words{};
    if(!read(at,words.data(),sizeof(words)))return {{"readable",false}};
    return {{"address",at},{"words",words}};
}
template<class T>T peek(uintptr_t at){T value{};read(at,&value,sizeof(value));return value;}
std::set<unsigned> pitchMask(uintptr_t object){
    std::set<unsigned> result;
    const auto context=peek<uintptr_t>(object+0x420),config=peek<uintptr_t>(context+0x148);
    const auto begin=peek<uintptr_t>(config+0x460),end=peek<uintptr_t>(config+0x468);
    bool valid=begin>=0x10000&&end>begin&&(end-begin)%8==0&&(end-begin)/8<=64;
    std::set<unsigned> known;
    if(valid)for(auto at=begin;at<end;at+=8){
        const auto entry=peek<uintptr_t>(at);const auto id=peek<unsigned char>(entry+0x10);
        const auto first=peek<uintptr_t>(entry+0x30),last=peek<uintptr_t>(entry+0x38);
        if(first<0x10000||last<first||last-first!=3||!known.insert(id).second){valid=false;break;}
        std::array<unsigned char,3> motivations{};if(!read(first,motivations.data(),3)){valid=false;break;}
        for(auto motivation:motivations){if(motivation>13){valid=false;break;}if(motivation==playingTimeMotivation)result.insert(id);}
        if(!valid)break;
    }
    // If the pitch configuration cannot be verified, hide bundle grades rather
    // than accidentally expose an aggregate containing the masked component.
    if(!valid){result.clear();for(unsigned i=0;i<256;++i)result.insert(i);}
    return result;
}
PlayingTimeStats applyPlayingTime(uintptr_t root,PlayingTimeSurface surface,unsigned selected,uintptr_t object){
    UiResponse view(read);std::set<unsigned> pitches;
    if(surface==PlayingTimeSurface::PitchGrid||surface==PlayingTimeSurface::Pitches)pitches=pitchMask(object);
    return maskPlayingTime(view,root,surface,selected,pitches,
        [&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);},
        [&](uintptr_t at,const char* key,unsigned value){reinterpret_cast<void(__fastcall*)(void*,const char*,unsigned)>(base+0x2bf67d0)(reinterpret_cast<void*>(at),key,value);});
}
std::string smallText(uintptr_t at){
    std::array<unsigned char,16> bytes{};if(!read(at,bytes.data(),bytes.size()))return {};
    if(bytes[15]&128){uintptr_t data=0;unsigned size=0;memcpy(&data,bytes.data(),8);memcpy(&size,bytes.data()+8,4);if(size>128)return {};std::string result(size,'\0');return !size||read(data,result.data(),size)?result:std::string();}
    return bytes[15]<=15?std::string(reinterpret_cast<const char*>(bytes.data()),15-bytes[15]):std::string();
}
Json snapshot(uintptr_t at,unsigned depth=0,bool full=false,size_t rootLimit=2){
    if(!at||depth>6)return nullptr;
    const auto kind=peek<unsigned>(at+0x10);
    if(kind==1)return Json(peek<unsigned char>(at+0x18)!=0);
    if(kind==2)return Json(peek<double>(at+0x18));
    if(kind==3)return Json(smallText(peek<uintptr_t>(at+0x20)));
    if(kind==4){
        const auto begin=peek<uintptr_t>(at+0x18),end=peek<uintptr_t>(at+0x20);
        if(begin>end||(end-begin)%8||end-begin>512*8)return {{"badArray",header(at)}};
        Json items=Json::array();const auto count=(std::min)(size_t((end-begin)/8),depth?size_t(24):rootLimit);
        for(size_t i=0;i<count;++i)items.push_back(snapshot(peek<uintptr_t>(begin+i*8),depth+1,full,rootLimit));
        return {{"count",(end-begin)/8},{"items",items}};
    }
    if(kind==5){
        const auto buckets=peek<uintptr_t>(at+0x20);const auto count=peek<unsigned>(at+0x28);
        if(!count||count>512)return {{"badMap",header(at)}};
        Json fields=Json::object();std::set<uintptr_t> visited;
        for(unsigned i=0;i<count;++i){auto node=peek<uintptr_t>(buckets+i*8);while(node&&node!=uintptr_t(-1)&&visited.insert(node).second&&visited.size()<256){
            const auto name=smallText(peek<uintptr_t>(node+8));const auto value=peek<uintptr_t>(node+0x10);
            if(full||depth>1||name=="FirstName"||name=="LastName"||name=="RecordId"||name=="PercentageScouted"||name=="Scouted"||name=="ScoutingAttributes")fields[name]=snapshot(value,depth+1,full,rootLimit);
            node=peek<uintptr_t>(node+0x18);
        }}return fields;
    }
    return {{"kind",kind},{"header",header(at)}};
}
struct CallGuard{CallGuard(){++inflight;}~CallGuard(){--inflight;}};
#if defined(RECRUIT_NOTES_UI)
uintptr_t __fastcall notesSetupHook(void* object,void* saved,uintptr_t receiver,uintptr_t parent,uintptr_t super){
    CallGuard guard;
    if(!disabled&&!notesAttachmentFailed)try{const auto index=notesUi.beforeInvoke(object,read);if(index>=0){const auto bit=1u<<index;
        if(!(notesAttachedMethods.fetch_or(bit)&bit))note({{"event","recruit_notes_method_attached"},{"program",index}});}}
    catch(const std::exception& error){notesAttachmentFailed=true;note({{"event","recruit_notes_attachment_failed"},{"reason",error.what()}});}
    return originalScriptSetup(object,saved,receiver,parent,super);
}
#endif
template<size_t Index>void* __fastcall detailHook(void* object,void** out,uintptr_t first,uintptr_t second){
    CallGuard guard;auto result=detailOriginal[Index](object,out,first,second);const auto call=++detailCalls[Index];
    if(!disabled){uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        try{const auto stats=applyPlayingTime(value,detailSurfaces[Index],static_cast<unsigned>(first),reinterpret_cast<uintptr_t>(object));
            if(call<=20&&(call==1||stats.grades||stats.previews||stats.unsupported))note({{"event","playing_time_masked"},{"getter",playingTimeGates[Index].name},{"call",call},{"first",first},{"grades",stats.grades},{"dealbreakers",stats.dealbreakers},{"previews",stats.previews},{"unsupported",stats.unsupported}});
        }catch(const std::exception& error){note({{"event","playing_time_failed"},{"getter",playingTimeGates[Index].name},{"reason",error.what()}});}}
    return result;
}
template<size_t... Index>constexpr auto detailHooks(std::index_sequence<Index...>){return std::array<DetailGetter,sizeof...(Index)>{detailHook<Index>...};}
constexpr auto hooks=detailHooks(std::make_index_sequence<detailCount>{});
void* __fastcall getterHook(void* object,void** out){
    CallGuard guard;
    auto result=original(object,out);
    const auto call=++calls;
    if(!disabled){
        const auto began=GetTickCount64();uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        try{
            UiResponse view(read);
#if defined(RECRUIT_NOTES_UI)
            const auto cached=resumeCache.current(base,read);bool notesLoading=false;
            const auto notesCount=appendRecruitNotes(view,value,[&](uintptr_t at,const char* key,const char* text){
                reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);
                reinterpret_cast<void(__fastcall*)(void*,const char*,bool)>(base+0x2bf6720)(reinterpret_cast<void*>(at),"DENotesLoading",notesLoading);
            },[&](const NotesProspect& p,double id,const std::string& first,const std::string& last){return resumeCache.compose(cached,p,id,first,last,notesLoading);});
            if(call<=5)note({{"event","recruit_notes_prepared"},{"recruits",notesCount},{"resumes",bool(cached)}});
#elif defined(RECRUIT_NOTES_PROBE)
            const auto notesCount=appendRecruitNotes(view,value,[&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);});
            if(call<=5)note({{"event","recruit_notes_prepared"},{"recruits",notesCount}});
#endif
            auto stats=convertRecruitingResponse(view,value,
                [&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);},
                [&](uintptr_t at,const char* key,bool flag){reinterpret_cast<void(__fastcall*)(void*,const char*,bool)>(base+0x2bf6720)(reinterpret_cast<void*>(at),key,flag);});
            if(call<=10||stats.unsupported)note({{"event","grades_applied"},{"call",call},{"recruits",stats.recruits},{"attributes",stats.attributes},{"revealed",stats.revealed},{"ranges",stats.ranges},{"unknown",stats.unknown},{"unsupported",stats.unsupported},{"ms",GetTickCount64()-began}});
            const auto mask=applyPlayingTime(value,PlayingTimeSurface::RecruitList,0,reinterpret_cast<uintptr_t>(object));
            if(call<=10)note({{"event","dealbreakers_masked"},{"fields",mask.dealbreakers},{"unsupported",mask.unsupported}});
        }catch(const std::exception& error){note({{"event","conversion_failed"},{"reason",error.what()}});}
    }
    if(!disabled&&call<=5){
        uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        note({{"event","post_conversion_response"},{"call",call},{"resultEqualsOut",result==out},{"snapshot",snapshot(value)}});
    }
    return result;
}
DWORD stop(){
#if defined(RECRUIT_NOTES_UI)
    if(notesUi.ownerCount()){note({{"event","notes_ui_restart_required"},{"reason","The game can retain cloned Notes definitions; use a clean restart"}});return 4;}
#endif
    disabled=true;
    bool ownershipFailed=false;
#if defined(RECRUIT_NOTES_UI)
    if(notesSetupInstalled){if(replace(reinterpret_cast<void*>(notesSetupHook),reinterpret_cast<void*>(originalScriptSetup),scriptTableRva,scriptSetupSlot))notesSetupInstalled=false;else ownershipFailed=true;}
#endif
#if defined(RECRUIT_NOTES_PROBE)
    if(notesProbeInstalled){if(replace(reinterpret_cast<void*>(notesLengthHook),reinterpret_cast<void*>(originalScriptLength),0xbc42fe8,0xb0))notesProbeInstalled=false;else ownershipFailed=true;}
#endif
    for(size_t i=0;i<detailCount;++i)if(detailInstalled[i]){const auto& gate=playingTimeGates[i];if(replace(reinterpret_cast<void*>(hooks[i]),reinterpret_cast<void*>(detailOriginal[i]),gate.vtable,gate.slot))detailInstalled[i]=false;else ownershipFailed=true;}
    if(installed){if(!replace(reinterpret_cast<void*>(getterHook),reinterpret_cast<void*>(original)))return 2;installed=false;}
    const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);
    return ownershipFailed?2:inflight?3:0;
}
DWORD WINAPI worker(void*){
    wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto folder=std::filesystem::path(path).parent_path();base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
    auto flush=[&](){std::deque<Json> items;{std::lock_guard<std::mutex> lock(queueMutex);items.swap(pending);}if(!items.empty()){std::ofstream out(folder/L"recruiting-fog.jsonl",std::ios::app);for(const auto& j:items)out<<j.dump(-1,' ',false,Json::error_handler_t::replace)<<'\n';}};
    try{
        std::array<unsigned char,32> actual{};uintptr_t current=0;
        if(!read(base+getterRva,actual.data(),actual.size())||actual!=prefix)throw std::runtime_error("Unsupported recruiting getter fingerprint");
        for(const auto& gate:recruitingUiGates){if(!read(base+gate.rva,actual.data(),actual.size())||actual!=gate.bytes)throw std::runtime_error("Unsupported UI-value setter fingerprint");}
        for(const auto& gate:playingTimeGates){if(!read(base+gate.rva,actual.data(),actual.size())||actual!=gate.bytes||!read(base+gate.vtable+gate.slot,&current,8)||current!=base+gate.rva)throw std::runtime_error("Unsupported or already-owned playing-time getter");}
        if(!read(base+vtableRva+slot,&current,8)||current!=base+getterRva)throw std::runtime_error("Recruiting getter already owned; no hook installed");
        HMODULE pinned=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pinned))throw std::runtime_error("Cannot pin recruiting runtime");
        original=reinterpret_cast<Getter>(current);
        if(!replace(reinterpret_cast<void*>(original),reinterpret_cast<void*>(getterHook)))throw std::runtime_error("Recruiting getter ownership changed");installed=true;
        for(size_t i=0;i<detailCount;++i){const auto& gate=playingTimeGates[i];detailOriginal[i]=reinterpret_cast<DetailGetter>(base+gate.rva);if(!replace(reinterpret_cast<void*>(detailOriginal[i]),reinterpret_cast<void*>(hooks[i]),gate.vtable,gate.slot))throw std::runtime_error("Playing-time getter ownership changed");detailInstalled[i]=true;}
#if defined(RECRUIT_NOTES_UI)
        if(!read(base+scriptSetupRva,actual.data(),scriptSetupPrefix.size())||memcmp(actual.data(),scriptSetupPrefix.data(),scriptSetupPrefix.size())||!read(base+scriptTableRva+scriptSetupSlot,&current,8)||current!=base+scriptSetupRva)throw std::runtime_error("Unsupported or already-owned script invocation setup");
        notesUi.prepare();originalScriptSetup=reinterpret_cast<ScriptSetup>(current);
        if(!replace(reinterpret_cast<void*>(originalScriptSetup),reinterpret_cast<void*>(notesSetupHook),scriptTableRva,scriptSetupSlot))throw std::runtime_error("Notes invocation setup ownership changed");
        notesSetupInstalled=true;note({{"event","recruit_notes_ui_prepared"},{"methods",notesUi.methodCount()},{"attachment","live invocation setup"},{"unload","clean restart required after entry"}});
#endif
#if defined(RECRUIT_NOTES_PROBE)
        constexpr unsigned char lengthPrefix[]={0x48,0x8b,0x41,0x58,0x8b,0x40,0x18,0xc3};
        if(!read(base+0xbc42fe8+0xb0,&current,8)||current!=base+0x7c34e40||!read(current,actual.data(),sizeof(lengthPrefix))||memcmp(actual.data(),lengthPrefix,sizeof(lengthPrefix)))throw std::runtime_error("Unsupported script length accessor; Notes probe stopped");
        originalScriptLength=reinterpret_cast<ScriptLength>(current);if(!replace(reinterpret_cast<void*>(originalScriptLength),reinterpret_cast<void*>(notesLengthHook),0xbc42fe8,0xb0))throw std::runtime_error("Script length accessor ownership changed");notesProbeInstalled=true;
#endif
        note({{"event","active"},{"mode","letter grades, ranges and Playing Time masking"},{"scope","recruiting UI responses only"}});
        while(!disabled){
#if defined(RECRUIT_NOTES_UI)
            static uint64_t nextResumeTick=0;if(GetTickCount64()>=nextResumeTick){nextResumeTick=GetTickCount64()+1000;
                try{auto report=resumeCache.tick(base,folder,read);if(!report.is_null())note(std::move(report));}
                catch(const std::exception& error){resumeCache.request();note({{"event","recruit_resume_deferred"},{"reason",error.what()}});}
            }
#endif
#if defined(RECRUIT_NOTES_PROBE)
            if(notesProbeInstalled&&notesObservedAsset){std::ofstream out(folder/L"recruit-notes-observed.json");out<<Json({{"pid",GetCurrentProcessId()},{"asset",notesObservedAsset.load()},{"owner",notesObservedOwner.load()}}).dump();
                if(replace(reinterpret_cast<void*>(notesLengthHook),reinterpret_cast<void*>(originalScriptLength),0xbc42fe8,0xb0))notesProbeInstalled=false;}
#endif
            flush();Sleep(200);}flush();
    }catch(const std::exception& error){stop();note({{"event","failed"},{"reason",error.what()}});flush();}
    return 0;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return recruitingfog::runtime::stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){recruitingfog::runtime::self=module;DisableThreadLibraryCalls(module);auto thread=CreateThread(nullptr,0,recruitingfog::runtime::worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}

