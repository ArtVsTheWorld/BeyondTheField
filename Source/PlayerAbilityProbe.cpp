// Bounded, read-only observation of ability description UI strings.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <atomic>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include "../Vendor/json.hpp"
#include "RecruitingUiResponse.h"
#include "PlayerAbilityDescriptions.h"
namespace {
using Json=nlohmann::json;using Getter=void*(__fastcall*)(void*,void**,bool);
HMODULE self;uintptr_t base;Getter original=nullptr;
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0},calls{0};
std::mutex mutex;std::deque<Json> pending;
bool read(uintptr_t at,void* out,size_t n){SIZE_T got=0;return ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(at),out,n,&got)&&got==n;}
void note(Json value){std::lock_guard<std::mutex> lock(mutex);if(pending.size()<8)pending.push_back(std::move(value));}
bool textValue(uintptr_t value,std::string& result){
    uintptr_t at=0;if(!read(value+0x20,&at,8))return false;
    std::array<unsigned char,16> data{};if(!read(at,data.data(),16))return false;
    if(data[15]&128){uintptr_t pointer=0;unsigned length=0;memcpy(&pointer,data.data(),8);memcpy(&length,data.data()+8,4);if(length>4096)return false;result.resize(length);return !length||read(pointer,result.data(),length);}
    if(data[15]>15)return false;result.assign(reinterpret_cast<const char*>(data.data()),15-data[15]);return true;
}
void* __fastcall hook(void* object,void** out,bool mentals){
    ++inflight;auto result=original(object,out,mentals);
    if(!disabled&&calls.fetch_add(1)<6&&out&&*out)try{
        recruitingfog::UiResponse view(read);std::vector<uintptr_t> entries;Json rows=Json::array();
        if(view.array(reinterpret_cast<uintptr_t>(*out),entries,128))for(auto entry:entries){
            std::map<std::string,uintptr_t> fields;Json row=Json::object();
            if(view.members(entry,fields))for(const char* key:{"Name","Description","UpgradeDescription"}){
                const auto found=fields.find(key);std::string value;if(found!=fields.end()&&view.kind(found->second)==3&&textValue(found->second,value)){
#if defined(PLAYER_ABILITY_PREVIEW)
                    if(strcmp(key,"Name")){const auto label=recruitingfog::playerfog::abilityDescriptionGrades(value);
                        if(label!=value){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(entry),key,label.c_str());value=label;}}
#endif
                    row[key]=value;
                }
            }
            rows.push_back(std::move(row));
        }
        note({{"event","ability_descriptions"},{"mentals",mentals},{"rows",rows}});
    }catch(...){note({{"event","ability_probe_read_failed"}});}
    --inflight;return result;
}
bool swap(void* before,void* after){auto at=reinterpret_cast<PVOID volatile*>(base+0xbab1b28+0xa0);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;auto prior=InterlockedCompareExchangePointer(at,after,before);VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return prior==before;}
DWORD stop(){disabled=true;if(original&&!swap(reinterpret_cast<void*>(hook),reinterpret_cast<void*>(original)))return 2;const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);return inflight?3:0;}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto file=std::filesystem::path(path).parent_path()/L"player-ability-probe.jsonl";
    constexpr unsigned char prefix[]={0x44,0x88,0x44,0x24,0x18,0x48,0x89,0x54,0x24,0x10,0x48,0x89,0x4c,0x24,0x08,0x55,0x53,0x56,0x41,0x54,0x41,0x56,0x41,0x57,0x48,0x8d,0x6c,0x24,0x88,0x48,0x81,0xec};
    const auto current=*reinterpret_cast<uintptr_t*>(base+0xbab1b28+0xa0);
    if(current!=base+0x794d200||memcmp(reinterpret_cast<void*>(current),prefix,sizeof(prefix)))return 1;
    HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 2;
    original=reinterpret_cast<Getter>(current);if(!swap(reinterpret_cast<void*>(original),reinterpret_cast<void*>(hook))){original=nullptr;return 3;}
    note({{"event","ability_probe_active"},{"pid",GetCurrentProcessId()}});const auto deadline=GetTickCount64()+120000;
    while(!disabled&&GetTickCount64()<deadline){std::deque<Json> rows;{std::lock_guard<std::mutex> lock(mutex);rows.swap(pending);}if(!rows.empty()){std::ofstream out(file,std::ios::app);for(const auto& row:rows)out<<row.dump()<<'\n';}Sleep(200);}
    if(!disabled)stop();return 0;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
