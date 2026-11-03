#pragma once
#include <memory>
#include <string>
#include <vector>
#include <map>
#include <array>
#include <algorithm>
#include <string_view>
#include "FeedRefresh.h"
namespace social {
struct FeedPost {std::string author,handle,body,stamp;int imageLibrary=79,imageValue=598;std::string category,voice,replyTo;bool transaction=false;int likes=-1,uniformTeamLogo=-1,draftPick=-1,draftRound=0;FeedPost(std::string a,std::string h,std::string b,std::string s,int l=79,int v=598):author(std::move(a)),handle(std::move(h)),body(std::move(b)),stamp(std::move(s)),imageLibrary(l),imageValue(v){};};
inline std::string compactCount(int value){
    if(value<1000)return std::to_string(value);
    const int unit=value>=999950?1000000:1000;const auto tenths=(static_cast<long long>(value)*10+unit/2)/unit;
    auto out=std::to_string(tenths/10);if(tenths%10)out+="."+std::to_string(tenths%10);return out+(unit==1000000?"M":"K");
}
inline std::string storyLabel(const nlohmann::json& post){
    if(post.contains("replyTo"))return "Reply";
    const auto category=post.value("category",std::string());
    if(category=="draft-discourse")return "Draft";
    if(category=="draft")return post.contains("draftRound")?"Round "+std::to_string(post.at("draftRound").get<int>())+" - Pick "+std::to_string(post.at("draftPick").get<int>()):"Draft";
    if(category=="offseason")return "Offseason";
    if(category=="upsets")return "Upset";
    if(category=="conference-talk")return "Conference Talk";
    if(category=="transactions")return "Transaction";
    if(category=="signings")return "Signing";
    if(category=="coaching")return "Coaching";
    if(category=="postseason")return "Postseason";
    if(category=="season-end")return "Season Review";
    if(category=="matchup-preview")return "Matchup";
    if(category=="matchup-recap")return "Matchup Recap";
    if(category=="history")return "Milestone";
    if(category=="championship")return "Title Race";
    if(category=="bowls")return "Bowl Watch";
    if(category=="records")return "Record Book";
    if(category=="streaks")return "Streak";
    if(category=="analytics")return "Analysis";
    if(category=="preseason")return "Preseason";
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
inline constexpr std::array<const char*,4> scopeLabels={"For You","National","Conference","My Team"};
struct Scope {std::string key,label;};
struct Edition {std::string key,label,conference,phase="RegularSeason";int season=0,week=0;std::map<std::string,FeedPost> stories;std::map<std::string,std::vector<std::string>> views;};
struct Catalog {std::vector<Edition> weeks;size_t active=0;std::vector<Scope> scopes;};
struct Feed {std::vector<FeedPost> posts;std::string key="runtime-waiting",label="Social Media";std::shared_ptr<const Catalog> catalog;size_t edition=0;unsigned scope=0,type=0;size_t page=0,pages=1,total=0,offset=0;};
inline const std::vector<Scope>& scopesFor(const Catalog& c){static const std::vector<Scope> legacy={{"all","For You"},{"national","National"},{"conference","Conference"},{"team","My Team"}};return c.scopes.empty()?legacy:c.scopes;}
inline size_t scopeLimit(const std::string& key){return key=="all"?30:key=="national"?100:key=="conference"||key.rfind("conference:",0)==0?60:20;}
inline constexpr std::array<const char*,12> typeLabels={"All Types","Recruiting","Recaps","Upcoming","Rankings & Awards","Analysts","Beat Reporters","Official Accounts","Players","Injuries","Fans","Transactions"};
inline bool matchesType(const FeedPost& p,unsigned type){switch(type){case 0:return true;case 1:return p.category=="recruiting"||p.category=="offers"||p.category=="signings"||p.voice=="recruit";case 2:return p.category=="results"||p.category=="team-stats"||p.category=="player-stats"||p.category=="upsets"||p.category=="streaks"||p.category=="matchup-recap"||p.category=="season-end";case 3:return p.category=="schedule"||p.category=="watch"||p.category=="lines"||p.category=="preseason"||p.category=="matchup-preview"||p.category=="offseason";case 4:return p.category=="polls"||p.category=="heisman"||p.category=="cfp"||p.category=="awards"||p.category=="records"||p.category=="history"||p.category=="championship"||p.category=="bowls";case 5:return p.voice=="analyst"||p.voice=="model";case 6:return p.voice=="beat";case 7:return p.voice=="official"||p.voice=="cfp"||p.voice=="nflDraft";case 8:return p.voice=="player";case 9:return p.category=="injuries";case 10:return p.voice=="fan";case 11:return p.transaction||(p.category=="coaching"||p.category=="nil"||p.category=="transactions"||p.category=="transfer"||p.category=="signings")&&(p.voice=="analyst"||p.voice=="beat");default:return false;}}
// System status is the only fallback; there are no illustrative tweet cards.
inline std::shared_ptr<const Feed> statusFeed(unsigned count=1){
    auto f=std::make_shared<Feed>();
    for(unsigned n=0;n<count;++n)f->posts.push_back({"Dynasty Enhancer","@DynastyEnhancer","Preparing news for the active Dynasty. Return to the hub briefly, then reopen Social Media.","Status",79,598});
    return f;
}
inline std::shared_ptr<const Feed> selectFeed(std::shared_ptr<const Catalog> catalog,size_t week,unsigned scope,unsigned type=0,size_t page=0){
    if(!catalog||week>=catalog->weeks.size()||scope>=scopesFor(*catalog).size()||type>=typeLabels.size())throw std::runtime_error("Invalid single-week feed selection");
    const auto& e=catalog->weeks.at(week);auto f=std::make_shared<Feed>();f->catalog=catalog;f->edition=week;f->scope=scope;f->type=type;f->key=e.key;
    f->label="Social Media";if(type)f->label+=" - "+std::string(typeLabels[type]);
    const auto& option=scopesFor(*catalog).at(scope);const auto view=e.views.find(option.key=="all"?(type&&e.views.count("all:expanded")?"all:expanded":!type&&e.views.count("all:default")?"all:default":"all"):option.key);auto limit=type?30:scopeLimit(option.key);
    if(view!=e.views.end()){
        std::set<std::string> members(view->second.begin(),view->second.end()),visited;std::vector<std::string> roots;std::map<std::string,std::vector<std::string>> children;
        for(const auto& id:view->second){const auto& p=e.stories.at(id);if(p.replyTo.empty()){if(matchesType(p,type))roots.push_back(id);}else if(members.count(p.replyTo))children[p.replyTo].push_back(id);}
        if(type==11){
            const bool draft=std::any_of(roots.begin(),roots.end(),[&](const auto& id){return e.stories.at(id).draftPick>0;});
            if(draft){std::stable_sort(roots.begin(),roots.end(),[&](const auto& a,const auto& b){const auto x=e.stories.at(a).draftPick,y=e.stories.at(b).draftPick;return x>0&&y>0?x<y:x>0&&y<=0;});}
        }
        // Build whole conversation blocks first. Page boundaries never strand
        // a reply or erase later factual announcements from a dedicated view.
        std::vector<std::vector<FeedPost>> pages(1);
        for(const auto& root:roots){std::vector<FeedPost> block;
            std::function<void(const std::string&)> visit=[&](const std::string& id){if(!visited.insert(id).second)return;block.push_back(e.stories.at(id));for(const auto& child:children[id])visit(child);};visit(root);
            if(!pages.back().empty()&&pages.back().size()+block.size()>limit)pages.emplace_back();
            pages.back().insert(pages.back().end(),block.begin(),block.end());f->total+=block.size();
        }
        f->pages=pages.size();f->page=(std::min)(page,pages.size()-1);
        for(size_t i=0;i<f->page;++i)f->offset+=pages[i].size();f->posts=std::move(pages[f->page]);

    }
    if(f->pages>1)f->label+=" | "+std::to_string(f->page+1)+"/"+std::to_string(f->pages)+" (LT: Pages)";
    if(f->posts.empty())f->posts.push_back({"Dynasty Enhancer","@DynastyEnhancer","No "+option.label+" stories were published in this weekly edition.","News",79,598});
    return f;
}
inline std::shared_ptr<const Feed> decodeFeed(const nlohmann::json& j){
    auto catalog=std::make_shared<Catalog>();
    if(j.contains("scopeOptions"))for(const auto& o:j.at("scopeOptions"))catalog->scopes.push_back({o.at("key").get<std::string>(),o.at("label").get<std::string>()});
    for(const auto& w:j.at("weeks")){
        Edition e;e.key=w.at("key").get<std::string>();e.week=w.at("week").get<int>();e.season=w.at("season").get<int>();e.conference=w.value("conference",nlohmann::json()).is_string()?w.at("conference").get<std::string>():"";
        e.phase=w.value("phase",std::string("RegularSeason"));
        e.label=e.phase=="PreSeason"?"Preseason, "+std::to_string(e.season):e.phase=="RegularSeason"?"Week "+std::to_string(e.week)+", "+std::to_string(e.season):e.phase+" - Week "+std::to_string(e.week)+", "+std::to_string(e.season);
        if(w.value("reconstructed",false))e.label+=" (recovered)";
        for(const auto& p:w.at("stories")){
            const auto stamp=storyLabel(p);
            FeedPost post{p.at("author").get<std::string>(),p.at("handle").get<std::string>(),p.at("body").get<std::string>(),stamp,p.at("imageLibrary").get<int>(),p.at("imageValue").get<int>()};post.category=p.value("category",std::string());post.voice=p.value("voice",std::string());post.replyTo=p.value("replyTo",std::string());post.likes=p.value("likes",-1);post.uniformTeamLogo=p.value("uniformTeamLogo",-1);post.transaction=p.value("transaction",false);post.draftPick=p.value("draftPick",-1);post.draftRound=p.value("draftRound",0);e.stories.emplace(p.at("id").get<std::string>(),std::move(post));
        }
        for(const auto& [key,view]:w.at("views").items())e.views[key]=view.get<std::vector<std::string>>();
        catalog->weeks.push_back(std::move(e));
    }
    std::sort(catalog->weeks.begin(),catalog->weeks.end(),[](const Edition& a,const Edition& b){return refresh::phaseIndex(a.phase)!=refresh::phaseIndex(b.phase)?refresh::phaseIndex(a.phase)<refresh::phaseIndex(b.phase):a.week<b.week;});
    const auto activeKey=j.at("activeWeekKey").get<std::string>();
    const auto active=std::find_if(catalog->weeks.begin(),catalog->weeks.end(),[&](const Edition& e){return e.key==activeKey;});
    if(active==catalog->weeks.end())throw std::runtime_error("Active publication week is missing");
    catalog->active=static_cast<size_t>(active-catalog->weeks.begin());
    return selectFeed(catalog,catalog->active,0);
}
}
