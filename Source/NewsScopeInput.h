#pragma once
#include "NewsScroll.h"
#include <cstdint>
#include <stdexcept>
namespace social {
inline constexpr char scopeInputName[]="CODE_L2";
inline constexpr char scopePanelName[]="CM_NEWSSUB";
inline constexpr char scopeFilterName[]="SOCIAL_SCOPE";
inline constexpr char scopeRootName[]="madden";
inline constexpr char scopeAdaptersName[]="Adapters";
inline constexpr char scopeGetAdapterName[]="GetPanelMenuAdapter";
inline constexpr char scopeSetFilterName[]="SetFilterChanged";
inline auto scopedNewsScroll(){
    auto b=newsScrollSmooth;size_t pos=0;
    auto byte=[&](unsigned char v){b.at(pos++)=v;};
    auto align=[&](){while(pos%8)byte(0);};
    auto word=[&](uint64_t v,size_t n){for(size_t i=0;i<n;++i)byte(static_cast<unsigned char>(v>>(8*i)));};
    auto literal=[&](const char* text){byte(0xa1);align();word(reinterpret_cast<uintptr_t>(text),8);};
    auto jump=[&](unsigned char op,size_t to){byte(op);align();const auto from=pos+4;word(static_cast<uint32_t>(static_cast<int64_t>(to)-static_cast<int64_t>(from)),4);};
    // Replace only the two unused bumper dispatch cases with native LT. RT is
    // still handled by News' genuine FilterGeneric week dropdown first.
    pos=0xbc;byte(0xb9);byte(0);byte(0xad);byte(3);byte(19);byte(20);byte(21);
    literal(scopeInputName);byte(0x4e);byte(0x66);jump(0x9d,0x2f4);
    if(pos!=0xdc)throw std::runtime_error("Scope input dispatch exceeds its reserved span");
    // Call the game's existing adapter binding; this is native APT input, not
    // an external controller hook. The DLL handles the scoped filter callback.
    pos=0x2f4;
    byte(0x59);literal(scopeFilterName);literal(scopePanelName);byte(0xb5);byte(3);
    byte(0x59);literal(scopeRootName);byte(0x1c);literal(scopeAdaptersName);byte(0x4e);
    literal(scopeGetAdapterName);byte(0x52);literal(scopeSetFilterName);byte(0x52);byte(0x17);
    byte(0x73);byte(0x3e); // Return immediately; a refresh can replace the grid.
    if(pos>0x395)throw std::runtime_error("Scope adapter call exceeds its reserved span");
    while(pos<0x395)byte(0);
    return b;
}
}
