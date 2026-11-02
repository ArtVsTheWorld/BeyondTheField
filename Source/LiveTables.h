#pragma once
#include <windows.h>
#include <cstdint>
#include <cstring>
#include <map>
#include <set>
#include <vector>
#include <string>
#include <stdexcept>
#include <chrono>
#include "../Vendor/json.hpp"
// Runtime observation only: no native calls, setters, handles, or reference-count writes.
namespace dynasty::live {
using Json=nlohmann::json;using Address=uintptr_t;
struct Memory {
    HANDLE process=GetCurrentProcess();size_t bytes=0;uint64_t deadline=GetTickCount64()+8000;
    std::vector<unsigned char> read(Address address,size_t size){
        if(address<0x10000||address+size<address||size>128u*1024*1024||bytes+size>512u*1024*1024||GetTickCount64()>deadline)throw std::runtime_error("Live capture exceeds bounds: bytes="+std::to_string(bytes)+" read="+std::to_string(size)+" at="+std::to_string(address));
        std::vector<unsigned char> result(size);SIZE_T got=0;
        if(size&&(!ReadProcessMemory(process,reinterpret_cast<void*>(address),result.data(),size,&got)||got!=size))throw std::runtime_error("Live session changed or memory is unavailable");bytes+=size;return result;
    }
    template<class T>T at(Address address){auto b=read(address,sizeof(T));T value;memcpy(&value,b.data(),sizeof(T));return value;}
    std::string text(Address address){
        if(!address)return {};std::string value;
        for(size_t i=0;i<1024;i+=32){auto block=read(address+i,32);for(auto ch:block){if(!ch)return value;value+=static_cast<char>(ch);}}throw std::runtime_error("Unbounded runtime string");
    }
    std::string sso(Address address){auto b=read(address,16);if(b[15]&128)return text(at<Address>(address));if(b[15]>15)throw std::runtime_error("Invalid short string");return std::string(reinterpret_cast<char*>(b.data()),15-b[15]);}
};
template<class T>T value(const std::vector<unsigned char>& b,size_t offset){if(offset+sizeof(T)>b.size())throw std::runtime_error("Native layout exceeds buffer");T v;memcpy(&v,b.data()+offset,sizeof(T));return v;}
inline uint32_t bits(const std::vector<unsigned char>& data,uint32_t words,uint32_t first,uint32_t row,uint32_t offset,unsigned width){
    if(!width||width>32||offset%32+width>32)throw std::runtime_error("Unsupported packed field");
    const auto pos=(uint64_t(first)+uint64_t(row)*words+offset/32)*4;
    return (value<uint32_t>(data,static_cast<size_t>(pos))>>(offset%32))&(width==32?0xffffffffu:(1u<<width)-1);
}
struct Field {std::string name;uint32_t id=0,kind=0;unsigned width=0;int minimum=0;Address fallback=0,descriptor=0;std::map<uint32_t,std::string> labels;};
struct Schema {std::string name;uint32_t capacity=0;std::vector<Field> fields;};
struct Table {Address address=0,context=0,dataAddress=0,stringBase=0;uint32_t id=0,rows=0,words=0,first=0;bool array=false;Schema* schema=nullptr;std::vector<unsigned char> data;std::set<uint32_t> free;};
inline std::set<std::string> wanted(const std::string& name){
    if(name=="SeasonInfo")return {"CurrentWeek","CurrentSeasonYear","CurrentYear","CurrentWeekType","CurrentStage"};
    if(name=="Franchise")return {"LeagueID"};
    if(name=="FranchiseServer_CareerFlow")return {"IsStageAdvancing","IsStageActive"};
    if(name=="FranchiseUser")return {"Team","UserEntity","IsRetired","AdminLevel"};
    if(name=="Team")return {"TeamIndex","DisplayName","LongName","ShortName","NickName","NickNameAlt","Hashtag1","Hashtag2","HeadCoach","TeamSeasonStats","TEAM_LOGO","MediaPoll_CurrentRank","MediaPoll_LastWeeksRank","CoachesPoll_CurrentRank","CoachesPoll_LastWeeksRank","CFPPoll_CurrentRank","CFPPoll_LastWeeksRank","CurSeasonConfStanding","LastWeekConferenceStanding","ConfWin","ConfLoss","ConfTie","HomeWin","RoadWin","HomeLoss","RoadLoss","HomeTie","RoadTie","Rival1TeamRef","Rival2TeamRef","Rival3TeamRef","RecruitingBoard"};
    if(name=="Coach")return {"FirstName","LastName","TeamIndex"};
    if(name=="Conference")return {"Name","TeamSlots","Divisions","ConferenceEnum"};
    if(name=="Player")return {"FirstName","LastName","Position","Personality","JerseyNum","TeamIndex","PLYR_PORTRAIT","IsNIL","OverallRating","Age","SchoolYear","InjuryStatus","InjuryType","LatestInjuryWeek","LatestInjuryYear","LatestInjuryStage","MinInjuryDuration","MaxInjuryDuration","AbsoluteTransferChance","CurrentNILCompensation","ProspectStarRating","GameStats"};
    if(name=="SeasonGame")return {"IsPractice","SeasonYear","SeasonWeek","SeasonWeekType","GameStatus","HomeTeam","AwayTeam","HomeScore","AwayScore","GameDateMonth","GameDateDay","DayOfWeek","TimeOfDay","GameOfTheWeekScore","ThanksgivingFlag","ChristmasFlag","NewYearsFlag","HomeTeamStatCache","AwayTeamStatCache"};
    if(name=="Awards")return {"HeismanRanking"};
    if(name=="Recruit")return {"RecruitStage","Player","TopSchoolsList","NationalRank"};
    // Referenced arrays and support records: primitive/ref fields only, never scripts.
    if(name.size()>=2&&name.substr(name.size()-2)=="[]")return {};
    return {"TeamIndex","Player","Team","CurrentRank","LastWeekRank","Teams","TeamId","TeamInfluence","Recruits","Recruit","ScholarshipStatus","CommittedWeekNumber","SeasonGame","OpposingTeam","OFFPASSYARDS","OFFRUSHYARDS","FIRSTDOWNS","GIVEAWAYS","TAKEAWAYS","THIRDDOWNCONV","THIRDDOWNS","WINS","LOSSES","TIES","PASSATTEMPTS","PASSCOMPLETED","PASSYARDS","PASSTDS","PASSINTS","RUSHATTEMPTS","RUSHYARDS","RUSHTDS","RECEIVECATCHES","RECEIVEYARDS","RECEIVETDS","DLINESACKS","DLINEHALFSACK","DSECINTS","DEFTACKLES"};
}
class Capture {
    Memory memory;Address image=0,root=0,context=0;std::map<Address,Schema> schemas;std::map<Address,Table> tables;std::map<uint32_t,Address> ids;std::map<Address,std::map<uint32_t,uint32_t>> referenceMaps;
    std::vector<std::pair<Address,uint32_t>> pending;std::set<std::pair<Address,uint32_t>> scheduled;Json records=Json::object();size_t recordCount=0;
    Address parent(Address ctx){return memory.at<Address>(ctx+0x1a8);}
    void inventory(Address begin,Address end){if(end<begin||(end-begin)%8||end-begin>0x100000)throw std::runtime_error("Invalid active table catalog");auto bytes=memory.read(begin,end-begin);for(size_t i=0;i<bytes.size();i+=8){const auto p=value<Address>(bytes,i);if(p&&(memory.at<Address>(p)==image+0xbd0df38||memory.at<Address>(p)==image+0xbd0ebe0)&&memory.at<Address>(p+8))ids.emplace(memory.at<uint32_t>(p+0x2c),p);}}
    Schema& schema(Address address){
        auto [it,fresh]=schemas.try_emplace(address);auto& s=it->second;if(!fresh)return s;
        s.name=memory.text(memory.at<Address>(address+0x18));s.capacity=memory.at<uint32_t>(address+0x28);
        const auto begin=memory.at<Address>(address+0x40),end=memory.at<Address>(address+0x48);
        if(end<begin||(end-begin)%0x58||end-begin>0x40000)throw std::runtime_error("Invalid runtime schema");
        auto selected=wanted(s.name);if(s.name.size()>=2&&s.name.substr(s.name.size()-2)=="[]")return s;
        for(Address p=begin;p<end;p+=0x58){auto name=memory.sso(p);if(!selected.empty()&&!selected.count(name))continue;
            auto meta=memory.read(p,0x58);Field f;f.name=name;f.id=static_cast<uint32_t>((p-begin)/0x58);f.kind=value<uint32_t>(meta,0x40);f.width=value<uint16_t>(meta,0x30);f.minimum=value<int>(meta,0x38);f.fallback=value<Address>(meta,0x48);f.descriptor=value<Address>(meta,0x50);
            if(f.kind<1||f.kind>7||f.kind==4||f.kind==6)continue;
            if(f.kind==7&&f.width)f.width=32;
            if(f.width>32)throw std::runtime_error("Unsupported runtime field width");
            if(f.kind==3&&f.descriptor){auto a=memory.at<Address>(f.descriptor+0x40),e=memory.at<Address>(f.descriptor+0x48);if(e<a||(e-a)%0x58||e-a>0x20000)throw std::runtime_error("Invalid enum descriptor");for(;a<e;a+=0x58){auto label=memory.sso(a);if(label.rfind("First_",0)&&label.rfind("Last_",0)){auto code=memory.at<uint32_t>(a+0x48);auto old=f.labels.find(code);if(old==f.labels.end()||(!label.empty()&&label.back()!='_'&&!old->second.empty()&&old->second.back()=='_'))f.labels[code]=label;}}}
            s.fields.push_back(std::move(f));
        }return s;
    }
    Table& table(Address address){
        auto [it,fresh]=tables.try_emplace(address);auto& t=it->second;if(!fresh)return t;
        t.array=memory.at<Address>(address)==image+0xbd0ebe0;if(!t.array&&memory.at<Address>(address)!=image+0xbd0df38)throw std::runtime_error("Unsupported live table implementation");
        t.address=address;t.context=memory.at<Address>(address+0x10);t.id=memory.at<uint32_t>(address+0x2c);t.schema=&schema(memory.at<Address>(address+8));t.dataAddress=memory.at<Address>(address+0x38);t.stringBase=memory.at<Address>(address+0x48);
        auto head=memory.read(t.dataAddress,0x20);t.words=value<uint32_t>(head,0xc);t.rows=value<uint32_t>(head,0x10);t.first=value<uint32_t>(head,0x18);
        if(t.rows>131072||t.words>4096||t.first>0x10000)throw std::runtime_error("Invalid live record layout");
        const uint64_t length=(uint64_t(t.first)+uint64_t(t.words)*t.rows)*4;if(length<0x20||length>128u*1024*1024)throw std::runtime_error("Invalid packed table size");t.data=memory.read(t.dataAddress,static_cast<size_t>(length));
        auto free=value<uint32_t>(t.data,0x1c);while(free<t.rows){if(!t.free.insert(free).second||t.free.size()>t.rows)throw std::runtime_error("Cyclic free row list");free=value<uint32_t>(t.data,(size_t(t.first)+size_t(free)*t.words)*4);}return t;
    }
    uint32_t remap(Address ctx,uint32_t serial){
        for(unsigned depth=0;ctx&&depth<8;++depth){auto [it,fresh]=referenceMaps.try_emplace(ctx);if(fresh){auto a=memory.at<Address>(ctx+0x170),e=memory.at<Address>(ctx+0x178);if(e<a||(e-a)%8||e-a>0x1000000)throw std::runtime_error("Invalid reference remapping");auto bytes=memory.read(a,e-a);for(size_t i=0;i<bytes.size();i+=8)it->second.emplace(value<uint32_t>(bytes,i),value<uint32_t>(bytes,i+4));}auto match=it->second.find(serial);if(match!=it->second.end())return match->second;ctx=parent(ctx);
        }throw std::runtime_error("Unresolved live reference");
    }
    std::string key(Table& t,uint32_t row){return std::to_string(t.id)+":"+std::to_string(row);}
    void schedule(Address address,uint32_t row){auto& t=table(address);if(row>=t.rows||t.free.count(row))throw std::runtime_error("Dangling native record");if(scheduled.emplace(address,row).second)pending.emplace_back(address,row);}
    Json reference(Table& owner,uint32_t serial){
        if(!serial)return nullptr;if(serial&0x80000000u)serial=remap(owner.context,serial);auto it=ids.find((serial>>17)&0x3fff);if(it==ids.end())throw std::runtime_error("Unknown runtime reference table "+std::to_string((serial>>17)&0x3fff)+" from "+owner.schema->name);auto& t=table(it->second);auto row=serial&0x1ffff;schedule(t.address,row);return key(t,row);
    }
    Json record(Table& t,uint32_t row){
        Json result=Json::object();if(t.array){auto length=value<uint32_t>(t.data,0x20+size_t(row)*4);if(length>t.words||length>4096)throw std::runtime_error("Invalid runtime array length");for(uint32_t i=0;i<length;++i)result["Member"+std::to_string(i)]=reference(t,bits(t.data,t.words,t.first,row,i*32,32));return result;}for(const auto& f:t.schema->fields){uint32_t raw=static_cast<uint32_t>(f.fallback);if(f.width){auto offset=value<uint32_t>(t.data,0x20+size_t(f.id)*4);raw=bits(t.data,t.words,t.first,row,offset,f.width);}
            if(f.kind==7){if(!f.width){if(!f.fallback){result[f.name]=nullptr;continue;}auto a=memory.at<Address>(f.fallback+0x10);auto r=memory.at<uint32_t>(f.fallback+0x18);schedule(a,r);result[f.name]=key(table(a),r);}else result[f.name]=reference(t,raw);}
            else if(f.kind==5)result[f.name]=memory.text(f.width?t.stringBase+raw:f.fallback);
            else if(f.kind==3){auto it=f.labels.find(raw);if(it==f.labels.end())throw std::runtime_error("Unknown native enum value: "+f.name);result[f.name]=it->second;}
            else if(f.kind==1)result[f.name]=raw!=0;
            else result[f.name]=f.width?int64_t(raw)+f.minimum:int64_t(static_cast<int32_t>(raw));
        }return result;
    }
    void open(){
        root=memory.at<Address>(image+0xe1eac10);if(!root||memory.at<Address>(root)!=image+0xb04bcd0)throw std::runtime_error("No supported active career session");
        context=memory.at<Address>(root+0x290);if(!context||memory.at<Address>(context)!=image+0xbd0d378)throw std::runtime_error("Active Dynasty tables unavailable");
        inventory(memory.at<Address>(context+0x1c0),memory.at<Address>(context+0x1c8));auto p=parent(context);for(auto offset:{0x200,0x268})inventory(memory.at<Address>(p+offset),memory.at<Address>(p+offset+8));
    }
public:
    explicit Capture(Address base,HANDLE process=GetCurrentProcess()):image(base){memory.process=process;}
    Json status(){
        open();Json result={{"context",context}};bool season=false,flow=false,league=false;
        for(const auto& [id,a]:ids){(void)id;auto name=memory.text(memory.at<Address>(memory.at<Address>(a+8)+0x18));
            if(name!="SeasonInfo"&&name!="Franchise"&&name!="FranchiseServer_CareerFlow")continue;
            auto& t=table(a);if(!t.rows||t.free.count(0))continue;auto values=record(t,0);
            if(name=="SeasonInfo"){result["season"]=values;season=true;}
            else if(name=="Franchise"){result["league"]=values.at("LeagueID");league=true;}
            else{if(!values.at("IsStageActive").get<bool>()||values.at("IsStageAdvancing").get<bool>())throw std::runtime_error("Dynasty is advancing or inactive");flow=true;}
        }
        if(!season||!flow||!league)throw std::runtime_error("Active Dynasty identity is incomplete");
        return result;
    }
    Json run(){
        const auto before=status();
        for(const auto& [id,a]:ids){(void)id;Schema s;s.name=memory.text(memory.at<Address>(memory.at<Address>(a+8)+0x18));if(s.name!="SeasonInfo"&&s.name!="Franchise"&&s.name!="FranchiseServer_CareerFlow"&&s.name!="FranchiseUser"&&s.name!="Team"&&s.name!="Conference"&&s.name!="Player"&&s.name!="SeasonGame"&&s.name!="Awards"&&s.name!="Recruit")continue;auto& t=table(a);for(uint32_t row=0;row<t.rows;++row)if(!t.free.count(row))schedule(a,row);}
        for(size_t i=0;i<pending.size();++i){if(++recordCount>350000)throw std::runtime_error("Runtime record budget exceeded");auto [a,row]=pending[i];auto& t=table(a);auto v=record(t,row);records[key(t,row)]={{"key",key(t,row)},{"type",t.schema->name},{"capacity",t.rows},{"v",std::move(v)}};}
        for(const auto& [a,t]:tables){if(memory.at<Address>(a+0x38)!=t.dataAddress||memory.read(t.dataAddress,t.data.size())!=t.data)throw std::runtime_error("Dynasty changed during capture; retry");}
        if(memory.at<Address>(image+0xe1eac10)!=root||memory.at<Address>(root+0x290)!=context)throw std::runtime_error("Active Dynasty changed during capture");
        return Json{{"format",1},{"sourceKind","runtime"},{"status",before},{"context",context},{"records",std::move(records)}};
    }
};
}
