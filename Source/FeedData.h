#pragma once
#include <memory>
#include <string>
#include <vector>
#include <map>
#include <array>
#include <algorithm>
#include <string_view>
#include "SamplePosts.h"
#include "FeedRefresh.h"
namespace social {
struct FeedPost {std::string author,handle,body,stamp;int imageLibrary=79,imageValue=598;};
inline std::string storyLabel(const nlohmann::json& post){
    const auto category=post.value("category",std::string());
    if(category=="results"||category=="team-stats"||category=="player-stats")return "Recap";
    if(category=="recruiting"||category=="offers")return "Recruiting";
    if(category=="schedule")return "Upcoming";
    if(category=="polls")return "Rankings";
    if(category=="heisman")return "Heisman";
    if(category=="cfp")return "Playoff Watch";
    if(category=="injuries")return "Injury Report";
    if(category=="standings")return "Standings";
    if(category=="watch")return "Spotlight";
    if(category=="lines")return "Odds";
    if(category=="holiday")return "Calendar";
    if(category=="awards")return "Awards";
    if(category=="nil")return "NIL";
    if(category=="transfer")return "Transfers";
    if(category=="depth-chart")return "Roster";
    return "News";
}
// The native multiline body now spans the available 1065 layout pixels.
// Conservative glyph widths and 36-pixel lines leave breathing room without
// truncating the text or reducing its font size. Long words/newlines count too.
inline int postHeight(std::string_view body){
    constexpr int width=1065;int lines=1,line=0,word=0;
    auto flush=[&](){if(!word)return;if(line&&line+8+word>width){++lines;line=0;}if(line)line+=8;while(word>width){++lines;word-=width;}line+=word;word=0;};
    for(size_t i=0;i<body.size();){
        auto ch=static_cast<unsigned char>(body[i++]);
        if(ch==' '||ch=='\t'||ch=='\n'||ch=='\r'){flush();if(ch=='\n'){++lines;line=0;}continue;}
        if(ch>=128){while(i<body.size()&&(static_cast<unsigned char>(body[i])&0xc0)==0x80)++i;word+=32;continue;}
        if(ch=='W'||ch=='M')word+=28;
        else if(ch=='w'||ch=='m'||ch=='@')word+=24;
        else if(ch=='i'||ch=='l'||ch=='I'||ch=='.'||ch==','||ch=='!'||ch=='\''||ch==':'||ch==';')word+=8;
        else if(ch>='A'&&ch<='Z')word+=20;
        else word+=16;
    }
    flush();return (std::max)(160,((68+lines*36+15)/16)*16);
}
inline constexpr std::array<const char*,4> scopeKeys={"all","national","conference","team"};
inline constexpr std::array<const char*,4> scopeLabels={"All Posts","National","Conference","My Team"};
struct Edition {std::string key,label,conference;int season=0,week=0;std::map<std::string,FeedPost> stories;std::array<std::vector<std::string>,4> views;};
struct Catalog {std::vector<Edition> weeks;size_t active=0;};
struct Feed {std::vector<FeedPost> posts;std::string key="prototype",label="Social Media";std::shared_ptr<const Catalog> catalog;size_t edition=0;unsigned scope=0;};
inline std::shared_ptr<const Feed> sampleFeed(unsigned count){
    auto f=std::make_shared<Feed>();
    for(unsigned n=0;n<count;++n){const auto& p=samplePosts[n%samplePosts.size()];f->posts.push_back({p.author,p.handle,p.body,"Sample post "+std::to_string(n+1),p.imageLibrary,p.imageValue});}
    return f;
}
inline std::shared_ptr<const Feed> selectFeed(std::shared_ptr<const Catalog> catalog,size_t week,unsigned scope){
    if(!catalog||week>=catalog->weeks.size()||scope>=scopeKeys.size())throw std::runtime_error("Invalid single-week feed selection");
    const auto& e=catalog->weeks.at(week);auto f=std::make_shared<Feed>();f->catalog=catalog;f->edition=week;f->scope=scope;f->key=e.key;
    f->label="Social Media";
    for(const auto& id:e.views[scope])f->posts.push_back(e.stories.at(id));
    if(f->posts.empty())f->posts.push_back({"Campus Football Wire","@CampusFBWire","No "+std::string(scopeLabels[scope])+" stories were published in this weekly edition.","News",79,598});
    return f;
}
inline std::shared_ptr<const Feed> decodeFeed(const nlohmann::json& j){
    auto catalog=std::make_shared<Catalog>();
    for(const auto& w:j.at("weeks")){
        Edition e;e.key=w.at("key").get<std::string>();e.week=w.at("week").get<int>();e.season=w.at("season").get<int>();e.conference=w.value("conference",nlohmann::json()).is_string()?w.at("conference").get<std::string>():"";
        e.label="Week "+std::to_string(e.week)+", "+std::to_string(e.season);
        for(const auto& p:w.at("stories")){
            const auto stamp=storyLabel(p);
            e.stories.emplace(p.at("id").get<std::string>(),FeedPost{p.at("author").get<std::string>(),p.at("handle").get<std::string>(),p.at("body").get<std::string>(),stamp,p.at("imageLibrary").get<int>(),p.at("imageValue").get<int>()});
        }
        for(unsigned scope=0;scope<scopeKeys.size();++scope)e.views[scope]=w.at("views").at(scopeKeys[scope]).get<std::vector<std::string>>();
        catalog->weeks.push_back(std::move(e));
    }
    std::sort(catalog->weeks.begin(),catalog->weeks.end(),[](const Edition& a,const Edition& b){return a.week<b.week;});
    const auto activeKey=j.at("activeWeekKey").get<std::string>();
    const auto active=std::find_if(catalog->weeks.begin(),catalog->weeks.end(),[&](const Edition& e){return e.key==activeKey;});
    if(active==catalog->weeks.end())throw std::runtime_error("Active publication week is missing");
    catalog->active=static_cast<size_t>(active-catalog->weeks.begin());
    return selectFeed(catalog,catalog->active,0);
}
}
