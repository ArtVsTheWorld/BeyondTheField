// Bounded development-only script-definition observation. No UI/data conversion.
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
#include "../Vendor/json.hpp"
namespace {
using Json=nlohmann::json;
using Setup=uintptr_t(__fastcall*)(void*,void*,uintptr_t,uintptr_t,uintptr_t);
using Length=unsigned(__fastcall*)(void*);
HMODULE self;uintptr_t base;Setup setup=nullptr;Length originalLength=nullptr;
std::atomic<bool> disabled{false};std::atomic<unsigned> calls{0},inflight{0};
std::mutex mutex,lifecycle;std::set<uintptr_t> seen;std::deque<Json> pending;bool setupInstalled=false,lengthInstalled=false;
constexpr uintptr_t table=0xbc42fe8,setupSlot=0xc8,lengthSlot=0xb0;
bool swap(uintptr_t slot,void* before,void* after){auto at=reinterpret_cast<PVOID volatile*>(base+table+slot);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;auto prior=InterlockedCompareExchangePointer(at,after,before);VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return prior==before;}
template<class T>T value(const unsigned char* p,size_t at){T v{};memcpy(&v,p+at,sizeof(v));return v;}
void observe(void* receiver,const char* path){
    if(disabled||calls.fetch_add(1,std::memory_order_relaxed)>=100000)return;
    const auto definition=*reinterpret_cast<const uintptr_t*>(static_cast<const unsigned char*>(receiver)+0x58);
    std::lock_guard<std::mutex> lock(mutex);if(seen.size()>=1024||!seen.insert(definition).second)return;
    std::array<unsigned char,48> header{};memcpy(header.data(),reinterpret_cast<const void*>(definition),48);
    const auto size=value<unsigned>(header.data(),24);if(size>32768)return;
    std::string prefix;constexpr char digits[]="0123456789abcdef";const auto* bytes=reinterpret_cast<const unsigned char*>(definition+48);
    for(unsigned i=0;i<(std::min)(64u,size);++i){prefix+=digits[bytes[i]>>4];prefix+=digits[bytes[i]&15];}
    pending.push_back({{"definition",definition},{"path",path},{"argc",value<unsigned>(header.data(),8)},{"registers",value<unsigned short>(header.data(),12)},{"flags",value<unsigned short>(header.data(),14)},{"size",size},{"prefix64",prefix}});
}
uintptr_t __fastcall setupHook(void* object,void* saved,uintptr_t receiver,uintptr_t parent,uintptr_t super){++inflight;observe(object,"setup");const auto result=setup(object,saved,receiver,parent,super);--inflight;return result;}
unsigned __fastcall lengthHook(void* object){++inflight;observe(object,"originalLength");const auto result=originalLength(object);--inflight;return result;}
DWORD stop(){bool okay=true;{std::lock_guard<std::mutex> lock(lifecycle);disabled=true;
    if(setupInstalled){if(swap(setupSlot,reinterpret_cast<void*>(setupHook),reinterpret_cast<void*>(setup)))setupInstalled=false;else okay=false;}
    if(lengthInstalled){if(swap(lengthSlot,reinterpret_cast<void*>(lengthHook),reinterpret_cast<void*>(originalLength)))lengthInstalled=false;else okay=false;}}
    const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);return !okay?2:inflight?3:0;}
bool ownerIs(void* pointer,bool setupOwner){HMODULE owner=nullptr;wchar_t path[32768]{};
    if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(pointer),&owner)||!GetModuleFileNameW(owner,path,32768))return false;
    const auto name=std::filesystem::path(path).filename();(void)setupOwner;return name==L"DynastyEnhancerRecruitFog-p61.dll";}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto file=std::filesystem::path(path).parent_path()/L"player-ui-trace.jsonl";
    {std::lock_guard<std::mutex> lock(lifecycle);if(disabled)return 1;
    const auto a=*reinterpret_cast<void**>(base+table+setupSlot),b=*reinterpret_cast<void**>(base+table+lengthSlot);if(!ownerIs(a,true)||!ownerIs(b,false))return 1;
    HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 2;
    setup=reinterpret_cast<Setup>(a);originalLength=reinterpret_cast<Length>(b);
    if(!swap(setupSlot,a,reinterpret_cast<void*>(setupHook)))return 3;setupInstalled=true;
    if(!swap(lengthSlot,b,reinterpret_cast<void*>(lengthHook))){
        // A concurrent owner may have chained our setup hook. Retain captured
        // forwarders if rollback loses ownership; never leave a null chain.
        disabled=true;
        if(swap(setupSlot,reinterpret_cast<void*>(setupHook),a))setupInstalled=false;
        return 4;
    }lengthInstalled=true;}
    const auto flush=[&](){std::deque<Json> batch;{std::lock_guard<std::mutex> lock(mutex);batch.swap(pending);}if(!batch.empty()){std::ofstream out(file,std::ios::app);for(const auto& row:batch)out<<row.dump()<<'\n';}};
    {std::lock_guard<std::mutex> lock(mutex);pending.push_back({{"event","trace_started"},{"pid",GetCurrentProcessId()}});}
    const auto deadline=GetTickCount64()+180000;
    do{flush();Sleep(200);}while(!disabled&&calls<100000&&GetTickCount64()<deadline);
    const auto result=stop();
    {std::lock_guard<std::mutex> lock(mutex);pending.push_back({{"event","trace_stopped"},{"result",result},{"inflight",inflight.load()},{"observed",seen.size()}});}
    flush();return result;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
