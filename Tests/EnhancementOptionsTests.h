#pragma once
#include <thread>
namespace optiontests {
using Json=nlohmann::json;
struct Output {void** table;std::map<unsigned,Json> rows;unsigned reserved=0;};
template<class T>void field(Output* out,unsigned row,const char* key,T value){out->rows[row][key]=value;}
void __fastcall boolean(Output* o,unsigned r,const char* k,bool v){field(o,r,k,v);}
void __fastcall integer(Output* o,unsigned r,const char* k,int v){field(o,r,k,v);}
void __fastcall real(Output* o,unsigned r,const char* k,float v){field(o,r,k,v);}
void __fastcall text(Output* o,unsigned r,const char* k,const char* v){field(o,r,k,v);}
void __fastcall reserve(Output* o,unsigned count){o->reserved=count;}
void* outputTable[]={nullptr,reinterpret_cast<void*>(reserve),nullptr,reinterpret_cast<void*>(boolean),reinterpret_cast<void*>(integer),reinterpret_cast<void*>(real),reinterpret_cast<void*>(text)};
struct Input {void** table;std::vector<std::pair<int,int>> rows;};
int __fastcall count(Input* in){return int(in->rows.size());}
int __fastcall get(Input* in,int row,const char* key){return !strcmp(key,"key")?in->rows.at(row).first:in->rows.at(row).second;}
void* inputTable[]={nullptr,reinterpret_cast<void*>(count),nullptr,reinterpret_cast<void*>(get)};
inline void run(){
    using namespace enhancements;
    require(Options{}.packed()==defaultOptions&&Options{}.scale==GradeScale::PlusMinus&&Options{}.team,"New default scale/team fog differs");
    require(!Options{}.dollars,"Dollar conversion must default Off");
    for(unsigned bits=0;bits<256;++bits)require(Options::unpack(bits).packed()==bits,"Option bit packing lost an independent control");
    for(int n=0;n<=100;++n){
        currentOptions=39;
        require(recruitingfog::display(recruitingfog::Visibility::Revealed,n)==std::string(1,recruitingfog::grade(n)),"Default grade scale changed");
        for(unsigned scale=0;scale<4;++scale){auto selected=options();selected.scale=GradeScale(scale);currentOptions=selected.packed();
            const auto expected=gradeLabel(n,GradeScale(scale));require(recruitingfog::display(recruitingfog::Visibility::Revealed,n)==expected,"Configured native grade display ignored its scale");
        }
    }
    constexpr std::pair<int,const char*> boundaries[]={{59,"F"},{60,"D-"},{62,"D-"},{63,"D"},{66,"D"},{67,"D+"},{69,"D+"},{70,"C-"},{73,"C"},{77,"C+"},{80,"B-"},{83,"B"},{87,"B+"},{90,"A-"},{93,"A"},{97,"A+"},{100,"A+"}};
    for(const auto& [n,label]:boundaries)require(!strcmp(gradeLabel(n,GradeScale::PlusMinus),label),"Plus/minus cutoff differs from the approved scale");
    require(!strcmp(gradeLabel(94,GradeScale::STier),"A")&&!strcmp(gradeLabel(95,GradeScale::STier),"S"),"S threshold differs");
    require(gradeColor("Fair,TrendWithDelta,(+2)")==0xEDB34F&&gradeColor("S")==0x409EFF&&gradeColor("Elite")==0xBB70EF,"Descriptive/S colors differ");
    const Json valid={{"format",1},{"league",1001},{"socialMedia",true},{"recruitingFog",true},{"rosterFog",true},{"gradeScale",0},{"ratingColors",true}};
    require(decodeOptions(valid,1001).packed()==103,"Valid profile did not decode");
    auto legacy=valid;legacy.erase("ratingColors");require(decodeOptions(legacy,1001).colors,"Older profile lost the default color setting");
    for(const auto* key:{"format","league","gradeScale"})for(const Json bad:std::vector<Json>{-1,1.5,true,nullptr,"1",Json::array({1})}){
        auto input=valid;input[key]=bad;bool rejected=false;try{decodeOptions(input,1001);}catch(const std::exception&){rejected=true;}
        require(rejected,"Non-integral/malformed profile field was silently coerced");
    }
    for(const auto* key:{"socialMedia","recruitingFog","rosterFog","ratingColors","teamFog","dollarValues"})for(const Json bad:std::vector<Json>{0,1,"true",nullptr}){
        auto input=valid;input[key]=bad;bool rejected=false;try{decodeOptions(input,1001);}catch(const std::exception&){rejected=true;}
        require(rejected,"Non-boolean toggle was silently coerced");
    }
    Options selected;selected.scale=GradeScale::Descriptive;selected.colors=false;
    Output output{outputTable,{}};output.rows[9]={{"label","Existing Commissioner Settings"},{"foreign",123}};
    menu::append(&output,10,selected,true);
    require(output.rows[9]["foreign"]==123&&output.rows.size()==10,"Enhancement section overwrote existing or foreign rows");
    require(output.rows[10]["label"]=="DYNASTY ENHANCEMENTS"&&output.rows[17]["label"]=="Rating Colors"&&output.rows[15]["label"]=="Player Grade Scale"&&output.rows[16]["label"]=="Team Grade Scale","Enhancement row ordering differs");
    require(output.rows[15]["numItems"]==5&&output.rows[16]["numItems"]==5&&output.rows[15]["isDefault"]==3&&output.rows[17]["isDefault"]==0&&output.rows[18]["label"]=="Dollar Values"&&output.rows[18]["isDefault"]==0,"Option choices/defaults differ");
    {
        // Native, Offline Dynasty Settings and AIO-shaped sections. Deliberately
        // write some header fields out of order and revisit one after later rows.
        Output reordered{outputTable,{}};menu::Collector sink{menu::collectorTable,&reordered,0,0,{}};
        menu::reserve(&sink,11);
        for(const auto& [row,label]:std::vector<std::pair<unsigned,const char*>>{{0,"Commissioner Settings"},{4,"Game Settings"},{7,"Team Settings"},{9,"Playoff Customization"}}){
            menu::text(&sink,row,"linkage","madden.ultimatecareer.component.ListCategoryHeader");
            menu::integer(&sink,row,"key",int(row));menu::text(&sink,row,"label",label);
        }
        for(const unsigned row:{1,2,3,5,6,8,10}){
            menu::integer(&sink,row,"key",900+int(row));menu::text(&sink,row,"label",("Row "+std::to_string(row)).c_str());
            menu::boolean(&sink,row,"isInteractive",row!=6);menu::real(&sink,row,"step",0.5f);
        }
        menu::text(&sink,4,"description","Other mod section");
        require(reordered.rows.empty(),"Buffered provider leaked partial rows before section placement");
        require(menu::emit(sink,selected,true)==4,"Enhancements were not inserted after the Commissioner section");
        require(reordered.reserved==20&&reordered.rows.size()==20,"Settings insertion lost rows or reservation capacity");
        require(reordered.rows[4]["label"]=="DYNASTY ENHANCEMENTS"&&reordered.rows[7]["label"]=="Roster Fog"&&reordered.rows[8]["label"]=="Team Fog"&&reordered.rows[11]["label"]=="Rating Colors"&&reordered.rows[12]["label"]=="Dollar Values"&&reordered.rows[13]["label"]=="Game Settings"&&reordered.rows[16]["label"]=="Team Settings"&&reordered.rows[18]["label"]=="Playoff Customization","Foreign section order changed or native Team Settings stayed above Enhancements");
        for(const unsigned row:{1,2,3,5,6,8,10}){
            const auto mapped=row+(row>=4?9:0);
            require(reordered.rows[mapped]["key"]==900+int(row)&&reordered.rows[mapped]["label"]=="Row "+std::to_string(row)&&reordered.rows[mapped]["isInteractive"]==(row!=6)&&reordered.rows[mapped]["step"]==0.5f,"Provider row values, types or setting keys were altered by insertion");
        }
        require(reordered.rows[13]["description"]=="Other mod section","Late write to a header was lost");
        Output fallback{outputTable,{}};menu::Collector unknown{menu::collectorTable,&fallback,0,0,{}};
        menu::integer(&unknown,0,"key",88);menu::text(&unknown,0,"label","Unknown section");menu::text(&unknown,0,"linkage","madden.ultimatecareer.component.ListCategoryHeader");
        require(menu::emit(unknown,selected,true)==1&&fallback.rows[0]["key"]==88&&fallback.rows[1]["label"]=="DYNASTY ENHANCEMENTS","Unknown provider section was displaced");
        Output empty{outputTable,{}};menu::Collector inactive{menu::collectorTable,&empty,0,0,{}};
        menu::emit(inactive,selected,true);require(empty.rows.empty(),"An inactive settings list acquired a section");
    }
#if defined(RECRUIT_NOTES_UI)
    for(unsigned scale=0;scale<4;++scale)for(const bool colors:{false,true}){
        Options boostOptions;boostOptions.scale=GradeScale(scale);boostOptions.colors=colors;currentOptions=boostOptions.packed();
        for(const auto* trend:{",TrendUp",",TrendDown",",TrendNone"})for(int rating=0;rating<=100;++rating){
            const auto source=std::to_string(rating)+trend;
            require(recruitingfog::playerfog::ratingLabel(source.c_str())==std::string(gradeLabel(rating,boostOptions.scale))+trend,"Configured grades removed the native boost indicator");
        }
        for(const auto& [schema,column]:std::vector<std::pair<recruitingfog::playerfog::GridSchema,int>>{{recruitingfog::playerfog::GridSchema::Roster,5},{recruitingfog::playerfog::GridSchema::DepthChart,7},{recruitingfog::playerfog::GridSchema::Redshirts,4},{recruitingfog::playerfog::GridSchema::EncouragePosition,3}}){
            Output boosted{outputTable,{}};recruitingfog::playerfog::GridSink cells{recruitingfog::playerfog::gridTable,&boosted};cells.count=1;cells.schema=schema;cells.columns[0]=column;
            recruitingfog::playerfog::gridString(&cells,0,"display","96,TrendUp");recruitingfog::playerfog::gridInt(&cells,0,"intValue",96);
            require(boosted.rows[0]["display"]==std::string(gradeLabel(96,boostOptions.scale))+",TrendUp"&&boosted.rows[0]["intValue"]==96,"Boost rendering changed numeric sorting or lost its public grade");
            require(boosted.rows[0].contains("DEGradeColor")==colors,"Boost arrow depends on rating colors being enabled");
            if(colors)require(boosted.rows[0]["DEGradeColor"]==gradeColor(gradeLabel(96,boostOptions.scale)),"Boost suffix changed grade color");
        }
        require(recruitingfog::playerfog::ratingLabel("92,TrendUp")==std::string(gradeLabel(92,boostOptions.scale))+",TrendUp","Within-band boost was suppressed");
        require(recruitingfog::playerfog::ratingLabel("?")=="?"&&recruitingfog::playerfog::ratingLabel("?,TrendUp")=="?,TrendUp","Unknown rating was revealed by boost conversion");
        boostOptions.roster=false;currentOptions=boostOptions.packed();
        Output numeric{outputTable,{}};recruitingfog::playerfog::GridSink numericCells{recruitingfog::playerfog::gridTable,&numeric};numericCells.count=1;numericCells.columns[0]=5;
        recruitingfog::playerfog::gridString(&numericCells,0,"display","96");recruitingfog::playerfog::gridInt(&numericCells,0,"intValue",96);
        require(numeric.rows[0]["display"]=="96"&&numeric.rows[0]["intValue"]==96&&numeric.rows[0].contains("DEGradeColor")==colors,"Numeric rating colors still depend on fog conversion");
        if(colors)require(numeric.rows[0]["DEGradeColor"]==ratingColor(96),"Numeric ratings ignored the selected scale's color");
        require(recruitingfog::playerfog::ratingLabel("96,TrendUp")=="96,TrendUp","Numeric color mode removed the boost arrow");
    }
    currentOptions=7;Output plain{outputTable,{}};
    recruitingfog::playerfog::GridSink cells{recruitingfog::playerfog::gridTable,&plain};cells.count=1;cells.columns[0]=5;
    recruitingfog::playerfog::gridString(&cells,0,"display","83");
    require(plain.rows[0]["display"]=="B"&&!plain.rows[0].contains("DEGradeColor")&&!plain.rows[0].contains("DEPlayerRating"),"Colors Off changed grades or replaced native row colors");
    currentOptions=39;
#endif
    Input in{inputTable,{{10,9},{menu::firstKey,0},{menu::firstKey+3,2},{menu::firstKey+4,0},{0x1001,3},{menu::firstKey+8,0}}};
    std::vector<std::pair<unsigned,int>> changes;
    const auto consumed=menu::consume(&in,[&](unsigned key,int value){changes.emplace_back(key,value);return true;});
    require(consumed==3&&changes==std::vector<std::pair<unsigned,int>>{{0,0},{3,2},{4,0}},"Settings writer consumed another mod's keys");
    const auto root=std::filesystem::current_path()/("enhancement-options-test-"+std::to_string(GetCurrentProcessId())+"-"+std::to_string(GetTickCount64()));
    require(!std::filesystem::exists(root),"Options fixture already exists");
    OptionStore store;store.configure(root);store.bind("1001");require(options().packed()==defaultOptions,"New Dynasty did not get enabled defaults");
    require(store.availableFor(1001)&&!store.availableFor(1002),"Settings menu admitted a different Dynasty identity");
    require(store.change(0,0)&&store.change(1,0)&&store.change(2,0)&&store.change(3,1)&&store.change(4,0)&&store.change(5,0)&&store.change(6,1),"Valid options were rejected");
    const auto first=options().packed();require(!store.change(8,1)&&!store.change(1,2)&&!store.change(3,5)&&!store.change(4,-1),"Invalid options were accepted");
    require(options().packed()==first,"Invalid setting changed the active profile");
    store.bind("1002");require(options().packed()==defaultOptions&&!options().dollars,"Preferences leaked into another Dynasty");
    store.change(3,3);store.flush();store.bind("1001");require(options().packed()==first,"Preferences did not survive a Dynasty switch");
    OptionStore reloaded;reloaded.configure(root);reloaded.bind("1002");require(options().scale==GradeScale::Descriptive&&options().colors,"Reload did not restore the other Dynasty independently");
    SharedOptions reader;reader.open();Options shared;uint32_t league=0;
    require(reader.read(shared,&league)&&league==1002&&shared.packed()==options().packed(),"Combined native payload settings do not agree");
    {
        auto corrupt=valid;corrupt["league"]=1003;corrupt["gradeScale"]=1.5;
        const auto file=root/L"DynastyEnhancementSettings/1003.json";const auto contents=corrupt.dump();
        {std::ofstream out(file);out<<contents;}
        bool rejected=false;try{store.bind("1003");}catch(const std::exception&){rejected=true;}
        require(rejected&&!store.available()&&options().packed()==defaultOptions&&!store.change(0,0),"Malformed profile reused another Dynasty's settings or accepted edits");
        std::ifstream input(file);const std::string after((std::istreambuf_iterator<char>(input)),{});
        require(after==contents,"Invalid settings were overwritten during a failed load");input.close();std::filesystem::remove(file);
    }
    store.bind("1001");store.change(3,2);
    const auto blocker=root/L"DynastyEnhancementSettings/1001.tmp";
    std::filesystem::create_directory(blocker);
    bool failed=false;try{store.bind("1002");}catch(const std::exception&){failed=true;}
    require(failed&&!store.availableFor(1001)&&options().packed()==defaultOptions,"Failed old-profile write leaked its options into the new Dynasty");
    std::filesystem::remove(blocker);store.bind("1002");
    OptionStore recovered;recovered.configure(root);recovered.bind("1001");
    require(options().scale==GradeScale::STier&&!options().roster&&!options().colors&&!options().team&&options().dollars,"Old edits were lost or overwritten by new-Dynasty defaults after retry");
    std::array<std::exception_ptr,2> errors{};
    std::thread firstWriter([&]{try{for(int i=0;i<64;++i){store.change(3,i%4);store.flush();std::this_thread::yield();}}catch(...){errors[0]=std::current_exception();}});
    std::thread secondWriter([&]{try{for(int i=0;i<128;++i){store.flush();std::this_thread::yield();}}catch(...){errors[1]=std::current_exception();}});
    firstWriter.join();secondWriter.join();for(const auto& error:errors)if(error)std::rethrow_exception(error);
    store.change(3,4);store.change(7,2);store.change(4,0);store.flush();
    OptionStore concurrent;concurrent.configure(root);concurrent.bind("1002");
    require(options().scale==GradeScale::Blind&&options().teamScale==GradeScale::STier&&!options().colors,"Concurrent writes lost the final independent settings revision");
    require(reader.read(shared,&league)&&league==1002&&shared.scale==GradeScale::Blind&&shared.teamScale==GradeScale::STier,"Shared payload lost independent player/team scales");
    for(const auto id:{1001,1002})std::filesystem::remove(root/L"DynastyEnhancementSettings"/(std::to_string(id)+".json"));
    std::filesystem::remove(root/L"DynastyEnhancementSettings");std::filesystem::remove(root);
    currentOptions=39;
    std::cout<<"Passed: eight independent options, five scales, native section/foreign rows, bounded private-key writer, per-Dynasty persistence and combined-payload sharing.\n";
}
}
