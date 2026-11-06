// Development-only bounded Rime integer-formatter observation. No text, input,
// source values, graph connections or game state are changed.
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
using Changed=void(__fastcall*)(void*,const void*);
using Init=void(__fastcall*)(void*);
HMODULE self;uintptr_t base;Changed changed;Init originalInitial;
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0};
std::mutex life,lock;std::set<uintptr_t> seen,targetSeen;ULONGLONG targetWindow=0;std::deque<Json> queue;bool hasChanged=false,hasInit=false;
bool read(uintptr_t p,void* out,size_t n){SIZE_T got=0;return p>=0x10000&&ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(p),out,n,&got)&&got==n;}
template<class T>T value(uintptr_t at){T out{};read(at,&out,sizeof(out));return out;}
std::string bytes(uintptr_t at,size_t n){std::array<unsigned char,512> b{};if(n>b.size()||!read(at,b.data(),n))return {};std::string s;const char* h="0123456789abcdef";for(size_t i=0;i<n;++i){s+=h[b[i]>>4];s+=h[b[i]&15];}return s;}
Json snap(uintptr_t at,size_t n=128){return {{"at",at},{"bytes",bytes(at,n)}};}
void note(Json j){std::lock_guard<std::mutex> g(lock);if(queue.size()<128)queue.push_back(std::move(j));}
void observe(void* object,const void* notification){
    if(disabled)return;const auto at=reinterpret_cast<uintptr_t>(object),data=value<uintptr_t>(at+0x38);
    if(value<uintptr_t>(at)!=base+0xb519b10||value<uintptr_t>(data)!=base+0xb511708)return;
    // Asset-field candidates narrow diagnostic logging only; they do not prove
    // that this live converter owns a rating. Never use this as a production gate.
    const auto flags=value<unsigned>(data+0x18);const bool target=flags==161576263||flags==157174688||flags==142592301;
    {std::lock_guard<std::mutex> g(lock);
        if(target){const auto now=GetTickCount64();if(now-targetWindow>=60000){targetSeen.clear();targetWindow=now;}if(targetSeen.size()>=256||!targetSeen.insert(at).second)return;}
        else if(seen.size()>=1024||!seen.insert(at).second)return;
    }
    const auto bus=value<uintptr_t>(at+0x30),tagged=value<uintptr_t>(bus+0x90);
    Json row={{"event","rime_integer"},{"pid",GetCurrentProcessId()},{"self",snap(at,0x48)},
              {"data",snap(data,0x28)},{"bus",snap(bus,0xa0)},{"notification",snap(reinterpret_cast<uintptr_t>(notification),32)},
              {"flags",flags},{"target",target},{"taggedContext",tagged}};
    if(tagged){
        row["taggedObject"]=snap(tagged&~uintptr_t(1),128);const auto context=(tagged&1)?(tagged&~uintptr_t(1)):value<uintptr_t>(tagged+0x10);row["resolvedContext"]=snap(context,256);
        Json pointers=Json::array();for(unsigned off=0;off<128;off+=8){const auto p=value<uintptr_t>(context+off);if(p>=0x10000)pointers.push_back({{"offset",off},{"target",snap(p,128)}});}row["contextPointers"]=pointers;
    }
    note(std::move(row));
}
void __fastcall onChanged(void* object,const void* notification){++inflight;observe(object,notification);changed(object,notification);--inflight;}
void __fastcall onInit(void* object){++inflight;observe(object,nullptr);originalInitial(object);--inflight;}
bool swap(uintptr_t off,void* old,void* next){auto p=reinterpret_cast<PVOID volatile*>(base+0xb519b10+off);DWORD before=0,tmp=0;if(!VirtualProtect(const_cast<PVOID*>(p),8,PAGE_READWRITE,&before))return false;const auto previous=InterlockedCompareExchangePointer(p,next,old);VirtualProtect(const_cast<PVOID*>(p),8,before,&tmp);return previous==old;}
DWORD stop(){bool okay=true;{std::lock_guard<std::mutex> g(life);disabled=true;
    if(hasChanged){if(swap(0x18,reinterpret_cast<void*>(onChanged),reinterpret_cast<void*>(changed)))hasChanged=false;else okay=false;}
    if(hasInit){if(swap(0x88,reinterpret_cast<void*>(onInit),reinterpret_cast<void*>(originalInitial)))hasInit=false;else okay=false;}}
    const auto until=GetTickCount64()+5000;while(inflight&&GetTickCount64()<until)Sleep(1);return !okay?2:inflight?3:0;
}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto file=std::filesystem::path(path).parent_path()/L"player-rime-probe.jsonl";
    {std::lock_guard<std::mutex> g(life);if(disabled)return 1;
        if(value<uintptr_t>(base+0xb519b10+0x18)!=base+0x3abc230||value<uintptr_t>(base+0xb519b10+0x88)!=base+0x3abb5e0)return 2;
        HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 3;
        changed=reinterpret_cast<Changed>(base+0x3abc230);originalInitial=reinterpret_cast<Init>(base+0x3abb5e0);
        if(!swap(0x18,reinterpret_cast<void*>(changed),reinterpret_cast<void*>(onChanged)))return 4;hasChanged=true;
        if(!swap(0x88,reinterpret_cast<void*>(originalInitial),reinterpret_cast<void*>(onInit))){disabled=true;if(swap(0x18,reinterpret_cast<void*>(onChanged),reinterpret_cast<void*>(changed)))hasChanged=false;return 5;}hasInit=true;
    }
    const auto flush=[&](){std::deque<Json> q;{std::lock_guard<std::mutex> g(lock);q.swap(queue);}if(!q.empty()){std::ofstream out(file,std::ios::app);for(const auto& j:q)out<<j.dump()<<'\n';}};
    note({{"event","rime_probe_active"},{"version",6},{"manualStop",false},{"maximumSeconds",240},{"pid",GetCurrentProcessId()}});
    const auto deadline=GetTickCount64()+240000;while(!disabled&&GetTickCount64()<deadline){flush();Sleep(200);}const auto result=stop();note({{"event","rime_probe_stopped"},{"result",result},{"inflight",inflight.load()}});flush();return result;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto t=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(t)CloseHandle(t);}return TRUE;}
