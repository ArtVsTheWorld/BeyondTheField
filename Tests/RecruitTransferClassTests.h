#pragma once
#include "../Source/RecruitResumeSource.h"
namespace recruitingfog::resume {
inline void transferClassLabelTests(){
    for(const auto* year:{"FR","SO","JR","SR"})for(bool redshirt:{false,true}){
        NativeEntry transfer;transfer.classYear=year;transfer.redshirt=redshirt;
        const auto expected="TR ("+std::string(year)+(redshirt?" RS)":")");
        if(nativeTransferClass(transfer)!=expected)throw std::runtime_error("Transfer profile lost compact TR/year/RS format");
        for(const auto& original:{"Transfer ("+std::string(year)+")","Transfer("+std::string(year)+")","TR ("+std::string(year)+")"})
            if(nativeRecruitClassLabel(transfer,original.c_str())!=expected)throw std::runtime_error("Transfer class column differs from profile format");
        if(!nativeRecruitClassLabel(transfer,"HS").empty()||!nativeRecruitClassLabel(transfer,nullptr).empty())throw std::runtime_error("Transfer class adapter changed an unrelated/unknown label");
        transfer.highSchool=true;if(!nativeTransferClass(transfer).empty()||!nativeRecruitClassLabel(transfer,("Transfer ("+std::string(year)+")").c_str()).empty())throw std::runtime_error("High-school label was formatted as a transfer");
        transfer.highSchool=false;transfer.juniorCollege=true;
        for(const auto* level:{"D3","D2","FCS"}){
            transfer.saved={{"competitionClass",level}};const auto original="JC ("+std::string(year)+")";
            if(!nativeTransferClass(transfer).empty()||nativeRecruitClassLabel(transfer,original.c_str())!=std::string(level)+" ("+year+")")throw std::runtime_error("Compact transfer format changed a JUCO association");
        }
    }
    NativeEntry unknown;if(!nativeTransferClass(unknown).empty()||!nativeRecruitClassLabel(unknown,"Transfer (JR)").empty())throw std::runtime_error("Missing transfer class year was fabricated");
}
}
