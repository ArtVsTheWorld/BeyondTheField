#pragma once
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include "RecruitingGradePolicy.h"

namespace recruitingfog::presentation {
// Football SystemMuse's TextVariable stores rendered text separately from
// its child expression. Never change the query/evaluator's numeric value.
constexpr uintptr_t textTable=0xbc82c08,queryTable=0xbc82ae8;
constexpr uintptr_t formatSlot=0x40,formatRva=0x7d79160;
constexpr uint32_t fourcc(const char* s){return (uint32_t(uint8_t(s[0]))<<24)|(uint32_t(uint8_t(s[1]))<<16)|(uint32_t(uint8_t(s[2]))<<8)|uint8_t(s[3]);}
// Exact player-rating columns found in the installed broadcast definitions.
// AGLP only: statistical QB rating and every team/stat table are excluded.
inline constexpr std::array<uint32_t,31> ratingColumns={
    fourcc("RVOP"),fourcc("PHTP"),fourcc("AHTP"),fourcc("DPSP"),
    fourcc("TKBP"),fourcc("VCBP"),fourcc("ICLP"),fourcc("CSLP"),
    fourcc("ALPP"),fourcc("IGAP"),fourcc("RTSP"),fourcc("HTCP"),
    fourcc("KBRP"),fourcc("MATP"),fourcc("RWAP"),fourcc("CCAP"),
    fourcc("CMLP"),fourcc("CZLP"),fourcc("EPLP"),fourcc("GSBP"),
    fourcc("mPLP"),fourcc("SMFP"),fourcc("RPLP"),fourcc("KATP"),
    fourcc("THLP"),fourcc("SATP"),fourcc("DATP"),fourcc("RPKP"),
    fourcc("CAKP"),fourcc("KSBP"),fourcc("PUTP")};
struct Value{uint64_t payload=0;uint32_t kind=7,reserved=0;};
static_assert(sizeof(Value)==16);
inline char numericGrade(const Value& value){
    double number=-1;
    if(value.kind==0)number=static_cast<uint32_t>(value.payload);
    else if(value.kind==1){int32_t integer=0;memcpy(&integer,&value.payload,4);number=integer;}
    else if(value.kind==2){float real=0;memcpy(&real,&value.payload,4);number=real;}
    else return 0; // Unknown, string, boolean, pointer and other kinds stay native.
    return std::isfinite(number)&&number>=0&&number<=100&&number==std::floor(number)?grade(static_cast<int>(number)):0;
}
template<class Read> char select(uintptr_t self,const Value* input,uintptr_t base,Read read,uint32_t* observedColumn=nullptr){
    if(!input)return 0;
    const auto label=numericGrade(*input);if(!label)return 0;
    uintptr_t table=0,child=0,descriptor=0;uint32_t format=~0u;
    if(!read(self,&table,8)||table!=base+textTable||
       !read(self+0x38,&format,4)||format!=0||
       !read(self+0x18,&child,8)||!child||
       !read(child,&table,8)||table!=base+queryTable||
       !read(child+0x18,&descriptor,8)||!descriptor)return 0;
    std::array<uint32_t,2> field{};
    if(!read(descriptor+8,field.data(),sizeof(field))||field[0]!=fourcc("AGLP"))return 0;
    for(const auto column:ratingColumns)if(field[1]==column){if(observedColumn)*observedColumn=column;return label;}
    return 0;
}
}
