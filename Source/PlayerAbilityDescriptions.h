#pragma once
#include "RecruitingGradePolicy.h"
#include <algorithm>
#include <cstdint>
#include <map>
#include <string>
#include <string_view>
#include <vector>
namespace recruitingfog::playerfog {
inline bool abilitySpace(char c){return c==' '||c=='\t'||c=='\r'||c=='\n';}
inline bool abilityWord(char c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_';}
inline bool abilityNumber(std::string_view text,size_t at,size_t& end,int& value){
    if(at>=text.size()||text[at]<'0'||text[at]>'9')return false;
    if(at&&(abilityWord(text[at-1])||text[at-1]=='.'||text[at-1]=='-'||text[at-1]=='+'))return false;
    unsigned number=0;end=at;
    while(end<text.size()&&text[end]>='0'&&text[end]<='9'){number=number*10+unsigned(text[end++]-'0');if(number>100)return false;}
    if(end<text.size()&&(abilityWord(text[end])||text[end]=='.'||text[end]=='%'))return false;
    value=int(number);return true;
}
inline const std::vector<std::string_view>& abilityAttributeNames(){
    static const std::vector<std::string_view> names=[](){
        std::vector<std::string_view> result={"Awareness","Speed","Acceleration","Agility","Change of Direction","Strength",
        "Carrying","Ball Carrier Vision","BC Vision","Break Tackle","Trucking","Stiff Arm","Spin Move","Juke Move",
        "Catching","Catch in Traffic","Spectacular Catch","Short Route Running","Medium Route Running","Deep Route Running",
        // Native receiver Physicals abbreviate these names in requirements.
        "Short Route","Medium Route","Deep Route","Release","Jumping",
        "Throw Power","Throw Accuracy Short","Throw Accuracy Mid","Throw Accuracy Deep","Short Throw Accuracy","Medium Throw Accuracy","Deep Throw Accuracy",
        "Short Accuracy","Medium Accuracy","Deep Accuracy","Throw on Run","Throw on the Run","Throw Under Pressure","Under Pressure","Break Sack","Play Action",
        "Pass Block Power","Pass Block Finesse","Pass Block","Run Block Power","Run Block Finesse","Run Block","Lead Block","Impact Blocking",
        "Play Recognition","Tackle","Tackling","Hit Power","Block Shedding","Finesse Moves","Power Moves","Pursuit","Man Coverage","Zone Coverage","Press",
        "Kick Return","Kick Power","Kick Accuracy","Stamina","Toughness","Injury","Long Snap","Long Snapping"};
        std::stable_sort(result.begin(),result.end(),[](auto a,auto b){return a.size()>b.size();});return result;
    }();return names;
}
// Only the verified ability UI requirement grammar qualifies. This never
// processes global/localized strings, gameplay data, costs, rank or statistics.
inline std::string abilityDescriptionGrades(const std::string& text){
    if(text.size()>4096)return text;
    const auto requires=text.find("Requires:");if(requires==std::string::npos)return text;
    struct Edit{size_t at,end;std::string grade;};std::vector<Edit> edits;
    for(size_t at=requires+9;at<text.size();++at){
        size_t end=0;int value=0;if(!abilityNumber(text,at,end,value)||end>=text.size()||!abilitySpace(text[end]))continue;
        auto nameAt=end;while(nameAt<text.size()&&abilitySpace(text[nameAt]))++nameAt;
        size_t nameEnd=0;
        for(auto name:abilityAttributeNames())if(text.compare(nameAt,name.size(),name)==0){
            const auto after=nameAt+name.size();
            if(after<text.size()&&!abilitySpace(text[after])&&text[after]!='('&&text[after]!=','&&text[after]!=';'&&text[after]!='.')continue;
            auto tail=after;while(tail<text.size()&&abilitySpace(text[tail]))++tail;
            const bool conjunction=(text.compare(tail,3,"and")==0&&tail+3<text.size()&&abilitySpace(text[tail+3]))||(text.compare(tail,2,"or")==0&&tail+2<text.size()&&abilitySpace(text[tail+2]));
            if(tail==text.size()||text[tail]=='('||text[tail]==','||text[tail]==';'||(text[tail]=='.'&&(tail+1==text.size()||abilitySpace(text[tail+1])))||conjunction){nameEnd=after;break;}
        }
        if(!nameEnd)continue;
        edits.push_back({at,end,display(Visibility::Revealed,value)});
        auto current=nameEnd;while(current<text.size()&&abilitySpace(text[current]))++current;
        if(current<text.size()&&text[current]=='('){
            ++current;while(current<text.size()&&abilitySpace(text[current]))++current;
            size_t currentEnd=0;int currentValue=0;
            if(abilityNumber(text,current,currentEnd,currentValue)&&currentEnd<text.size()&&abilitySpace(text[currentEnd])){
                auto suffix=currentEnd;while(suffix<text.size()&&abilitySpace(text[suffix]))++suffix;
                if(text.compare(suffix,9,"Currently")==0){suffix+=9;while(suffix<text.size()&&abilitySpace(text[suffix]))++suffix;
                    if(suffix<text.size()&&text[suffix]==')')edits.push_back({current,currentEnd,display(Visibility::Revealed,currentValue)});
                }
            }
        }
        at=nameEnd-1;
    }
    if(edits.empty())return text;
    std::string result;result.reserve(text.size());size_t copied=0;
    for(const auto& edit:edits){if(edit.at<copied)continue;result.append(text,copied,edit.at-copied);result+=edit.grade;copied=edit.end;}
    result.append(text,copied,std::string::npos);return result;
}
template<class View,class Setter>unsigned convertAbilityDescriptions(View& view,uintptr_t root,Setter set){
    std::vector<uintptr_t> entries;if(!view.array(root,entries,128))return 0;unsigned changed=0;
    for(auto entry:entries){std::map<std::string,uintptr_t> fields;if(!view.members(entry,fields))continue;
        for(const char* key:{"Description","UpgradeDescription"}){const auto found=fields.find(key);std::string original;
            if(found==fields.end()||!view.string(found->second,original))continue;
            const auto converted=abilityDescriptionGrades(original);if(converted!=original){set(entry,key,converted.c_str());++changed;}
        }
    }return changed;
}
}
