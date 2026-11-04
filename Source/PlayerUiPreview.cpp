// Development-only renderer supplement. No reader, database or native data hooks.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <atomic>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include "../Vendor/json.hpp"
#include "RecruitNotesUiRuntime.h"
#include "PlayerCardUiPrograms.h"
#include "PlayerFogUiPrograms.h"
namespace {
using Json=nlohmann::json;using Setup=uintptr_t(__fastcall*)(void*,void*,uintptr_t,uintptr_t,uintptr_t);
HMODULE self;uintptr_t base;Setup previousSetup=nullptr;
std::atomic<bool> disabled{false},failed{false};std::atomic<unsigned> inflight{0},attached{0};
std::vector<recruitingfog::notesui::Program> previewPrograms(){return recruitingfog::playercardui::sliderPrograms();}
recruitingfog::notesui::Runtime previewUi(previewPrograms());
std::mutex mutex;std::deque<Json> pending;
bool read(uintptr_t at,void* out,size_t size){SIZE_T copied=0;return ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<const void*>(at),out,size,&copied)&&copied==size;}
void note(Json row){std::lock_guard<std::mutex> lock(mutex);pending.push_back(std::move(row));}
bool swap(void* before,void* after){auto at=reinterpret_cast<PVOID volatile*>(base+0xbc42fe8+0xc8);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(at),8,PAGE_READWRITE,&old))return false;const auto prior=InterlockedCompareExchangePointer(at,after,before);VirtualProtect(const_cast<PVOID*>(at),8,old,&unused);return prior==before;}
uintptr_t __fastcall setupHook(void* object,void* saved,uintptr_t receiver,uintptr_t parent,uintptr_t super){
    ++inflight;
    if(!disabled&&!failed)try{const auto index=previewUi.beforeInvoke(object,read);if(index>=0){const auto bit=1u<<index;if(!(attached.fetch_or(bit)&bit))note({{"event","player_ui_preview_attached"},{"method",index}});}}
    catch(const std::exception& error){failed=true;note({{"event","player_ui_preview_failed"},{"reason",error.what()}});}
    const auto result=previousSetup(object,saved,receiver,parent,super);--inflight;return result;
}
DWORD stop(){if(previewUi.ownerCount())return 4;disabled=true;if(previousSetup&&!swap(reinterpret_cast<void*>(setupHook),reinterpret_cast<void*>(previousSetup)))return 2;const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);return inflight?3:previewUi.ownerCount()?4:0;}
DWORD WINAPI worker(void*){
    base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto file=std::filesystem::path(path).parent_path()/L"player-ui-preview.jsonl";
    const auto current=*reinterpret_cast<void**>(base+0xbc42fe8+0xc8);HMODULE owner=nullptr;wchar_t ownerPath[32768]{};
    if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(current),&owner)||!GetModuleFileNameW(owner,ownerPath,32768)||std::filesystem::path(ownerPath).filename()!=L"DynastyEnhancerRecruitFog-p43.dll")return 1;
    HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))return 2;
    previewUi.prepare();previousSetup=reinterpret_cast<Setup>(current);if(!swap(current,reinterpret_cast<void*>(setupHook))){previousSetup=nullptr;return 3;}
    note({{"event","player_ui_preview_active"},{"pid",GetCurrentProcessId()},{"reader",false},{"sourceFilesChanged",false}});
    do{std::deque<Json> batch;{std::lock_guard<std::mutex> lock(mutex);batch.swap(pending);}if(!batch.empty()){std::ofstream out(file,std::ios::app);for(const auto& row:batch)out<<row.dump()<<'\n';}Sleep(200);}while(!disabled);return 0;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);const auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
