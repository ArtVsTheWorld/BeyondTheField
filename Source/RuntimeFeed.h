#pragma once
#include "LiveTables.h"
#include "FeedRefresh.h"
namespace dynasty::live {
inline uint64_t fingerprint(std::string_view text){uint64_t value=14695981039346656037ull;for(unsigned char c:text){value^=c;value*=1099511628211ull;}return value;}
inline void validateRuntimeIdentity(const Json& feed,const Json& status){
    const auto& season=status.at("season");
    if(feed.value("sourceKind",std::string())!="runtime"||feed.at("leagueId")!=status.at("league")||feed.at("phase")!=season.at("CurrentWeekType")||feed.at("week")!=season.at("CurrentWeek")||feed.at("season")!=season.at("CurrentSeasonYear"))throw std::runtime_error("Cached/generated edition differs from the active Dynasty");
}
// A worker reads memory only. It never invokes the game's getters or changes its tables.
// Two matching full captures, with packed-table verification inside each capture,
// debounce both simulation completion and midweek edits independently of save I/O.
class FeedWorker {
    std::filesystem::path folder,node,exporter,resumer;Address base=0,lastContext=0;
    uint64_t pollAt=0,observed=0,accepted=0;bool haveObserved=false,haveAccepted=false;
    std::string lastError,lastStatus;unsigned failures=0;
    PackedChangeWatch settledProbe;uint64_t fastPolls=0,lastProbeReport=0,sameContentRefreshes=0,lastSameReport=0;
public:
    void configure(const std::filesystem::path& directory,Address image){
        folder=directory;base=image;auto c=social::refresh::readJson(folder/L"dynasty-enhancer.json");
        auto resolve=[&](const char* key){auto p=std::filesystem::u8path(c.at(key).get<std::string>());return std::filesystem::absolute(p.is_absolute()?p:folder/p);};node=resolve("node");exporter=resolve("exporter");
        resumer=exporter.parent_path()/L"resume_runtime.mjs";
        // A diagnostic hot reload may reuse a previously verified context only
        // in this exact process lifetime; Capture rechecks native ownership.
        if(c.contains("diagnosticSessionHint")){
            const auto& hint=c.at("diagnosticSessionHint");FILETIME created{},exited{},kernel{},user{};uint64_t creation=0;
            if(GetProcessTimes(GetCurrentProcess(),&created,&exited,&kernel,&user))memcpy(&creation,&created,sizeof(creation));
            if(hint.value("pid",DWORD(0))==GetCurrentProcessId()&&creation&&hint.value("creation",uint64_t(0))==creation)
                sessionContextHint()={hint.at("career").get<Address>(),hint.at("database").get<Address>(),hint.at("context").get<Address>()};
        }
        if(!std::filesystem::is_regular_file(node)||!std::filesystem::is_regular_file(exporter)||!std::filesystem::is_regular_file(resumer))throw std::runtime_error("Dynasty Enhancer runtime generator is unavailable");
    }
    std::optional<Json> tick(const std::function<bool()>& cancelled,const std::function<void(Json)>& report,const std::function<void()>& invalidate){
        auto now=GetTickCount64();if(now<pollAt||cancelled())return {};pollAt=now+3000;
        try{
            if(haveAccepted&&settledProbe.available()){
                const auto began=GetTickCount64();size_t bytes=0,calls=0;
                const bool unchanged=settledProbe.unchanged([&](uintptr_t address,void* out,size_t size){
                    if(cancelled()||GetTickCount64()-began>500||bytes+size>PackedChangeWatch::maximumBytes)return false;
                    SIZE_T got=0;++calls;bytes+=size;return ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(address),out,size,&got)&&got==size;
                });
                if(unchanged){++fastPolls;lastError.clear();failures=0;pollAt=GetTickCount64()+5000;
                    if(GetTickCount64()-lastProbeReport>=30000){lastProbeReport=GetTickCount64();report({{"event","runtime_unchanged_probe"},{"probeMs",GetTickCount64()-began},{"readBytes",bytes},{"readCalls",calls},{"fastPolls",fastPolls},{"sameContentRefreshes",sameContentRefreshes}});}return {};
                }
            }
            if(cancelled())return {};
            PackedChangeWatch candidateProbe;
            const auto captureBegan=GetTickCount64();auto raw=Capture(base).run(&candidateProbe);const auto captureMs=GetTickCount64()-captureBegan;const auto ctx=raw.at("context").get<Address>();
            auto status=raw.at("status").dump();if(ctx!=lastContext||status!=lastStatus){lastStatus=status;lastContext=ctx;haveObserved=false;haveAccepted=false;invalidate();report({{"event","active_dynasty_context"},{"context",ctx}});}
            auto payload=raw.at("records").dump();auto hash=fingerprint(payload);
            auto accept=[&](Json feed,const char* event)->std::optional<Json>{
                social::refresh::validate(feed,Json{{"save",feed.at("source")},{"leagueId",feed.at("leagueId")},{"userTeamIndex",feed.at("userTeamIndex")}});validateRuntimeIdentity(feed,raw.at("status"));
                if(Capture(base).status().dump()!=status||cancelled()){haveObserved=false;invalidate();return {};}
                accepted=hash;haveAccepted=true;lastError.clear();failures=0;settledProbe=std::move(candidateProbe);
                social::refresh::writeAtomic(folder/L"runtime-feed.json.tmp",folder/L"runtime-feed.json",feed);
                report({{"event",event},{"league",feed.at("leagueId")},{"team",feed.at("userTeamIndex")},{"week",feed.at("week")},{"stories",feed.at("stories").size()},{"saveRequired",false}});return feed;
            };
            if(haveAccepted&&hash==accepted){settledProbe=std::move(candidateProbe);lastError.clear();failures=0;pollAt=GetTickCount64()+5000;++sameContentRefreshes;
                if(GetTickCount64()-lastSameReport>=30000){lastSameReport=GetTickCount64();report({{"event","runtime_same_content_refresh"},{"captureMs",captureMs},{"captureAndHashMs",GetTickCount64()-captureBegan},{"sameContentRefreshes",sameContentRefreshes}});}return {};}
            if(!haveObserved||hash!=observed){const bool mayResume=!haveObserved&&!haveAccepted;observed=hash;haveObserved=true;report({{"event","runtime_change_observed"},{"records",raw.at("records").size()},{"captureMs",captureMs}});
                if(mayResume&&!cancelled()){
                    const auto input=folder/L"runtime-raw.json",output=folder/L"runtime-resume.json";social::refresh::writeAtomic(folder/L"runtime-raw.json.tmp",input,raw);
                    social::refresh::Settings settings{{},node,resumer,input};const auto code=social::refresh::exportSave(settings,output,folder/L"runtime-generator.log",cancelled);
                    if(code==0)return accept(social::refresh::readJson(output),"runtime_feed_resumed");
                    if(code!=3)throw std::runtime_error("Runtime cache check failed; see runtime-generator.log");
                }return {};
            }
            if(cancelled())return {};
            const auto input=folder/L"runtime-raw.json",output=folder/L"runtime-export.json";
            social::refresh::writeAtomic(folder/L"runtime-raw.json.tmp",input,raw);
            social::refresh::Settings settings{{},node,exporter,input};
            const auto generationBegan=GetTickCount64();
            if(social::refresh::exportSave(settings,output,folder/L"runtime-generator.log",cancelled))throw std::runtime_error("Runtime generator failed; see runtime-generator.log");
            report({{"event","runtime_generation_timing"},{"captureMs",captureMs},{"generationMs",GetTickCount64()-generationBegan}});
            return accept(social::refresh::readJson(output),"runtime_feed_published");
        }catch(const std::exception& e){haveObserved=false;if(++failures>=2){haveAccepted=false;invalidate();}if(lastError!=e.what()){lastError=e.what();report({{"event","runtime_waiting"},{"reason",lastError}});}return {};}
    }
};
}
