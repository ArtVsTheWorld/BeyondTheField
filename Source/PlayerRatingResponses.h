#pragma once
#include "PlayerRatingGrid.h"
namespace recruitingfog::playerfog {
enum class Surface{TopAttributes,Comparison,PlaycallSubstitution};
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
    std::vector<uintptr_t> entries;if(!view.array(root,entries,128))return 0;unsigned changed=0;
    for(auto entry:entries){
        if(surface==Surface::TopAttributes){if(ratingField(view,entry,"Value",set))++changed;continue;}
        std::map<std::string,uintptr_t> fields;if(!view.members(entry,fields))continue;
        for(const char* side:{"PlayerA","PlayerB"}){const auto found=fields.find(side);if(found!=fields.end()&&ratingField(view,found->second,"Overall",set))++changed;}
    }
    return changed;
}
}
