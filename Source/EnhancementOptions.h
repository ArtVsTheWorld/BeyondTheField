#pragma once
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <string>
#include <string_view>

namespace enhancements {
enum class GradeScale : unsigned {Letters, PlusMinus, STier, Descriptive, Blind};
struct Options {
    bool social=true,recruiting=true,roster=true;
    GradeScale scale=GradeScale::PlusMinus;
    bool colors=true;
    bool team=true;
    bool dollars=false;
    GradeScale teamScale=GradeScale::PlusMinus;
    // Retain the existing toggle bits; the extra player-scale bit and team
    // scale occupy previously unused bits. Shared payload protocol is v4.
    unsigned packed()const{return unsigned(social)|(unsigned(recruiting)<<1)|(unsigned(roster)<<2)|((unsigned(scale)&3)<<3)|(unsigned(colors)<<5)|(unsigned(team)<<6)|(unsigned(dollars)<<7)|((unsigned(scale)&4)<<6)|(unsigned(teamScale)<<9);}
    static Options unpack(unsigned bits){return {bool(bits&1),bool(bits&2),bool(bits&4),GradeScale(((bits>>3)&3)|((bits>>6)&4)),bool(bits&32),bool(bits&64),bool(bits&128),GradeScale((bits>>9)&7)};}
    static bool validBits(unsigned bits){return bits<=4095&&unsigned(unpack(bits).scale)<=4&&unsigned(unpack(bits).teamScale)<=4;}
};
inline constexpr unsigned defaultOptions=623;
inline std::atomic<unsigned> currentOptions{defaultOptions};
inline Options options(){return Options::unpack(currentOptions.load(std::memory_order_relaxed));}
inline const char* gradeLabel(int rating,GradeScale scale){
    if(rating<0||rating>100)return "?";
    if(scale==GradeScale::Blind)return u8"–";
    if(scale==GradeScale::PlusMinus){
        if(rating<60)return "F";
        if(rating>=97)return "A+";
        constexpr const char* labels[]={"D-","D","D+","C-","C","C+","B-","B","B+","A-","A","A+"};
        const auto band=(rating-60)/10;const auto digit=rating%10;
        return labels[(band>3?3:band)*3+(digit<3?0:digit<7?1:2)];
    }
    const unsigned band=rating>=90?0:rating>=80?1:rating>=70?2:rating>=60?3:4;
    constexpr const char* letters[]={"A","B","C","D","F"};
    constexpr const char* words[]={"Elite","Great","Good","Fair","Poor"};
    if(scale==GradeScale::Descriptive)return words[band];
    return scale==GradeScale::STier&&rating>=95?"S":letters[band];
}
inline int gradeColor(std::string_view label){
    label=label.substr(0,label.find(','));
    if(label=="Elite")return 0xBB70EF;if(label=="Great")return 0x529FF0;if(label=="S")return 0x409EFF;
    if(label=="Good")return 0x66CF75;if(label=="Fair")return 0xEDB34F;if(label=="Poor")return 0xEA6666;
    if(label.empty())return 0xF3F0E7;
    switch(label[0]){case 'A':return 0x1FE840;case 'B':return 0xA8D943;case 'C':return 0xFFD34D;case 'D':return 0xF68C2E;case 'F':return 0xF04444;default:return 0xF3F0E7;}
}
inline std::string ratingDisplay(int value){return gradeLabel(value,options().scale);}
inline std::string scopedRatingDisplay(int value,bool fog){return value<0||value>100?"?":fog?ratingDisplay(value):std::to_string(value);}
inline int ratingColor(int value){return gradeColor(gradeLabel(value,options().scale));}
inline bool playerColors(){return options().colors&&options().scale!=GradeScale::Blind;}
}
