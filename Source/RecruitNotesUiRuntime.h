#pragma once
#include "RecruitNotesUiPrograms.h"
#include <array>
#include <atomic>
#include <mutex>
#include <fstream>
#include <set>
#include <stdexcept>
#include <string>
#include <map>
#include <memory>

namespace recruitingfog::notesui {
inline uint64_t bodyHash(const std::vector<unsigned char>& bytes){uint64_t hash=14695981039346656037ull;for(auto b:bytes){hash^=b;hash*=1099511628211ull;}return hash;}
template<class T>T field(const unsigned char* bytes,size_t at){T value{};memcpy(&value,bytes+at,sizeof(value));return value;}
inline uint64_t sourceBodyHash(const Program& p,const std::array<unsigned char,48>& h,const std::vector<unsigned char>& original,uintptr_t asset){
    if(p.nestedDefinitions.empty())return bodyHash(original);
    auto normalized=original;
    for(const auto& nested:p.nestedDefinitions){
        if(nested.offset>original.size()||original.size()-nested.offset<48)throw std::runtime_error("Nested player UI definition exceeds its method");
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
    if(!headerMatches(p,h)||original.size()!=p.size||sourceBodyHash(p,h,original,asset)!=p.hash||p.newRegisters>64||p.newRegisters<p.registers||p.code.empty()||p.code.size()>32768||p.copyBytes>original.size()||p.copyAt>p.code.size()||p.copyBytes>p.code.size()-p.copyAt)throw std::runtime_error("Native UI method unsupported at offset "+std::to_string(p.offset)+" (body hash "+std::to_string(bodyHash(original))+")");
    std::vector<unsigned char> result(h.begin(),h.end());result.insert(result.end(),p.code.begin(),p.code.end());
    if(p.copyBytes)memcpy(result.data()+48+p.copyAt,original.data(),p.copyBytes);
    const auto registers=static_cast<unsigned short>(p.newRegisters);const auto size=static_cast<unsigned>(p.code.size());memcpy(result.data()+12,&registers,2);memcpy(result.data()+24,&size,4);return result;
}
struct OwnedDefinition {uintptr_t original=0,owned=0;std::map<unsigned,uintptr_t> variants{};};
inline int redirectDefinition(PVOID volatile* location,const std::vector<OwnedDefinition>& definitions){
    const auto current=reinterpret_cast<uintptr_t>(*location);
    for(size_t i=0;i<definitions.size();++i){const auto& d=definitions[i];if(current!=d.original)continue;
        return InterlockedCompareExchangePointer(location,reinterpret_cast<void*>(d.owned),reinterpret_cast<void*>(d.original))==reinterpret_cast<void*>(d.original)?static_cast<int>(i):-1;
    }
    return -1;
}
class Runtime {
    struct Bank {uintptr_t asset=0;std::vector<OwnedDefinition> definitions;std::vector<std::array<unsigned char,48>> headers;std::vector<std::vector<unsigned char>> nativeBodies;};
    std::vector<Program> code;std::vector<Bank> banks;std::mutex bankMutex;
    std::atomic<unsigned> attached{0};
    std::atomic<size_t> retainedBytes{0};
    std::atomic<size_t> retainedSourceBytes{0};
    std::atomic<unsigned> retainedDefinitions{0},retainedBanks{0};
    // A known immutable definition already selected for these options needs
    // no mutex, bank walk or allocation on subsequent Draw/focus callbacks.
    static constexpr unsigned variantModes=1024,cacheBuckets=32;
    using Cache=std::array<std::array<std::atomic<uintptr_t>,cacheBuckets>,variantModes+1>;
    std::unique_ptr<Cache> satisfied=std::make_unique<Cache>();
public:
    explicit Runtime(std::vector<Program> selected=programs()):code(std::move(selected)){}
    bool prepared=false;
    void prepare(){prepared=true;}
    bool acceptsFrame(const unsigned char* h,bool fixedFrame=false)const{
        if(!prepared)return false;
        for(const auto& p:code){
            const bool native=field<unsigned>(h,24)==p.size&&field<unsigned short>(h,12)==p.registers;
            const bool owned=field<unsigned>(h,24)==p.code.size()&&field<unsigned short>(h,12)==p.newRegisters;
            if((!fixedFrame||p.newRegisters==p.registers)&&(native||owned)&&field<unsigned>(h,8)==p.argc&&field<unsigned short>(h,14)==p.flags)return true;
        }
        return false;
    }
    template<class Read>int beforeInvoke(void* object,Read read,bool fixedFrame=false,bool enabled=true,unsigned scale=0,bool colors=true,bool fog=true,bool team=true,bool dollars=false,unsigned teamScale=UINT32_MAX){
        if(!prepared)return -1;
        // The native invocation guarantees a live ScriptFunction2 receiver and
        // definition. Most calls leave after these small in-process comparisons;
        // no process scan, allocation or ReadProcessMemory is used on that path.
        auto location=reinterpret_cast<PVOID volatile*>(static_cast<unsigned char*>(object)+0x58);
        const auto definition=reinterpret_cast<uintptr_t>(*location);
        std::array<unsigned char,48> current{};memcpy(current.data(),reinterpret_cast<const void*>(definition),current.size());
        if(teamScale==UINT32_MAX)teamScale=scale;
        if(scale>4||teamScale>4)throw std::runtime_error("Unsupported grade scale");
        if(!acceptsFrame(current.data(),fixedFrame))return -1;
        const auto selectedVariant=scale+(teamScale<<3)+(colors?0u:64u)+(fog?0u:128u)+(team?0u:256u)+(dollars?512u:0u),cacheMode=enabled?selectedVariant:variantModes;
        const auto cachedIndex=(definition>>12)&(cacheBuckets-1);
        if((*satisfied)[cacheMode][cachedIndex].load(std::memory_order_relaxed)==definition)return -1;
        std::lock_guard<std::mutex> lock(bankMutex);
        const auto redirect=[&](Bank& bank)->int{
            for(size_t i=0;i<bank.definitions.size();++i){
                if(fixedFrame&&code[i].newRegisters!=code[i].registers)continue;
                auto& owned=bank.definitions[i];bool ours=definition==owned.original;
                for(const auto& variant:owned.variants)ours=ours||definition==variant.second;
                if(!ours)continue;
                auto targetVariant=selectedVariant;
                if(code[i].scaleOffsets.empty())targetVariant&=~7u;
                if(code[i].teamScaleOffsets.empty())targetVariant&=~56u;
                if(code[i].colorOffsets.empty())targetVariant&=~64u;
                if(code[i].fogOffsets.empty())targetVariant&=~128u;
                if(code[i].teamOffsets.empty())targetVariant&=~256u;
                if(code[i].dollarOffsets.empty())targetVariant&=~512u;
                if(enabled&&!owned.variants[targetVariant]){
                    auto bytes=makeDefinition(code[i],bank.headers[i],bank.nativeBodies[i],bank.asset);
                    for(const auto at:code[i].scaleOffsets)bytes[48+at]=static_cast<unsigned char>(scale);
                    for(const auto at:code[i].teamScaleOffsets)bytes[48+at]=static_cast<unsigned char>(teamScale);
                    for(const auto at:code[i].colorOffsets)bytes[48+at]=colors?1:0;
                    for(const auto at:code[i].fogOffsets)bytes[48+at]=fog?1:0;
                    for(const auto at:code[i].teamOffsets)bytes[48+at]=team?1:0;
                    for(const auto at:code[i].dollarOffsets)bytes[48+at]=dollars?1:0;
                    const auto allocationBytes=(bytes.size()+4095)&~size_t(4095);
                    auto memory=VirtualAlloc(nullptr,allocationBytes,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!memory)throw std::runtime_error("Cannot retain a player grade definition");
                    memcpy(memory,bytes.data(),bytes.size());owned.variants[targetVariant]=reinterpret_cast<uintptr_t>(memory);
                    if(targetVariant==0)owned.owned=owned.variants[0];
                    retainedBytes.fetch_add(allocationBytes,std::memory_order_relaxed);retainedDefinitions.fetch_add(1,std::memory_order_relaxed);
                }
                const auto desired=enabled?owned.variants[targetVariant]:owned.original;
                if(desired==definition){(*satisfied)[cacheMode][cachedIndex]=desired;return -1;}
                if(InterlockedCompareExchangePointer(location,reinterpret_cast<void*>(desired),reinterpret_cast<void*>(definition))==reinterpret_cast<void*>(definition)){(*satisfied)[cacheMode][(desired>>12)&(cacheBuckets-1)]=desired;++attached;return static_cast<int>(i);}
                return -1;
            }return -1;
        };
        for(auto& bank:banks){
            for(size_t i=0;i<bank.definitions.size();++i){const auto& owned=bank.definitions[i];
                bool ours=definition==owned.original&&bank.headers[i]==current;for(const auto& variant:owned.variants)ours=ours||definition==variant.second;
                if(ours)return redirect(bank);
            }
        }
        if(!enabled)return -1;
        size_t index=0;for(;index<code.size();++index)if((!fixedFrame||code[index].newRegisters==code[index].registers)&&headerMatches(code[index],current))break;
        if(index==code.size()||definition<code[index].offset+0x10000)return -1;
        const auto asset=definition-code[index].offset;
        char magic[14]{};if(!read(asset,magic,14)||memcmp(magic,"Apt Data:1:",11))return -1;
        if(banks.size()>=512)throw std::runtime_error("Notes reached its bounded asset-generation limit");
        Bank bank;bank.asset=asset;
        std::set<std::pair<uintptr_t,unsigned>> checkedPools;
        for(const auto& p:code){
            const auto original=asset+p.offset;std::array<unsigned char,48> h{};std::vector<unsigned char> body(p.size);
            if(!read(original,h.data(),48)||!read(original+48,body.data(),body.size()))throw std::runtime_error("Notes source definition is no longer readable");
            makeDefinition(p,h,body,asset);
            const auto poolAddress=field<uintptr_t>(h.data(),40);const auto poolCount=field<unsigned>(h.data(),32);
            if(checkedPools.emplace(poolAddress,poolCount).second){std::vector<unsigned char> pool(size_t(poolCount)*8);
                if(!read(poolAddress,pool.data(),pool.size()))throw std::runtime_error("Notes native constant pool is no longer readable");}
            bank.headers.push_back(h);bank.nativeBodies.push_back(std::move(body));
        }
        // Gate the entire set before allocating or changing the first receiver.
        for(size_t i=0;i<code.size();++i){
            const auto nativeByte=[&](unsigned at){return code[i].copyBytes&&at>=code[i].copyAt&&at-code[i].copyAt<code[i].copyBytes;};
            for(const auto at:code[i].scaleOffsets)if(at==0||at>=code[i].code.size()||nativeByte(at)||nativeByte(at-1)||code[i].code[at-1]!=0xB5||code[i].code[at]!=0)throw std::runtime_error("Invalid grade scale literal metadata");
            for(const auto at:code[i].teamScaleOffsets)if(at==0||at>=code[i].code.size()||nativeByte(at)||nativeByte(at-1)||code[i].code[at-1]!=0xB5||code[i].code[at]!=0)throw std::runtime_error("Invalid team grade scale literal metadata");
            for(const auto at:code[i].colorOffsets)if(at==0||at>=code[i].code.size()||nativeByte(at)||nativeByte(at-1)||code[i].code[at-1]!=0xB5||code[i].code[at]!=1)throw std::runtime_error("Invalid rating color literal metadata");
            for(const auto* offsets:{&code[i].fogOffsets,&code[i].teamOffsets})for(const auto at:*offsets)if(at==0||at>=code[i].code.size()||nativeByte(at)||nativeByte(at-1)||code[i].code[at-1]!=0xB5||code[i].code[at]!=1)throw std::runtime_error("Invalid rating fog literal metadata");
            for(const auto at:code[i].dollarOffsets)if(at==0||at>=code[i].code.size()||nativeByte(at)||nativeByte(at-1)||code[i].code[at-1]!=0xB5||code[i].code[at]!=0)throw std::runtime_error("Invalid dollar literal metadata");
            OwnedDefinition retained;retained.original=asset+code[i].offset;bank.definitions.push_back(retained);
        }
        // Script owners are released on leaving Recruiting. Never retain their
        // addresses: attach only to the live receiver at native invocation setup,
        // before flags, argument registers, body length or body are consumed.
        size_t sourceBytes=bank.headers.size()*48;for(const auto& body:bank.nativeBodies)sourceBytes+=body.size();
        banks.push_back(std::move(bank));retainedSourceBytes.fetch_add(sourceBytes,std::memory_order_relaxed);retainedBanks.fetch_add(1,std::memory_order_relaxed);return redirect(banks.back());
    }
    unsigned ownerCount()const{return attached.load();}
    size_t methodCount()const{return code.size();}
    size_t retainedByteCount()const{return retainedBytes.load(std::memory_order_relaxed)+retainedSourceBytes.load(std::memory_order_relaxed);}
    size_t retainedSourceByteCount()const{return retainedSourceBytes.load(std::memory_order_relaxed);}
    unsigned retainedDefinitionCount()const{return retainedDefinitions.load(std::memory_order_relaxed);}
    unsigned retainedBankCount()const{return retainedBanks.load(std::memory_order_relaxed);}
};
}
