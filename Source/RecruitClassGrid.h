#pragma once
#include <string>
#include <cstring>
#include <cstddef>
#include <array>
#include <cstdint>
namespace recruitingfog {
struct ClassKeySink {void** vtable;std::string value;};
inline void __fastcall classKeyString(ClassKeySink* sink,const char* value){if(value&&strlen(value)<32)sink->value=value;}
inline void* classKeyTable[]={nullptr,nullptr,nullptr,nullptr,nullptr,reinterpret_cast<void*>(classKeyString)};
struct ClassKeyBlob {unsigned size,pad;const unsigned char* bytes;bool owned;};
static_assert(offsetof(ClassKeyBlob,bytes)==8&&offsetof(ClassKeyBlob,owned)==16);
inline bool juniorCollegeLabel(const char* text){
    if(!text||text[0]!='J'||text[1]!='C')return false;
    return !strcmp(text,"JC (SO)")||!strcmp(text,"JC (JR)")||!strcmp(text,"JC (SR)")||!strcmp(text,"JC(SO)")||!strcmp(text,"JC(JR)")||!strcmp(text,"JC(SR)");
}
inline bool classGridColumns(void* columns){
    auto** table=*reinterpret_cast<void***>(columns);const auto count=reinterpret_cast<int(__fastcall*)(void*)>(table[1])(columns);
    if(count<0||count>90)return false;
    for(int i=0;i<count;++i)if(reinterpret_cast<int(__fastcall*)(void*,int)>(table[2])(columns,i)==15)return true;
    return false;
}
// A synchronous, per-call adapter. Only the displayed JC Class cell is eligible;
// every other typed callback and all original getter arguments pass through.
struct ClassGridSink {
    void** vtable;void* target;void* source;int form,row;
    std::string (*label)(void*,int,int,const char*);
    struct Pending{unsigned row=0;std::string value;};
    std::array<Pending,4> pending{};unsigned count=0;
};
template<class T>inline void classGridPut(ClassGridSink* sink,unsigned row,const char* key,T value,unsigned slot){
    reinterpret_cast<void(__fastcall*)(void*,unsigned,const char*,T)>((*reinterpret_cast<void***>(sink->target))[slot])(sink->target,row,key,value);
}
inline void __fastcall classGridReserve(ClassGridSink* sink,unsigned n){reinterpret_cast<void(__fastcall*)(void*,unsigned)>((*reinterpret_cast<void***>(sink->target))[1])(sink->target,n);}
inline void __fastcall classGridBool(ClassGridSink* s,unsigned r,const char* k,bool v){classGridPut(s,r,k,v,3);}
inline void __fastcall classGridInt(ClassGridSink* s,unsigned r,const char* k,int v){classGridPut(s,r,k,v,4);}
inline void __fastcall classGridFloat(ClassGridSink* s,unsigned r,const char* k,float v){classGridPut(s,r,k,v,5);}
inline void __fastcall classGridString(ClassGridSink* s,unsigned r,const char* k,const char* v){
    if(k&&strcmp(k,"display")==0&&juniorCollegeLabel(v)&&s->count<s->pending.size()){
        // Defer the one Class field until the native row getter returns. Never
        // reenter its data source from inside a typed collector callback.
        s->pending[s->count++]={r,v};return;
    }
    classGridPut(s,r,k,v,6);
}
inline void classGridFlush(ClassGridSink* sink){
    for(unsigned i=0;i<sink->count;++i){const auto& item=sink->pending[i];std::string label;
        try{label=sink->label(sink->source,sink->form,sink->row,item.value.c_str());}catch(...){}
        classGridPut(sink,item.row,"display",label.empty()?item.value.c_str():label.c_str(),6);
    }sink->count=0;
}
inline void* classGridTable[]={nullptr,reinterpret_cast<void*>(classGridReserve),nullptr,reinterpret_cast<void*>(classGridBool),reinterpret_cast<void*>(classGridInt),reinterpret_cast<void*>(classGridFloat),reinterpret_cast<void*>(classGridString)};
}
