#pragma once
#include "DraftResultsCapture.h"
#include "DraftResultsRuntime.h"
#include "FeedRefresh.h"
#include <array>

namespace recruitingfog::draftresults {
struct ProofCheck {uintptr_t address=0;uint64_t expected=0,mask=0;unsigned size=0;};
struct Proof {
    dynasty::live::SessionBinding binding;uintptr_t context=0;Identity identity;
    std::array<ProofCheck,120> checks{};unsigned count=0;
};
inline Proof parseProof(const Json& raw,const Json& fields,const dynasty::live::SessionBinding& binding){
    Proof proof;proof.binding=binding;proof.context=raw.at("context").get<uintptr_t>();
    const auto league=raw.at("status").at("league").get<int64_t>();
    if(league<INT32_MIN||league>UINT32_MAX)throw std::runtime_error("Invalid draft capture LeagueID");
    proof.identity={std::to_string(static_cast<uint32_t>(league)),integer(raw.at("status").at("season").at("CurrentSeasonYear"),1800,3000)};
    if(!fields.is_array()||fields.size()!=3)throw std::runtime_error("Incomplete draft status proof");std::set<std::string> names;
    for(const auto& table:fields){const auto name=table.at("name").get<std::string>();
        if((name!="SeasonInfo"&&name!="Franchise"&&name!="FranchiseServer_CareerFlow")||!names.insert(name).second)throw std::runtime_error("Invalid draft status proof table");
        const auto& checks=table.at("checks");if(!checks.is_array()||checks.empty()||checks.size()>40)throw std::runtime_error("Invalid draft status checks");
        for(const auto& item:checks){if(proof.count>=proof.checks.size())throw std::runtime_error("Draft status proof exceeds bounds");auto& c=proof.checks[proof.count++];
            c.address=item.at("address").get<uintptr_t>();c.expected=item.at("expected").get<uint64_t>();c.mask=item.at("mask").get<uint64_t>();c.size=item.at("size").get<unsigned>();
            if(c.address<0x10000||c.address+8<c.address||(c.size!=2&&c.size!=4&&c.size!=8)||!c.mask||(c.size<8&&(c.mask>>(c.size*8))))throw std::runtime_error("Invalid draft proof word");
        }
    }return proof;
}
template<class Read>bool proofWordsMatch(const Proof& proof,Read read){
    if(!proof.count||proof.count>proof.checks.size())return false;
    for(unsigned i=0;i<proof.count;++i){const auto& c=proof.checks[i];uint64_t value=0;
        if(c.address<0x10000||c.address+8<c.address||(c.size!=2&&c.size!=4&&c.size!=8)||!c.mask)return false;
        if(!read(c.address,&value,c.size)||((value^c.expected)&c.mask))return false;
    }return true;
}
template<class Read>bool proofMatches(const Proof& proof,uintptr_t image,Read read){
    try{auto q=[&](uintptr_t address){uintptr_t value=0;if(!read(address,&value,8))throw std::runtime_error("Draft identity unavailable");return value;};
        const auto active=dynasty::live::activeSession(image,q);if(!(active==proof.binding))return false;
        auto owned=[&]{return proof.context==active.database||dynasty::live::ownedCareerContext(image,active,q)==proof.context;};if(!owned())return false;
        if(!proofWordsMatch(proof,read))return false;
        return dynasty::live::activeSession(image,q)==active&&owned();
    }catch(...){return false;}
}
class Worker {
    Cache cache;std::shared_ptr<const Proof> published;
    std::filesystem::path folder,node,exporter;bool configured=false;uint64_t retryAt=0,serial=0;std::string lastError;
public:
    void configure(const std::filesystem::path& directory){
        folder=directory;const auto config=social::refresh::readJson(folder/L"dynasty-enhancer.json");
        auto resolve=[&](const char* key){auto p=std::filesystem::u8path(config.at(key).get<std::string>());return std::filesystem::absolute(p.is_absolute()?p:folder/p);};
        node=resolve("node");exporter=resolve("exporter").parent_path()/L"export_draft_results.mjs";
        if(!std::filesystem::is_regular_file(node)||!std::filesystem::is_regular_file(exporter))throw std::runtime_error("Draft view exporter is unavailable");configured=true;
    }
    void request(){cache.request();}
    void clear(){std::atomic_store(&published,std::shared_ptr<const Proof>{});cache.clear();}
    // UI callback: fixed-size local reads and immutable pointer acquisition.
    // The caller supplies its bounded in-process read, never Capture/RPM here.
    template<class Read>std::shared_ptr<const Board> current(uintptr_t image,Read read){
        const auto proof=std::atomic_load(&published);if(!proof||!proofMatches(*proof,image,read)){cache.request();return {};}
        return cache.current(proof->identity);
    }
    template<class Read>void tick(uintptr_t image,Read read,const std::function<bool()>& cancelled,const std::function<void(Json)>& report){
        if(!configured||cancelled()||GetTickCount64()<retryAt||!cache.takeRequest())return;
        // Repeated native getter visits do not recapture a ready valid board.
        if(current(image,read))return;cache.takeRequest();std::filesystem::path input,output;
        try{
            auto q=[&](uintptr_t address){uintptr_t value=0;if(!read(address,&value,8))throw std::runtime_error("Draft Dynasty identity unavailable");return value;};
            const auto binding=dynasty::live::activeSession(image,q);const auto began=GetTickCount64();
            dynasty::live::Capture capture(image,GetCurrentProcess(),captureFields,captureRoot);auto raw=capture.run();auto proof=parseProof(raw,capture.identityProof(),binding);
            if(cancelled()||!proofMatches(proof,image,read))throw std::runtime_error("Dynasty changed during draft capture");
            const auto suffix=std::to_wstring(GetCurrentProcessId())+L"-"+std::to_wstring(++serial);input=folder/(L"draft-view-raw-"+suffix+L".json");output=folder/(L"draft-view-export-"+suffix+L".json");
            auto pending=input;pending+=L".tmp";social::refresh::writeAtomic(pending,input,raw);
            const auto identity=raw.at("status").dump();social::refresh::Settings settings{{},node,exporter,input};
            if(social::refresh::exportSave(settings,output,folder/L"draft-view-worker.log",[&]{return cancelled()||!proofMatches(proof,image,read);}))throw std::runtime_error("Draft view exporter failed; see draft-view-worker.log");
            if(cancelled()||!proofMatches(proof,image,read)||dynasty::live::Capture(image,GetCurrentProcess(),captureFields,captureRoot).status().dump()!=identity)throw std::runtime_error("Dynasty changed while publishing draft view");
            cache.publishFile(output,proof.identity);if(cancelled()||!proofMatches(proof,image,read)){clear();throw std::runtime_error("Draft identity changed before publication");}
            std::atomic_store(&published,std::make_shared<const Proof>(std::move(proof)));lastError.clear();retryAt=0;
            report({{"event","draft_view_published"},{"ms",GetTickCount64()-began},{"league",raw.at("status").at("league")},{"season",raw.at("status").at("season").at("CurrentSeasonYear")},{"records",raw.at("records").size()}});
        }catch(const std::exception& error){clear();retryAt=GetTickCount64()+5000;if(!cancelled()&&lastError!=error.what()){lastError=error.what();report({{"event","draft_view_waiting"},{"reason",lastError}});}}
        std::error_code ignored;if(!input.empty())std::filesystem::remove(input,ignored);if(!output.empty())std::filesystem::remove(output,ignored);
    }
};
}
