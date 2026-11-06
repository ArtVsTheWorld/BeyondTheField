#pragma once
#include <cmath>
#include <string>
#include <string_view>
#include "EnhancementOptions.h"

namespace enhancements::currency {
inline std::string dollars(double points){
    if(!std::isfinite(points)||std::abs(points)>1000000000.0)return {};
    const auto magnitude=std::abs(points);const std::string prefix=points<0?"-":"";
    if(magnitude==0)return "0";
    if(magnitude<250)return prefix+std::to_string(static_cast<long long>(std::round(magnitude*4)))+"K";
    const auto tenths=static_cast<long long>(std::round(magnitude/25));
    return prefix+std::to_string(tenths/10)+"."+std::to_string(tenths%10)+"M";
}
inline bool pointsText(std::string_view input,double& points){
    if(input.empty()||input.size()>16)return false;
    size_t start=input[0]=='-'?1:0;if(start==input.size())return false;
    unsigned long long value=0;unsigned digits=0,group=0;bool comma=false;
    for(size_t i=start;i<input.size();++i){
        const char c=input[i];
        if(c==','){
            if(!group||(!comma&&group>3)||(comma&&group!=3))return false;
            comma=true;group=0;continue;
        }
        if(c<'0'||c>'9'||value>1000000000)return false;
        value=value*10+unsigned(c-'0');++digits;++group;
    }
    if(!digits||(comma&&group!=3)||value>1000000000)return false;
    points=static_cast<double>(value)*(start?-1:1);return true;
}
inline std::string display(const char* native){
    double points=0;if(!native||!options().dollars||!pointsText(native,points))return native?native:"";
    return dollars(points);
}
}
