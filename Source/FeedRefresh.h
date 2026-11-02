#pragma once
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <functional>
#include <optional>
#include <vector>
#include <set>
#include "../Vendor/json.hpp"
namespace social::refresh {
using Json=nlohmann::json;
namespace fs=std::filesystem;
struct Stamp {
    uint64_t size=0,modified=0,identity=0;DWORD volume=0;
    bool operator==(const Stamp& r)const{return size==r.size&&modified==r.modified&&identity==r.identity&&volume==r.volume;}
    bool operator!=(const Stamp& r)const{return !(*this==r);}
};
inline Stamp stamp(const fs::path& path){
    HANDLE h=CreateFileW(path.c_str(),FILE_READ_ATTRIBUTES,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(h==INVALID_HANDLE_VALUE)throw std::runtime_error("Watched save is unavailable");
    BY_HANDLE_FILE_INFORMATION i{};BOOL ok=GetFileInformationByHandle(h,&i);CloseHandle(h);
    if(!ok)throw std::runtime_error("Cannot inspect watched save");
    return {(uint64_t(i.nFileSizeHigh)<<32)|i.nFileSizeLow,(uint64_t(i.ftLastWriteTime.dwHighDateTime)<<32)|i.ftLastWriteTime.dwLowDateTime,
        (uint64_t(i.nFileIndexHigh)<<32)|i.nFileIndexLow,i.dwVolumeSerialNumber};
}
// Pure debounce/retry policy, including same-size saves and atomic replacements.
class Watch {
    std::optional<Stamp> observed,completed;
    uint64_t changed=0,retryAt=0;
public:
    uint64_t settleMs=1500,retryMs=5000;
    bool ready(const Stamp& s,uint64_t now){
        if(!observed||*observed!=s){observed=s;changed=now;retryAt=0;return false;}
        return (!completed||*completed!=s)&&now-changed>=settleMs&&now>=retryAt;
    }
    void success(const Stamp& s){completed=s;retryAt=0;}
    void failure(uint64_t now){retryAt=now+retryMs;}
};
// Quote argv directly for CreateProcessW; no shell is involved.
inline std::wstring quote(const std::wstring& input){
    std::wstring out=L"\"";size_t slashes=0;
    for(wchar_t c:input){if(c==L'\\'){++slashes;continue;}if(c==L'\"')out.append(slashes*2+1,L'\\');else out.append(slashes,L'\\');slashes=0;out+=c;}
    out.append(slashes*2,L'\\');return out+L"\"";
}
inline Json readJson(const fs::path& path){
    if(fs::file_size(path)>128ull*1024*1024)throw std::runtime_error("Weekly feed JSON exceeds size limit");
    std::ifstream in(path);if(!in)throw std::runtime_error("Cannot read weekly feed JSON");Json j;in>>j;return j;
}
inline void validate(const Json& j,const Json& config){
    if(j.at("format")!=1||j.at("engineVersion")!=2||!j.at("sourceUnchanged").get<bool>()||j.at("leagueId")!=config.at("leagueId")||j.at("userTeamIndex")!=config.at("userTeamIndex"))throw std::runtime_error("Feed identity or version mismatch");
    if(j.at("source").get<std::string>()!=config.at("save").get<std::string>())throw std::runtime_error("Feed source differs from the watched save");
    const auto& weeks=j.at("weeks");if(!weeks.is_array()||weeks.empty()||weeks.size()>48)throw std::runtime_error("Invalid weekly catalog size");
    if(j.contains("scopeOptions")){const auto& options=j.at("scopeOptions");if(!options.is_array()||options.size()<2||options.size()>512)throw std::runtime_error("Invalid scope catalog");std::set<std::string> scopeIds;for(const auto& o:options){auto key=o.at("key").get<std::string>(),label=o.at("label").get<std::string>();if(key.empty()||key.size()>128||label.empty()||label.size()>128||!scopeIds.insert(key).second)throw std::runtime_error("Invalid scope identity");}if(options[0].at("key")!="all"||options[1].at("key")!="national")throw std::runtime_error("Missing default scopes");}
    std::set<std::string> keys;bool active=false;
    for(const auto& w:weeks){
      if(w.at("leagueId")!=j.at("leagueId")||w.at("userTeamIndex")!=j.at("userTeamIndex")||w.at("season")!=j.at("season")||w.at("phase")!=j.at("phase")||w.at("week").get<int>()>j.at("week").get<int>())throw std::runtime_error("Catalog contains another Dynasty or future publication week");
      const auto key=w.at("key").get<std::string>();if(!keys.insert(key).second)throw std::runtime_error("Duplicate publication week");if(key==j.at("activeWeekKey").get<std::string>())active=true;
      const auto& posts=w.at("stories");if(!posts.is_array()||posts.size()>4096)throw std::runtime_error("Invalid weekly story count");
      std::set<std::string> ids;
      for(const auto& p:posts){
        if(p.at("publication").at("key")!=w.at("key")||p.at("publication").at("week")!=w.at("week"))throw std::runtime_error("Story publication week mismatch");
        if(!ids.insert(p.at("id").get<std::string>()).second)throw std::runtime_error("Duplicate feed post");
        for(const char* k:{"author","handle","body","stamp"})if(!p.at(k).is_string()||p.at(k).get_ref<const std::string&>().empty()||p.at(k).get_ref<const std::string&>().size()>512)throw std::runtime_error("Invalid feed text");
        if(p.at("imageLibrary").get<int>()<0||p.at("imageValue").get<int>()<0)throw std::runtime_error("Invalid feed avatar");
      }
      if(!w.at("views").is_object()||w.at("views").size()>516)throw std::runtime_error("Invalid scope views");
      for(const auto& [scope,view]:w.at("views").items()){if(!view.is_array()||view.size()>(scope=="all"?20u:4096u))throw std::runtime_error("Invalid scope view size");
        std::set<std::string> seen;for(const auto& id:view){const auto v=id.get<std::string>();if(!ids.count(v)||!seen.insert(v).second)throw std::runtime_error("Invalid or duplicate scope story reference");}
      }
    }
    if(!active)throw std::runtime_error("Active publication week is missing");
}
struct Settings {fs::path save,node,exporter,config;};
inline Settings settings(const Json& j,const fs::path& folder){
    auto path=[&](const char* k){auto p=fs::u8path(j.at(k).get<std::string>());return fs::absolute(p.is_absolute()?p:folder/p);};
    Settings s{path("save"),path("node"),path("exporter"),folder/L"social-refresh.json"};
    for(const auto& p:{s.save,s.node,s.exporter,path("schema"),path("parser")})if(!fs::is_regular_file(p))throw std::runtime_error("A configured feed dependency is missing");return s;
}
inline DWORD exportSave(const Settings& s,const fs::path& output,const fs::path& log,const std::function<bool()>& cancelled){
    SECURITY_ATTRIBUTES sa{sizeof(sa),nullptr,TRUE};
    HANDLE stream=CreateFileW(log.c_str(),FILE_APPEND_DATA,FILE_SHARE_READ|FILE_SHARE_WRITE,&sa,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    HANDLE nullIn=CreateFileW(L"NUL",GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,&sa,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(stream==INVALID_HANDLE_VALUE||nullIn==INVALID_HANDLE_VALUE){if(stream!=INVALID_HANDLE_VALUE)CloseHandle(stream);if(nullIn!=INVALID_HANDLE_VALUE)CloseHandle(nullIn);throw std::runtime_error("Cannot create exporter log handles");}
    std::wstring command=quote(s.node.wstring())+L" "+quote(s.exporter.wstring())+L" "+quote(s.config.wstring())+L" "+quote(output.wstring());
    SIZE_T attributeBytes=0;InitializeProcThreadAttributeList(nullptr,1,0,&attributeBytes);
    std::vector<unsigned char> storage(attributeBytes);auto attributes=reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(storage.data());
    HANDLE inherited[]={stream,nullIn};
    if(!InitializeProcThreadAttributeList(attributes,1,0,&attributeBytes)){CloseHandle(stream);CloseHandle(nullIn);throw std::runtime_error("Cannot prepare exporter handles");}
    if(!UpdateProcThreadAttribute(attributes,0,PROC_THREAD_ATTRIBUTE_HANDLE_LIST,inherited,sizeof(inherited),nullptr,nullptr)){DeleteProcThreadAttributeList(attributes);CloseHandle(stream);CloseHandle(nullIn);throw std::runtime_error("Cannot isolate exporter handles");}
    STARTUPINFOEXW startup{};startup.StartupInfo.cb=sizeof(startup);startup.StartupInfo.dwFlags=STARTF_USESTDHANDLES;startup.StartupInfo.hStdOutput=stream;startup.StartupInfo.hStdError=stream;startup.StartupInfo.hStdInput=nullIn;startup.lpAttributeList=attributes;
    PROCESS_INFORMATION process{};
    BOOL launched=CreateProcessW(s.node.c_str(),command.data(),nullptr,nullptr,TRUE,CREATE_NO_WINDOW|EXTENDED_STARTUPINFO_PRESENT|BELOW_NORMAL_PRIORITY_CLASS,nullptr,s.exporter.parent_path().c_str(),&startup.StartupInfo,&process);
    DeleteProcThreadAttributeList(attributes);
    CloseHandle(stream);CloseHandle(nullIn);if(!launched)throw std::runtime_error("Cannot start save exporter");
    CloseHandle(process.hThread);uint64_t start=GetTickCount64();
    while(WaitForSingleObject(process.hProcess,100)==WAIT_TIMEOUT){
        if(cancelled()||GetTickCount64()-start>60000){TerminateProcess(process.hProcess,ERROR_CANCELLED);WaitForSingleObject(process.hProcess,5000);CloseHandle(process.hProcess);throw std::runtime_error("Save export cancelled or timed out");}
    }
    DWORD code=1;GetExitCodeProcess(process.hProcess,&code);CloseHandle(process.hProcess);return code;
}
inline void writeAtomic(const fs::path& temporary,const fs::path& final,const Json& j){
    {std::ofstream out(temporary,std::ios::binary|std::ios::trunc);if(!out)throw std::runtime_error("Cannot create refreshed cache");out<<j.dump();out.flush();if(!out)throw std::runtime_error("Cannot finish refreshed cache");}
    if(!MoveFileExW(temporary.c_str(),final.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))throw std::runtime_error("Cannot publish refreshed cache");
}
class Worker {
    Settings config;Watch watch;Json identity;fs::path directory;
    bool enabled=false;uint64_t pollAt=0;std::string lastHash,lastError;
public:
    void configure(const fs::path& folder){directory=folder;identity=readJson(folder/L"social-refresh.json");config=settings(identity,folder);enabled=true;}
    Json initial()const{auto j=readJson(directory/L"social-feed.json");validate(j,identity);return j;}
    std::optional<Json> tick(const std::function<bool()>& cancelled,const std::function<void(Json)>& report){
        const auto now=GetTickCount64();if(!enabled||now<pollAt||cancelled())return {};pollAt=now+500;
        fs::path raw;
        try{
            const auto before=stamp(config.save);if(!watch.ready(before,now))return {};
            raw=directory/(L"feed-export-"+std::to_wstring(GetCurrentProcessId())+L"-"+std::to_wstring(now)+L".json");
            report({{"event","feed_refresh_started"}});
            const auto code=exportSave(config,raw,directory/L"feed-refresh-worker.log",cancelled);
            if(code!=0)throw std::runtime_error("Feed exporter failed (exit "+std::to_string(code)+"); see feed-refresh-worker.log");
            auto feed=readJson(raw);validate(feed,identity);
            if(stamp(config.save)!=before)throw std::runtime_error("Save changed during feed refresh; retrying");
            if(cancelled())throw std::runtime_error("Feed refresh stopped");
            const auto hash=feed.at("sha256").get<std::string>();
            writeAtomic(directory/L"social-feed.json.tmp",directory/L"social-feed.json",feed);
            std::error_code ec;fs::remove(raw,ec);raw.clear();watch.success(before);lastError.clear();
            if(hash==lastHash)return {};lastHash=hash;
            report({{"event","feed_refresh_ready"},{"sha256",hash},{"week",feed.at("week")},{"posts",feed.at("posts").size()}});return feed;
        }catch(const std::exception& e){watch.failure(GetTickCount64());if(lastError!=e.what()){lastError=e.what();report({{"event","feed_refresh_failed"},{"reason",lastError},{"lastGoodFeedRetained",true}});}std::error_code ec;if(!raw.empty())fs::remove(raw,ec);return {};}
    }
};
}
