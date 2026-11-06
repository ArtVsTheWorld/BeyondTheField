#pragma once
#include "../Vendor/json.hpp"
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace recruitingfog::draftresults {
using Json=nlohmann::json;
struct Identity {std::string league;int season=0;bool operator==(const Identity& r)const{return league==r.league&&season==r.season;}};
struct Row {std::string key,name,position,year,school,conference;int overall=0,team=0,round=0;};
struct Scope {std::string key,label;std::vector<int> teams;};
struct Board {Identity identity;int userTeam=-1;std::vector<Row> rows;std::vector<Scope> scopes;std::string wire;};
inline std::string safeText(const Json& value,size_t maximum){
    if(!value.is_string())throw std::runtime_error("Draft field is not text");auto text=value.get<std::string>();
    if(text.empty()||text.size()>maximum||std::any_of(text.begin(),text.end(),[](unsigned char c){return c<32||c==127;}))throw std::runtime_error("Invalid draft display field");return text;
}
inline bool recordKey(const std::string& value){
    const auto colon=value.find(':');if(colon==std::string::npos||colon==0||colon+1==value.size()||value.size()>22)return false;
    uint64_t numbers[2]{};size_t part=0;for(char c:value){if(c==':'&&part==0){part=1;continue;}if(c<'0'||c>'9')return false;numbers[part]=numbers[part]*10+unsigned(c-'0');if(numbers[part]>uint64_t(part?131071:16383))return false;}
    return value==std::to_string(numbers[0])+":"+std::to_string(numbers[1]);
}
inline int integer(const Json& value,int low,int high){if(!value.is_number_integer())throw std::runtime_error("Non-integer draft field");const auto n=value.get<int64_t>();if(n<low||n>high)throw std::runtime_error("Draft field exceeds bounds");return int(n);}
inline Board parse(const Json& data,const Identity& expected){
    if(data.at("format")!=2||data.at("sourceKind")!="runtime-draft-view"||!data.at("actualRoundsOnly").get<bool>())throw std::runtime_error("Unsupported draft view");
    Board board;board.identity={safeText(data.at("league"),10),integer(data.at("season"),1800,3000)};
    if(!(board.identity==expected))throw std::runtime_error("Draft view belongs to another Dynasty or season");
    if(board.identity.league!=std::to_string(std::stoull(board.identity.league))||std::stoull(board.identity.league)>UINT32_MAX)throw std::runtime_error("Invalid draft LeagueID");
    board.userTeam=data.at("userTeam").is_null()?-1:integer(data.at("userTeam"),0,254);
    const auto& rows=data.at("rows");if(!rows.is_array()||rows.size()>1024)throw std::runtime_error("Draft class exceeds display bounds");
    std::set<std::string> keys;
    for(const auto& v:rows){
        Row r;r.key=safeText(v.at("key"),22);r.name=safeText(v.at("name"),96);r.position=safeText(v.at("position"),12);r.year=safeText(v.at("year"),12);r.school=safeText(v.at("school"),96);
        // Conference membership comes from the captured Conference records.
        r.conference=safeText(v.at("conference"),22);
        r.overall=integer(v.at("overall"),0,100);r.team=integer(v.at("team"),0,254);r.round=integer(v.at("round"),1,7);
        if(!recordKey(r.key)||!recordKey(r.conference)||!keys.insert(r.key).second)throw std::runtime_error("Inconsistent actual draft row");
        board.rows.push_back(std::move(r));
    }
    std::sort(board.rows.begin(),board.rows.end(),[](const auto& a,const auto& b){return std::tie(a.round,a.school,a.name,a.key)<std::tie(b.round,b.school,b.name,b.key);});
    const auto& scopes=data.at("scopes");if(!scopes.is_array()||scopes.empty()||scopes.size()>300)throw std::runtime_error("Invalid draft scope list");
    std::set<std::string> scopeKeys;std::set<int> teamScopes;std::set<std::string> confScopes;
    for(const auto& v:scopes){Scope s;s.key=safeText(v.at("key"),40);s.label=safeText(v.at("label"),96);if(!scopeKeys.insert(s.key).second)throw std::runtime_error("Duplicate draft scope");
        const auto& teams=v.at("teams");if(!teams.is_array()||teams.empty()||teams.size()>255)throw std::runtime_error("Invalid draft scope membership");std::set<int> members;
        for(const auto& t:teams){const auto id=integer(t,0,254);if(!members.insert(id).second)throw std::runtime_error("Duplicate scope member");s.teams.push_back(id);}
        if(s.key=="national"){if(!board.scopes.empty())throw std::runtime_error("National must be the first scope");}
        else if(s.key.rfind("conference:",0)==0){if(!recordKey(s.key.substr(11)))throw std::runtime_error("Invalid conference scope");confScopes.insert(s.key.substr(11));}
        else if(s.key.rfind("team:",0)==0){if(s.teams.size()!=1||s.key!="team:"+std::to_string(s.teams[0]))throw std::runtime_error("Invalid team scope");teamScopes.insert(s.teams[0]);}
        else throw std::runtime_error("Unknown draft scope");
        board.scopes.push_back(std::move(s));
    }
    if(board.scopes.front().key!="national"||teamScopes.empty())throw std::runtime_error("Draft scopes are incomplete");
    for(const auto& r:board.rows){if(!teamScopes.count(r.team)||!confScopes.count(r.conference))throw std::runtime_error("Draft row has no valid scope");for(const auto& s:board.scopes)if(s.key=="conference:"+r.conference&&std::find(s.teams.begin(),s.teams.end(),r.team)==s.teams.end())throw std::runtime_error("Draft conference does not own row");}
    board.wire="DE_DRAFT_2\t"+board.identity.league+'\t'+std::to_string(board.identity.season)+'\t'+std::to_string(board.userTeam)+'\n';
    for(const auto& s:board.scopes){board.wire+="S\t"+s.key+'\t'+s.label+'\t';for(size_t i=0;i<s.teams.size();++i){if(i)board.wire+=',';board.wire+=std::to_string(s.teams[i]);}board.wire+='\n';}
    for(const auto& r:board.rows)board.wire+="P\t"+r.key+'\t'+r.name+'\t'+r.position+'\t'+r.year+'\t'+std::to_string(r.overall)+'\t'+std::to_string(r.team)+'\t'+r.school+'\t'+r.conference+'\t'+std::to_string(r.round)+'\n';
    if(board.wire.size()>512*1024)throw std::runtime_error("Draft view wire exceeds bounds");return board;
}
// Immutable publication: menus only acquire a shared pointer and copy a ready
// string. File IO, JSON parsing and actual-result projection belong to the worker.
class Cache {
    std::shared_ptr<const Board> published;std::atomic<bool> requested{false};
public:
    void request(){requested.store(true,std::memory_order_relaxed);}
    bool takeRequest(){return requested.exchange(false,std::memory_order_relaxed);}
    std::shared_ptr<const Board> current(const Identity& active){auto p=std::atomic_load(&published);if(p&&p->identity==active)return p;request();return {};}
    void clear(){std::atomic_store(&published,std::shared_ptr<const Board>{});}
    void publish(const Json& data,const Identity& active){auto board=std::make_shared<const Board>(parse(data,active));std::atomic_store(&published,std::move(board));}
    void publishFile(const std::filesystem::path& file,const Identity& active){if(!std::filesystem::exists(file)||std::filesystem::file_size(file)>1024*1024)throw std::runtime_error("Draft view missing or oversized");std::ifstream in(file,std::ios::binary);Json data;in>>data;if(!in)throw std::runtime_error("Cannot read draft view");publish(data,active);}
    template<class Set>bool inject(const Identity& active,uintptr_t target,Set set){auto value=current(active);if(!value)return false;set(target,"DEDraftBoard",value->wire.c_str());return true;}
};
}
