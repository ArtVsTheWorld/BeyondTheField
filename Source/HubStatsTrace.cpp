// Development-only, bounded general script-definition observation.
// No definitions, text, model fields, AS properties or game data are changed.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <array>
#include <atomic>
#include <cstring>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <set>
#include <utility>
#include "../Vendor/json.hpp"

namespace {
using Json=nlohmann::json;
using Setup=uintptr_t(__fastcall*)(void*,void*,uintptr_t,uintptr_t,uintptr_t);
using Length=unsigned(__fastcall*)(void*);
struct Candidate {const char* name;uintptr_t offset;unsigned argc;unsigned short registers,flags;unsigned size;uint64_t hash;};
struct Family {const char* name;uintptr_t offset;unsigned argc;unsigned short registers,flags;unsigned size;uint64_t prefixHash,bodyHash;};
#include "HubStatsTraceCatalog.h"
constexpr std::array<Candidate,4> candidates={{
    {"InfoPanelPregameStats.Init",0x38588,1,23,25,1869,0xb49c571125c7ada0ull},
    {"InfoPanelPregameTeamStats.HandleArtEvent",0x3a0b0,6,6,41,180,0x8118d02b8475f9c1ull},
    {"InfoPanelPregameTeamStats.BindingFinished",0x11d98,0,2,41,128,0x2f3c594f678e456cull},
    {"InfoPanelPregameTeamStats.BindWidget",0x114f8,2,5,25,1284,0x6347b3585977d943ull},
}};
constexpr uintptr_t table=0xbc42fe8,setupSlot=0xc8,lengthSlot=0xb0;
HMODULE self;uintptr_t base;Setup originalSetup=nullptr;Length originalLength=nullptr;
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0},observed{0};
std::array<std::atomic<uintptr_t>,1024> satisfied{};
std::array<std::atomic<uintptr_t>,1024> rejected{};
std::mutex lifecycle,queueMutex;
std::set<uintptr_t> seen;
std::deque<Json> pending;
bool setupInstalled=false,lengthInstalled=false;

bool read(uintptr_t at,void* out,size_t size){
    if(at<0x10000)return false;
    __try{memcpy(out,reinterpret_cast<const void*>(at),size);return true;}
    __except(EXCEPTION_EXECUTE_HANDLER){return false;}
}
template<class T>T field(const unsigned char* bytes,size_t at){T out{};memcpy(&out,bytes+at,sizeof(out));return out;}
template<class T>T value(uintptr_t at){T out{};read(at,&out,sizeof(out));return out;}
uint64_t hash(const unsigned char* bytes,size_t size){uint64_t out=14695981039346656037ull;for(size_t i=0;i<size;++i){out^=bytes[i];out*=1099511628211ull;}return out;}
std::string hex(const unsigned char* bytes,size_t size){constexpr char digits[]="0123456789abcdef";std::string out;out.reserve(size*2);for(size_t i=0;i<size;++i){out+=digits[bytes[i]>>4];out+=digits[bytes[i]&15];}return out;}
struct Match {uintptr_t definition=0;std::array<unsigned char,48> header{};};
Match match(void* object,bool lengthPath){
    Match out;
    if(disabled||observed.load(std::memory_order_relaxed)>=128)return out;
    if(!read(reinterpret_cast<uintptr_t>(object)+0x58,&out.definition,8))return {};
    const auto index=((out.definition>>4)&511)+(lengthPath?512:0);
    // Repeated Draw calls need no header/body read, mutex or allocation.
    if(satisfied[index].load(std::memory_order_relaxed)==out.definition||rejected[index].load(std::memory_order_relaxed)==out.definition)return {};
    const auto reject=[&](){rejected[index].store(out.definition,std::memory_order_relaxed);return Match{};};
    if(!read(out.definition,out.header.data(),48))return {};
    const auto size=field<unsigned>(out.header.data(),24);
    if(!size||size>32768)return reject();
    const auto argc=field<unsigned>(out.header.data(),8);
    const auto registers=field<unsigned short>(out.header.data(),12),flags=field<unsigned short>(out.header.data(),14);
    // The four exact candidate frames are diagnostic admissions even when
    // the current body's hash or source offsets have changed.
    for(const auto& candidate:candidates)
        if(argc==candidate.argc&&registers==candidate.registers&&flags==candidate.flags&&size==candidate.size)return out;
    bool possible=false;
    for(const auto& family:families)
        if(argc==family.argc&&registers==family.registers&&flags==family.flags&&size==family.size){possible=true;break;}
    if(!possible)return reject();
    std::array<unsigned char,64> prefix{};const auto count=(std::min)(64u,size);
    if(!read(out.definition+48,prefix.data(),count))return {};
    const auto prefixHash=hash(prefix.data(),count);
    for(const auto& family:families)
        if(argc==family.argc&&registers==family.registers&&flags==family.flags&&size==family.size&&prefixHash==family.prefixHash)return out;
    return reject();
}
void observe(const Match& matched,void* object,bool lengthPath){
    if(!matched.definition||disabled)return;
    std::lock_guard<std::mutex> lock(queueMutex);
    if(observed>=128||pending.size()>=128)return;
    const auto index=((matched.definition>>4)&511)+(lengthPath?512:0);
    if(!seen.emplace(matched.definition).second){satisfied[index]=matched.definition;return;}
    satisfied[index]=matched.definition;
    const auto size=field<unsigned>(matched.header.data(),24);
    std::array<unsigned char,32768> body{};
    if(!read(matched.definition+48,body.data(),size))return;
    const auto bodyHash=hash(body.data(),size);
    Json row={{"event","hub_stats_definition"},{"pid",GetCurrentProcessId()},
        {"path",lengthPath?"body accessor":"setup"},{"object",reinterpret_cast<uintptr_t>(object)},
        {"definition",matched.definition},{"argc",field<unsigned>(matched.header.data(),8)},
        {"registers",field<unsigned short>(matched.header.data(),12)},{"flags",field<unsigned short>(matched.header.data(),14)},{"size",size},
        {"hash",bodyHash},{"prefix64",hex(body.data(),(std::min)(64u,size))},{"header",hex(matched.header.data(),matched.header.size())}};
    std::string name;bool terminated=false;const auto namePointer=field<uintptr_t>(matched.header.data(),0);
    for(unsigned at=0;at<96;++at){unsigned char c=0;if(!read(namePointer+at,&c,1))break;if(!c){terminated=true;break;}if(c<32||c>126)break;name+=static_cast<char>(c);}
    if(terminated&&!name.empty())row["methodName"]=name;
    Json possible=Json::array();
    for(const auto& candidate:candidates){
        if(field<unsigned>(matched.header.data(),8)!=candidate.argc||field<unsigned short>(matched.header.data(),12)!=candidate.registers||
           field<unsigned short>(matched.header.data(),14)!=candidate.flags||size!=candidate.size)continue;
        char magic[14]{};const auto asset=matched.definition>candidate.offset?matched.definition-candidate.offset:0;
        possible.push_back({{"method",candidate.name},{"asset",asset},{"sourceMagic",read(asset,magic,sizeof(magic))&&!memcmp(magic,"Apt Data:1:",11)},
                           {"bodyMatches",bodyHash==candidate.hash},{"expectedHash",candidate.hash}});
    }
    if(!possible.empty())row["candidateFrames"]=std::move(possible);
    Json familyMatches=Json::array();const auto prefixHash=hash(body.data(),(std::min)(64u,size));
    for(const auto& family:families){
        if(field<unsigned>(matched.header.data(),8)!=family.argc||field<unsigned short>(matched.header.data(),12)!=family.registers||
           field<unsigned short>(matched.header.data(),14)!=family.flags||size!=family.size||prefixHash!=family.prefixHash)continue;
        familyMatches.push_back({{"method",family.name},{"sourceOffset",family.offset},{"bodyMatches",bodyHash==family.bodyHash},{"expectedHash",family.bodyHash}});
    }
    if(!familyMatches.empty())row["hubFamilies"]=std::move(familyMatches);
    // On the setup path ONLY, the original native setup has populated VM r1.
    // Read its pointer/raw shape without calling GetMember or any script.
    if(!lengthPath){
        const auto registers=value<uintptr_t>(base+0xfa632f0);
        const auto actualThis=registers?value<uintptr_t>(registers+8):0;
        std::array<unsigned char,96> bytes{};
        if(actualThis&&read(actualThis,bytes.data(),bytes.size()))row["actualThis"]={{"at",actualThis},{"bytes",hex(bytes.data(),bytes.size())}};
    }
    pending.push_back(std::move(row));++observed;
}
uintptr_t __fastcall setupHook(void* object,void* saved,uintptr_t receiver,uintptr_t parent,uintptr_t super){
    ++inflight;const auto matched=match(object,false);const auto result=originalSetup(object,saved,receiver,parent,super);
    try{observe(matched,object,false);}catch(...){disabled=true;}--inflight;return result;
}
unsigned __fastcall lengthHook(void* object){
    ++inflight;const auto matched=match(object,true);const auto result=originalLength(object);
    try{observe(matched,object,true);}catch(...){disabled=true;}--inflight;return result;
}
bool swap(uintptr_t slot,void* before,void* after){
    auto at=reinterpret_cast<PVOID volatile*>(base+table+slot);DWORD old=0,unused=0;
    if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;
    const auto previous=InterlockedCompareExchangePointer(at,after,before);
    VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return previous==before;
}
DWORD stop(){
    bool okay=true;
    {std::lock_guard<std::mutex> lock(lifecycle);disabled=true;
        if(setupInstalled){if(swap(setupSlot,reinterpret_cast<void*>(setupHook),reinterpret_cast<void*>(originalSetup)))setupInstalled=false;else okay=false;}
        if(lengthInstalled){if(swap(lengthSlot,reinterpret_cast<void*>(lengthHook),reinterpret_cast<void*>(originalLength)))lengthInstalled=false;else okay=false;}}
    const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);
    return !okay?2:inflight?3:0;
}
bool ownerIs(void* pointer){
    HMODULE owner=nullptr;wchar_t path[32768]{};
    return GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(pointer),&owner)&&
        GetModuleFileNameW(owner,path,32768)&&std::filesystem::path(path).filename()==L"DynastyEnhancerRecruitFog-v1.dll";
}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);
    const auto file=std::filesystem::path(path).parent_path()/L"hub-stats-trace.jsonl";
    {std::lock_guard<std::mutex> lock(lifecycle);if(disabled)return 1;
        const auto setup=value<void*>(base+table+setupSlot),length=value<void*>(base+table+lengthSlot);
        if(!ownerIs(setup)||!ownerIs(length))return 2;
        HMODULE pin=nullptr;
        if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 3;
        originalSetup=reinterpret_cast<Setup>(setup);originalLength=reinterpret_cast<Length>(length);
        if(!swap(setupSlot,setup,reinterpret_cast<void*>(setupHook)))return 4;setupInstalled=true;
        if(!swap(lengthSlot,length,reinterpret_cast<void*>(lengthHook))){disabled=true;if(swap(setupSlot,reinterpret_cast<void*>(setupHook),setup))setupInstalled=false;return 5;}
        lengthInstalled=true;
    }
    const auto enqueue=[&](Json row){std::lock_guard<std::mutex> lock(queueMutex);pending.push_back(std::move(row));};
    const auto flush=[&](){std::deque<Json> batch;{std::lock_guard<std::mutex> lock(queueMutex);batch.swap(pending);}if(!batch.empty()){std::ofstream out(file,std::ios::app);for(const auto& row:batch)out<<row.dump()<<'\n';}};
    enqueue({{"event","hub_stats_trace_started"},{"pid",GetCurrentProcessId()},{"version",3},{"maximumEvents",128},{"maximumSeconds",180},{"hubFingerprints",families.size()}});
    const auto deadline=GetTickCount64()+180000;
    while(!disabled&&observed<128&&GetTickCount64()<deadline){flush();Sleep(200);}
    const auto result=stop();enqueue({{"event","hub_stats_trace_stopped"},{"result",result},{"inflight",inflight.load()},{"observed",observed.load()}});flush();return result;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
