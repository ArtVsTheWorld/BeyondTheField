#pragma once
#include "NewsDropdowns.h"
#include <stdexcept>
namespace social::embedded {
inline void scopeTemplateFlow(std::vector<social::dropdown::Patch>& patches){
    auto& code=patches.at(0).changed;
    constexpr size_t first=0xcd,last=first+41,vertical=0x118;
    const unsigned char layoutGate[]={0xb9,5,0xa2,60,0xb5,80,0x4f};
    const unsigned char inputGate[]={0x74,0x5a,0xb9,4,0xb2,73};
    if(code.size()!=726||memcmp(code.data()+first,layoutGate,sizeof(layoutGate))||memcmp(code.data()+vertical,inputGate,sizeof(inputGate)))throw std::runtime_error("Unknown News instance layout setup");
    size_t position=first;
    auto byte=[&](unsigned char value){if(position>=last)throw std::runtime_error("News instance layout exceeds its reserved span");code[position++]=value;};
    auto literal=[&](const char* value){byte(0xa1);while(position%8)byte(0);const auto pointer=reinterpret_cast<uintptr_t>(value);for(size_t i=0;i<8;++i)byte(static_cast<unsigned char>(pointer>>(8*i)));};
    // Verified native Direction bit flags: RIGHT=2, DOWN=8. Configure only
    // News' own layout object, never the shared grid constructor or setter.
    for(const auto& field:std::vector<std::pair<const char*,unsigned char>>{{"FillDirection",static_cast<unsigned char>(2)},{"ExpandDirection",static_cast<unsigned char>(8)}}){byte(0xb9);byte(5);literal(field.first);byte(0xb5);byte(field.second);byte(0x4f);}
    byte(0xb9);byte(5);byte(0xa2);byte(60);byte(0xb5);byte(80);byte(0x4f);
    if((last-position)%2)throw std::runtime_error("News instance layout padding is not stack neutral");
    while(position<last){byte(0x76);byte(0x17);}
    code[vertical]=0x73;
}
}
