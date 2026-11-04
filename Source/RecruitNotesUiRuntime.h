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
inline uint64_t sourceBodyHash(const Program& p,const std::array<unsigned char,48>& h,const std::vector<unsigned char>& original,uintptr_t asset){
    if(p.nestedDefinitions.empty())return bodyHash(original);
    auto normalized=original;
    for(const auto& nested:p.nestedDefinitions){
        if(nested.offset+48>original.size())throw std::runtime_error("Nested player UI definition exceeds its method");
        const auto at=nested.offset;const auto name=field<uintptr_t>(original.data(),at),params=field<uintptr_t>(original.data(),at+16);
        const auto poolCount=field<unsigned>(original.data(),at+32);const auto pool=field<uintptr_t>(original.data(),at+40);
        if((name!=nested.name&&(!asset||name!=asset+nested.name))||(params!=nested.params&&(!asset||params!=asset+nested.params)))throw std::runtime_error("Nested player UI pointer relocation is unsupported");
        if(!((poolCount==0x98765432u&&pool==0x12345678u)||(poolCount==field<unsigned>(h.data(),32)&&pool==field<uintptr_t>(h.data(),40))))throw std::runtime_error("Nested player UI pool differs from its enclosing class");
        const unsigned sourceCount=0x98765432u;const uintptr_t sourcePool=0x12345678u;
        memcpy(normalized.data()+at,&nested.name,8);memcpy(normalized.data()+at+16,&nested.params,8);
        memcpy(normalized.data()+at+32,&sourceCount,4);memcpy(normalized.data()+at+40,&sourcePool,8);
    }
    return bodyHash(normalized);
}
inline bool headerMatches(const Program& p,const std::array<unsigned char,48>& h){return field<unsigned>(h.data(),8)==p.argc&&field<unsigned short>(h.data(),12)==p.registers&&field<unsigned short>(h.data(),14)==p.flags&&field<unsigned>(h.data(),24)==p.size&&field<unsigned>(h.data(),32)>0&&field<unsigned>(h.data(),32)<16384&&field<uintptr_t>(h.data(),40)>=0x10000;}
inline std::vector<unsigned char> makeDefinition(const Program& p,const std::array<unsigned char,48>& h,const std::vector<unsigned char>& original,uintptr_t asset=0){
    if(!headerMatches(p,h)||original.size()!=p.size||sourceBodyHash(p,h,original,asset)!=p.hash||p.newRegisters>64||p.newRegisters<p.registers||p.code.empty()||p.code.size()>32768||p.copyBytes>original.size()||p.copyAt+p.copyBytes>p.code.size())throw std::runtime_error("Native UI method unsupported at offset "+std::to_string(p.offset)+" (body hash "+std::to_string(bodyHash(original))+")");
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
    std::atomic<size_t> retainedBytes{0};
    std::atomic<unsigned> retainedDefinitions{0},retainedBanks{0};
public:
    explicit Runtime(std::vector<Program> selected=programs()):code(std::move(selected)){}
    bool prepared=false;
    void prepare(){prepared=true;}
    bool acceptsFrame(const unsigned char* h,bool fixedFrame=false)const{
        if(!prepared)return false;
        for(const auto& p:code)if((!fixedFrame||p.newRegisters==p.registers)&&field<unsigned>(h,24)==p.size&&field<unsigned>(h,8)==p.argc&&field<unsigned short>(h,12)==p.registers&&field<unsigned short>(h,14)==p.flags)return true;
        return false;
    }
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
            const auto bytes=makeDefinition(p,h,body,asset);std::vector<unsigned char> pool(field<unsigned>(h.data(),32)*8);
            if(!read(field<uintptr_t>(h.data(),40),pool.data(),pool.size()))throw std::runtime_error("Notes native constant pool is no longer readable");
            bank.headers.push_back(h);verified.push_back(bytes);
        }
        // Gate the entire set before allocating or changing the first receiver.
        for(size_t i=0;i<code.size();++i){const auto& bytes=verified[i];
            const auto allocationBytes=(bytes.size()+4095)&~size_t(4095);
            auto memory=VirtualAlloc(nullptr,allocationBytes,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!memory)throw std::runtime_error("Cannot retain a Notes script definition");
            retainedBytes.fetch_add(allocationBytes,std::memory_order_relaxed);retainedDefinitions.fetch_add(1,std::memory_order_relaxed);
            memcpy(memory,bytes.data(),bytes.size());bank.definitions.push_back({asset+code[i].offset,reinterpret_cast<uintptr_t>(memory)});
        }
        // Script owners are released on leaving Recruiting. Never retain their
        // addresses: attach only to the live receiver at native invocation setup,
        // before flags, argument registers, body length or body are consumed.
        banks.push_back(std::move(bank));retainedBanks.fetch_add(1,std::memory_order_relaxed);const auto result=redirectDefinition(location,banks.back().definitions);if(result>=0)++attached;return result;
    }
    unsigned ownerCount()const{return attached.load();}
    size_t methodCount()const{return code.size();}
    size_t retainedByteCount()const{return retainedBytes.load(std::memory_order_relaxed);}
    unsigned retainedDefinitionCount()const{return retainedDefinitions.load(std::memory_order_relaxed);}
    unsigned retainedBankCount()const{return retainedBanks.load(std::memory_order_relaxed);}
};
}
