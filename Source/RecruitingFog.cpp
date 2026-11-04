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

namespace recruitingfog::runtime {
using Json=nlohmann::json;
using Getter=void*(__fastcall*)(void*,void**);
HMODULE self=nullptr;uintptr_t base=0;
Getter original=nullptr;
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0},calls{0};bool installed=false;
std::mutex queueMutex;std::deque<Json> pending;
constexpr uintptr_t vtableRva=0xc752bc8,slot=0x40,getterRva=0xa0e91a0;
constexpr std::array<unsigned char,32> prefix={0x48,0x89,0x54,0x24,0x10,0x48,0x89,0x4c,0x24,0x08,0x55,0x53,0x41,0x56,0x48,0x8d,0xac,0x24,0xd0,0xfc,0xff,0xff,0x48,0x81,0xec,0x30,0x04,0x00,0x00,0x48,0x8b,0xda};
bool read(uintptr_t at,void* out,size_t size){SIZE_T got=0;return at>=0x10000&&ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<const void*>(at),out,size,&got)&&got==size;}
void note(Json value)noexcept{try{std::lock_guard<std::mutex> lock(queueMutex);if(pending.size()<16)pending.push_back(std::move(value));}catch(...){}}
bool replace(void* expected,void* wanted){
    auto address=reinterpret_cast<PVOID volatile*>(base+vtableRva+slot);DWORD old=0,unused=0;
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
std::string smallText(uintptr_t at){
    std::array<unsigned char,16> bytes{};if(!read(at,bytes.data(),bytes.size()))return {};
    if(bytes[15]&128){uintptr_t data=0;unsigned size=0;memcpy(&data,bytes.data(),8);memcpy(&size,bytes.data()+8,4);if(size>128)return {};std::string result(size,'\0');return !size||read(data,result.data(),size)?result:std::string();}
    return bytes[15]<=15?std::string(reinterpret_cast<const char*>(bytes.data()),15-bytes[15]):std::string();
}
Json snapshot(uintptr_t at,unsigned depth=0){
    if(!at||depth>4)return nullptr;
    const auto kind=peek<unsigned>(at+0x10);
    if(kind==1)return Json(peek<unsigned char>(at+0x18)!=0);
    if(kind==2)return Json(peek<double>(at+0x18));
    if(kind==3)return Json(smallText(peek<uintptr_t>(at+0x20)));
    if(kind==4){
        const auto begin=peek<uintptr_t>(at+0x18),end=peek<uintptr_t>(at+0x20);
        if(begin>end||(end-begin)%8||end-begin>512*8)return {{"badArray",header(at)}};
        Json items=Json::array();const auto count=(std::min)(size_t((end-begin)/8),depth?size_t(12):size_t(2));
        for(size_t i=0;i<count;++i)items.push_back(snapshot(peek<uintptr_t>(begin+i*8),depth+1));
        return {{"count",(end-begin)/8},{"items",items}};
    }
    if(kind==5){
        const auto buckets=peek<uintptr_t>(at+0x20);const auto count=peek<unsigned>(at+0x28);
        if(!count||count>512)return {{"badMap",header(at)}};
        Json fields=Json::object();std::set<uintptr_t> visited;
        for(unsigned i=0;i<count;++i){auto node=peek<uintptr_t>(buckets+i*8);while(node&&node!=uintptr_t(-1)&&visited.insert(node).second&&visited.size()<256){
            const auto name=smallText(peek<uintptr_t>(node+8));const auto value=peek<uintptr_t>(node+0x10);
            if(depth>1||name=="FirstName"||name=="LastName"||name=="RecordId"||name=="PercentageScouted"||name=="Scouted"||name=="ScoutingAttributes")fields[name]=snapshot(value,depth+1);
            node=peek<uintptr_t>(node+0x18);
        }}return fields;
    }
    return {{"kind",kind},{"header",header(at)}};
}
struct CallGuard{CallGuard(){++inflight;}~CallGuard(){--inflight;}};
void* __fastcall getterHook(void* object,void** out){
    CallGuard guard;
    auto result=original(object,out);
    const auto call=++calls;
    if(!disabled){
        const auto began=GetTickCount64();uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        try{
            UiResponse view(read);
            auto stats=convertRecruitingResponse(view,value,
                [&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);},
                [&](uintptr_t at,const char* key,bool flag){reinterpret_cast<void(__fastcall*)(void*,const char*,bool)>(base+0x2bf6720)(reinterpret_cast<void*>(at),key,flag);});
            if(call<=10||stats.unsupported)note({{"event","grades_applied"},{"call",call},{"recruits",stats.recruits},{"attributes",stats.attributes},{"revealed",stats.revealed},{"ranges",stats.ranges},{"unknown",stats.unknown},{"unsupported",stats.unsupported},{"ms",GetTickCount64()-began}});
        }catch(const std::exception& error){note({{"event","conversion_failed"},{"reason",error.what()}});}
    }
    if(!disabled&&call<=5){
        uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        note({{"event","post_conversion_response"},{"call",call},{"resultEqualsOut",result==out},{"root",header(value)},{"snapshot",snapshot(value)}});
    }
    return result;
}
DWORD stop(){
    disabled=true;
    if(installed){if(!replace(reinterpret_cast<void*>(getterHook),reinterpret_cast<void*>(original)))return 2;installed=false;}
    const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);
    return inflight?3:0;
}
DWORD WINAPI worker(void*){
    wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto folder=std::filesystem::path(path).parent_path();base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
    auto flush=[&](){std::deque<Json> items;{std::lock_guard<std::mutex> lock(queueMutex);items.swap(pending);}if(!items.empty()){std::ofstream out(folder/L"recruiting-fog.jsonl",std::ios::app);for(const auto& j:items)out<<j.dump(-1,' ',false,Json::error_handler_t::replace)<<'\n';}};
    try{
        std::array<unsigned char,32> actual{};uintptr_t current=0;
        if(!read(base+getterRva,actual.data(),actual.size())||actual!=prefix)throw std::runtime_error("Unsupported recruiting getter fingerprint");
        for(const auto& gate:recruitingUiGates){if(!read(base+gate.rva,actual.data(),actual.size())||actual!=gate.bytes)throw std::runtime_error("Unsupported UI-value setter fingerprint");}
        if(!read(base+vtableRva+slot,&current,8)||current!=base+getterRva)throw std::runtime_error("Recruiting getter already owned; no hook installed");
        HMODULE pinned=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pinned))throw std::runtime_error("Cannot pin recruiting runtime");
        original=reinterpret_cast<Getter>(current);
        if(!replace(reinterpret_cast<void*>(original),reinterpret_cast<void*>(getterHook)))throw std::runtime_error("Recruiting getter ownership changed");installed=true;
        note({{"event","active"},{"mode","letter grades and ranges"},{"scope","recruiting UI response only"}});
        while(!disabled){flush();Sleep(200);}flush();
    }catch(const std::exception& error){stop();note({{"event","failed"},{"reason",error.what()}});flush();}
    return 0;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return recruitingfog::runtime::stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){recruitingfog::runtime::self=module;DisableThreadLibraryCalls(module);auto thread=CreateThread(nullptr,0,recruitingfog::runtime::worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}

