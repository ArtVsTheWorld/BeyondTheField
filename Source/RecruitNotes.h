#pragma once
#include <algorithm>
#include <cctype>
#include <map>
#include <string>
#include <vector>
#include <cstdint>
#include <cmath>

namespace recruitingfog {
inline uint64_t notesHash(const std::string& text){uint64_t hash=14695981039346656037ull;for(unsigned char c:text){hash^=c;hash*=1099511628211ull;}return hash;}
inline std::string notesKey(std::string text){while(!text.empty()&&text.back()==' ')text.pop_back();for(auto& c:text)c=static_cast<char>(std::tolower(static_cast<unsigned char>(c)));return text;}
struct NotesObservation {std::string name;double low=0,high=0;bool exact=false;};
struct NotesProspect {std::string identity,position,tendency,hometown,classification;double progress=0;std::vector<NotesObservation> observations;};
struct NotesLanguage {const char* attribute;const char* strong;const char* developing;};
inline constexpr NotesLanguage notesLanguage[]={
    {"throw power","There is real zip on his throws, including when he has to reach the far sideline.","The deep and opposite-hash throws will need a closer look before the staff builds around them."},
    {"short accuracy","Quick-game placement is one of the cleaner parts of his passing tape.","The short-game placement still needs to become more dependable."},
    {"medium accuracy","He gives receivers a good chance to stay in stride on intermediate routes.","Intermediate placement is still a part of his game the staff wants to sharpen."},
    {"deep accuracy","His deep ball gives the receiver a chance to make a play without constantly having to adjust.","Deep-ball placement remains a development point."},
    {"throw on run","He looks comfortable delivering the ball without having a perfectly set base.","The passing mechanics become less settled once he is moving."},
    {"under pressure","The pocket can get crowded without his passing mechanics immediately unraveling.","Pressure can hurry his delivery and take him out of his preferred rhythm."},
    {"break sack","He has a knack for keeping a play alive when a defender gets to him.","Escaping a clean hit in the pocket is not something the staff should count on yet."},
    {"awareness","He seems to process what is developing in front of him quickly.","Recognition and anticipation are areas for the staff to bring along."},
    {"speed","His straight-line pace stands out when there is space to open up.","He is more likely to win with positioning and timing than simply outrun everyone."},
    {"acceleration","He gets into his stride quickly rather than needing a long runway.","It takes him a little time to get going; the first few steps are a development point."},
    {"agility","There is some natural ease to the way he redirects and works in tight spaces.","Sudden changes of direction are less comfortable than playing on a straight track."},
    {"change of direction","He can put a foot in the ground and redirect without losing much of his momentum.","He is still working toward cleaner, more efficient changes of direction."},
    {"strength","He has the physical base to hold his ground when the play turns into a contest of strength.","Adding functional strength should be part of his development plan."},
    {"catching","His hands look dependable when the ball reaches him.","Making the routine catch consistently needs more work."},
    {"catch in traffic","He stays involved at the catch point even when a defender is arriving with the ball.","Contested catches are not yet a dependable part of his game."},
    {"spectacular catch","He can adjust to a difficult ball rather than needing every throw put right on him.","He is more comfortable with a clean target than a difficult adjustment at the catch point."},
    {"short route running","His short routes have the sort of detail that can help him find a little separation.","There is room to become more precise at the top of shorter routes."},
    {"medium route running","He understands how to set up the break on intermediate routes.","The intermediate route work still needs polish."},
    {"deep route running","He has a feel for creating an opening when the route takes him downfield.","His downfield route setup is still a work in progress."},
    {"carrying","Ball security looks like a dependable part of his current game.","Protecting the ball through contact deserves attention in practice."},
    {"break tackle","He can keep his feet and make the first tackle attempt less than straightforward.","He will need to make more of the first contact rather than expecting to run through it."},
    {"trucking","He is comfortable taking the direct route through contact.","Running through a square hit is less reliable than finding the clean lane."},
    {"elusiveness","He has a way of making a defender take a second try in space.","Making an unblocked defender miss is still a part of his game to develop."},
    {"run block","There is a useful physical foundation to his work in the run game.","He needs to become more consistent at sustaining blocks in the run game."},
    {"run block power","He can move a defender when the assignment calls for a direct, physical block.","Creating movement on power runs is still a development point."},
    {"run block finesse","His movement and positioning can help him find leverage on run blocks.","The angles and positioning on movement blocks still need work."},
    {"pass block","His pass-protection work gives the staff something dependable to build on.","Pass protection will need attention before he is asked to handle difficult assignments alone."},
    {"pass block power","He has a useful anchor against a direct power rush.","A strong bull rush can put his anchor under stress."},
    {"pass block finesse","He looks comfortable dealing with a rusher who tries to win with movement.","Quick counters and changes of direction can test his pass-protection footwork."},
    {"impact blocking","When he gets square to a defender, the contact can change the play.","He needs to make his contact count more consistently."},
    {"tackle","He has a dependable finishing foundation when he reaches the ball carrier.","Finishing the tackle cleanly is an area for the staff to emphasize."},
    {"tackling","He has a dependable finishing foundation when he reaches the ball carrier.","Finishing the tackle cleanly is an area for the staff to emphasize."},
    {"hit power","There is a physical edge to the way he arrives at the ball.","Positioning and a secure finish matter more for him than chasing a big collision."},
    {"block shedding","He can separate from contact and get himself back into the play.","Getting clear of a well-positioned blocker remains a development point."},
    {"power moves","There is some force behind the way he attacks a blocker.","He needs more dependable answers when the rush becomes a contest of strength."},
    {"finesse moves","He has a feel for winning a rush with his hands and a change of angle.","His pass-rush counters still need to become more varied and dependable."},
    {"pursuit","He takes useful angles once the ball declares itself.","He needs to tighten up his pursuit angles rather than leave himself chasing the play."},
    {"play recognition","He seems comfortable sorting through the action rather than reacting late to everything.","Play recognition is still catching up with the physical side of his game."},
    {"man coverage","He has the movement and feel to stay involved in a receiver's route.","Staying connected through a receiver's breaks is still a development point."},
    {"zone coverage","He looks comfortable working with space and keeping the play in front of him.","His spacing and awareness within a zone still need work."},
    {"press","He can disrupt a clean release rather than give every receiver an easy start.","The technique at the line of scrimmage still needs to become more dependable."},
    {"kick power","There is useful distance in his leg when he strikes the ball cleanly.","The staff should be careful about asking for distance before the strike becomes more dependable."},
    {"kick accuracy","The placement gives the staff a dependable starting point.","Placement and repeatability deserve more attention than simply chasing distance."}
};
inline std::string makeRecruitNotes(const NotesProspect& prospect){
    const auto seed=notesHash(prospect.identity);const auto pos=notesKey(prospect.position);
    const auto progress=std::isfinite(prospect.progress)&&prospect.progress>=0&&prospect.progress<=100?prospect.progress:0;
    const char* profile="The early profile offers a starting point, but the staff still needs to see how it holds up against different competition.";
    const char* focus="Look for whether his technique stays consistent when the assignment gets more difficult.";
    if(pos=="qb"){profile="The first look should separate the throws he is comfortable with from the ones the offense would have to develop.";focus="Watch what happens after the first read is covered, rather than judging only the clean-pocket throws.";}
    else if(pos=="hb"||pos=="rb"||pos=="fb"){profile="The running style is worth watching alongside the blocking in front of him; a clean lane does not tell the whole story.";focus="Look for what he creates when the designed lane closes and how he handles work without the ball.";}
    else if(pos=="wr"||pos=="te"){profile="The receiving profile needs a look beyond the highlight catches: releases, route detail and work through contact all matter.";focus="Watch how he earns separation and whether the routine catches stay routine.";}
    else if(pos=="lt"||pos=="lg"||pos=="c"||pos=="rg"||pos=="rt"){profile="The first look is about how he wins a block, rather than simply whether the play ends well.";focus="Watch his feet and recovery after a defender changes direction or gets underneath him.";}
    else if(pos=="k"||pos=="p"){profile="The specialist profile is worth judging through repeatable contact and placement, not just the longest attempt.";focus="Look for whether his technique holds up when the setup is less than perfect.";}
    else if(pos=="cb"||pos=="fs"||pos=="ss"){profile="The coverage profile needs to be read alongside his responsibilities; the result of the play can hide the quality of the assignment.";focus="Watch his transitions and recovery when a receiver changes pace or direction.";}
    else {profile="The defensive profile needs a look at how he handles the play before the finish, not just the final tackle.";focus="Watch how he reads the action and what he does when a blocker reaches him first.";}
    const auto style=notesKey(prospect.tendency);
    if(pos=="qb"&&style.find("pocket")!=std::string::npos)profile="His profile is built around pocket work: staying on schedule and delivering from a settled platform.";
    else if(pos=="qb"&&(style.find("dual")!=std::string::npos||style.find("scrambl")!=std::string::npos))profile="There is an improvisational element to his profile. The staff will want to separate useful escapes from leaving the structure too early.";
    else if((pos=="hb"||pos=="rb")&&style.find("power")!=std::string::npos)profile="The running profile leans toward handling traffic and finishing a run, rather than turning every touch into a foot race.";
    else if((pos=="hb"||pos=="rb")&&style.find("receiv")!=std::string::npos)profile="Passing-game involvement is part of the appeal of his profile. Look beyond the handoffs when reviewing him.";
    else if(style.find("raw strength")!=std::string::npos)profile="This is a power-oriented blocking profile. The staff should look at leverage and technique alongside the physical approach.";
    std::string result="EARLY PROFILE\n";
    if(!prospect.tendency.empty())result+=prospect.tendency+" profile. ";
    result+=profile;
    const char* introductions[]={"\n\nWHAT TO WATCH\n","\n\nFILM FOCUS\n","\n\nCLOSER LOOK\n"};
    result+=introductions[seed%3];result+=focus;
    if(progress<25){result+="\n\nThe initial look is broad. More specific observations will be added as scouting progresses.";return result;}
    std::vector<std::pair<uint64_t,std::string>> strengths,development;
    for(const auto& observed:prospect.observations){
        if(!std::isfinite(observed.low)||!std::isfinite(observed.high)||observed.low<0||observed.high>100||observed.low>observed.high)continue;
        const auto key=notesKey(observed.name);
        for(const auto& wording:notesLanguage)if(key==wording.attribute){
            const auto order=notesHash(prospect.identity+":"+key);
            if(observed.low>=80)strengths.emplace_back(order,wording.strong);
            else if(observed.high<80)development.emplace_back(order,wording.developing);
            break;
        }
    }
    std::sort(strengths.begin(),strengths.end());std::sort(development.begin(),development.end());
    const auto limit=progress>=75?3u:progress>=50?2u:1u;
    unsigned added=0;
    if(!strengths.empty()){result+="\n\nENCOURAGING SIGNS\n";for(size_t i=0;i<strengths.size()&&i<limit;++i){if(i)result+=' ';result+=strengths[i].second;++added;}}
    if(!development.empty()){result+="\n\nDEVELOPMENT FOCUS\n";result+=development.front().second;++added;}
    if(!added)result+="\n\nThe available film is still too broad to pin down a dependable strength or development priority.";
    if(result.size()>1500)result.resize(1500);
    return result;
}
template<class View,class StringSetter>unsigned appendRecruitNotes(View& view,uintptr_t root,StringSetter setter){
    std::vector<uintptr_t> recruits;if(!view.array(root,recruits,512))return 0;unsigned count=0;
    for(auto at:recruits){
        std::map<std::string,uintptr_t> fields;if(!view.members(at,fields))continue;
        auto text=[&](const char* key){std::string value;if(fields.count(key))view.string(fields.at(key),value);return value;};
        NotesProspect prospect;prospect.position=text("Position");prospect.tendency=text("Tendency");prospect.hometown=text("Hometown");prospect.classification=text("ClassAbbreviation");
        prospect.identity=text("FirstName")+"|"+text("LastName")+"|"+prospect.hometown+"|"+text("State");
        double id=0;if(fields.count("RecordId")&&view.number(fields.at("RecordId"),id)&&id>=0&&id<9007199254740992.0)prospect.identity+="|"+std::to_string(static_cast<uint64_t>(id));
        if(fields.count("PercentageScouted")&&(!view.number(fields.at("PercentageScouted"),prospect.progress)||prospect.progress<0||prospect.progress>100))prospect.progress=0;
        std::vector<uintptr_t> attrs;if(fields.count("ScoutingAttributes")&&view.array(fields.at("ScoutingAttributes"),attrs,32))for(auto attribute:attrs){
            std::map<std::string,uintptr_t> a;NotesObservation observation;bool slider=false;
            if(!view.members(attribute,a)||!a.count("Name")||!a.count("HaveSlider")||!a.count("SliderStart")||!a.count("SliderEnd")||!view.string(a.at("Name"),observation.name)||!view.boolean(a.at("HaveSlider"),slider)||!view.number(a.at("SliderStart"),observation.low)||!view.number(a.at("SliderEnd"),observation.high))continue;
            if(!slider&&observation.low==0&&prospect.progress<100)continue;
            observation.exact=!slider;prospect.observations.push_back(std::move(observation));
        }
        const auto body=makeRecruitNotes(prospect);setter(at,"DENotesBody",body.c_str());++count;
    }
    return count;
}
}
