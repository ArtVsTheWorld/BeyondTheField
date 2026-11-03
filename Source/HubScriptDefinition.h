#pragma once
#include "HubNewsLifecycle.h"
#include <array>
#include <algorithm>
#include <optional>
namespace social::embedded::lifecycle {
inline constexpr uintptr_t functionVtable=0xbc42fe8;
inline constexpr size_t definitionField=0x58,definitionHeader=0x30;
template<class T>T field(const unsigned char* bytes,size_t at){T result{};memcpy(&result,bytes+at,sizeof(T));return result;}
inline bool headerMatches(const Program& program,const std::array<unsigned char,definitionHeader>& bytes){
    return field<unsigned>(bytes.data(),8)==program.argc&&field<unsigned short>(bytes.data(),12)==program.registers&&field<unsigned short>(bytes.data(),14)==program.flags&&field<unsigned>(bytes.data(),24)==program.original.size()&&field<uintptr_t>(bytes.data(),0)>=0x10000&&field<uintptr_t>(bytes.data(),16)>=0x10000&&field<unsigned>(bytes.data(),32)>0&&field<unsigned>(bytes.data(),32)<4096&&field<uintptr_t>(bytes.data(),40)>=0x10000;
}
inline std::optional<std::vector<unsigned char>> clone(const Program& program,const std::array<unsigned char,definitionHeader>& header){
    if(!headerMatches(program,header)||program.body.empty()||program.body.size()>4096-definitionHeader)return {};
    std::vector<unsigned char> bytes(header.begin(),header.end());bytes.insert(bytes.end(),program.body.begin(),program.body.end());const auto size=static_cast<unsigned>(program.body.size());memcpy(bytes.data()+24,&size,4);return bytes;
}
template<class Read>bool ownerMatches(uintptr_t owner,uintptr_t image,uintptr_t definition,Read read){
    std::array<unsigned char,0x60> bytes{};return owner>=0x10000&&owner%8==0&&read(owner,bytes.data(),bytes.size())&&field<uintptr_t>(bytes.data(),0)==image+functionVtable&&bytes[11]==0x46&&field<uintptr_t>(bytes.data(),definitionField)==definition;
}
}
