#pragma once
#include "RecruitNotesUiPrograms.h"
#include <array>
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
struct Owner {uintptr_t address=0;size_t program=0;};
class Runtime {
    std::vector<Program> code=programs();std::vector<OwnedDefinition> definitions;std::vector<Owner> owners;
    static bool exchange(uintptr_t address,uintptr_t expected,uintptr_t desired){DWORD old=0,unused=0;if(!VirtualProtect(reinterpret_cast<void*>(address),8,PAGE_READWRITE,&old))return false;const auto before=InterlockedCompareExchangePointer(reinterpret_cast<PVOID volatile*>(address),reinterpret_cast<void*>(desired),reinterpret_cast<void*>(expected));VirtualProtect(reinterpret_cast<void*>(address),8,old,&unused);return before==reinterpret_cast<void*>(expected);}
public:
    bool installed=false;
    template<class Read>void install(const std::filesystem::path& folder,uintptr_t image,Read read){
        std::ifstream in(folder/L"recruit-notes-runtime.json");if(!in)throw std::runtime_error("Notes runtime manifest is missing");nlohmann::json config;in>>config;
        if(config.at("pid").get<DWORD>()!=GetCurrentProcessId())throw std::runtime_error("Notes manifest belongs to a different session");
        const auto asset=config.at("asset").get<uintptr_t>();char magic[14]{};if(!read(asset,magic,14)||memcmp(magic,"Apt Data:1:",11))throw std::runtime_error("Notes APT stream is no longer loaded");
        for(const auto& p:code){
            const auto original=asset+p.offset;std::array<unsigned char,48> h{};std::vector<unsigned char> body(p.size);
            if(!read(original,h.data(),48)||!read(original+48,body.data(),body.size()))throw std::runtime_error("Notes source definition is no longer readable");
            const auto bytes=makeDefinition(p,h,body);auto memory=VirtualAlloc(nullptr,(bytes.size()+4095)&~size_t(4095),MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!memory)throw std::runtime_error("Cannot retain a Notes script definition");
            memcpy(memory,bytes.data(),bytes.size());definitions.push_back({original,reinterpret_cast<uintptr_t>(memory)});
        }
        if(!config.at("owners").is_array()||config.at("owners").size()>128)throw std::runtime_error("Notes owner count is unsupported");
        std::set<uintptr_t> unique;std::set<size_t> matched;
        for(const auto& item:config.at("owners")){
            Owner owner{item.at("address").get<uintptr_t>(),item.at("program").get<size_t>()};if(owner.program>=definitions.size()||owner.address%8||!unique.insert(owner.address).second)throw std::runtime_error("Notes owner metadata is unsupported");
            // Leaving Recruiting can release instance/delegate clones. Skip
            // stale instances, but require a valid owner for every method.
            std::array<unsigned char,96> object{};if(!read(owner.address,object.data(),object.size())||field<uintptr_t>(object.data(),0)!=image+0xbc42fe8||field<uintptr_t>(object.data(),0x58)!=definitions[owner.program].original)continue;
            owners.push_back(owner);matched.insert(owner.program);
        }
        if(matched.size()!=code.size())throw std::runtime_error("A Notes script owner is unavailable");
        size_t done=0;
        for(const auto& owner:owners){const auto& d=definitions[owner.program];if(!exchange(owner.address+0x58,d.original,d.owned)){
                while(done){const auto& previous=owners[--done];const auto& saved=definitions[previous.program];exchange(previous.address+0x58,saved.owned,saved.original);}throw std::runtime_error("Notes script ownership changed before installation");}
            ++done;
        }
        // Native ScriptFunction clones retain these definition pointers. Keep
        // both data pages and the containing DLL pinned until a clean restart.
        installed=true;
    }
    size_t ownerCount()const{return owners.size();}
};
}
