#pragma once
#include "PlayerRatingGrid.h"
#include <cstring>
namespace recruitingfog::playerfog {
// Native property-map collector, distinct from the row-indexed spreadsheet ABI.
// Forwarding preserves original types and opaque nested values exactly.
struct MapSink{void** vtable;void* target;const char* key;unsigned changed=0;const char* labelKey=nullptr;};
template<class T>inline void mapPut(MapSink* s,const char* key,T value,unsigned slot){reinterpret_cast<void(__fastcall*)(void*,const char*,T)>((*reinterpret_cast<void***>(s->target))[slot])(s->target,key,value);}
inline void __fastcall mapBool(MapSink* s,const char* k,bool v){mapPut(s,k,v,1);}
inline void __fastcall mapInt(MapSink* s,const char* k,int v){
    if(k&&!strcmp(k,s->key)&&v>=0&&v<=100){const auto text=playerDisplay(v);
        // Shared progression models still require their numeric Overall.
        // Supply a separate display field rather than changing that input.
        if(s->labelKey)mapPut(s,k,v,2);mapPut(s,s->labelKey?s->labelKey:k,text.c_str(),4);++s->changed;}
    else mapPut(s,k,v,2);
}
inline void __fastcall mapFloat(MapSink* s,const char* k,float v){mapPut(s,k,v,3);}
inline void __fastcall mapString(MapSink* s,const char* k,const char* v){mapPut(s,k,v,4);}
inline void __fastcall mapUndefined(MapSink* s,const char* k){reinterpret_cast<void(__fastcall*)(void*,const char*)>((*reinterpret_cast<void***>(s->target))[5])(s->target,k);}
inline void __fastcall mapOpaque(MapSink* s,const char* k,void* v){mapPut(s,k,v,6);}
inline void* mapTable[]={nullptr,reinterpret_cast<void*>(mapBool),reinterpret_cast<void*>(mapInt),reinterpret_cast<void*>(mapFloat),reinterpret_cast<void*>(mapString),reinterpret_cast<void*>(mapUndefined),reinterpret_cast<void*>(mapOpaque)};
}
