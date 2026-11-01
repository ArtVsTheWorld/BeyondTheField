#pragma once
#include "LiveTables.h"
#include "FeedRefresh.h"
namespace dynasty::live {
inline uint64_t fingerprint(std::string_view text){uint64_t value=14695981039346656037ull;for(unsigned char c:text){value^=c;value*=1099511628211ull;}return value;}
// A worker reads memory only. It never invokes the game's getters or changes its tables.
// Two matching full captures, with packed-table verification inside each capture,
// debounce both simulation completion and midweek edits independently of save I/O.
class FeedWorker {
    std::filesystem::path folder,node,exporter;Address base=0,lastContext=0;
    uint64_t pollAt=0,observed=0,accepted=0;bool haveObserved=false,haveAccepted=false;
    std::string lastError,lastStatus;unsigned failures=0;
public:
    void configure(const std::filesystem::path& directory,Address image){
        folder=directory;base=image;auto c=social::refresh::readJson(folder/L"dynasty-enhancer.json");
        auto resolve=[&](const char* key){auto p=std::filesystem::u8path(c.at(key).get<std::string>());return std::filesystem::absolute(p.is_absolute()?p:folder/p);};node=resolve("node");exporter=resolve("exporter");
        if(!std::filesystem::is_regular_file(node)||!std::filesystem::is_regular_file(exporter))throw std::runtime_error("Dynasty Enhancer runtime generator is unavailable");
    }
    std::optional<Json> tick(const std::function<bool()>& cancelled,const std::function<void(Json)>& report,const std::function<void()>& invalidate){
        auto now=GetTickCount64();if(now<pollAt||cancelled())return {};pollAt=now+3000;
        try{
            auto raw=Capture(base).run();const auto ctx=raw.at("context").get<Address>();
            auto status=raw.at("status").dump();if(ctx!=lastContext||status!=lastStatus){lastStatus=status;lastContext=ctx;haveObserved=false;haveAccepted=false;invalidate();report({{"event","active_dynasty_context"},{"context",ctx}});}
            auto payload=raw.at("records").dump();auto hash=fingerprint(payload);
            if(haveAccepted&&hash==accepted){lastError.clear();failures=0;return {};}
            if(!haveObserved||hash!=observed){observed=hash;haveObserved=true;report({{"event","runtime_change_observed"},{"records",raw.at("records").size()}});return {};}
            if(cancelled())return {};
            const auto input=folder/L"runtime-raw.json",output=folder/L"runtime-export.json";
            social::refresh::writeAtomic(folder/L"runtime-raw.json.tmp",input,raw);
            social::refresh::Settings settings{{},node,exporter,input};
            if(social::refresh::exportSave(settings,output,folder/L"runtime-generator.log",cancelled))throw std::runtime_error("Runtime generator failed; see runtime-generator.log");
            auto feed=social::refresh::readJson(output);social::refresh::validate(feed,Json{{"save",feed.at("source")},{"leagueId",feed.at("leagueId")},{"userTeamIndex",feed.at("userTeamIndex")}});
            if(feed.value("sourceKind",std::string())!="runtime")throw std::runtime_error("Expected active Dynasty feed");
            // A Dynasty unload/reload during generation may never publish the old page.
            if(Capture(base).status().dump()!=status||cancelled()){haveObserved=false;invalidate();return {};}
            accepted=hash;haveAccepted=true;lastError.clear();failures=0;
            social::refresh::writeAtomic(folder/L"runtime-feed.json.tmp",folder/L"runtime-feed.json",feed);
            report({{"event","runtime_feed_published"},{"league",feed.at("leagueId")},{"team",feed.at("userTeamIndex")},{"week",feed.at("week")},{"stories",feed.at("stories").size()},{"saveRequired",false}});return feed;
        }catch(const std::exception& e){haveObserved=false;if(++failures>=2){haveAccepted=false;invalidate();}if(lastError!=e.what()){lastError=e.what();report({{"event","runtime_waiting"},{"reason",lastError}});}return {};}
    }
};
}
