#pragma once
#define RECRUIT_RESUME_CAPTURE
#include "LiveTables.h"
#include "RecruitResumeSource.h"
#include <atomic>
namespace recruitingfog::resume {
struct Published {dynasty::live::SessionBinding binding;NativeClass data;};
class Cache {
    std::shared_ptr<const Published> published;std::atomic<bool> requested{true};uint64_t nextAttempt=0;
public:
    void request(){requested=true;}
    template<class Read>std::shared_ptr<const Published> current(uintptr_t image,Read read){
        auto value=std::atomic_load(&published);if(!value){requested=true;return {};}
        try{auto q=[&](uintptr_t address){uintptr_t v=0;if(!read(address,&v,8))throw std::runtime_error("Dynasty ownership unavailable");return v;};
            if(dynasty::live::activeSession(image,q)==value->binding)return value;
        }catch(...){}
        requested=true;return {};
    }
    template<class Read>Json tick(uintptr_t image,const std::filesystem::path& folder,Read read){
        if(GetTickCount64()<nextAttempt)return nullptr;
        auto q=[&](uintptr_t address){uintptr_t v=0;if(!read(address,&v,8))throw std::runtime_error("Dynasty ownership unavailable");return v;};
        dynasty::live::SessionBinding binding;
        try{binding=dynasty::live::activeSession(image,q);}catch(...){std::atomic_store(&published,std::shared_ptr<const Published>{});requested=true;nextAttempt=GetTickCount64()+1000;return nullptr;}
        auto existing=std::atomic_load(&published);if(existing&&existing->binding==binding&&!requested.exchange(false))return nullptr;
        requested=false;nextAttempt=GetTickCount64()+2000;
        const auto began=GetTickCount64();auto raw=dynasty::live::Capture(image).run();auto data=parseNativeClass(raw);persistClass(data,folder);
        if(!(dynasty::live::activeSession(image,q)==binding))throw std::runtime_error("Dynasty changed while preparing resume cache");
        auto value=std::make_shared<Published>();value->binding=binding;value->data=std::move(data);size_t hs=0;for(const auto& [id,e]:value->data.entries){(void)id;if(e.highSchool)++hs;}
        std::atomic_store(&published,std::shared_ptr<const Published>(value));requested=false;
        return {{"event","recruit_resume_cache_ready"},{"highSchoolProspects",hs},{"records",raw.at("records").size()},{"ms",GetTickCount64()-began},{"league",value->data.league},{"season",value->data.season}};
    }
    std::string compose(const std::shared_ptr<const Published>& cache,const NotesProspect& publicNotes,double rawId,const std::string& first,const std::string& last,bool& loading){
        loading=false;const NativeEntry* found=nullptr;
        if(cache&&rawId>=0&&rawId<=4294967295.0&&std::floor(rawId)==rawId){auto it=cache->data.entries.find(static_cast<uint32_t>(rawId));if(it!=cache->data.entries.end()&&it->second.first==first&&it->second.last==last)found=&it->second;}
        if(!found){request();loading=true;return "PREVIOUS HIGH SCHOOL SEASON\nPreparing background report...\n\n"+scoutingSection(publicNotes);}
        auto notes=publicNotes;
        if(found->highSchool){notes.identity=found->identity;return composeNotes(found->saved,notes);}
        return "BACKGROUND\nNo high school season report on file.\n\n"+scoutingSection(notes);
    }
};
}
