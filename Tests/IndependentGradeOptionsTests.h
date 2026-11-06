#pragma once
namespace optiontests {
inline void independentGradeOptions(){
    using namespace enhancements;
    for(unsigned ps=0;ps<5;++ps)for(unsigned ts=0;ts<5;++ts)for(unsigned flags=0;flags<64;++flags){
        Options value;value.scale=GradeScale(ps);value.teamScale=GradeScale(ts);
        value.social=bool(flags&1);value.recruiting=bool(flags&2);value.roster=bool(flags&4);
        value.team=bool(flags&8);value.colors=bool(flags&16);value.dollars=bool(flags&32);
        require(Options::validBits(value.packed())&&Options::unpack(value.packed()).packed()==value.packed(),"Independent scale bit packing failed");
    }
    for(unsigned bits=0;bits<4096;++bits)if(Options::validBits(bits))require(Options::unpack(bits).packed()==bits,"Reserved scale bit was lost");
    require(!Options::validBits(4096)&&!Options::validBits(5u<<9),"Invalid shared scale admitted");
    Json old={{"format",1},{"league",99},{"socialMedia",true},{"recruitingFog",true},{"rosterFog",true},{"gradeScale",3},{"ratingColors",false},{"dollarValues",true}};
    const auto migrated=decodeOptions(old,99);
    require(migrated.scale==GradeScale::Descriptive&&migrated.teamScale==migrated.scale&&!migrated.colors&&migrated.dollars,"Legacy scale did not migrate to both controls");
    Json fresh=old;fresh["format"]=2;fresh.erase("gradeScale");fresh["playerGradeScale"]=4;fresh["teamGradeScale"]=1;
    auto value=decodeOptions(fresh,99);currentOptions=value.packed();
    require(options().scale==GradeScale::Blind&&options().teamScale==GradeScale::PlusMinus&&!playerColors(),"Split scales or Blind native colors differ");
    for(int n=0;n<=100;++n)require(ratingDisplay(n)==u8"–","Blind exposed a player rating");
    require(recruitingfog::display(recruitingfog::Visibility::Range,0,60,99)==u8"–"&&recruitingfog::display(recruitingfog::Visibility::Unknown,0)==u8"–","Blind revealed scouting bounds or unknown values");
    for(const auto* key:{"playerGradeScale","teamGradeScale"})for(const Json bad:std::vector<Json>{-1,5,1.5,true,nullptr,"1"}){
        auto invalid=fresh;invalid[key]=bad;bool rejected=false;try{decodeOptions(invalid,99);}catch(const std::exception&){rejected=true;}
        require(rejected,"Invalid independent scale accepted");
    }
    currentOptions=39;
}
}
