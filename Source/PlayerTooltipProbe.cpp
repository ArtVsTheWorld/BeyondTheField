// Development-only bounded capture. Forwards every native collector field unchanged.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <array>
#include <atomic>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <memory>
#include <string>
#include "../Vendor/json.hpp"
#include "PlayerRatingGrid.h"
namespace {
using Json=nlohmann::json;
using Getter=void(__fastcall*)(void*,int,void*);
HMODULE self;uintptr_t base;Getter original=nullptr;
std::atomic<bool> disabled{false};std::atomic<unsigned> calls{0},inflight{0};
std::mutex lifecycle,queueMutex;std::deque<Json> pending;bool installed=false;
constexpr uintptr_t table=0xbab5778,slot=0xa8,native=0x796e160;
constexpr std::array<unsigned char,32> prefix={0x4c,0x8b,0xdc,0x48,0x81,0xec,0x18,0x01,0x00,0x00,0x48,0x8b,0x05,0xcf,0x46,0x12,0x06,0x48,0x33,0xc4,0x48,0x89,0x84,0x24,0xe0,0x00,0x00,0x00,0x48,0x8b,0x89,0x20};
bool read(uintptr_t at,void* out,size_t bytes){SIZE_T got=0;return ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(at),out,bytes,&got)&&got==bytes;}
void note(Json row){std::lock_guard<std::mutex> lock(queueMutex);if(pending.size()<10)pending.push_back(std::move(row));}
struct Sink{void** vtable;void* target;Json fields=Json::array();};
void field(Sink* s,unsigned row,const char* key,Json value,unsigned kind)noexcept{try{
    if(s->fields.size()>=128||row>=32)return;
    const auto length=key?strnlen_s(key,129):0;if(length>128)return;
    s->fields.push_back({{"row",row},{"key",key?Json(std::string(key,length)):Json(nullptr)},{"kind",kind},{"value",std::move(value)}});
}catch(...){} }
void __fastcall reserve(Sink* s,unsigned n){recruitingfog::playerfog::reserve(s->target,n);field(s,n,nullptr,n,1);}
void __fastcall flag(Sink* s,unsigned r,const char* k,bool v){recruitingfog::playerfog::put(s->target,r,k,v,3);field(s,r,k,v,3);}
void __fastcall integer(Sink* s,unsigned r,const char* k,int v){recruitingfog::playerfog::put(s->target,r,k,v,4);field(s,r,k,v,4);}
void __fastcall real(Sink* s,unsigned r,const char* k,float v){recruitingfog::playerfog::put(s->target,r,k,v,5);field(s,r,k,v,5);}
void __fastcall string(Sink* s,unsigned r,const char* k,const char* v){
    recruitingfog::playerfog::put(s->target,r,k,v,6);
    const auto length=v?strnlen_s(v,4097):0;
    try{field(s,r,k,!v?Json(nullptr):length>4096?Json("<long>"):Json(std::string(v,length)),6);}catch(...){}
}
void* sinkTable[]={nullptr,reinterpret_cast<void*>(reserve),nullptr,reinterpret_cast<void*>(flag),reinterpret_cast<void*>(integer),reinterpret_cast<void*>(real),reinterpret_cast<void*>(string)};
void __fastcall hook(void* source,int id,void* target){
    ++inflight;
    if(disabled||!target||calls.fetch_add(1)>=6){original(source,id,target);--inflight;return;}
    std::unique_ptr<Sink> sink;
    try{sink=std::make_unique<Sink>(Sink{sinkTable,target});}catch(...){original(source,id,target);--inflight;return;}
    original(source,id,sink.get());
    try{note({{"event","ability_tooltip_rows"},{"abilityId",id},{"fields",std::move(sink->fields)}});}catch(...){}
    --inflight;
}
bool swap(void* from,void* to){auto at=reinterpret_cast<PVOID volatile*>(base+table+slot);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;const auto prior=InterlockedCompareExchangePointer(at,to,from);VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return prior==from;}
DWORD stop(){
    {std::lock_guard<std::mutex> lock(lifecycle);disabled=true;if(installed){if(!swap(reinterpret_cast<void*>(hook),reinterpret_cast<void*>(original)))return 2;installed=false;}}
    const auto until=GetTickCount64()+5000;while(inflight&&GetTickCount64()<until)Sleep(1);return inflight?3:0;
}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto file=std::filesystem::path(path).parent_path()/L"player-tooltip-probe.jsonl";
    {std::lock_guard<std::mutex> lock(lifecycle);if(disabled)return 1;
        const auto current=*reinterpret_cast<uintptr_t*>(base+table+slot);std::array<unsigned char,32> bytes{};
        if(current!=base+native||!read(current,bytes.data(),bytes.size())||bytes!=prefix)return 2;
        HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 3;
        original=reinterpret_cast<Getter>(current);if(!swap(reinterpret_cast<void*>(original),reinterpret_cast<void*>(hook))){original=nullptr;return 4;}installed=true;
    }
    const auto flush=[&](){std::deque<Json> rows;{std::lock_guard<std::mutex> lock(queueMutex);rows.swap(pending);}if(!rows.empty()){std::ofstream out(file,std::ios::app);for(const auto& row:rows)out<<row.dump(-1,' ',false,Json::error_handler_t::replace)<<'\n';}};
    note({{"event","ability_tooltip_probe_active"},{"pid",GetCurrentProcessId()}});const auto until=GetTickCount64()+300000;
    while(!disabled&&calls<6&&GetTickCount64()<until){flush();Sleep(200);}
    const auto result=stop();note({{"event","ability_tooltip_probe_stopped"},{"result",result},{"inflight",inflight.load()}});flush();return result;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
