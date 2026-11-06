#define NOMINMAX
#include <windows.h>
#include "../Source/RecruitNotesUiRuntime.h"
#include "../Source/DraftOvrUiPrograms.h"
#include <iostream>

// Synthetic method bodies isolate native-frame attachment from game data. The
// UI VM suite separately executes actual custom code and real draft fixtures.
void checkFrames(std::vector<recruitingfog::notesui::Program> programs,bool relocated){
    using namespace recruitingfog::notesui;
    size_t size=0;for(auto& p:programs){if(p.newRegisters!=p.registers)throw std::runtime_error("Draft callback expands an already allocated frame");size=std::max(size,size_t(p.offset+48+p.size));}
    std::vector<unsigned char> image(size+4096);memcpy(image.data(),"Apt Data:1:",11);std::array<uintptr_t,1> pool={0};
    for(auto& p:programs){
        auto* h=image.data()+p.offset;const auto name=reinterpret_cast<uintptr_t>("synthetic draft callback");memcpy(h,&name,8);memcpy(h+8,&p.argc,4);const auto registers=static_cast<unsigned short>(p.registers),flags=static_cast<unsigned short>(p.flags);memcpy(h+12,&registers,2);memcpy(h+14,&flags,2);memcpy(h+24,&p.size,4);const unsigned count=1;const auto address=reinterpret_cast<uintptr_t>(pool.data());memcpy(h+32,&count,4);memcpy(h+40,&address,8);
        std::vector<unsigned char> original(p.size,0);
        for(const auto& n:p.nestedDefinitions){const unsigned sourceCount=0x98765432u;const uintptr_t sourcePool=0x12345678u;memcpy(original.data()+n.offset,&n.name,8);memcpy(original.data()+n.offset+16,&n.params,8);memcpy(original.data()+n.offset+32,&sourceCount,4);memcpy(original.data()+n.offset+40,&sourcePool,8);}
        p.hash=bodyHash(original);
        if(relocated)for(const auto& n:p.nestedDefinitions){const auto liveName=reinterpret_cast<uintptr_t>(image.data())+n.name,liveParams=reinterpret_cast<uintptr_t>(image.data())+n.params;memcpy(original.data()+n.offset,&liveName,8);memcpy(original.data()+n.offset+16,&liveParams,8);memcpy(original.data()+n.offset+32,&count,4);memcpy(original.data()+n.offset+40,&address,8);}
        memcpy(h+48,original.data(),original.size());
        std::array<unsigned char,48> header{};memcpy(header.data(),h,48);
        if(sourceBodyHash(p,header,original,reinterpret_cast<uintptr_t>(image.data()))!=p.hash)throw std::runtime_error("Verified nested relocation changed full-body hash");
        auto changed=original;changed.back()^=1;if(sourceBodyHash(p,header,changed,reinterpret_cast<uintptr_t>(image.data()))==p.hash)throw std::runtime_error("Changed instruction bypassed full-body hash");
        for(const auto& n:p.nestedDefinitions){changed=original;changed[n.offset]^=1;bool rejected=false;try{sourceBodyHash(p,header,changed,reinterpret_cast<uintptr_t>(image.data()));}catch(const std::exception&){rejected=true;}if(!rejected)throw std::runtime_error("Unknown nested name relocation passed");changed=original;changed[n.offset+40]^=1;rejected=false;try{sourceBodyHash(p,header,changed,reinterpret_cast<uintptr_t>(image.data()));}catch(const std::exception&){rejected=true;}if(!rejected)throw std::runtime_error("Unknown nested pool passed");}
    }
    const auto begin=reinterpret_cast<uintptr_t>(image.data()),poolBegin=reinterpret_cast<uintptr_t>(pool.data());
    const auto read=[&](uintptr_t at,void* out,size_t bytes){if((at>=begin&&at+bytes>=at&&at+bytes<=begin+image.size())||(at>=poolBegin&&at+bytes>=at&&at+bytes<=poolBegin+sizeof(pool))){memcpy(out,reinterpret_cast<void*>(at),bytes);return true;}return false;};
    Runtime runtime(programs);runtime.prepare();
    for(const auto& p:programs){alignas(uintptr_t)std::array<unsigned char,0x60> function{};const auto original=begin+p.offset;memcpy(function.data()+0x58,&original,8);if(!runtime.acceptsFrame(image.data()+p.offset,true))throw std::runtime_error("Native draft frame was rejected");const auto changed=runtime.beforeInvoke(function.data(),read,true);if(changed<0)throw std::runtime_error("Draft callback failed fixed-frame attachment");uintptr_t owned=0;memcpy(&owned,function.data()+0x58,8);const auto* header=reinterpret_cast<const unsigned char*>(owned);if(owned==original||field<unsigned short>(header,12)!=p.registers||field<unsigned short>(header,14)!=p.flags||field<unsigned>(header,8)!=p.argc)throw std::runtime_error("Draft callback frame contract changed");}
}
int main(){const auto strategy=recruitingfog::draftovrui::strategyPrograms(),rows=recruitingfog::draftovrui::rowPrograms();for(bool relocated:{false,true}){checkFrames(strategy,relocated);checkFrames(rows,relocated);}std::cout<<"All "<<(strategy.size()+rows.size())<<" minimal Draft OVR callbacks attach with native fixed frames\n";}
