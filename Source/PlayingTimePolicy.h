#pragma once
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cstdint>

namespace recruitingfog {
enum class PlayingTimeSurface { RecruitList, Motivations, SchoolPitch, PitchSummary, Pitches, PitchGrid, VisitActivities, VisitGrid, VisitSummary, SchoolGrid, SchoolModule };
struct PlayingTimeStats {unsigned grades=0,dealbreakers=0,previews=0,unsupported=0;};
// The verified native motivation enum is 9. My School's separately ordered
// tile index is 13. Neither is a player rating or a derived roster comparison.
constexpr unsigned playingTimeMotivation=9,playingTimeSchoolTile=13;

template<class View,class StringSetter,class NumberSetter>
PlayingTimeStats maskPlayingTime(View& view,uintptr_t root,PlayingTimeSurface surface,unsigned selection,
                                const std::set<unsigned>& playingTimePitches,StringSetter setString,NumberSetter setNumber){
    PlayingTimeStats stats;unsigned visited=0;std::set<uintptr_t> seen;
    if((surface==PlayingTimeSurface::SchoolModule||surface==PlayingTimeSurface::SchoolPitch)&&selection!=playingTimeSchoolTile)return stats;
    auto walk=[&](auto&& self,uintptr_t at,unsigned depth,bool schoolContext)->void {
        if(depth>7||++visited>4096){++stats.unsupported;return;}
        const auto kind=view.kind(at);
        if(kind!=4&&kind!=5){if(depth==0)++stats.unsupported;return;}
        if(!seen.insert(at).second)return;
        if(kind==4){std::vector<uintptr_t> items;if(!view.array(at,items,512)){++stats.unsupported;return;}for(auto item:items)self(self,item,depth+1,schoolContext);return;}
        std::map<std::string,uintptr_t> fields;if(!view.members(at,fields)){++stats.unsupported;return;}
        std::vector<uintptr_t> children;
        for(const auto& field:fields){const auto childKind=view.kind(field.second);if(childKind==4||childKind==5)children.push_back(field.second);}
        auto named=[&](const char* key){std::string label;return fields.count(key)&&view.string(fields.at(key),label)&&label=="Playing Time";};
        bool direct=named("MotivationString")||named("Name")||named("PitchName")||named("Motivation");
        double motivation=0;
        if(fields.count("Motivation")&&view.number(fields.at("Motivation"),motivation)&&motivation==playingTimeMotivation)direct=true;
        if(named("RecruitingMotivation")){
            // Both labels use the widget's existing unknown-grade sentinel.
            // Preserve Locked, IsDealbreakerViolated and every native action ID.
            for(const auto key:{"DealbreakerTeamGrade","DealbreakerTeamLevel"})if(fields.count(key)){setNumber(at,key,255);++stats.dealbreakers;}
        }
        bool bundle=false;double pitch=0;
        if((surface==PlayingTimeSurface::PitchGrid||surface==PlayingTimeSurface::Pitches)&&fields.count("PitchTypeID")&&view.number(fields.at("PitchTypeID"),pitch)&&pitch>=0&&pitch<=255&&pitch==static_cast<unsigned>(pitch))bundle=playingTimePitches.count(static_cast<unsigned>(pitch))!=0;
        if((direct||bundle||schoolContext)&&fields.count("Grade")){setString(at,"Grade","?");++stats.grades;}
        if(direct&&surface==PlayingTimeSurface::VisitActivities){
            // These are UI-only estimates derived from the same hidden grade.
            // Removing their meters prevents the preview becoming a second
            // ranking tool. Native earned influence and action logic are intact.
            for(const auto key:{"Triangles","MaxInfluenceTriangles","MinInfluenceTriangles","InfluenceArrowsTotal"})if(fields.count(key)){setNumber(at,key,0);++stats.previews;}
        }
        if(bundle&&surface==PlayingTimeSurface::Pitches){
            if(fields.count("Gain")){setString(at,"Gain","?");++stats.previews;}
            for(const auto key:{"InfluenceArrows","InfluenceArrowsMax"})if(fields.count(key)){setNumber(at,key,0);++stats.previews;}
        }
        if(surface==PlayingTimeSurface::RecruitList||surface==PlayingTimeSurface::SchoolPitch)return; // never walk player attributes/other school data
        for(auto child:children)self(self,child,depth+1,schoolContext);
    };
    walk(walk,root,0,surface==PlayingTimeSurface::SchoolModule&&selection==playingTimeSchoolTile);
    return stats;
}
}
