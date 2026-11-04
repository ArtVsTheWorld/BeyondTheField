#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <atomic>
#include <array>
#include <deque>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <set>
#include "../Vendor/json.hpp"
#include "RecruitingGradePolicy.h"
#include "RecruitingUiResponse.h"
#include "RecruitingUiGates.h"
#include "PlayingTimeGates.h"
#include "PlayingTimePolicy.h"
#if defined(RECRUIT_NOTES_PROBE) || defined(RECRUIT_NOTES_UI)
#include "RecruitNotes.h"
#include "RecruitNotesUiPrograms.h"
#endif
#if defined(RECRUIT_NOTES_UI)
#include "RecruitNotesUiRuntime.h"
#include "RecruitResumeRuntime.h"
#include "RecruitClassGrid.h"
#include "PlayerRatingGrid.h"
#include "PlayerRatingResponses.h"
#include "PlayerRatingMap.h"
#include "PlayerFogUiPrograms.h"
#include "PlayerCardUiPrograms.h"
#include "PlayerFogPerformance.h"
#include "PlayerHubUiPrograms.h"
#endif

namespace recruitingfog::runtime {
using Json=nlohmann::json;
using Getter=void*(__fastcall*)(void*,void**);
HMODULE self=nullptr;uintptr_t base=0;
Getter original=nullptr;
using DetailGetter=void*(__fastcall*)(void*,void**,uintptr_t,uintptr_t);
constexpr size_t detailCount=sizeof(playingTimeGates)/sizeof(playingTimeGates[0]);
std::array<DetailGetter,detailCount> detailOriginal{};
std::array<bool,detailCount> detailInstalled{};
std::array<std::atomic<unsigned>,detailCount> detailCalls{};
constexpr PlayingTimeSurface detailSurfaces[]={PlayingTimeSurface::Motivations,PlayingTimeSurface::SchoolPitch,PlayingTimeSurface::Pitches,PlayingTimeSurface::PitchGrid,PlayingTimeSurface::VisitActivities,PlayingTimeSurface::VisitSummary,PlayingTimeSurface::SchoolModule,PlayingTimeSurface::ProspectEntry};
static_assert(sizeof(detailSurfaces)/sizeof(detailSurfaces[0])==detailCount);
std::atomic<bool> disabled{false};std::atomic<unsigned> inflight{0},calls{0};bool installed=false;
std::mutex queueMutex;std::deque<Json> pending;
#if defined(RECRUIT_NOTES_UI)
notesui::Runtime notesUi;
notesui::Runtime playerUi(playerui::programs());
notesui::Runtime modernPlayerUi(playerui::modernPrograms());
notesui::Runtime playerControlUi(playercardui::controlPrograms());
notesui::Runtime playerCardUi(playercardui::cardPrograms());
notesui::Runtime playerTemplateUi(playercardui::templatePrograms());
notesui::Runtime playerSkillUi(playercardui::skillPrograms());
notesui::Runtime playerHubUi(playerhubui::programs());
const std::array<notesui::Runtime*,5> cardUiBanks={&playerControlUi,&playerCardUi,&playerTemplateUi,&playerSkillUi,&playerHubUi};
std::array<std::atomic<bool>,5> cardUiFailed{};
std::array<std::atomic<unsigned>,5> cardUiAttached{};
std::atomic<bool> playerUiFailed{false},playerUiLogged{false};
resume::Cache resumeCache;
using ClassRows=void(__fastcall*)(void*,void*,int,int,void*);
ClassRows originalClassRows=nullptr;bool classRowsInstalled=false;
constexpr uintptr_t classTableRva=0xbacd668,classRowsRva=0x7a88cd0,classKeyRva=0x7a89180,classParseRva=0x376f6d0;
std::atomic<unsigned> classGridChanges{0};
using RosterColumns=void(__fastcall*)(void*,void*,int);
using GridClose=void(__fastcall*)(void*,int);
using RosterPlayer=void*(__fastcall*)(void*,void**,void*);
RosterColumns originalRosterColumns=nullptr;GridClose originalGridClose=nullptr;RosterPlayer originalRosterPlayer=nullptr;
bool rosterColumnsInstalled=false,gridCloseInstalled=false,rosterPlayerInstalled=false;
std::atomic<int> rosterForm{-1};std::atomic<unsigned> rosterCells{0},rosterPanels{0};
std::atomic<unsigned> rosterColumnCalls{0};
constexpr uintptr_t rosterColumnsTable=0xbaa78b8,rosterColumnsRva=0x78ef740,gridCloseRva=0x7a88c90,rosterPlayerTable=0xbab18c0,rosterPlayerRva=0x79472b0;
struct PlayerBinding{uintptr_t table,slot,rva;const char* prefix;playerfog::Surface surface;};
constexpr PlayerBinding playerBindings[]={
    {0xbab1b28,0x228,0x7955fc0,"405553565741554156488d6c24c84881ec38010000488b0564c813064833c448",playerfog::Surface::TopAttributes},
    {0xbab0e60,0xc0,0x793d8c0,"48895c240855565741564157488d6c24c94881ec900000004c8bf24c8bf9e8ed",playerfog::Surface::Comparison},
    {0xbac4e50,0xb8,0x7a0f320,"405557415441564157488d6c24c94881ec00010000488b05043508064833c448",playerfog::Surface::PlaycallSubstitution},
    {0xbab5778,0xd0,0x796ee90,"48894c24085553565741554157488d6c24d14881ecf8000000498bd84c8bfa48",playerfog::Surface::RosterNIL},
    {0xc74ed78,0x28,0xa0b6110,"48895c24085556574154415541564157488dac2420faffff4881ec2007000048",playerfog::Surface::ContextPlayer},
    {0xbab5b70,0x40,0x7975c70,"488bc448894808554156488d68b84881ec38010000488958e84c8bf2488970e0",playerfog::Surface::RosterNIL},
    {0xc7522c8,0x38,0xa0ddfe0,"405553574156488d6c24c14881ec88000000498bd8488bfa4c8bf1e8d0c1e2f9",playerfog::Surface::RosterNIL},
    {0xc74fd70,0x58,0xa0c03f0,"4c8944241848894c2408555357415441554156488d6c24d14881ecd80000004d",playerfog::Surface::RosterNIL},
    {0xc751ea0,0x58,0xa0da9c0,"488bc448894808554157488d68b84881ec38010000488958e84c8bfa488970e0",playerfog::Surface::RosterNIL},
    {0xc753aa0,0x38,0xa0f2e20,"48894c2408555356574154415541564157488d6c24f84881ec08010000498bf0",playerfog::Surface::RosterNIL},
    {0xc754328,0x38,0xa0f9fb0,"488bc448894808554156488d68a14881ecc8000000488958e84c8bf2488970e0",playerfog::Surface::RosterNIL}};
constexpr size_t playerBindingCount=sizeof(playerBindings)/sizeof(playerBindings[0]);
std::array<DetailGetter,playerBindingCount> playerOriginal{};std::array<bool,playerBindingCount> playerInstalled{};std::array<std::atomic<unsigned>,playerBindingCount> playerCalls{};
using PlayerMap=void(__fastcall*)(void*,void*);
struct MapBinding{uintptr_t slot,rva;const char* prefix;const char* ratingKey;};
constexpr MapBinding mapBindings[]={
    {0x58,0x794ba00,"48896c24104889742418574883ec50488bb118040000488bfa488be94885f60f","overall"},
    {0x118,0x7951580,"48896c2420565741564883ec70488b05ac1214064833c44889442468488be948","Overall"}};
std::array<PlayerMap,2> mapOriginal{};std::array<bool,2> mapInstalled{};std::array<std::atomic<unsigned>,2> mapCalls{};
using ScriptSetup=uintptr_t(__fastcall*)(void*,void*,uintptr_t,uintptr_t,uintptr_t);
ScriptSetup originalScriptSetup=nullptr;bool notesSetupInstalled=false;
using ColorLength=unsigned(__fastcall*)(void*);
ColorLength originalColorLength=nullptr;bool colorLengthInstalled=false;
std::atomic<unsigned> notesAttachedMethods{0};
std::atomic<bool> notesAttachmentFailed{false};
constexpr uintptr_t scriptSetupRva=0x7c36850,scriptTableRva=0xbc42fe8,scriptSetupSlot=0xc8;
constexpr std::array<unsigned char,24> scriptSetupPrefix={0x48,0x89,0x5c,0x24,0x10,0x48,0x89,0x6c,0x24,0x18,0x48,0x89,0x74,0x24,0x20,0x57,0x41,0x56,0x41,0x57,0x48,0x83,0xec,0x20};
#endif
constexpr uintptr_t vtableRva=0xc752bc8,slot=0x40,getterRva=0xa0e91a0;
constexpr std::array<unsigned char,32> prefix={0x48,0x89,0x54,0x24,0x10,0x48,0x89,0x4c,0x24,0x08,0x55,0x53,0x41,0x56,0x48,0x8d,0xac,0x24,0xd0,0xfc,0xff,0xff,0x48,0x81,0xec,0x30,0x04,0x00,0x00,0x48,0x8b,0xda};
bool read(uintptr_t at,void* out,size_t size){SIZE_T got=0;return at>=0x10000&&ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<const void*>(at),out,size,&got)&&got==size;}
void note(Json value)noexcept{try{std::lock_guard<std::mutex> lock(queueMutex);if(pending.size()<16)pending.push_back(std::move(value));}catch(...){}}
#if defined(RECRUIT_NOTES_PROBE)
using ScriptLength=unsigned(__fastcall*)(void*);
ScriptLength originalScriptLength=nullptr;bool notesProbeInstalled=false;
std::atomic<uintptr_t> notesObservedAsset{0};
std::atomic<uintptr_t> notesObservedOwner{0};
const auto notesPrograms=notesui::programs();
uint64_t notesBodyHash(const std::vector<unsigned char>& bytes){uint64_t h=14695981039346656037ull;for(auto b:bytes){h^=b;h*=1099511628211ull;}return h;}
unsigned __fastcall notesLengthHook(void* object){
    const auto length=originalScriptLength(object);
    if(disabled||notesObservedAsset)return length;
    if(std::none_of(notesPrograms.begin(),notesPrograms.end(),[&](const auto& p){return p.size==length;}))return length;
    uintptr_t definition=0;if(!read(reinterpret_cast<uintptr_t>(object)+0x58,&definition,8))return length;
    for(const auto& p:notesPrograms)if(p.size==length&&definition>p.offset+0x10000){
        const auto asset=definition-p.offset;char magic[14]{};if(!read(asset,magic,14)||memcmp(magic,"Apt Data:1:",11))continue;
        std::vector<unsigned char> bytes(length);if(!read(definition+0x30,bytes.data(),bytes.size())||notesBodyHash(bytes)!=p.hash)continue;
        notesObservedOwner=reinterpret_cast<uintptr_t>(object);notesObservedAsset=asset;note({{"event","notes_asset_observed"},{"asset",asset},{"owner",notesObservedOwner.load()}});break;
    }
    return length;
}
#endif
bool replace(void* expected,void* wanted,uintptr_t table=vtableRva,uintptr_t offset=slot){
    auto address=reinterpret_cast<PVOID volatile*>(base+table+offset);DWORD old=0,unused=0;
    if(!VirtualProtect(const_cast<PVOID*>(address),8,PAGE_READWRITE,&old))return false;
    const auto previous=InterlockedCompareExchangePointer(address,wanted,expected);
    VirtualProtect(const_cast<PVOID*>(address),8,old,&unused);return previous==expected;
}
Json header(uintptr_t at){
    std::array<uint64_t,10> words{};
    if(!read(at,words.data(),sizeof(words)))return {{"readable",false}};
    return {{"address",at},{"words",words}};
}
template<class T>T peek(uintptr_t at){T value{};read(at,&value,sizeof(value));return value;}
std::set<unsigned> pitchMask(uintptr_t object){
    std::set<unsigned> result;
    const auto context=peek<uintptr_t>(object+0x420),config=peek<uintptr_t>(context+0x148);
    const auto begin=peek<uintptr_t>(config+0x460),end=peek<uintptr_t>(config+0x468);
    bool valid=begin>=0x10000&&end>begin&&(end-begin)%8==0&&(end-begin)/8<=64;
    std::set<unsigned> known;
    if(valid)for(auto at=begin;at<end;at+=8){
        const auto entry=peek<uintptr_t>(at);const auto id=peek<unsigned char>(entry+0x10);
        const auto first=peek<uintptr_t>(entry+0x30),last=peek<uintptr_t>(entry+0x38);
        if(first<0x10000||last<first||last-first!=3||!known.insert(id).second){valid=false;break;}
        std::array<unsigned char,3> motivations{};if(!read(first,motivations.data(),3)){valid=false;break;}
        for(auto motivation:motivations){if(motivation>13){valid=false;break;}if(motivation==playingTimeMotivation)result.insert(id);}
        if(!valid)break;
    }
    // If the pitch configuration cannot be verified, hide bundle grades rather
    // than accidentally expose an aggregate containing the masked component.
    if(!valid){result.clear();for(unsigned i=0;i<256;++i)result.insert(i);}
    return result;
}
PlayingTimeStats applyPlayingTime(uintptr_t root,PlayingTimeSurface surface,unsigned selected,uintptr_t object){
    UiResponse view(read);std::set<unsigned> pitches;
    if(surface==PlayingTimeSurface::PitchGrid||surface==PlayingTimeSurface::Pitches)pitches=pitchMask(object);
    return maskPlayingTime(view,root,surface,selected,pitches,
        [&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);},
        [&](uintptr_t at,const char* key,unsigned value){reinterpret_cast<void(__fastcall*)(void*,const char*,unsigned)>(base+0x2bf67d0)(reinterpret_cast<void*>(at),key,value);});
}
std::string smallText(uintptr_t at){
    std::array<unsigned char,16> bytes{};if(!read(at,bytes.data(),bytes.size()))return {};
    if(bytes[15]&128){uintptr_t data=0;unsigned size=0;memcpy(&data,bytes.data(),8);memcpy(&size,bytes.data()+8,4);if(size>128)return {};std::string result(size,'\0');return !size||read(data,result.data(),size)?result:std::string();}
    return bytes[15]<=15?std::string(reinterpret_cast<const char*>(bytes.data()),15-bytes[15]):std::string();
}
Json snapshot(uintptr_t at,unsigned depth=0,bool full=false,size_t rootLimit=2){
    if(!at||depth>6)return nullptr;
    const auto kind=peek<unsigned>(at+0x10);
    if(kind==1)return Json(peek<unsigned char>(at+0x18)!=0);
    if(kind==2)return Json(peek<double>(at+0x18));
    if(kind==3)return Json(smallText(peek<uintptr_t>(at+0x20)));
    if(kind==4){
        const auto begin=peek<uintptr_t>(at+0x18),end=peek<uintptr_t>(at+0x20);
        if(begin>end||(end-begin)%8||end-begin>512*8)return {{"badArray",header(at)}};
        Json items=Json::array();const auto count=(std::min)(size_t((end-begin)/8),depth?size_t(24):rootLimit);
        for(size_t i=0;i<count;++i)items.push_back(snapshot(peek<uintptr_t>(begin+i*8),depth+1,full,rootLimit));
        return {{"count",(end-begin)/8},{"items",items}};
    }
    if(kind==5){
        const auto buckets=peek<uintptr_t>(at+0x20);const auto count=peek<unsigned>(at+0x28);
        if(!count||count>512)return {{"badMap",header(at)}};
        Json fields=Json::object();std::set<uintptr_t> visited;
        for(unsigned i=0;i<count;++i){auto node=peek<uintptr_t>(buckets+i*8);while(node&&node!=uintptr_t(-1)&&visited.insert(node).second&&visited.size()<256){
            const auto name=smallText(peek<uintptr_t>(node+8));const auto value=peek<uintptr_t>(node+0x10);
            if(full||depth>1||name=="FirstName"||name=="LastName"||name=="RecordId"||name=="PercentageScouted"||name=="Scouted"||name=="ScoutingAttributes")fields[name]=snapshot(value,depth+1,full,rootLimit);
            node=peek<uintptr_t>(node+0x18);
        }}return fields;
    }
    return {{"kind",kind},{"header",header(at)}};
}
struct CallGuard{CallGuard(){++inflight;}~CallGuard(){--inflight;}};
#if defined(RECRUIT_NOTES_UI)
// Focus callbacks use a native path that can bypass invocation setup. Their
// replacement keeps argc, flags, parameters and register count unchanged, so
// redirecting before the body length is returned preserves the existing frame.
unsigned __fastcall colorLengthHook(void* object){
    // Ordinary scripts leave through a read-only fast path: no atomics are
    // incremented, no allocation, no logging, and no process-memory queries.
    if(!disabled){
        const auto definition=*reinterpret_cast<const uintptr_t*>(static_cast<const unsigned char*>(object)+0x58);
        const auto* h=reinterpret_cast<const unsigned char*>(definition);
        const auto size=notesui::field<unsigned>(h,24),argc=notesui::field<unsigned>(h,8);const auto registers=notesui::field<unsigned short>(h,12),flags=notesui::field<unsigned short>(h,14);
        for(size_t bank=0;bank<cardUiBanks.size();++bank)if(!cardUiFailed[bank]&&cardUiBanks[bank]->acceptsFrame(h,true))
        try{CallGuard guard;if(disabled)return originalColorLength(object);const auto index=cardUiBanks[bank]->beforeInvoke(object,read,true);
            if(index>=0){const auto bit=1u<<index;if(!(cardUiAttached[bank].fetch_or(bit)&bit))note({{"event","player_fog_card_adapter_attached"},{"bank",bank},{"method",index},{"path","fixed frame body accessor"}});}}
        catch(const std::exception& error){cardUiFailed[bank]=true;note({{"event","player_fog_card_adapter_failed"},{"bank",bank},{"reason",error.what()}});}
        if(!notesAttachmentFailed&&size==148&&argc==1&&registers==2&&flags==41)
        try{CallGuard guard;if(disabled)return originalColorLength(object);const auto index=notesUi.beforeInvoke(object,read,true);if(index>=0){const auto bit=1u<<index;if(!(notesAttachedMethods.fetch_or(bit)&bit))note({{"event","recruit_color_focus_attached"},{"program",index}});}}
        catch(const std::exception& error){notesAttachmentFailed=true;note({{"event","recruit_color_focus_failed"},{"reason",error.what()}});}
    }
    return originalColorLength(object);
}
std::string classGridLabel(void* source,int form,int row,const char* originalLabel){
    const auto cached=resumeCache.current(base,read);if(!cached)return {};
    ClassKeySink key{classKeyTable,{}};
    reinterpret_cast<void(__fastcall*)(void*,void*,int,int)>(base+classKeyRva)(source,&key,form,row);
    if(key.value.empty()||key.value.size()>=32)return {};
    std::array<unsigned char,32> bytes{};memcpy(bytes.data(),key.value.data(),key.value.size());
    ClassKeyBlob blob{32,0,bytes.data(),false};
    const auto record=reinterpret_cast<unsigned(__fastcall*)(void*)>(base+classParseRva)(&blob);
    const auto found=cached->data.entries.find(static_cast<uint32_t>(record));
    if(found==cached->data.entries.end()||!found->second.juniorCollege||found->second.classYear.empty())return {};
    const auto& entry=found->second;
    if(std::string(originalLabel).find(entry.classYear)==std::string::npos)return {};
    const auto label=entry.saved.at("competitionClass").get<std::string>()+" ("+entry.classYear+")";
    if(classGridChanges.fetch_add(1)<3)note({{"event","recruit_class_grid_label"},{"record",record},{"label",label}});return label;
}
void __fastcall classRowsHook(void* source,void* target,int form,int row,void* columns){
    playerperf::Sample performance(playerperf::rows);
    if(!disabled&&form==rosterForm.load()){
        playerfog::GridSink sink{playerfog::gridTable,target};
        if(playerfog::gridColumns(sink,columns)){CallGuard guard;{playerperf::Sample nativePerformance(playerperf::nativeRows);originalClassRows(source,&sink,form,row,columns);}rosterCells+=sink.changed;return;}
    }
    CallGuard guard;if(disabled||!classGridColumns(columns)){originalClassRows(source,target,form,row,columns);return;}
    ClassGridSink sink{classGridTable,target,source,form,row,classGridLabel};originalClassRows(source,&sink,form,row,columns);classGridFlush(&sink);
}
void __fastcall rosterColumnsHook(void* source,void* target,int form){
    playerperf::Sample performance(playerperf::columns);
    CallGuard guard;if(disabled){originalRosterColumns(source,target,form);return;}
    playerfog::ColumnSink sink{playerfog::columnTable};sink.fields.reserve(768);
    originalRosterColumns(source,&sink,form);
    unsigned columnCount=0;for(unsigned i=0;i<sink.names.size();++i)if(!sink.names[i].empty())columnCount=i+1;
    const bool recognized=form>=0&&playerfog::rosterSchema(sink.names,columnCount);rosterForm=recognized?form:-1;
    playerfog::replayColumns(sink,target,recognized);
    if(rosterColumnCalls.fetch_add(1)<3)note({{"event","player_fog_roster_columns"},{"form",form},{"columns",columnCount},{"recognized",recognized},{"names",sink.names}});
}
void __fastcall gridCloseHook(void* source,int form){
    CallGuard guard;if(form==rosterForm.load())rosterForm=-1;originalGridClose(source,form);
}
void* __fastcall rosterPlayerHook(void* source,void** out,void* argument){
    CallGuard guard;auto* result=originalRosterPlayer(source,out,argument);
    if(!disabled&&out&&*out){
        UiResponse view(read);
        const auto changed=playerfog::convert(view,reinterpret_cast<uintptr_t>(*out),playerfog::Surface::RosterNIL,[&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);});
        if(changed&&rosterPanels.fetch_add(1)<3)note({{"event","player_fog_roster_panel"},{"changed",changed}});
    }
    return result;
}
template<size_t Index>void* __fastcall playerResponseHook(void* source,void** out,uintptr_t first,uintptr_t second){
    CallGuard guard;auto* result=playerOriginal[Index](source,out,first,second);
    if(!disabled&&out&&*out){UiResponse view(read);
        const auto changed=playerfog::convert(view,reinterpret_cast<uintptr_t>(*out),playerBindings[Index].surface,[&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);});
        if(playerCalls[Index].fetch_add(1)<3)note({{"event","player_fog_response"},{"surface",Index},{"changed",changed}});
    }return result;
}
const DetailGetter playerHooks[]={playerResponseHook<0>,playerResponseHook<1>,playerResponseHook<2>,playerResponseHook<3>,playerResponseHook<4>,playerResponseHook<5>,playerResponseHook<6>,playerResponseHook<7>,playerResponseHook<8>,playerResponseHook<9>,playerResponseHook<10>};
template<size_t Index>void __fastcall playerMapHook(void* source,void* target){
    CallGuard guard;if(disabled){mapOriginal[Index](source,target);return;}
    playerfog::MapSink sink{playerfog::mapTable,target,mapBindings[Index].ratingKey};
    if constexpr(Index==1)sink.labelKey="DEOverallGrade";mapOriginal[Index](source,&sink);
    if(mapCalls[Index].fetch_add(1)<3)note({{"event","player_fog_card_map"},{"surface",Index},{"changed",sink.changed}});
}
const PlayerMap mapHooks[]={playerMapHook<0>,playerMapHook<1>};
uintptr_t __fastcall notesSetupHook(void* object,void* saved,uintptr_t receiver,uintptr_t parent,uintptr_t super){
    CallGuard guard;
    {
    playerperf::Sample performance(playerperf::scriptAdapters);
#if !defined(PLAYER_FOG_PREVIEW) || defined(PLAYER_FOG_COLORS)
    if(!disabled&&!playerUiFailed)try{const auto legacy=playerUi.beforeInvoke(object,read);const auto modern=legacy>=0?-1:modernPlayerUi.beforeInvoke(object,read);
        if((legacy>=0||modern>=0)&&!playerUiLogged.exchange(true))note({{"event","player_fog_color_adapter_attached"},{"legacy",legacy>=0}});}
    catch(const std::exception& error){playerUiFailed=true;note({{"event","player_fog_color_adapter_failed"},{"reason",error.what()}});}
    if(!disabled)for(size_t bank=0;bank<cardUiBanks.size();++bank)if(!cardUiFailed[bank])try{
        const auto index=cardUiBanks[bank]->beforeInvoke(object,read);
        if(index>=0){const auto bit=1u<<index;if(!(cardUiAttached[bank].fetch_or(bit)&bit))note({{"event","player_fog_card_adapter_attached"},{"bank",bank},{"method",index}});}
    }catch(const std::exception& error){cardUiFailed[bank]=true;note({{"event","player_fog_card_adapter_failed"},{"bank",bank},{"reason",error.what()}});}
#endif
    if(!disabled&&!notesAttachmentFailed)try{const auto index=notesUi.beforeInvoke(object,read);if(index>=0){const auto bit=1u<<index;
        if(!(notesAttachedMethods.fetch_or(bit)&bit))note({{"event","recruit_notes_method_attached"},{"program",index}});}}
    catch(const std::exception& error){notesAttachmentFailed=true;note({{"event","recruit_notes_attachment_failed"},{"reason",error.what()}});}
    }
    return originalScriptSetup(object,saved,receiver,parent,super);
}
#endif
template<size_t Index>void* __fastcall detailHook(void* object,void** out,uintptr_t first,uintptr_t second){
    CallGuard guard;auto result=detailOriginal[Index](object,out,first,second);const auto call=++detailCalls[Index];
    if(!disabled){uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        try{const auto stats=applyPlayingTime(value,detailSurfaces[Index],static_cast<unsigned>(first),reinterpret_cast<uintptr_t>(object));
#if defined(RECRUIT_NOTES_UI)
            if constexpr(Index==detailCount-1){
                const auto cache=resumeCache.current(base,read);UiResponse view(read);std::map<std::string,uintptr_t> fields;
                if(cache&&view.members(value,fields)&&fields.count("recordKey")&&fields.count("firstName")&&fields.count("lastName")){
                    double id=0;std::string firstName,lastName;
                    if(view.number(fields.at("recordKey"),id)&&id>=0&&id<=4294967295.&&std::floor(id)==id&&view.string(fields.at("firstName"),firstName)&&view.string(fields.at("lastName"),lastName)){
                        const auto found=cache->data.entries.find(static_cast<uint32_t>(id));
                        if(found!=cache->data.entries.end()&&found->second.first==firstName&&found->second.last==lastName&&found->second.juniorCollege&&!found->second.classYear.empty()){
                            const auto label=found->second.saved.at("competitionClass").get<std::string>()+" ("+found->second.classYear+")";
                            reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(value),"className",label.c_str());
                        }
                    }
                }
            }
#endif
            if(call<=20&&(call==1||stats.grades||stats.previews||stats.unsupported))note({{"event","playing_time_masked"},{"getter",playingTimeGates[Index].name},{"call",call},{"first",first},{"grades",stats.grades},{"dealbreakers",stats.dealbreakers},{"previews",stats.previews},{"unsupported",stats.unsupported}});
        }catch(const std::exception& error){note({{"event","playing_time_failed"},{"getter",playingTimeGates[Index].name},{"reason",error.what()}});}}
    return result;
}
template<size_t... Index>constexpr auto detailHooks(std::index_sequence<Index...>){return std::array<DetailGetter,sizeof...(Index)>{detailHook<Index>...};}
constexpr auto hooks=detailHooks(std::make_index_sequence<detailCount>{});
void* __fastcall getterHook(void* object,void** out){
    CallGuard guard;
    auto result=original(object,out);
    const auto call=++calls;
    if(!disabled){
        const auto began=GetTickCount64();uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        try{
            UiResponse view(read);
#if defined(RECRUIT_NOTES_UI)
            const auto cached=resumeCache.current(base,read);bool notesLoading=false;
            const auto notesCount=appendRecruitNotes(view,value,[&](uintptr_t at,const char* key,const char* text){
                reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);
                reinterpret_cast<void(__fastcall*)(void*,const char*,bool)>(base+0x2bf6720)(reinterpret_cast<void*>(at),"DENotesLoading",notesLoading);
            },[&](NotesProspect& p,double id,const std::string& first,const std::string& last){return resumeCache.compose(cached,p,id,first,last,notesLoading);});
            if(call<=5)note({{"event","recruit_notes_prepared"},{"recruits",notesCount},{"resumes",bool(cached)}});
#elif defined(RECRUIT_NOTES_PROBE)
            const auto notesCount=appendRecruitNotes(view,value,[&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);});
            if(call<=5)note({{"event","recruit_notes_prepared"},{"recruits",notesCount}});
#endif
            auto stats=convertRecruitingResponse(view,value,
                [&](uintptr_t at,const char* key,const char* text){reinterpret_cast<void(__fastcall*)(void*,const char*,const char*)>(base+0x25a3e60)(reinterpret_cast<void*>(at),key,text);},
                [&](uintptr_t at,const char* key,bool flag){reinterpret_cast<void(__fastcall*)(void*,const char*,bool)>(base+0x2bf6720)(reinterpret_cast<void*>(at),key,flag);});
            if(call<=10||stats.unsupported)note({{"event","grades_applied"},{"call",call},{"recruits",stats.recruits},{"attributes",stats.attributes},{"revealed",stats.revealed},{"ranges",stats.ranges},{"unknown",stats.unknown},{"unsupported",stats.unsupported},{"ms",GetTickCount64()-began}});
            const auto mask=applyPlayingTime(value,PlayingTimeSurface::RecruitList,0,reinterpret_cast<uintptr_t>(object));
            if(call<=10)note({{"event","dealbreakers_masked"},{"fields",mask.dealbreakers},{"unsupported",mask.unsupported}});
        }catch(const std::exception& error){note({{"event","conversion_failed"},{"reason",error.what()}});}
    }
    if(!disabled&&call<=5){
        uintptr_t value=0;if(out)read(reinterpret_cast<uintptr_t>(out),&value,8);
        note({{"event","post_conversion_response"},{"call",call},{"resultEqualsOut",result==out},{"snapshot",snapshot(value)}});
    }
    return result;
}
#if defined(RECRUIT_NOTES_UI)
void installRosterProviders(bool preflightOnly=false){
    struct Binding{uintptr_t table,offset,rva;const char* prefix;void* hook;};
    const Binding bindings[]={
        {rosterColumnsTable,0x70,rosterColumnsRva,"488bc455488bec4881ec80000000488958084881c11804000048897010488bda",reinterpret_cast<void*>(rosterColumnsHook)},
        {classTableRva,0x60,gridCloseRva,"40534883ec204863dae89285c5fb488bd3488bc8e8679bc5fb4885c0740a4c8b",reinterpret_cast<void*>(gridCloseHook)},
        {rosterPlayerTable,0x50,rosterPlayerRva,"4055535741554156488d6c24c94881ec00010000498bd84c8bf24c8be933ffe8",reinterpret_cast<void*>(rosterPlayerHook)}};
    for(const auto& binding:bindings){
        uintptr_t current=0;std::array<unsigned char,32> actual{};
        if(!read(base+binding.table+binding.offset,&current,8)||current!=base+binding.rva||!read(current,actual.data(),32))throw std::runtime_error("Unsupported or owned roster provider");
        const auto digit=[](char c){return c<='9'?c-'0':c-'a'+10;};
        for(size_t b=0;b<32;++b)if(actual[b]!=(digit(binding.prefix[2*b])*16+digit(binding.prefix[2*b+1])))throw std::runtime_error("Unsupported roster provider fingerprint");
    }
    for(size_t i=0;i<playerOriginal.size();++i){const auto& binding=playerBindings[i];uintptr_t current=0;std::array<unsigned char,32> actual{};
        if(!read(base+binding.table+binding.slot,&current,8)||current!=base+binding.rva||!read(current,actual.data(),32))throw std::runtime_error("Unsupported or owned player response");
        const auto digit=[](char c){return c<='9'?c-'0':c-'a'+10;};for(size_t b=0;b<32;++b)if(actual[b]!=(digit(binding.prefix[2*b])*16+digit(binding.prefix[2*b+1])))throw std::runtime_error("Unsupported player response fingerprint");
    }
    for(size_t i=0;i<mapOriginal.size();++i){const auto& binding=mapBindings[i];uintptr_t current=0;std::array<unsigned char,32> actual{};
        if(!read(base+0xbab1b28+binding.slot,&current,8)||current!=base+binding.rva||!read(current,actual.data(),32))throw std::runtime_error("Unsupported or owned card map provider");
        const auto digit=[](char c){return c<='9'?c-'0':c-'a'+10;};for(size_t b=0;b<32;++b)if(actual[b]!=(digit(binding.prefix[2*b])*16+digit(binding.prefix[2*b+1])))throw std::runtime_error("Unsupported card map fingerprint");
    }
    if(preflightOnly)return;
    originalRosterColumns=reinterpret_cast<RosterColumns>(base+rosterColumnsRva);originalGridClose=reinterpret_cast<GridClose>(base+gridCloseRva);originalRosterPlayer=reinterpret_cast<RosterPlayer>(base+rosterPlayerRva);
    if(!replace(reinterpret_cast<void*>(originalRosterColumns),reinterpret_cast<void*>(rosterColumnsHook),rosterColumnsTable,0x70))throw std::runtime_error("Roster columns ownership changed");rosterColumnsInstalled=true;
    if(!replace(reinterpret_cast<void*>(originalGridClose),reinterpret_cast<void*>(gridCloseHook),classTableRva,0x60))throw std::runtime_error("Roster close ownership changed");gridCloseInstalled=true;
    if(!replace(reinterpret_cast<void*>(originalRosterPlayer),reinterpret_cast<void*>(rosterPlayerHook),rosterPlayerTable,0x50))throw std::runtime_error("Roster player ownership changed");rosterPlayerInstalled=true;
    for(size_t i=0;i<playerOriginal.size();++i){const auto& binding=playerBindings[i];playerOriginal[i]=reinterpret_cast<DetailGetter>(base+binding.rva);
        if(!replace(reinterpret_cast<void*>(playerOriginal[i]),reinterpret_cast<void*>(playerHooks[i]),binding.table,binding.slot))throw std::runtime_error("Player response ownership changed");playerInstalled[i]=true;
    }
    for(size_t i=0;i<mapOriginal.size();++i){const auto& binding=mapBindings[i];mapOriginal[i]=reinterpret_cast<PlayerMap>(base+binding.rva);
        if(!replace(reinterpret_cast<void*>(mapOriginal[i]),reinterpret_cast<void*>(mapHooks[i]),0xbab1b28,binding.slot))throw std::runtime_error("Card map ownership changed");mapInstalled[i]=true;
    }
}
#endif
DWORD stop(){
#if defined(RECRUIT_NOTES_UI)
#if !defined(PLAYER_FOG_PREVIEW) || defined(PLAYER_FOG_COLORS)
    bool retainedPlayerUi=playerUi.ownerCount()||modernPlayerUi.ownerCount();
    for(const auto* bank:cardUiBanks)retainedPlayerUi=retainedPlayerUi||bank->ownerCount();
    if(retainedPlayerUi){note({{"event","player_ui_restart_required"},{"reason","Native player UI retains a copied script definition"}});return 4;}
#endif
    if(notesUi.ownerCount()){note({{"event","notes_ui_restart_required"},{"reason","The game can retain cloned Notes definitions; use a clean restart"}});return 4;}
#endif
    disabled=true;
    bool ownershipFailed=false;
#if defined(RECRUIT_NOTES_UI)
    rosterForm=-1;
    for(size_t i=0;i<mapOriginal.size();++i)if(mapInstalled[i]){const auto& binding=mapBindings[i];if(replace(reinterpret_cast<void*>(mapHooks[i]),reinterpret_cast<void*>(mapOriginal[i]),0xbab1b28,binding.slot))mapInstalled[i]=false;else ownershipFailed=true;}
    for(size_t i=0;i<playerOriginal.size();++i)if(playerInstalled[i]){const auto& binding=playerBindings[i];if(replace(reinterpret_cast<void*>(playerHooks[i]),reinterpret_cast<void*>(playerOriginal[i]),binding.table,binding.slot))playerInstalled[i]=false;else ownershipFailed=true;}
    if(rosterPlayerInstalled){if(replace(reinterpret_cast<void*>(rosterPlayerHook),reinterpret_cast<void*>(originalRosterPlayer),rosterPlayerTable,0x50))rosterPlayerInstalled=false;else ownershipFailed=true;}
    if(gridCloseInstalled){if(replace(reinterpret_cast<void*>(gridCloseHook),reinterpret_cast<void*>(originalGridClose),classTableRva,0x60))gridCloseInstalled=false;else ownershipFailed=true;}
    if(rosterColumnsInstalled){if(replace(reinterpret_cast<void*>(rosterColumnsHook),reinterpret_cast<void*>(originalRosterColumns),rosterColumnsTable,0x70))rosterColumnsInstalled=false;else ownershipFailed=true;}
    if(classRowsInstalled){if(replace(reinterpret_cast<void*>(classRowsHook),reinterpret_cast<void*>(originalClassRows),classTableRva,0x68))classRowsInstalled=false;else ownershipFailed=true;}
    if(colorLengthInstalled){if(replace(reinterpret_cast<void*>(colorLengthHook),reinterpret_cast<void*>(originalColorLength),scriptTableRva,0xb0))colorLengthInstalled=false;else ownershipFailed=true;}
    if(notesSetupInstalled){if(replace(reinterpret_cast<void*>(notesSetupHook),reinterpret_cast<void*>(originalScriptSetup),scriptTableRva,scriptSetupSlot))notesSetupInstalled=false;else ownershipFailed=true;}
#endif
#if defined(RECRUIT_NOTES_PROBE)
    if(notesProbeInstalled){if(replace(reinterpret_cast<void*>(notesLengthHook),reinterpret_cast<void*>(originalScriptLength),0xbc42fe8,0xb0))notesProbeInstalled=false;else ownershipFailed=true;}
#endif
    for(size_t i=0;i<detailCount;++i)if(detailInstalled[i]){const auto& gate=playingTimeGates[i];if(replace(reinterpret_cast<void*>(hooks[i]),reinterpret_cast<void*>(detailOriginal[i]),gate.vtable,gate.slot))detailInstalled[i]=false;else ownershipFailed=true;}
    if(installed){if(!replace(reinterpret_cast<void*>(getterHook),reinterpret_cast<void*>(original)))return 2;installed=false;}
    const auto deadline=GetTickCount64()+5000;while(inflight&&GetTickCount64()<deadline)Sleep(1);
    return ownershipFailed?2:inflight?3:0;
}
DWORD WINAPI worker(void*){
    wchar_t path[32768]{};GetModuleFileNameW(self,path,32768);const auto folder=std::filesystem::path(path).parent_path();base=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
    auto flush=[&](){std::deque<Json> items;{std::lock_guard<std::mutex> lock(queueMutex);items.swap(pending);}if(!items.empty()){std::ofstream out(folder/L"recruiting-fog.jsonl",std::ios::app);for(const auto& j:items)out<<j.dump(-1,' ',false,Json::error_handler_t::replace)<<'\n';}};
    try{
#if defined(PLAYER_FOG_PREVIEW)
        // Development-only bridge into the already installed recruiting hook.
        // This never installs Notes/reader hooks or changes installed files.
        uintptr_t parent=0;if(!read(base+classTableRva+0x68,&parent,8))throw std::runtime_error("Cannot read shared row owner");
        HMODULE owner=nullptr;wchar_t ownerPath[32768]{};
        if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(parent),&owner)||!GetModuleFileNameW(owner,ownerPath,32768)||std::filesystem::path(ownerPath).filename()!=L"DynastyEnhancerRecruitFog-v1.dll")throw std::runtime_error("Preview requires the installed recruiting owner");
        HMODULE pin=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pin))throw std::runtime_error("Cannot pin preview");
        originalClassRows=reinterpret_cast<ClassRows>(parent);installRosterProviders();
        if(!replace(reinterpret_cast<void*>(originalClassRows),reinterpret_cast<void*>(classRowsHook),classTableRva,0x68))throw std::runtime_error("Shared row owner changed");classRowsInstalled=true;
#if defined(PLAYER_FOG_COLORS)
        if(!read(base+scriptTableRva+scriptSetupSlot,&parent,8)||!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(parent),&owner)||!GetModuleFileNameW(owner,ownerPath,32768)||std::filesystem::path(ownerPath).filename()!=L"DynastyEnhancerRecruitFog-v1.dll")throw std::runtime_error("Preview requires installed script owner");
        playerUi.prepare();modernPlayerUi.prepare();for(auto* bank:cardUiBanks)bank->prepare();originalScriptSetup=reinterpret_cast<ScriptSetup>(parent);
        if(!replace(reinterpret_cast<void*>(originalScriptSetup),reinterpret_cast<void*>(notesSetupHook),scriptTableRva,scriptSetupSlot))throw std::runtime_error("Script invocation owner changed");notesSetupInstalled=true;
#endif
        note({{"event","player_fog_preview_active"},{"reader",false},{"installedFilesChanged",false}});
        while(!disabled){flush();Sleep(200);}flush();return 0;
#endif
        std::array<unsigned char,32> actual{};uintptr_t current=0;
#if defined(RECRUIT_NOTES_UI)
        // Reject an unsupported/occupied player surface before Notes definitions
        // can be attached and retained by a concurrent native UI request.
        installRosterProviders(true);
#endif
        if(!read(base+getterRva,actual.data(),actual.size())||actual!=prefix)throw std::runtime_error("Unsupported recruiting getter fingerprint");
        for(const auto& gate:recruitingUiGates){if(!read(base+gate.rva,actual.data(),actual.size())||actual!=gate.bytes)throw std::runtime_error("Unsupported UI-value setter fingerprint");}
        for(const auto& gate:playingTimeGates){if(!read(base+gate.rva,actual.data(),actual.size())||actual!=gate.bytes||!read(base+gate.vtable+gate.slot,&current,8)||current!=base+gate.rva)throw std::runtime_error("Unsupported or already-owned playing-time getter");}
        if(!read(base+vtableRva+slot,&current,8)||current!=base+getterRva)throw std::runtime_error("Recruiting getter already owned; no hook installed");
        HMODULE pinned=nullptr;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,reinterpret_cast<LPCWSTR>(&worker),&pinned))throw std::runtime_error("Cannot pin recruiting runtime");
        original=reinterpret_cast<Getter>(current);
        if(!replace(reinterpret_cast<void*>(original),reinterpret_cast<void*>(getterHook)))throw std::runtime_error("Recruiting getter ownership changed");installed=true;
        for(size_t i=0;i<detailCount;++i){const auto& gate=playingTimeGates[i];detailOriginal[i]=reinterpret_cast<DetailGetter>(base+gate.rva);if(!replace(reinterpret_cast<void*>(detailOriginal[i]),reinterpret_cast<void*>(hooks[i]),gate.vtable,gate.slot))throw std::runtime_error("Playing-time getter ownership changed");detailInstalled[i]=true;}
#if defined(RECRUIT_NOTES_UI)
        if(!read(base+scriptSetupRva,actual.data(),scriptSetupPrefix.size())||memcmp(actual.data(),scriptSetupPrefix.data(),scriptSetupPrefix.size())||!read(base+scriptTableRva+scriptSetupSlot,&current,8)||current!=base+scriptSetupRva)throw std::runtime_error("Unsupported or already-owned script invocation setup");
        notesUi.prepare();playerUi.prepare();modernPlayerUi.prepare();for(auto* bank:cardUiBanks)bank->prepare();originalScriptSetup=reinterpret_cast<ScriptSetup>(current);
        if(!replace(reinterpret_cast<void*>(originalScriptSetup),reinterpret_cast<void*>(notesSetupHook),scriptTableRva,scriptSetupSlot))throw std::runtime_error("Notes invocation setup ownership changed");
        notesSetupInstalled=true;
        constexpr unsigned char colorLengthPrefix[]={0x48,0x8b,0x41,0x58,0x8b,0x40,0x18,0xc3};
        if(!read(base+scriptTableRva+0xb0,&current,8)||current!=base+0x7c34e40||!read(current,actual.data(),sizeof(colorLengthPrefix))||memcmp(actual.data(),colorLengthPrefix,sizeof(colorLengthPrefix)))throw std::runtime_error("Unsupported or already-owned color focus accessor");
        originalColorLength=reinterpret_cast<ColorLength>(current);
        if(!replace(reinterpret_cast<void*>(originalColorLength),reinterpret_cast<void*>(colorLengthHook),scriptTableRva,0xb0))throw std::runtime_error("Color focus accessor ownership changed");colorLengthInstalled=true;
        constexpr unsigned char classRowsPrefix[]={0x40,0x53,0x55,0x56,0x41,0x56,0x41,0x57,0x48,0x81,0xec,0x70,0x01,0,0,0x48,0x8b,0x05,0x5a,0x9b,0,0x06,0x48,0x33,0xc4,0x48,0x89,0x84,0x24,0x60,0x01,0};
        constexpr unsigned char classKeyPrefix[]={0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x74,0x24,0x20,0x57,0x48,0x81,0xec,0x70,0x01,0,0};
        constexpr unsigned char classParsePrefix[]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xf9};
        if(!read(base+classRowsRva,actual.data(),sizeof(classRowsPrefix))||memcmp(actual.data(),classRowsPrefix,sizeof(classRowsPrefix))||!read(base+classKeyRva,actual.data(),sizeof(classKeyPrefix))||memcmp(actual.data(),classKeyPrefix,sizeof(classKeyPrefix))||!read(base+classParseRva,actual.data(),sizeof(classParsePrefix))||memcmp(actual.data(),classParsePrefix,sizeof(classParsePrefix))||!read(base+classTableRva+0x78,&current,8)||current!=base+classKeyRva||!read(base+classTableRva+0x68,&current,8)||current!=base+classRowsRva)throw std::runtime_error("Unsupported or already-owned recruit Class grid provider");
        originalClassRows=reinterpret_cast<ClassRows>(current);
        if(!replace(reinterpret_cast<void*>(originalClassRows),reinterpret_cast<void*>(classRowsHook),classTableRva,0x68))throw std::runtime_error("Class grid provider ownership changed");classRowsInstalled=true;
        installRosterProviders();
        note({{"event","recruit_notes_ui_prepared"},{"methods",notesUi.methodCount()},{"attachment","live invocation setup"},{"unload","clean restart required after entry"}});
#endif
#if defined(RECRUIT_NOTES_PROBE)
        constexpr unsigned char lengthPrefix[]={0x48,0x8b,0x41,0x58,0x8b,0x40,0x18,0xc3};
        if(!read(base+0xbc42fe8+0xb0,&current,8)||current!=base+0x7c34e40||!read(current,actual.data(),sizeof(lengthPrefix))||memcmp(actual.data(),lengthPrefix,sizeof(lengthPrefix)))throw std::runtime_error("Unsupported script length accessor; Notes probe stopped");
        originalScriptLength=reinterpret_cast<ScriptLength>(current);if(!replace(reinterpret_cast<void*>(originalScriptLength),reinterpret_cast<void*>(notesLengthHook),0xbc42fe8,0xb0))throw std::runtime_error("Script length accessor ownership changed");notesProbeInstalled=true;
#endif
        note({{"event","active"},{"mode","letter grades, ranges and Playing Time masking"},{"scope","recruiting UI responses only"}});
        while(!disabled){
#if defined(PLAYER_FOG_PERF) && defined(RECRUIT_NOTES_UI)
            static uint64_t nextPerformance=0;if(GetTickCount64()>=nextPerformance){nextPerformance=GetTickCount64()+30000;
                note({{"event","player_fog_performance"},{"sampleCapPerPath",8192},{"rows",playerperf::report<Json>(playerperf::rows)},{"nativeRowsIncludingCollector",playerperf::report<Json>(playerperf::nativeRows)},{"scriptAdapters",playerperf::report<Json>(playerperf::scriptAdapters)},{"columns",playerperf::report<Json>(playerperf::columns)}});
            }
#endif
#if defined(RECRUIT_NOTES_UI)
            static uint64_t nextResumeTick=0;if(GetTickCount64()>=nextResumeTick){nextResumeTick=GetTickCount64()+1000;
                try{auto report=resumeCache.tick(base,folder,read);if(!report.is_null())note(std::move(report));}
                catch(const std::exception& error){resumeCache.request();note({{"event","recruit_resume_deferred"},{"reason",error.what()}});}
            }
#endif
#if defined(RECRUIT_NOTES_PROBE)
            if(notesProbeInstalled&&notesObservedAsset){std::ofstream out(folder/L"recruit-notes-observed.json");out<<Json({{"pid",GetCurrentProcessId()},{"asset",notesObservedAsset.load()},{"owner",notesObservedOwner.load()}}).dump();
                if(replace(reinterpret_cast<void*>(notesLengthHook),reinterpret_cast<void*>(originalScriptLength),0xbc42fe8,0xb0))notesProbeInstalled=false;}
#endif
            flush();Sleep(200);}flush();
    }catch(const std::exception& error){stop();note({{"event","failed"},{"reason",error.what()}});flush();}
    return 0;
}
}
extern "C" __declspec(dllexport) DWORD WINAPI DynastyEnhancerStop(void*){return recruitingfog::runtime::stop();}
BOOL WINAPI DllMain(HMODULE module,DWORD why,LPVOID){if(why==DLL_PROCESS_ATTACH){recruitingfog::runtime::self=module;DisableThreadLibraryCalls(module);auto thread=CreateThread(nullptr,0,recruitingfog::runtime::worker,nullptr,0,nullptr);if(thread)CloseHandle(thread);}return TRUE;}

