#pragma once
#include "../Source/CurrencyDisplay.h"
#include "../Source/PlayerRatingGrid.h"
#include <array>
#include <limits>
#include <stdexcept>
#include <vector>

namespace currencydisplaytests {
inline void check(bool value,const char* message){if(!value)throw std::runtime_error(message);}
struct RestoreOptions {
    unsigned saved=enhancements::currentOptions.load();
    ~RestoreOptions(){enhancements::currentOptions.store(saved);}
};
struct Event {
    unsigned slot=0,row=0;std::string key,text;int integer=0;float real=0;bool flag=false,nullText=false;
};
struct Output {void** vtable;std::vector<Event> events;};
inline Event field(unsigned slot,unsigned row,const char* key){Event e;e.slot=slot;e.row=row;e.key=key?key:"";return e;}
inline void __fastcall reserve(Output* out,unsigned count){out->events.push_back(field(1,count,nullptr));}
inline void __fastcall boolean(Output* out,unsigned row,const char* key,bool value){auto e=field(3,row,key);e.flag=value;out->events.push_back(std::move(e));}
inline void __fastcall integer(Output* out,unsigned row,const char* key,int value){auto e=field(4,row,key);e.integer=value;out->events.push_back(std::move(e));}
inline void __fastcall real(Output* out,unsigned row,const char* key,float value){auto e=field(5,row,key);e.real=value;out->events.push_back(std::move(e));}
inline void __fastcall text(Output* out,unsigned row,const char* key,const char* value){auto e=field(6,row,key);e.text=value?value:"";e.nullText=!value;out->events.push_back(std::move(e));}
inline void* outputTable[]={nullptr,reinterpret_cast<void*>(reserve),nullptr,reinterpret_cast<void*>(boolean),reinterpret_cast<void*>(integer),reinterpret_cast<void*>(real),reinterpret_cast<void*>(text)};

inline void run(){
    RestoreOptions restore;
    using enhancements::currency::dollars;using enhancements::currency::pointsText;
    using namespace recruitingfog::playerfog;
    const std::array<std::pair<double,const char*>,12> amounts={{{0,"0"},{1,"4K"},{2.5,"10K"},{150,"600K"},{249,"996K"},{250,"1.0M"},{262.5,"1.1M"},{275,"1.1M"},{1000,"4.0M"},{-150,"-600K"},{-250,"-1.0M"},{1000000000.0,"4000000.0M"}}};
    for(const auto& [points,expected]:amounts)check(dollars(points)==expected,"NIL dollar conversion/rounding boundary differs from $4K per point");
    for(double value:{std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN(),1000000001.0,-1000000001.0})check(dollars(value).empty(),"Invalid/unbounded NIL amount was converted");
    for(const auto& [source,expected]:std::array<std::pair<const char*,double>,8>{{{"0",0},{"150",150},{"-150",-150},{"1,250",1250},{"-1,250",-1250},{"000150",150},{"1,000,000,000",1000000000.0},{"1000000000",1000000000.0}}}){
        double value=-12345;check(pointsText(source,value)&&value==expected,"Valid native integer/grouped NIL text was rejected");
    }
    const std::array<const char*,29> invalid={{"","-","+150"," 150","150 ","1.5","1e3","$150","150K","150%","150,TrendUp","1,50","1,500,","1,,500",",150","1000,000","1,2345","1,234,56","1,234,5678","1.000","--1","NaN","inf","?","1000000001","-1000000001","1,000,000,001","12345678901234567","\t150"}};
    for(const auto* source:invalid){double value=-12345;check(!pointsText(source,value)&&value==-12345,"Non-numeric/unsupported NIL text was accepted or changed the output value");}

    const std::array<GridSchema,11> schemas={{GridSchema::None,GridSchema::Roster,GridSchema::DepthChart,GridSchema::Redshirts,GridSchema::InjuryReport,GridSchema::PositionAth,GridSchema::PlayersLeaving,GridSchema::Training,GridSchema::EncourageTransfers,GridSchema::EncourageFiltered,GridSchema::EncouragePosition}};
    const std::array<int,11> nilColumns={{-1,6,8,5,-1,-1,-1,6,5,5,4}};
    for(size_t i=0;i<schemas.size();++i)for(int column=-1;column<=90;++column)check(nilColumn(schemas[i],column)==(nilColumns[i]>=0&&column==nilColumns[i]),"NIL recognition touched an unknown grid/schema column");

    // Dollars is independent of every fog toggle and of grade colors. Test
    // reordered semantic columns: the cell's screen index is deliberately 0.
    for(bool enabled:{false,true})for(bool roster:{false,true})for(bool recruiting:{false,true})for(bool team:{false,true})for(bool colors:{false,true}){
        auto option=enhancements::Options{};option.dollars=enabled;option.roster=roster;option.recruiting=recruiting;option.team=team;option.colors=colors;enhancements::currentOptions.store(option.packed());
        check(enhancements::currency::display("150")==std::string(enabled?"600K":"150"),"NIL display depends on a fog/color option");
        check(enhancements::currency::display("1,250")==std::string(enabled?"5.0M":"1,250"),"Grouped NIL display does not obey its own toggle");
        check(enhancements::currency::display(nullptr).empty(),"Null NIL display did not remain empty");
        for(const auto* source:invalid)check(enhancements::currency::display(source)==source,"Currency adapter rewrote unsupported native text");
        for(size_t i=0;i<schemas.size();++i){
            if(nilColumns[i]<0)continue;
            Output out{outputTable,{}};GridSink sink{gridTable,&out};sink.schema=schemas[i];sink.count=2;sink.columns[0]=nilColumns[i];sink.columns[1]=0;
            gridReserve(&sink,2);gridInt(&sink,0,"value",150);gridFloat(&sink,0,"sortValue",150.5f);gridBool(&sink,0,"isTrend",true);
            gridString(&sink,0,"display","150");gridString(&sink,0,"tooltip","150");gridString(&sink,0,"sortKey","150");gridString(&sink,1,"display","150");
            check(out.events.size()==8&&out.events[0].slot==1&&out.events[0].row==2,"Currency conversion changed reserve count or native event order");
            check(out.events[1].slot==4&&out.events[1].integer==150&&out.events[1].key=="value"&&out.events[2].slot==5&&out.events[2].real==150.5f&&out.events[2].key=="sortValue"&&out.events[3].slot==3&&out.events[3].flag,"Currency conversion changed numeric values, sorting data, or boolean fields");
            check(out.events[4].slot==6&&out.events[4].row==0&&out.events[4].key=="display"&&out.events[4].text==std::string(enabled?"600K":"150"),"Known NIL schema display was not converted at its semantic column");
            check(out.events[5].key=="tooltip"&&out.events[5].text=="150"&&out.events[6].key=="sortKey"&&out.events[6].text=="150"&&out.events[7].row==1&&out.events[7].text=="150"&&sink.changed==0,"Currency conversion leaked into unrelated fields/columns or emitted rating metadata");
            out.events.clear();gridString(&sink,0,"display","?");gridString(&sink,0,"display",nullptr);
            check(out.events.size()==2&&out.events[0].text=="?"&&out.events[1].nullText,"Unknown/null native NIL labels were not preserved");
        }
    }
    // Replaying native column metadata must preserve native sort modes/types;
    // currency conversion belongs only to rendered row display strings.
    ColumnSink columns{columnTable};columnReserve(&columns,2);columnInt(&columns,0,"sort",1);columnFloat(&columns,0,"weight",1.25f);columnBool(&columns,0,"sortable",true);columnString(&columns,0,"display","NIL");
    Output metadata{outputTable,{}};replayColumns(columns,&metadata,false,GridSchema::Roster);
    check(metadata.events.size()==5&&metadata.events[1].key=="sort"&&metadata.events[1].integer==1&&metadata.events[2].real==1.25f&&metadata.events[3].flag&&metadata.events[4].text=="NIL","NIL column replay changed native sort metadata or numeric field types");
}
}
