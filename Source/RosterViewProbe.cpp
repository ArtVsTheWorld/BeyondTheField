// Development-only event observation. Installed files and UI values unchanged.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <atomic>
#include <filesystem>
#include <fstream>
#include <deque>
#include <mutex>
#include "../Vendor/json.hpp"
#include "PlayerRatingGrid.h"
namespace {
using Json=nlohmann::json;using Columns=void(__fastcall*)(void*,void*,int);
HMODULE self;uintptr_t base;Columns original=nullptr;std::atomic<bool> disabled{false};std::atomic<unsigned> calls{0},inflight{0};std::mutex mutex,lifecycle;std::deque<Json> queue;bool installed=false;
constexpr uintptr_t table=0xbacd668,slot=0x88,rva=0x7a89420;
constexpr unsigned char prefix[]={0x48,0x89,0x5c,0x24,0x20,0x55,0x56,0x57,0x48,0x8d,0xac,0x24,0x60,0xfe,0xff,0xff,0x48,0x81,0xec,0xa0,0x02,0x00,0x00,0x48,0x8b,0x05,0x02,0x94,0x00,0x06,0x48,0x33};
bool swap(void* from,void* to){auto at=reinterpret_cast<PVOID volatile*>(base+table+slot);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;auto* prior=InterlockedCompareExchangePointer(at,to,from);VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return prior==from;}
void __fastcall hook(void* source,void* target,int form){
    ++inflight;
    if(disabled||calls.fetch_add(1)>=64){original(source,target,form);--inflight;return;}
    recruitingfog::playerfog::ColumnSink sink{recruitingfog::playerfog::columnTable};sink.fields.reserve(768);original(source,&sink,form);
    recruitingfog::playerfog::replayColumns(sink,target,false);
    Json fields=Json::array();for(const auto& f:sink.fields){
        Json value={{"row",f.row},{"slot",f.slot},{"key",f.key}};
        if(f.slot==6)value["value"]=f.nullText?Json(nullptr):Json(f.text);
        else if(f.slot==4)value["value"]=f.integer;else if(f.slot==3)value["value"]=f.flag;else if(f.slot==5)value["value"]=f.real;
        fields.push_back(std::move(value));
    }
    {std::lock_guard<std::mutex> lock(mutex);if(queue.size()<16)queue.push_back({{"form",form},{"names",sink.names},{"fields",fields}});}--inflight;
}
DWORD stop(){{std::lock_guard<std::mutex> lock(lifecycle);disabled=true;if(installed){if(!swap(reinterpret_cast<void*>(hook),reinterpret_cast<void*>(original)))return 2;installed=false;}}const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);return inflight?3:0;}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto file=std::filesystem::path(path).parent_path()/L"roster-view-probe.jsonl";
    {std::lock_guard<std::mutex> lock(lifecycle);if(disabled)return 1;
    auto* parent=*reinterpret_cast<void**>(base+table+slot);
    if(parent!=reinterpret_cast<void*>(base+rva)||memcmp(parent,prefix,sizeof(prefix)))return 1;
    HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 2;
    original=reinterpret_cast<Columns>(parent);if(!swap(parent,reinterpret_cast<void*>(hook))){original=nullptr;return 3;}installed=true;}
    const auto flush=[&](){std::deque<Json> batch;{std::lock_guard<std::mutex> lock(mutex);batch.swap(queue);}if(!batch.empty()){std::ofstream out(file,std::ios::app);for(const auto& item:batch)out<<item.dump()<<'\n';}};
    const auto deadline=GetTickCount64()+600000;
    while(!disabled&&calls<64&&GetTickCount64()<deadline){flush();Sleep(200);}
    const auto result=stop();
    {std::lock_guard<std::mutex> lock(mutex);queue.push_back({{"event","column_probe_stopped"},{"result",result},{"inflight",inflight.load()}});}
    flush();return result;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
