#pragma once
#include <cmath>
#include <optional>
#include <set>
namespace social::hubtab {
inline constexpr char id[]="CM_DYNASTY_SOCIAL";
template<class Read>bool sso(uintptr_t address,std::string& value,Read read){
    std::array<unsigned char,16> b{};if(!read(address,b.data(),b.size()))return false;
    if(b[15]&128){uintptr_t p=0;uint32_t length=0;memcpy(&p,b.data(),8);memcpy(&length,b.data()+8,4);if(length>512)return false;value.resize(length);return !length||read(p,value.data(),length);}
    if(b[15]>15)return false;value.assign(reinterpret_cast<const char*>(b.data()),15-b[15]);return true;
}
template<class Read>std::optional<nlohmann::json> fields(uintptr_t object,uintptr_t image,Read read){
    using J=nlohmann::json;std::array<unsigned char,48> b{};if(!read(object,b.data(),b.size()))return {};
    auto u64=[](const unsigned char* p){uintptr_t n=0;memcpy(&n,p,8);return n;};auto u32=[](const unsigned char* p){unsigned n=0;memcpy(&n,p,4);return n;};
    if(u32(b.data()+16)!=5||u64(b.data())<image||u64(b.data())>=image+0x11ffe000)return {};
    const auto buckets=u64(b.data()+32);const auto count=u32(b.data()+40);if(!count||count>257)return {};
    J result=J::object();std::set<uintptr_t> visited;
    for(unsigned i=0;i<count;++i){uintptr_t node=0;if(!read(buckets+i*8,&node,8))return {};
        while(node&&node!=~uintptr_t(0)){
            if(visited.count(node))return {};if(visited.size()>=256)return {};visited.insert(node);
            std::array<unsigned char,32> n{};if(!read(node,n.data(),n.size()))return {};std::string key;
            if(!sso(u64(n.data()+8),key,read)||key.empty()||key.size()>128)return {};
            const auto value=u64(n.data()+16);std::array<unsigned char,40> v{};if(!read(value,v.data(),v.size()))return {};
            if(u64(v.data())<image||u64(v.data())>=image+0x11ffe000)return {};
            const auto kind=u32(v.data()+16);
            if(kind==3){std::string text;if(!sso(u64(v.data()+32),text,read))return {};result[key]=text;}
            else if(kind==2){double number=0;memcpy(&number,v.data()+24,8);if(!std::isfinite(number))return {};result[key]=number;}
            else if(kind==1)result[key]=v[24]!=0;
            node=u64(n.data()+24);
        }
    }return result;
}
inline std::optional<nlohmann::json> plan(const std::vector<nlohmann::json>& rows){
    using J=nlohmann::json;const J* team=nullptr;const J* stats=nullptr;const J* donor=nullptr;
    for(const auto& row:rows){const auto key=row.value("id",std::string());if(key==id)return {};if(key=="cm_team"){if(team)return {};team=&row;}if(key=="CM_LEAGUE"){if(stats)return {};stats=&row;}if(key=="DynastyCentral"){if(donor)return {};donor=&row;}}
    if(!team||!stats||!donor||!team->contains("priority")||!stats->contains("priority")||!(*team)["priority"].is_number()||!(*stats)["priority"].is_number())return {};
    const double a=(*team)["priority"].get<double>(),b=(*stats)["priority"].get<double>();if(a==b||!std::isfinite(a)||!std::isfinite(b))return {};
    double nearest=b;for(const auto& candidate:rows)if(candidate.contains("priority")&&candidate["priority"].is_number()){const auto n=candidate["priority"].get<double>();if((b<a&&n<a&&n>nearest)||(b>a&&n>a&&n<nearest))nearest=n;}
    auto row=*donor;row["id"]=id;row["name"]="Social Media";row["priority"]=(a+nearest)/2;row["Priority"]=(a+nearest)/2;row["numRows"]=1;row["numColumns"]=1;row["NumRows"]=1;row["NumColumns"]=1;row["isSubPanel"]=false;row["isVisible"]=true;return row;
}
}
