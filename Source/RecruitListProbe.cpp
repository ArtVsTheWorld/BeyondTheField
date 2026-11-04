// Development-only, synchronous pass-through spreadsheet observation.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <array>
#include <atomic>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <map>
#include "../Vendor/json.hpp"
#include "RecruitingUiResponse.h"
namespace {
using Json=nlohmann::json;
HMODULE self;uintptr_t base;std::atomic<bool> disabled{false};std::mutex mutex;std::map<int,unsigned> seen;std::filesystem::path logFile;
using Columns=void(__fastcall*)(void*,void*,int);using Rows=void(__fastcall*)(void*,void*,int,int,void*);
Columns originalColumns=nullptr;Rows originalRows=nullptr;
using Entry=void*(__fastcall*)(void*,void**,void*);Entry originalEntry=nullptr;std::atomic<unsigned> entryCalls{0};
void note(const Json& value){std::lock_guard<std::mutex> lock(mutex);std::ofstream out(logFile,std::ios::app);out<<value.dump()<<'\n';}
struct Sink {void** vtable;void* target;Json values=Json::array();};
template<class T>void emit(Sink* sink,unsigned row,const char* key,T value,unsigned slot){
    if(sink->values.size()<400)sink->values.push_back({{"row",row},{"key",key?key:""},{"value",value}});
    reinterpret_cast<void(__fastcall*)(void*,unsigned,const char*,T)>((*reinterpret_cast<void***>(sink->target))[slot])(sink->target,row,key,value);
}
void __fastcall reserve(Sink* sink,unsigned count){reinterpret_cast<void(__fastcall*)(void*,unsigned)>((*reinterpret_cast<void***>(sink->target))[1])(sink->target,count);}
void __fastcall boolean(Sink* s,unsigned r,const char* k,bool v){emit(s,r,k,v,3);}
void __fastcall integer(Sink* s,unsigned r,const char* k,int v){emit(s,r,k,v,4);}
void __fastcall real(Sink* s,unsigned r,const char* k,float v){emit(s,r,k,v,5);}
void __fastcall string(Sink* s,unsigned r,const char* k,const char* v){emit(s,r,k,v,6);}
void* sinkTable[]={nullptr,reinterpret_cast<void*>(reserve),nullptr,reinterpret_cast<void*>(boolean),reinterpret_cast<void*>(integer),reinterpret_cast<void*>(real),reinterpret_cast<void*>(string)};
void __fastcall columnsHook(void* object,void* target,int form){
    if(disabled){originalColumns(object,target,form);return;}
    Sink sink{sinkTable,target};originalColumns(object,&sink,form);note({{"event","columns"},{"form",form},{"values",sink.values}});
}
struct KeySink{void** vt;std::string value;};
void __fastcall keyString(KeySink* sink,const char* text){sink->value=text?text:"";}
void* keyTable[]={nullptr,nullptr,nullptr,nullptr,nullptr,reinterpret_cast<void*>(keyString)};
void __fastcall rowsHook(void* object,void* target,int form,int row,void* columns){
    if(disabled||seen[form]>=160){originalRows(object,target,form,row,columns);return;}++seen[form];
    Sink sink{sinkTable,target};originalRows(object,&sink,form,row,columns);
    auto** vt=*reinterpret_cast<void***>(columns);const auto count=reinterpret_cast<int(__fastcall*)(void*)>(vt[1])(columns);Json ids=Json::array();
    if(count>=0&&count<=90)for(int i=0;i<count;++i)ids.push_back(reinterpret_cast<int(__fastcall*)(void*,int)>(vt[2])(columns,i));
    KeySink key{keyTable,{}};reinterpret_cast<void(__fastcall*)(void*,void*,int,int)>(base+0x7a89180)(object,&key,form,row);const auto& record=key.value;
    std::array<unsigned char,32> bytes{};if(record.size()<bytes.size())memcpy(bytes.data(),record.data(),record.size());
    struct Blob{unsigned size;unsigned pad;const unsigned char* bytes;bool owned;};Blob blob{32,0,bytes.data(),false};
    const auto nativeKey=reinterpret_cast<unsigned(__fastcall*)(void*)>(base+0x376f6d0)(&blob);
    note({{"event","row"},{"record",record},{"nativeKey",nativeKey},{"form",form},{"row",row},{"columns",ids},{"values",sink.values}});
}
bool readUi(uintptr_t address,void* out,size_t n){SIZE_T got=0;return ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(address),out,n,&got)&&got==n;}
template<class View>Json uiJson(View& view,uintptr_t at,unsigned depth=0){
    if(depth>4)return nullptr;const auto kind=view.kind(at);std::string text;double number=0;bool flag=false;
    if(kind==3&&view.string(at,text))return text;if(kind==2&&view.number(at,number))return number;if(kind==1&&view.boolean(at,flag))return flag;
    if(kind==4){std::vector<uintptr_t> values;Json out=Json::array();if(view.array(at,values,128))for(auto child:values)out.push_back(uiJson(view,child,depth+1));return out;}
    if(kind==5){std::map<std::string,uintptr_t> values;Json out=Json::object();if(view.members(at,values))for(auto [key,child]:values)out[key]=uiJson(view,child,depth+1);return out;}return nullptr;
}
void* __fastcall entryHook(void* object,void** out,void* argument){auto result=originalEntry(object,out,argument);if(!disabled&&entryCalls.fetch_add(1)<4&&out&&*out){try{recruitingfog::UiResponse view(readUi);note({{"event","entry"},{"value",uiJson(view,reinterpret_cast<uintptr_t>(*out))}});}catch(...){}}return result;}
bool swap(uintptr_t table,uintptr_t slot,void* from,void* to){auto* p=reinterpret_cast<PVOID volatile*>(base+table+slot);DWORD old=0,unused=0;if(!VirtualProtect(const_cast<PVOID*>(p),8,PAGE_READWRITE,&old))return false;auto* before=InterlockedCompareExchangePointer(p,to,from);VirtualProtect(const_cast<PVOID*>(p),8,old,&unused);return before==from;}
DWORD stop(){disabled=true;if(originalEntry)swap(0xc752560,0x40,reinterpret_cast<void*>(entryHook),reinterpret_cast<void*>(originalEntry));bool okay=true;if(originalColumns)okay=swap(0xbaa78b8,0x70,reinterpret_cast<void*>(columnsHook),reinterpret_cast<void*>(originalColumns))&&okay;if(originalRows)okay=swap(0xbacd668,0x68,reinterpret_cast<void*>(rowsHook),reinterpret_cast<void*>(originalRows))&&okay;return okay?0:2;}
DWORD WINAPI worker(void*){
    wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);logFile=std::filesystem::path(path).parent_path()/L"recruit-list-probe.jsonl";base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
    originalColumns=reinterpret_cast<Columns>(base+0x78ef740);originalRows=reinterpret_cast<Rows>(base+0x7a88cd0);
    constexpr unsigned char columnsPrefix[]={0x48,0x8b,0xc4,0x55,0x48,0x8b,0xec,0x48,0x81,0xec,0x80,0,0,0};
    constexpr unsigned char rowsPrefix[]={0x40,0x53,0x55,0x56,0x41,0x56,0x41,0x57,0x48,0x81,0xec,0x70,0x01,0,0};
    if(memcmp(reinterpret_cast<void*>(base+0x78ef740),columnsPrefix,sizeof(columnsPrefix))||memcmp(reinterpret_cast<void*>(base+0x7a88cd0),rowsPrefix,sizeof(rowsPrefix))||*reinterpret_cast<uintptr_t*>(base+0xbaa78b8+0x70)!=base+0x78ef740||*reinterpret_cast<uintptr_t*>(base+0xbacd668+0x68)!=base+0x7a88cd0){originalColumns=nullptr;originalRows=nullptr;note({{"event","rejected"}});return 1;}
    HMODULE pinned=nullptr;GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pinned);
    if(!swap(0xbaa78b8,0x70,reinterpret_cast<void*>(originalColumns),reinterpret_cast<void*>(columnsHook))||!swap(0xbacd668,0x68,reinterpret_cast<void*>(originalRows),reinterpret_cast<void*>(rowsHook))){stop();return 2;}
    originalEntry=reinterpret_cast<Entry>(base+0xa0e0cc0);
    if(*reinterpret_cast<uintptr_t*>(base+0xc752560+0x40)!=base+0xa0e0cc0||!swap(0xc752560,0x40,reinterpret_cast<void*>(originalEntry),reinterpret_cast<void*>(entryHook))){originalEntry=nullptr;stop();return 3;}
    note({{"event","active"},{"mode","synchronous pass-through; no display edits"}});return 0;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);HANDLE thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}
