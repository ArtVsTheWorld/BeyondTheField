#pragma once
#include "PlayerRatingGrid.h"
namespace recruitingfog::playerfog {
enum class Surface{TopAttributes,Comparison,PlaycallSubstitution,RosterNIL,ContextPlayer};
template<class View,class Setter>bool ratingField(View& view,uintptr_t object,const char* key,Setter set){
    std::map<std::string,uintptr_t> fields;if(!view.members(object,fields))return false;
    const auto found=fields.find(key);if(found==fields.end())return false;
    double value=0;std::string text,label;
    if(view.number(found->second,value))label=display(Visibility::Revealed,value);
    else if(view.string(found->second,text)){int rating=0;if(!ratingText(text,rating))return false;label=display(Visibility::Revealed,rating);}
    else return false;
    if(label=="?")return false;set(object,key,label.c_str());return true;
}
// Each schema belongs to a verified UI getter. Never recursively replace
// numeric-looking values: RecordList/StatLine contain genuine statistics.
template<class View,class Setter>unsigned convert(View& view,uintptr_t root,Surface surface,Setter set){
    if(surface==Surface::PlaycallSubstitution)return ratingField(view,root,"OVR",set)?1u:0u;
    if(surface==Surface::ContextPlayer)return ratingField(view,root,"ovr",set)?1u:0u;
    if(surface==Surface::RosterNIL){
        unsigned changed=ratingField(view,root,"overall",set)?1u:0u;
        std::map<std::string,uintptr_t> fields;std::vector<uintptr_t> attributes;
        if(!view.members(root,fields)||!fields.count("attributesSubpanelInfo")||!view.array(fields.at("attributesSubpanelInfo"),attributes,32))return changed;
        for(auto attribute:attributes){
            std::map<std::string,uintptr_t> info;bool revealed=false;double value=0;
            if(!view.members(attribute,info)||!info.count("isFullyScouted")||!info.count("ratingValue")||!view.boolean(info.at("isFullyScouted"),revealed)||!revealed||!view.number(info.at("ratingValue"),value)||value<0||value>100||std::floor(value)!=value)continue;
            const auto label=display(Visibility::Revealed,value);set(attribute,"ratingValue",label.c_str());++changed;
        }
        return changed;
    }
    std::vector<uintptr_t> entries;if(!view.array(root,entries,128))return 0;unsigned changed=0;
    for(auto entry:entries){
        if(surface==Surface::TopAttributes){if(ratingField(view,entry,"Value",set))++changed;continue;}
        std::map<std::string,uintptr_t> fields;if(!view.members(entry,fields))continue;
        for(const char* side:{"PlayerA","PlayerB"}){const auto found=fields.find(side);if(found!=fields.end()&&ratingField(view,found->second,"Overall",set))++changed;}
    }
    return changed;
}
}
