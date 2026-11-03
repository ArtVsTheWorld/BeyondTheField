#pragma once
#include "NewsScroll.h"
#include <cstdint>
#include <cstring>
#include <stdexcept>
namespace social {
inline constexpr char reverseTypeName[]="SOCIAL_TYPE_PREV";
inline constexpr char scopePanelName[]="CM_NEWSSUB";
inline constexpr char scopeFilterName[]="SOCIAL_TYPE";
inline constexpr char scopeRootName[]="madden";
inline constexpr char scopeAdaptersName[]="Adapters";
inline constexpr char scopeGetAdapterName[]="GetPanelMenuAdapter";
inline constexpr char scopeSetFilterName[]="SetFilterChanged";
inline constexpr char embeddedTypeKey[]="CODE_R3";
inline auto embeddedNewsScroll(){
    auto b=newsScrollSmooth;size_t pos=0x2f4;
    auto byte=[&](unsigned char v){b.at(pos++)=v;};
    auto align=[&](){while(pos%8)byte(0);};
    auto word=[&](uint64_t v,size_t n){for(size_t i=0;i<n;++i)byte(static_cast<unsigned char>(v>>(8*i)));};
    auto literal=[&](const char* text){byte(0xa1);align();word(reinterpret_cast<uintptr_t>(text),8);};
    auto jump=[&](unsigned char op,size_t to){byte(op);align();const auto from=pos+4;word(static_cast<uint32_t>(static_cast<int64_t>(to)-static_cast<int64_t>(from)),4);};
    auto branch=[&](size_t displacement,size_t target){const auto relative=static_cast<int32_t>(target-(displacement+4));memcpy(b.data()+displacement,&relative,4);};
    // Dictionary 19/20/21 is the vanilla cafe.enum.Input namespace. Resolve R3
    // through the runtime enum, never an assumed platform-specific number.
    branch(0xc8,0x3ec);branch(0xd8,0x3ec);branch(0x100,0x2f4);
    byte(0xb9);byte(0);byte(0xad);byte(3);byte(19);byte(20);byte(21);literal(embeddedTypeKey);byte(0x4e);byte(0x66);
    const auto conditional=pos;jump(0x9d,0);jump(0x99,0x3ec);const auto callback=pos;
    byte(0x59);literal(scopeFilterName);literal(scopePanelName);byte(0xb5);byte(3);
    byte(0x59);literal(scopeRootName);byte(0x1c);literal(scopeAdaptersName);byte(0x4e);
    literal(scopeGetAdapterName);byte(0x52);literal(scopeSetFilterName);byte(0x52);byte(0x17);byte(0x73);byte(0x3e);
    if(pos>0x395)throw std::runtime_error("Embedded type input exceeds its reserved span");
    const auto end=pos;pos=conditional;jump(0x9d,callback);pos=end;while(pos<0x395)byte(0);
    return b;
}
inline auto scopedNewsScroll(){
    auto b=newsScrollSmooth;size_t pos=0;
    auto byte=[&](unsigned char v){b.at(pos++)=v;};
    auto align=[&](){while(pos%8)byte(0);};
    auto word=[&](uint64_t v,size_t n){for(size_t i=0;i<n;++i)byte(static_cast<unsigned char>(v>>(8*i)));};
    auto literal=[&](const char* text){byte(0xa1);align();word(reinterpret_cast<uintptr_t>(text),8);};
    auto jump=[&](unsigned char op,size_t to){byte(op);align();const auto from=pos+4;word(static_cast<uint32_t>(static_cast<int64_t>(to)-static_cast<int64_t>(from)),4);};
    // Retain the game's genuine LB/RB enum aliases and their 16-byte cases.
    // Both branch to a shared callback tail; its native key chooses direction.
    const int32_t reverseDispatch=0x2f4-(0xd8+4);memcpy(b.data()+0xd8,&reverseDispatch,4);
    // Call the game's existing adapter binding; this is native APT input, not
    // an external controller hook. The DLL handles the category callback.
    pos=0x2f4;
    byte(0x59);byte(0xb9);byte(0);byte(0xad);byte(4);byte(53);byte(20);byte(21);byte(61);byte(0x66);
    const auto reverseJump=pos;jump(0x9d,0);literal(scopeFilterName);
    const auto sharedJump=pos;jump(0x99,0);const auto reverse=pos;literal(reverseTypeName);const auto shared=pos;
    literal(scopePanelName);byte(0xb5);byte(3);
    byte(0x59);literal(scopeRootName);byte(0x1c);literal(scopeAdaptersName);byte(0x4e);
    literal(scopeGetAdapterName);byte(0x52);literal(scopeSetFilterName);byte(0x52);byte(0x17);
    byte(0x73);byte(0x3e); // Return immediately; a refresh can replace the grid.
    if(pos>0x395)throw std::runtime_error("Scope adapter call exceeds its reserved span");
    const auto end=pos;pos=reverseJump;jump(0x9d,reverse);pos=sharedJump;jump(0x99,shared);pos=end;
    while(pos<0x395)byte(0);
    return b;
}
}
