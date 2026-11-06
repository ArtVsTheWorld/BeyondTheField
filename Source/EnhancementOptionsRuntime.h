#pragma once
#include "EnhancementOptions.h"
#include <filesystem>
#include <fstream>
#include <mutex>
#include "../Vendor/json.hpp"

namespace enhancements {
inline Options decodeOptions(const nlohmann::json& saved,uint32_t league){
    const auto integer=[&](const char* key,uint32_t maximum){
        const auto& value=saved.at(key);
        if(!value.is_number_integer()||value<0||value>maximum)throw std::runtime_error(std::string("Invalid Dynasty Enhancement setting: ")+key);
        return value.get<uint32_t>();
    };
    const auto format=integer("format",2);
    if((format!=1&&format!=2)||integer("league",UINT32_MAX)!=league)throw std::runtime_error("Dynasty Enhancement settings identity differs");
    Options selected;selected.social=saved.at("socialMedia").get<bool>();selected.recruiting=saved.at("recruitingFog").get<bool>();selected.roster=saved.at("rosterFog").get<bool>();
    selected.scale=GradeScale(integer(format==1?"gradeScale":"playerGradeScale",format==1?3:4));
    selected.teamScale=format==1?selected.scale:GradeScale(integer("teamGradeScale",4));
    selected.colors=saved.value("ratingColors",true);selected.team=saved.value("teamFog",true);selected.dollars=saved.value("dollarValues",false);return selected;
}
// Shared by the two native payloads in this process. No game database fields
// are used to store mod settings, and neither payload polls files at the hub.
class SharedOptions {
    struct Page {volatile LONG sequence;DWORD version;DWORD league;DWORD bits;};
    HANDLE mapping=nullptr;Page* page=nullptr;
public:
    SharedOptions()=default;
    SharedOptions(const SharedOptions&)=delete;
    SharedOptions& operator=(const SharedOptions&)=delete;
    ~SharedOptions(){if(page)UnmapViewOfFile(page);if(mapping)CloseHandle(mapping);}
    void open(){
        if(page)return;
        const auto name=L"Local\\DynastyEnhancer.Options."+std::to_wstring(GetCurrentProcessId());
        mapping=CreateFileMappingW(INVALID_HANDLE_VALUE,nullptr,PAGE_READWRITE,0,sizeof(Page),name.c_str());
        if(!mapping)throw std::runtime_error("Cannot share Dynasty Enhancement options");
        page=static_cast<Page*>(MapViewOfFile(mapping,FILE_MAP_ALL_ACCESS,0,0,sizeof(Page)));
        if(!page){CloseHandle(mapping);mapping=nullptr;throw std::runtime_error("Cannot map Dynasty Enhancement options");}
    }
    void publish(uint32_t league,Options value){
        if(!page)return;
        InterlockedIncrement(&page->sequence);page->version=4;page->league=league;page->bits=value.packed();MemoryBarrier();InterlockedIncrement(&page->sequence);
    }
    bool read(Options& value,uint32_t* league=nullptr)const{
        if(!page)return false;
        for(unsigned i=0;i<3;++i){const auto first=InterlockedCompareExchange(&page->sequence,0,0);if(first&1)continue;
            const auto version=page->version,id=page->league,bits=page->bits;MemoryBarrier();
            if(first!=InterlockedCompareExchange(&page->sequence,0,0))continue;
            if(version!=4||!Options::validBits(bits))return false;value=Options::unpack(bits);if(league)*league=id;return true;
        }return false;
    }
};
class OptionStore {
    std::filesystem::path root;std::mutex mutex,ioMutex;SharedOptions shared;Options selectedProfile;
    bool ready=false,dirty=false;uint32_t league=0;unsigned revision=0;
public:
    void configure(const std::filesystem::path& folder){root=folder/L"DynastyEnhancementSettings";shared.open();}
    bool available(){std::lock_guard<std::mutex> guard(mutex);return ready;}
    bool availableFor(uint32_t identity){std::lock_guard<std::mutex> guard(mutex);return ready&&league==identity;}
    void bind(const std::string& identity){
        size_t consumed=0;const auto number=std::stoull(identity,&consumed);if(consumed!=identity.size()||number>UINT32_MAX)throw std::runtime_error("Invalid enhancement Dynasty identity");
        Options selected;
        {std::lock_guard<std::mutex> guard(mutex);if(ready&&league==number)return;ready=false;currentOptions=selected.packed();shared.publish(static_cast<uint32_t>(number),selected);}
        // Pending edits belong to their original profile even if its write
        // fails during a Dynasty switch. The next worker pass can retry them.
        flush();std::lock_guard<std::mutex> ioGuard(ioMutex);
        const auto file=root/(std::to_string(number)+".json");
        if(std::filesystem::exists(file)){
            if(std::filesystem::file_size(file)>4096)throw std::runtime_error("Dynasty Enhancement settings exceed bounds");
            std::ifstream input(file);nlohmann::json saved;input>>saved;
            selected=decodeOptions(saved,static_cast<uint32_t>(number));
        }
        std::lock_guard<std::mutex> guard(mutex);league=static_cast<uint32_t>(number);selectedProfile=selected;ready=true;dirty=false;++revision;currentOptions=selected.packed();shared.publish(league,selected);
    }
    bool change(unsigned index,int value){
        std::lock_guard<std::mutex> guard(mutex);if(!ready||index>7||value<0||value>((index==3||index==7)?4:1))return false;
        auto next=selectedProfile;if(index==0)next.social=value!=0;else if(index==1)next.recruiting=value!=0;else if(index==2)next.roster=value!=0;else if(index==3)next.scale=GradeScale(value);else if(index==4)next.colors=value!=0;else if(index==5)next.team=value!=0;else if(index==6)next.dollars=value!=0;else next.teamScale=GradeScale(value);
        if(next.packed()==selectedProfile.packed())return true;
        selectedProfile=next;currentOptions=next.packed();++revision;dirty=true;shared.publish(league,next);return true;
    }
    void flush(){
        std::lock_guard<std::mutex> ioGuard(ioMutex);
        uint32_t id=0;unsigned serial=0;Options value;
        {std::lock_guard<std::mutex> guard(mutex);if(!dirty)return;id=league;serial=revision;value=selectedProfile;}
        std::filesystem::create_directories(root);const auto file=root/(std::to_string(id)+".json"),temp=root/(std::to_string(id)+".tmp");
        nlohmann::json saved={{"format",2},{"league",id},{"socialMedia",value.social},{"recruitingFog",value.recruiting},{"rosterFog",value.roster},{"teamFog",value.team},{"dollarValues",value.dollars},{"playerGradeScale",unsigned(value.scale)},{"teamGradeScale",unsigned(value.teamScale)},{"ratingColors",value.colors}};
        {std::ofstream out(temp,std::ios::binary|std::ios::trunc);out<<saved.dump(2);out.flush();if(!out)throw std::runtime_error("Cannot write Dynasty Enhancement settings");}
        if(!MoveFileExW(temp.c_str(),file.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))throw std::runtime_error("Cannot commit Dynasty Enhancement settings");
        std::lock_guard<std::mutex> guard(mutex);if(league==id&&revision==serial)dirty=false;
    }
};
}
