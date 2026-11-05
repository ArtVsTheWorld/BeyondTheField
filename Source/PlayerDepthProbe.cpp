// Development-only bounded, unchanged renderer observation. No UI definitions,
// rating values, game models, resources or save files are modified.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <array>
#include <atomic>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <set>
#include "../Vendor/json.hpp"
namespace {
using Json=nlohmann::json;
using Setup=uintptr_t(__fastcall*)(void*,void*,uintptr_t,uintptr_t,uintptr_t);
using Member=uintptr_t(__fastcall*)(uintptr_t,uintptr_t,uintptr_t,bool);
HMODULE self;uintptr_t base;Setup previous=nullptr;
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0};
std::mutex lifecycle,mutex;std::deque<Json> pending;std::set<uintptr_t> seen;bool installed=false;
bool read(uintptr_t at,void* out,size_t n){SIZE_T got=0;return at>=0x10000&&ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(at),out,n,&got)&&got==n;}
template<class T>T value(uintptr_t at){T v{};read(at,&v,sizeof(v));return v;}
std::string bytes(uintptr_t at,size_t n){std::array<unsigned char,256> b{};if(n>b.size()||!read(at,b.data(),n))return {};std::string s;const char* d="0123456789abcdef";for(size_t i=0;i<n;++i){s+=d[b[i]>>4];s+=d[b[i]&15];}return s;}
uint64_t hash(uintptr_t at,size_t n){std::array<unsigned char,64> b{};if(n>b.size()||!read(at,b.data(),n))return 0;uint64_t h=14695981039346656037ull;for(size_t i=0;i<n;++i){h^=b[i];h*=1099511628211ull;}return h;}
bool nameIs(uintptr_t at,const char* expected){
    if(value<uintptr_t>(at)!=base+0xbc41750)return false;
    const auto data=value<uintptr_t>(at+16);const auto n=strlen(expected);
    std::array<char,64> text{};
    return n<text.size()&&value<unsigned short>(data+4)==n&&read(data+12,text.data(),n+1)&&!memcmp(text.data(),expected,n+1);
}
void note(Json row){std::lock_guard<std::mutex> lock(mutex);if(pending.size()<8)pending.push_back(std::move(row));}
Json snapshot(uintptr_t at){Json j={{"at",at},{"header",bytes(at,96)}};if(!at)return j;
    const auto v=value<uintptr_t>(at);j["vtable"]=v;j["vtableBytes"]=bytes(v,128);
    for(unsigned off=16;off<=64;off+=8){const auto p=value<uintptr_t>(at+off);j["pointer"+std::to_string(off)]={{"at",p},{"bytes",bytes(p,128)}};}return j;}
bool swap(void* from,void* to){auto at=reinterpret_cast<PVOID volatile*>(base+0xbc42fe8+0xc8);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;const auto prior=InterlockedCompareExchangePointer(at,to,from);VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return prior==from;}
uintptr_t __fastcall hook(void* object,void* saved,uintptr_t receiver,uintptr_t parent,uintptr_t super){
    ++inflight;
    const auto def=value<uintptr_t>(reinterpret_cast<uintptr_t>(object)+0x58);
    const bool target=!disabled&&value<unsigned>(def+8)==2&&value<unsigned short>(def+12)==7&&value<unsigned short>(def+14)==41&&hash(def+48,64)==0xBAEDA4DD50C8FF98ull;
    const auto result=previous(object,saved,receiver,parent,super);
    if(target&&!disabled){
            // Native Setup resolves a null r9 through its lexical scope. Read
            // the actual preloaded register1 after that resolution, not r8/r9.
            const auto registers=value<uintptr_t>(base+0xfa632f0);const auto actual=value<uintptr_t>(registers+8);
            bool capture=false;{std::lock_guard<std::mutex> lock(mutex);capture=actual&&seen.size()<4&&seen.insert(actual).second;}
            if(capture){const auto pool=value<uintptr_t>(def+40);const auto name=value<uintptr_t>(pool+27*8),colsName=value<uintptr_t>(pool+81*8);
                if(value<unsigned>(def+32)>=82&&nameIs(name,"mSpreadsheetId")&&nameIs(colsName,"mNumCols")){
                    const auto getter=reinterpret_cast<Member>(base+0x7c21220);
                    const auto sheet=getter(actual,name+16,0,false);const auto cols=getter(actual,colsName+16,0,false);
                    note({{"event","depth_provider"},{"pid",GetCurrentProcessId()},{"definition",def},{"receiver",snapshot(receiver)},{"thisValue",snapshot(actual)},{"sheet",snapshot(sheet)},{"numCols",snapshot(cols)}});
                }else note({{"event","unsupported_depth_pool"},{"name",name},{"bytes",bytes(name,48)}});
            }
    }
    --inflight;return result;
}
DWORD stop(){{std::lock_guard<std::mutex> lock(lifecycle);disabled=true;if(installed){if(!swap(reinterpret_cast<void*>(hook),reinterpret_cast<void*>(previous)))return 2;installed=false;}}
    const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);return inflight?3:0;}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto file=std::filesystem::path(path).parent_path()/L"player-depth-probe.jsonl";
    {std::lock_guard<std::mutex> lock(lifecycle);if(disabled)return 1;const auto parent=*reinterpret_cast<void**>(base+0xbc42fe8+0xc8);HMODULE owner=nullptr;wchar_t ownerPath[32768]{};
        if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(parent),&owner)||!GetModuleFileNameW(owner,ownerPath,32768)||std::filesystem::path(ownerPath).filename()!=L"DynastyEnhancerRecruitFog-p63.dll")return 1;
        const auto gate=bytes(base+0x7c21220,32);if(gate!="48895c240848896c2410488974241857415641574883ec204d85c0488bd94c8b")return 2;
        HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 3;
        previous=reinterpret_cast<Setup>(parent);if(!swap(parent,reinterpret_cast<void*>(hook)))return 4;installed=true;
    }
    const auto flush=[&](){std::deque<Json> batch;{std::lock_guard<std::mutex> lock(mutex);batch.swap(pending);}if(!batch.empty()){std::ofstream out(file,std::ios::app);for(const auto& r:batch)out<<r.dump()<<'\n';}};
    note({{"event","depth_probe_active"},{"pid",GetCurrentProcessId()}});const auto deadline=GetTickCount64()+600000;
    while(!disabled&&GetTickCount64()<deadline){flush();Sleep(200);}const auto result=stop();note({{"event","depth_probe_stopped"},{"result",result},{"inflight",inflight.load()}});flush();return result;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto t=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(t)CloseHandle(t);}return TRUE;}
