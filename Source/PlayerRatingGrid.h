#pragma once
#include "RecruitingGradePolicy.h"
#include "CurrencyDisplay.h"
#include <array>
#include <cstring>
#include <map>
#include <string_view>
#include <vector>

namespace recruitingfog::playerfog {
inline std::string playerDisplay(double rating){
    if(!std::isfinite(rating)||rating<0||rating>100||rating!=std::floor(rating))return "?";
    return enhancements::scopedRatingDisplay(static_cast<int>(rating),enhancements::options().roster);
}
// Semantic column IDs, not screen positions. Native position/team filters may
// reorder or request only a subset of these columns.
inline bool rosterRatingColumn(int id){return id==5||(id>=8&&id<=61);}
enum class GridSchema{None,Roster,DepthChart,Redshirts,InjuryReport,PositionAth,PlayersLeaving,Training,EncourageTransfers,EncourageFiltered,EncouragePosition};
inline bool nilColumn(GridSchema schema,int id){
    return schema==GridSchema::Roster?id==6:schema==GridSchema::DepthChart?id==8:
        (schema==GridSchema::Redshirts||schema==GridSchema::EncourageTransfers||schema==GridSchema::EncourageFiltered)?id==5:
        schema==GridSchema::Training?id==6:schema==GridSchema::EncouragePosition?id==4:false;
}
inline uint64_t gridState(int form,GridSchema schema){return form<0||schema==GridSchema::None?0:(uint64_t(uint32_t(form)+1)<<32)|uint32_t(schema);}
inline int gridStateForm(uint64_t state){return state?int((state>>32)-1):-1;}
inline GridSchema gridStateSchema(uint64_t state){return GridSchema(uint32_t(state));}
inline bool ratingColumn(GridSchema schema,int id){return schema==GridSchema::Roster?rosterRatingColumn(id):schema==GridSchema::DepthChart?(id==7||(id>=10&&id<=63)):schema==GridSchema::Redshirts?(id==4||(id>=7&&id<=59)):(schema==GridSchema::InjuryReport||schema==GridSchema::PlayersLeaving)?id==4:schema==GridSchema::PositionAth?(id==5||(id>=7&&id<=31)):schema==GridSchema::Training?(id==5||(id>=7&&id<=60)):schema==GridSchema::EncourageTransfers?(id==4||(id>=7&&id<=60)):schema==GridSchema::EncourageFiltered?(id==4||(id>=6&&id<=59)):schema==GridSchema::EncouragePosition?(id==3||(id>=5&&id<=58)):false;}
inline bool ratingText(std::string_view text,int& value){
    unsigned result=0;size_t i=0;
    while(i<text.size()&&text[i]>='0'&&text[i]<='9'){
        result=result*10+unsigned(text[i++]-'0');if(result>100)return false;
    }
    if(!i)return false;
    const auto suffix=text.substr(i);
    if(!suffix.empty()&&suffix!=",TrendNone"&&suffix!=",TrendUp"&&suffix!=",TrendDown")return false;
    value=int(result);return true;
}
inline std::string ratingLabel(const char* value){
    int rating=0;if(value&&ratingText(value,rating)){
        const std::string_view text(value);const auto comma=text.find(',');
        // The native trend cell reads the label and indicator separately.
        // Convert only the rating; retain coach boosts/drops and their colors.
        return playerDisplay(rating)+(comma==std::string_view::npos?std::string():std::string(text.substr(comma)));
    }
    // Hidden/unsupported cells stay hidden; never interpret a sentinel as zero.
    return value?value:"";
}
inline std::string trainingRatingLabel(const char* value,bool fog=enhancements::options().roster){
    if(!value)return {};
    const std::string_view text(value);const auto comma=text.find(',');
    const auto base=text.substr(0,comma);int rating=0;
    if(!ratingText(base,rating)||base!=std::to_string(rating))return value;
    if(comma==std::string_view::npos)return enhancements::scopedRatingDisplay(rating,fog);
    // Native format35 emits current,TrendWithDelta,(+delta) or (-delta).
    // Preserve its delimiter/token/adjustment exactly for SpreadsheetTrendCell.
    const auto suffix=text.substr(comma);constexpr std::string_view prefix=",TrendWithDelta,(";
    if(suffix.size()<=prefix.size()+2||suffix.substr(0,prefix.size())!=prefix||suffix.back()!=')')return value;
    const auto signedDelta=suffix.substr(prefix.size(),suffix.size()-prefix.size()-1);
    if(signedDelta[0]!='+'&&signedDelta[0]!='-')return value;
    const auto digits=signedDelta.substr(1);int delta=0;
    if(!ratingText(digits,delta)||delta==0||digits!=std::to_string(delta))return value;
    return enhancements::scopedRatingDisplay(rating,fog)+std::string(suffix);
}
inline int gradeColor(char value){
    switch(value){case 'A':return 0x1FE840;case 'B':return 0xA8D943;case 'C':return 0xFFD34D;case 'D':return 0xF68C2E;default:return 0xF04444;}
}
inline bool knownAttributeColumns(const std::array<std::string,90>& names,unsigned first,unsigned count){
    // Position views retain the roster identity fields but select/reorder a
    // smaller attribute set. Admit only known rating headers after that prefix.
    const std::string allowed="|SPD|ACC|AGI|COD|STR|AWR|CAR|BCV|BTK|TRK|SFA|SPM|JKM|CTH|CIT|SPC|SRR|MRR|DRR|RLS|JMP|THP|SAC|MAC|DAC|RUN|TUP|BSK|PAC|PBK|PBP|PBF|RBK|RBP|RBF|LBK|IBL|PRC|TAK|POW|BSH|FMV|PMV|PUR|MCV|ZCV|PRS|RET|KPW|KAC|STA|TGH|INJ|LSP|";
    for(unsigned i=first;i<count;++i)if(names[i].empty()||allowed.find("|"+names[i]+"|")==std::string::npos)return false;
    return true;
}
inline bool rosterSchema(const std::array<std::string,90>& names,unsigned count){
    return count>=9&&count<=62&&names[1]=="RS"&&names[2]=="Name"&&names[3]=="Year"&&names[4]=="POS"&&names[5]=="OVR"&&names[6]=="NIL"&&names[7]=="DEV"&&knownAttributeColumns(names,8,count);
}
inline GridSchema classifyGrid(const std::array<std::string,90>& names,unsigned count){
    if(rosterSchema(names,count))return GridSchema::Roster;
    // Verified native depth-chart identity prefix. # is depth, not a rating;
    // hidden position/morale, year and NIL also retain their original types.
    if(count>=10&&count<=64&&names[1]=="POS"&&names[2]=="#"&&names[3]=="RS"&&names[4]=="Name"&&names[5]=="Year"&&names[6]=="POS"&&names[7]=="OVR"&&names[8]=="NIL"&&names[9]=="MOR"&&knownAttributeColumns(names,10,count))return GridSchema::DepthChart;
    // Captured Redshirts uses zero-based RS, swaps position/year, includes
    // games played and ends with a hidden last-name column. Those remain native.
    if(count==61&&names[0]=="RS"&&names[1]=="Name"&&names[2]=="POS"&&names[3]=="Year"&&names[4]=="OVR"&&names[5]=="NIL"&&names[6]=="GP"&&names[60]=="Last Name"&&knownAttributeColumns(names,7,60))return GridSchema::Redshirts;
    if(count==10&&names[0].empty()&&names[1]=="POS"&&names[2]=="Name"&&names[3]=="POS"&&names[4]=="OVR"&&names[5]=="Injury"&&names[6]=="Length"&&names[7]=="IR"&&names[8]=="Return"&&names[9]=="Status")return GridSchema::InjuryReport;
    // Captured Position Changes ATH view omits NIL and hides DEV at6.
    // Require its complete identity prefix and only verified attribute headers.
    if(count==32&&names[0].empty()&&names[1]=="RS"&&names[2]=="Name"&&names[3]=="Year"&&names[4]=="POS"&&names[5]=="OVR"&&names[6]=="DEV"&&knownAttributeColumns(names,7,count))return GridSchema::PositionAth;
    if(count==8&&names[0]=="Name"&&names[1].empty()&&names[2]=="POS"&&names[3]=="Year"&&names[4]=="OVR"&&names[5]=="Reason"&&names[6]=="Persuasion Chance"&&names[7]=="RS")return GridSchema::PlayersLeaving;
    if(count>=8&&count<=61&&names[0].empty()&&names[1]=="RS"&&names[2]=="Name"&&names[3]=="Year"&&names[4]=="POS"&&names[5]=="OVR"&&names[6]=="NIL"&&knownAttributeColumns(names,7,count))return GridSchema::Training;
    if(count==61&&names[0].empty()&&names[1]=="Name"&&names[2]=="Year"&&names[3]=="POS"&&names[4]=="OVR"&&names[5]=="NIL"&&names[6]=="DEV"&&knownAttributeColumns(names,7,count))return GridSchema::EncourageTransfers;
    // Encourage Transfers filters omit DEV and select/reorder attributes from6.
    // Keep NIL at5 numeric; require the complete identity prefix and rating-only tail.
    if(count>=7&&count<=60&&names[0].empty()&&names[1]=="Name"&&names[2]=="Year"&&names[3]=="POS"&&names[4]=="OVR"&&names[5]=="NIL"&&knownAttributeColumns(names,6,count))return GridSchema::EncourageFiltered;
    // Individual position filters omit POS as well as DEV (captured QB).
    if(count>=6&&count<=59&&names[0].empty()&&names[1]=="Name"&&names[2]=="Year"&&names[3]=="OVR"&&names[4]=="NIL"&&knownAttributeColumns(names,5,count))return GridSchema::EncouragePosition;
    return GridSchema::None;
}
struct GridSink{
    void** vtable;void* target;
    std::array<int,90> columns{};unsigned count=0,changed=0;
    GridSchema schema=GridSchema::Roster;
};
template<class T>inline void put(void* target,unsigned row,const char* key,T value,unsigned slot){
    reinterpret_cast<void(__fastcall*)(void*,unsigned,const char*,T)>((*reinterpret_cast<void***>(target))[slot])(target,row,key,value);
}
inline void reserve(void* target,unsigned count){reinterpret_cast<void(__fastcall*)(void*,unsigned)>((*reinterpret_cast<void***>(target))[1])(target,count);}
inline void __fastcall gridReserve(GridSink* s,unsigned n){reserve(s->target,n);}
inline void __fastcall gridBool(GridSink* s,unsigned r,const char* k,bool v){put(s->target,r,k,v,3);}
inline void __fastcall gridInt(GridSink* s,unsigned r,const char* k,int v){put(s->target,r,k,v,4);}
inline void __fastcall gridFloat(GridSink* s,unsigned r,const char* k,float v){put(s->target,r,k,v,5);}
inline void __fastcall gridString(GridSink* s,unsigned r,const char* k,const char* v){
    if(v&&r<s->count&&nilColumn(s->schema,s->columns[r])&&k&&!strcmp(k,"display")&&enhancements::options().dollars){
        const auto label=enhancements::currency::display(v);put(s->target,r,k,label.c_str(),6);return;
    }
    if(r<s->count&&ratingColumn(s->schema,s->columns[r])&&k&&!strcmp(k,"display")){
        const auto label=s->schema==GridSchema::Training?trainingRatingLabel(v):ratingLabel(v);put(s->target,r,k,label.c_str(),6);
        if(v){
            int rating=0;const std::string_view source(v);
            const bool valid=s->schema==GridSchema::Training?trainingRatingLabel(v,true)!=v:ratingText(source,rating);
            if(label!=v)++s->changed;
            if(valid&&enhancements::playerColors()){
                ratingText(source.substr(0,source.find(',')),rating);
                put(s->target,r,"DEPlayerRating",true,3);put(s->target,r,"DEGradeColor",enhancements::ratingColor(rating),4);
            }
        }
    }else put(s->target,r,k,v,6);
}
inline void* gridTable[]={nullptr,reinterpret_cast<void*>(gridReserve),nullptr,reinterpret_cast<void*>(gridBool),reinterpret_cast<void*>(gridInt),reinterpret_cast<void*>(gridFloat),reinterpret_cast<void*>(gridString)};
inline bool gridColumns(GridSink& sink,void* columns){
    if(!columns)return false;auto** table=*reinterpret_cast<void***>(columns);
    const int count=reinterpret_cast<int(__fastcall*)(void*)>(table[1])(columns);
    if(count<0||count>90)return false;sink.count=unsigned(count);
    for(int i=0;i<count;++i)sink.columns[i]=reinterpret_cast<int(__fastcall*)(void*,int)>(table[2])(columns,i);
    return true;
}
// Capture column metadata once, then replay after recognizing its full schema.
// Never call the native getter twice, reenter the provider or sort its data.
struct ColumnField{
    unsigned row=0,slot=0;std::string key,text;int integer=0;float real=0;bool flag=false,nullText=false;
};
struct ColumnSink{
    void** vtable;unsigned count=0;std::array<std::string,90> names{};std::vector<ColumnField> fields;
};
inline void __fastcall columnReserve(ColumnSink* s,unsigned n){s->count=n;ColumnField f;f.slot=1;f.row=n;s->fields.push_back(std::move(f));}
inline void __fastcall columnBool(ColumnSink* s,unsigned r,const char* k,bool v){ColumnField f;f.row=r;f.slot=3;f.key=k?k:"";f.flag=v;s->fields.push_back(std::move(f));}
inline void __fastcall columnInt(ColumnSink* s,unsigned r,const char* k,int v){ColumnField f;f.row=r;f.slot=4;f.key=k?k:"";f.integer=v;s->fields.push_back(std::move(f));}
inline void __fastcall columnFloat(ColumnSink* s,unsigned r,const char* k,float v){ColumnField f;f.row=r;f.slot=5;f.key=k?k:"";f.real=v;s->fields.push_back(std::move(f));}
inline void __fastcall columnString(ColumnSink* s,unsigned r,const char* k,const char* v){
    ColumnField f;f.row=r;f.slot=6;f.key=k?k:"";f.text=v?v:"";f.nullText=!v;
    if(r<s->names.size()&&f.key=="display")s->names[r]=f.text;s->fields.push_back(std::move(f));
}
inline void* columnTable[]={nullptr,reinterpret_cast<void*>(columnReserve),nullptr,reinterpret_cast<void*>(columnBool),reinterpret_cast<void*>(columnInt),reinterpret_cast<void*>(columnFloat),reinterpret_cast<void*>(columnString)};
inline void replayColumns(const ColumnSink& sink,void* target,bool roster,GridSchema schema=GridSchema::Roster){
    for(const auto& f:sink.fields){
        switch(f.slot){
        case 1:reserve(target,f.row);break;
        case 3:put(target,f.row,f.key.c_str(),f.flag,3);break;
        case 4:put(target,f.row,f.key.c_str(),f.integer,4);break;
        case 5:put(target,f.row,f.key.c_str(),f.real,5);break;
        case 6:put(target,f.row,f.key.c_str(),f.nullText?nullptr:f.text.c_str(),6);break;
        }
    }
    if(roster)for(unsigned column=0;column<sink.names.size();++column)if(ratingColumn(schema,int(column))&&!sink.names[column].empty())put(target,column,"DEPlayerRating",true,3);
}
template<class View,class Setter>bool selectedOverall(View& view,uintptr_t root,Setter setString){
    std::map<std::string,uintptr_t> fields;double rating=0;
    if(!view.members(root,fields)||!fields.count("overall")||!view.number(fields.at("overall"),rating))return false;
    const auto label=playerDisplay(rating);if(label=="?")return false;
    setString(root,"overall",label.c_str());return true;
}
}
