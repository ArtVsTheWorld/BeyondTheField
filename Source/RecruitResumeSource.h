#pragma once
#include "RecruitResumeNotes.h"
#include "RecruitResumeStateRanks.h"
#include <windows.h>
#include <bcrypt.h>
#include <filesystem>
#include <fstream>
#include <memory>
#pragma comment(lib,"bcrypt.lib")
namespace recruitingfog::resume {
inline std::string digest(const std::string& text){
    BCRYPT_ALG_HANDLE algorithm=nullptr;BCRYPT_HASH_HANDLE handle=nullptr;
    if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)throw std::runtime_error("SHA256 unavailable");
    unsigned char bytes[32]{};const auto opened=BCryptCreateHash(algorithm,&handle,nullptr,0,nullptr,0,0);
    auto status=opened;if(status>=0)status=BCryptHashData(handle,reinterpret_cast<PUCHAR>(const_cast<char*>(text.data())),static_cast<ULONG>(text.size()),0);if(status>=0)status=BCryptFinishHash(handle,bytes,32,0);
    if(handle)BCryptDestroyHash(handle);BCryptCloseAlgorithmProvider(algorithm,0);if(status<0)throw std::runtime_error("Cannot create resume identity");
    static constexpr char digits[]="0123456789abcdef";std::string out;for(auto b:bytes){out+=digits[b>>4];out+=digits[b&15];}return out;
}
inline std::string identity(const std::string& league,const Json& v){
    if(!v.contains("PresentationId")||!v.at("PresentationId").is_number_integer()||v.at("PresentationId").get<int64_t>()<=0)throw std::runtime_error("No persistent recruit presentation identity");
    const auto birth=v.value("PLYR_BIRTHDATE",int64_t(0));
    return digest(Json::array({league,v.at("PresentationId"),v.at("FirstName"),v.at("LastName"),v.at("PLYR_HOME_TOWN"),v.at("PLYR_HOME_STATE"),birth>0?Json(birth):Json(nullptr)}).dump());
}
struct NativeEntry {uint32_t nativeId=0;std::string first,last,identity;bool highSchool=false;Prospect prospect;Json saved;};
struct NativeClass {std::string league;int season=0;std::map<uint32_t,NativeEntry> entries;};
inline NativeClass parseNativeClass(const Json& raw){
    if(raw.at("format")!=1||raw.at("sourceKind")!="runtime")throw std::runtime_error("Not a native resume snapshot");
    NativeClass result;result.league=std::to_string(static_cast<uint32_t>(raw.at("status").at("league").get<int64_t>()));result.season=raw.at("status").at("season").at("CurrentSeasonYear");
    if(result.season<1800||result.season>3000)throw std::runtime_error("Invalid resume season");
    std::set<std::string> identities;const auto& records=raw.at("records");
    for(const auto& row:records){
        if(row.at("type")!="Recruit"||row.at("capacity").get<unsigned>()<=1)continue;
        const auto& r=row.at("v");if(r.at("Player").is_null())continue;const auto& v=records.at(r.at("Player").get<std::string>()).at("v");
        const auto key=row.at("key").get<std::string>();const auto colon=key.find(':');if(colon==std::string::npos)throw std::runtime_error("Invalid recruit record key");
        const auto table=std::stoull(key.substr(0,colon)),index=std::stoull(key.substr(colon+1));if(table>=16384||index>=131072)throw std::runtime_error("Recruit key exceeds native bounds");
        NativeEntry entry;entry.nativeId=static_cast<uint32_t>(table*131072+index);entry.first=v.at("FirstName");entry.last=v.at("LastName");entry.highSchool=r.at("Class")=="HighSchool";
        if(entry.highSchool){
            Prospect p;p.identity=identity(result.league,v);p.name=entry.first+" "+entry.last;p.position=v.at("Position");p.state=v.at("PLYR_HOME_STATE");p.town=v.at("PLYR_HOME_TOWN");p.development=v.at("TraitDevelopment");p.stateRank=stateRank(p.state);
            const std::map<std::string,int> stars={{"ONE_STAR",1},{"TWO_STAR",2},{"THREE_STAR",3},{"FOUR_STAR",4},{"FIVE_STAR",5}};p.stars=stars.at(v.at("ProspectStarRating").get<std::string>());
            for(auto it=v.begin();it!=v.end();++it)if(it.key().size()>=6&&it.key().substr(it.key().size()-6)=="Rating"&&it.value().is_number())p.ratings[it.key()]=it.value().get<double>();
            if(!identities.insert(p.identity).second)throw std::runtime_error("Duplicate recruit identity");entry.identity=p.identity;entry.prospect=std::move(p);
        }
        if(!result.entries.emplace(entry.nativeId,std::move(entry)).second)throw std::runtime_error("Duplicate native recruit serial");
    }
    if(result.entries.empty()||result.entries.size()>16000)throw std::runtime_error("Native recruit class unavailable or oversized");return result;
}
inline Json loadJournal(const std::filesystem::path& file,const std::string& league){
    if(!std::filesystem::exists(file))return {{"format",1},{"league",league},{"entries",Json::object()}};
    if(std::filesystem::file_size(file)>16u*1024*1024)throw std::runtime_error("Resume journal exceeds bounds");
    std::ifstream in(file,std::ios::binary);Json data;in>>data;if(!in||data.at("format")!=1||data.at("league")!=league||!data.at("entries").is_object()||data.at("entries").size()>16000)throw std::runtime_error("Unsupported resume journal");
    for(const auto& v:data.at("entries")){if(v.at("modelVersion")!=2)throw std::runtime_error("Unsupported saved resume model");validate(v);}return data;
}
inline void persistClass(NativeClass& c,const std::filesystem::path& root){
    const auto folder=root/L"RecruitResumeHistory"/c.league;std::filesystem::create_directories(folder);
    const auto path=folder/(std::to_string(c.season)+".json");auto data=loadJournal(path,c.league);const auto previous=loadJournal(folder/(std::to_string(c.season-1)+".json"),c.league);bool dirty=false;
    for(auto& [id,entry]:c.entries){(void)id;if(!entry.highSchool)continue;
        if(data["entries"].contains(entry.identity))entry.saved=data["entries"].at(entry.identity);
        else if(previous.at("entries").contains(entry.identity))entry.saved=previous.at("entries").at(entry.identity);
        else{entry.saved=generate(entry.prospect).publicData;validate(entry.saved);data["entries"][entry.identity]=entry.saved;dirty=true;}
    }
    if(dirty){const auto text=data.dump();if(text.size()>16u*1024*1024)throw std::runtime_error("Resume journal exceeds write bounds");auto temp=path;temp+=L".tmp";{std::ofstream out(temp,std::ios::binary|std::ios::trunc);out<<text;out.flush();if(!out)throw std::runtime_error("Cannot write resume journal");}
        if(!MoveFileExW(temp.c_str(),path.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))throw std::runtime_error("Cannot atomically publish resume journal");}
}
}
