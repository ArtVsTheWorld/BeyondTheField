#pragma once
#include "../Source/DraftResultsWorker.h"
#include <map>

namespace draftworkertests {
inline void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
struct Memory {
    std::map<uintptr_t,unsigned char> bytes;unsigned calls=0;
    template<class T>void put(uintptr_t address,T value){const auto* p=reinterpret_cast<const unsigned char*>(&value);for(size_t i=0;i<sizeof(T);++i)bytes[address+i]=p[i];}
    bool read(uintptr_t address,void* out,size_t size){++calls;auto* p=static_cast<unsigned char*>(out);for(size_t i=0;i<size;++i){const auto found=bytes.find(address+i);if(found==bytes.end())return false;p[i]=found->second;}return true;}
};
inline void run(){
    using namespace recruitingfog::draftresults;
    constexpr uintptr_t image=0x10000000,service=0x20000000,career=0x30000000,ui=0x40000000,owner=0x50000000,database=0x60000000,object=0x70000000,binding=0x71000000,context=0x72000000;
    constexpr uintptr_t year=0x80000000,league=0x80000008,stage=0x80000010,metadata=0x80000018;
    Memory m;auto set=[&](uintptr_t at,uintptr_t value){m.put(at,value);};
    set(image+0xfa519b8,service);set(service,image+0xbaa8998);set(service+0x468,career);set(service+0x470,ui);set(service+0x460,owner);set(service+0x7b1,1);
    set(career,image+0xbce9b08);set(ui,image+0xbd7a538);set(career+0x20,owner);set(career+0x238,database);set(database,image+0xbd0d2d8);
    set(career+0x230,object);set(object,image+0xb4dbb18);set(career+0x240,binding);set(binding,object);set(binding+8,context);set(context,image+0xbd0d378);set(context+0x1a8,database);
    m.put(year,uint32_t(0xabcd0000|2028));m.put(league,uint32_t(123));m.put(stage,uint32_t(1));m.put(metadata,uint64_t(0x90000000));
    const auto read=[&](uintptr_t at,void* out,size_t size){return m.read(at,out,size);};
    const dynasty::live::SessionBinding active{service,career,database};
    Json raw={{"context",context},{"status",{{"league",123},{"season",{{"CurrentSeasonYear",2028}}}}}};
    auto check=[](uintptr_t at,unsigned size,uint64_t expected,uint64_t mask){return Json{{"address",at},{"size",size},{"expected",expected},{"mask",mask}};};
    Json fields=Json::array({Json{{"name","SeasonInfo"},{"checks",Json::array({check(year,4,2028,0xffff),check(metadata,8,0x90000000,UINT64_MAX)})}},Json{{"name","Franchise"},{"checks",Json::array({check(league,4,123,UINT32_MAX)})}},Json{{"name","FranchiseServer_CareerFlow"},{"checks",Json::array({check(stage,4,1,3)})}}});
    const auto proof=parseProof(raw,fields,active);require(proofMatches(proof,image,read),"Ready draft proof rejected the active Dynasty");
    m.put(year,uint32_t(0x12340000|2028));require(proofMatches(proof,image,read),"Unconsumed packed status bits invalidated draft cache");
    m.put(year,uint32_t(0x12340000|2029));require(!proofMatches(proof,image,read),"Same-binding season rollover exposed a stale draft board");m.put(year,uint32_t(2028));
    m.put(stage,uint32_t(3));require(!proofMatches(proof,image,read),"Advancing status exposed a stale draft board");m.put(stage,uint32_t(1));
    m.put(league,uint32_t(456));require(!proofMatches(proof,image,read),"Changed LeagueID exposed another Dynasty's draft board");m.put(league,uint32_t(123));
    m.put(metadata,uint64_t(0x90000100));require(!proofMatches(proof,image,read),"Moved schema/data/offset metadata passed the draft proof");m.put(metadata,uint64_t(0x90000000));
    const auto changing=[&](uintptr_t at,void* out,size_t size){const auto result=m.read(at,out,size);if(at==year)set(binding+8,context+0x1000);return result;};
    require(!proofMatches(proof,image,changing),"Same-binding child context changed during the UI proof");set(binding+8,context);
    m.bytes.erase(image+0xfa519b8);require(!proofMatches(proof,image,read),"Unreadable identity proof was treated as ready");set(image+0xfa519b8,service);
    auto invalid=fields;invalid[0]["checks"][0]["size"]=16;bool rejected=false;try{parseProof(raw,invalid,active);}catch(...){rejected=true;}require(rejected,"Oversized status check escaped its stack-read bound");
    invalid=fields;invalid[1]["name"]="SeasonInfo";rejected=false;try{parseProof(raw,invalid,active);}catch(...){rejected=true;}require(rejected,"Duplicate identity table was accepted");
    invalid=fields;invalid[0]["checks"][0]["mask"]=uint64_t(1)<<40;rejected=false;try{parseProof(raw,invalid,active);}catch(...){rejected=true;}require(rejected,"Packed field mask exceeded its read width");
    Worker worker;const auto before=m.calls;require(!worker.current(image,read)&&m.calls==before,"Missing draft publication performed reads/work in the UI callback");
    unsigned reports=0;worker.tick(image,read,[]{return false;},[&](Json){++reports;});require(m.calls==before&&!reports,"Unconfigured/requestless draft worker started capture work");
}
}
