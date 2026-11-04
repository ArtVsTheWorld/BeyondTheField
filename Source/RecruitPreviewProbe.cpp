// Bounded development-only observation. Never changes response/model values.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <atomic>
#include <array>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include "../Vendor/json.hpp"
#include "RecruitingUiResponse.h"
#include "PlayingTimeGates.h"
namespace {
using Json=nlohmann::json;using Getter=void*(__fastcall*)(void*,void**,uintptr_t,uintptr_t);
HMODULE self;uintptr_t base;Getter original=nullptr;
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0},calls{0};
std::mutex queueMutex,lifecycle;std::deque<Json> pending;bool installed=false;
constexpr uintptr_t table=0xc752560,slot=0x40,native=0xa0e0cc0;
bool read(uintptr_t at,void* out,size_t size){SIZE_T got=0;return at>=0x10000&&ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(at),out,size,&got)&&got==size;}
Json snapshot(recruitingfog::UiResponse<decltype(&read)>& view,uintptr_t value,unsigned depth=0){
    if(depth>3)return "<bounded>";
    double number=0;bool flag=false;std::string text;
    if(view.number(value,number))return number;
    if(view.boolean(value,flag))return flag;
    if(view.string(value,text))return text;
    std::vector<uintptr_t> items;if(view.array(value,items,32)){Json result=Json::array();for(auto child:items)result.push_back(snapshot(view,child,depth+1));return result;}
    std::map<std::string,uintptr_t> fields;if(view.members(value,fields)){Json result=Json::object();unsigned n=0;for(const auto& field:fields){
        if(++n>80)break;
        // Only the attribute preview needs nested inspection. Other roster/stat
        // containers are identified without traversing their potentially large data.
        const auto kind=view.kind(field.second);
        if((depth==0&&field.first!="attributesSubpanelInfo"&&kind>=4)||(depth>=2&&kind>=4)){result[field.first]="<container>";continue;}
        result[field.first]=snapshot(view,field.second,depth+1);
    }return result;}
    return nullptr;
}
void note(Json value){std::lock_guard<std::mutex> lock(queueMutex);if(pending.size()<12)pending.push_back(std::move(value));}
void* __fastcall hook(void* object,void** out,uintptr_t first,uintptr_t second){
    ++inflight;auto* result=original(object,out,first,second);
    if(!disabled&&calls.fetch_add(1)<8&&out&&*out)try{
        recruitingfog::UiResponse view(&read,1024);
        note({{"event","prospect_entry_preview"},{"snapshot",snapshot(view,reinterpret_cast<uintptr_t>(*out))}});
    }catch(...){note({{"event","prospect_preview_read_failed"}});}
    --inflight;return result;
}
bool swap(void* before,void* after){auto at=reinterpret_cast<PVOID volatile*>(base+table+slot);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;const auto prior=InterlockedCompareExchangePointer(at,after,before);VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return prior==before;}
DWORD stop(){
    {std::lock_guard<std::mutex> lock(lifecycle);disabled=true;if(installed){if(!swap(reinterpret_cast<void*>(hook),reinterpret_cast<void*>(original)))return 2;installed=false;}}
    const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);return inflight?3:0;
}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t ownPath[32768]{};GetModuleFileNameW(self,ownPath,32768);const auto file=std::filesystem::path(ownPath).parent_path()/L"recruit-preview-probe.jsonl";
    {std::lock_guard<std::mutex> lock(lifecycle);if(disabled)return 1;
        const auto parent=*reinterpret_cast<void**>(base+table+slot);HMODULE owner=nullptr;wchar_t ownerPath[32768]{};std::array<unsigned char,32> bytes{};
        if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(parent),&owner)||!GetModuleFileNameW(owner,ownerPath,32768)||std::filesystem::path(ownerPath).filename()!=L"DynastyEnhancerRecruitFog-p51.dll"||!read(base+native,bytes.data(),bytes.size())||bytes!=playingTimeGates[7].bytes)return 2;
        HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 3;
        original=reinterpret_cast<Getter>(parent);if(!swap(parent,reinterpret_cast<void*>(hook))){original=nullptr;return 4;}installed=true;
    }
    const auto flush=[&](){std::deque<Json> batch;{std::lock_guard<std::mutex> lock(queueMutex);batch.swap(pending);}if(!batch.empty()){std::ofstream out(file,std::ios::app);for(const auto& row:batch)out<<row.dump(-1,' ',false,Json::error_handler_t::replace)<<'\n';}};
    note({{"event","prospect_preview_probe_active"},{"pid",GetCurrentProcessId()}});const auto deadline=GetTickCount64()+300000;
    while(!disabled&&calls<8&&GetTickCount64()<deadline){flush();Sleep(200);}
    if(!disabled)stop();flush();return 0;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
