#pragma once
#include <cmath>
#include <string>
#include <string_view>
#include <cstdlib>
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
    // AIO 1.4.1 may have formatted this known currency cell already. Decode
    // explicit dollars only; bare numbers remain Dynasty points.
    if(native&&options().dollars&&native[0]=='$'){
        std::string text(native+1),clean;double multiplier=1;
        if(!text.empty()&&(text.back()=='K'||text.back()=='M')){multiplier=text.back()=='K'?1000:1000000;text.pop_back();}
        for(char c:text)if(c!=',')clean+=c;
        bool digit=false,decimal=false,valid=!clean.empty();
        for(size_t i=0;i<clean.size();++i){const char c=clean[i];if(c>='0'&&c<='9')digit=true;else if(c=='.'&&!decimal)decimal=true;else if(c!='-'||i!=0)valid=false;}
        if(valid&&digit){char* end=nullptr;const auto amount=std::strtod(clean.c_str(),&end);if(end&&!*end){const auto label=dollars(amount*multiplier/4000);if(!label.empty())return label;}}
        return native;
    }
    double points=0;if(!native||!options().dollars||!pointsText(native,points))return native?native:"";
    return dollars(points);
}
}
