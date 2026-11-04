#pragma once
#include "RecruitNotesUiPrograms.h"
#include <array>
#include <atomic>
#include <mutex>
#include <fstream>
#include <set>
#include <stdexcept>

namespace recruitingfog::notesui {
inline uint64_t bodyHash(const std::vector<unsigned char>& bytes){uint64_t hash=14695981039346656037ull;for(auto b:bytes){hash^=b;hash*=1099511628211ull;}return hash;}
template<class T>T field(const unsigned char* bytes,size_t at){T value{};memcpy(&value,bytes+at,sizeof(value));return value;}
inline bool headerMatches(const Program& p,const std::array<unsigned char,48>& h){return field<unsigned>(h.data(),8)==p.argc&&field<unsigned short>(h.data(),12)==p.registers&&field<unsigned short>(h.data(),14)==p.flags&&field<unsigned>(h.data(),24)==p.size&&field<unsigned>(h.data(),32)>0&&field<unsigned>(h.data(),32)<16384&&field<uintptr_t>(h.data(),40)>=0x10000;}
inline std::vector<unsigned char> makeDefinition(const Program& p,const std::array<unsigned char,48>& h,const std::vector<unsigned char>& original){
    if(!headerMatches(p,h)||original.size()!=p.size||bodyHash(original)!=p.hash||p.newRegisters>64||p.newRegisters<p.registers||p.code.empty()||p.code.size()>32768||p.copyBytes>original.size()||p.copyAt+p.copyBytes>p.code.size())throw std::runtime_error("Notes method definition is unsupported");
    std::vector<unsigned char> result(h.begin(),h.end());result.insert(result.end(),p.code.begin(),p.code.end());
    if(p.copyBytes)memcpy(result.data()+48+p.copyAt,original.data(),p.copyBytes);
    const auto registers=static_cast<unsigned short>(p.newRegisters);const auto size=static_cast<unsigned>(p.code.size());memcpy(result.data()+12,&registers,2);memcpy(result.data()+24,&size,4);return result;
}
struct OwnedDefinition {uintptr_t original=0,owned=0;};
inline int redirectDefinition(PVOID volatile* location,const std::vector<OwnedDefinition>& definitions){
    const auto current=reinterpret_cast<uintptr_t>(*location);
    for(size_t i=0;i<definitions.size();++i){const auto& d=definitions[i];if(current!=d.original)continue;
        return InterlockedCompareExchangePointer(location,reinterpret_cast<void*>(d.owned),reinterpret_cast<void*>(d.original))==reinterpret_cast<void*>(d.original)?static_cast<int>(i):-1;
    }
    return -1;
}
class Runtime {
    struct Bank {uintptr_t asset=0;std::vector<OwnedDefinition> definitions;std::vector<std::array<unsigned char,48>> headers;};
    std::vector<Program> code;std::vector<Bank> banks;std::mutex bankMutex;
    std::atomic<unsigned> attached{0};
public:
    explicit Runtime(std::vector<Program> selected=programs()):code(std::move(selected)){}
    bool prepared=false;
    void prepare(){prepared=true;}
    template<class Read>int beforeInvoke(void* object,Read read,bool fixedFrame=false){
        if(!prepared)return -1;
        // The native invocation guarantees a live ScriptFunction2 receiver and
        // definition. Most calls leave after these small in-process comparisons;
        // no process scan, allocation or ReadProcessMemory is used on that path.
        auto location=reinterpret_cast<PVOID volatile*>(static_cast<unsigned char*>(object)+0x58);
        const auto definition=reinterpret_cast<uintptr_t>(*location);
        std::array<unsigned char,48> current{};memcpy(current.data(),reinterpret_cast<const void*>(definition),current.size());
        size_t index=0;for(;index<code.size();++index)if((!fixedFrame||code[index].newRegisters==code[index].registers)&&headerMatches(code[index],current))break;
        if(index==code.size()||definition<code[index].offset+0x10000)return -1;
        const auto asset=definition-code[index].offset;
        std::lock_guard<std::mutex> lock(bankMutex);
        for(const auto& bank:banks)if(bank.asset==asset&&bank.headers[index]==current){
            const auto result=redirectDefinition(location,bank.definitions);if(result>=0)++attached;return result;
        }
        char magic[14]{};if(!read(asset,magic,14)||memcmp(magic,"Apt Data:1:",11))return -1;
        if(banks.size()>=512)throw std::runtime_error("Notes reached its bounded asset-generation limit");
        Bank bank;bank.asset=asset;
        std::vector<std::vector<unsigned char>> verified;
        for(const auto& p:code){
            const auto original=asset+p.offset;std::array<unsigned char,48> h{};std::vector<unsigned char> body(p.size);
            if(!read(original,h.data(),48)||!read(original+48,body.data(),body.size()))throw std::runtime_error("Notes source definition is no longer readable");
            const auto bytes=makeDefinition(p,h,body);std::vector<unsigned char> pool(field<unsigned>(h.data(),32)*8);
            if(!read(field<uintptr_t>(h.data(),40),pool.data(),pool.size()))throw std::runtime_error("Notes native constant pool is no longer readable");
            bank.headers.push_back(h);verified.push_back(bytes);
        }
        // Gate the entire set before allocating or changing the first receiver.
        for(size_t i=0;i<code.size();++i){const auto& bytes=verified[i];
            auto memory=VirtualAlloc(nullptr,(bytes.size()+4095)&~size_t(4095),MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!memory)throw std::runtime_error("Cannot retain a Notes script definition");
            memcpy(memory,bytes.data(),bytes.size());bank.definitions.push_back({asset+code[i].offset,reinterpret_cast<uintptr_t>(memory)});
        }
        // Script owners are released on leaving Recruiting. Never retain their
        // addresses: attach only to the live receiver at native invocation setup,
        // before flags, argument registers, body length or body are consumed.
        banks.push_back(std::move(bank));const auto result=redirectDefinition(location,banks.back().definitions);if(result>=0)++attached;return result;
    }
    unsigned ownerCount()const{return attached.load();}
    size_t methodCount()const{return code.size();}
};
}
