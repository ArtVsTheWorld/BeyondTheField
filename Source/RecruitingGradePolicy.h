#pragma once
#include <cmath>
#include <string>

namespace recruitingfog {
enum class Visibility {Unknown, Revealed, Range};
inline char grade(int rating){return rating>=90?'A':rating>=80?'B':rating>=70?'C':rating>=60?'D':'F';}
inline std::string display(Visibility visibility,double value,double low=0,double high=100){
    if(visibility==Visibility::Unknown)return "?";
    if(visibility==Visibility::Revealed){
        if(!std::isfinite(value)||value<0||value>100||value!=std::floor(value))return "?";
        return std::string(1,grade(static_cast<int>(value)));
    }
    if(!std::isfinite(low)||!std::isfinite(high)||low<0||high>100||low>high)return "?";
    const auto first=grade(static_cast<int>(std::floor(low))),last=grade(static_cast<int>(std::ceil(high)));
    return first==last?std::string(1,first):std::string(1,first)+u8"–"+last;
}
}
