#include "../Source/NativeMapValue.h"
#include "../Source/HubTab.h"
#include "../Source/HubFeedModel.h"
#include "../Source/NewsScopeInput.h"
#include "../Source/HubScriptDefinition.h"
#include "../Source/HubNewsTemplate.h"
#include <array>
#include <cstring>
#include <iostream>
#include <stdexcept>
namespace {
bool insertion=true;
void* __fastcall nativeWrite(void* target,social::native::InsertResult* out,const char*){
    // Reproduce the observed machine-code write footprint rather than assign
    // C++ fields: vmovups [out] (16 bytes), then mov byte ptr [out+16].
    const std::array<void*,2> iterator={target,reinterpret_cast<void*>(0x12340000)};
    std::memcpy(out,iterator.data(),16);
    reinterpret_cast<unsigned char*>(out)[16]=insertion?1:0;
    return out;
}
void require(bool ok){if(!ok)throw std::runtime_error("Native map insertion ABI regression");}
}
int main(){
    struct Guarded {social::native::InsertResult result;std::array<unsigned char,16> canary;};
    Guarded g{};g.canary.fill(0xa5);const auto expected=g.canary;
    auto node=reinterpret_cast<void*>(0x100000);
    nativeWrite(node,&g.result,"key");require(g.canary==expected&&g.result.inserted&&g.result.node==node);
    for(bool value:{true,false}){insertion=value;const auto result=social::native::findOrInsert(nativeWrite,node,"key");require(result.node==node&&result.bucket==reinterpret_cast<void*>(0x12340000)&&result.inserted==value);}
    {
        std::array<unsigned char,2048> arena{};const auto start=reinterpret_cast<uintptr_t>(arena.data()),image=uintptr_t(0x140000000);
        auto put=[&](size_t offset,auto value){std::memcpy(arena.data()+offset,&value,sizeof(value));};
        auto read=[&](uintptr_t address,void* output,size_t size){if(address<start||address-start>arena.size()||size>arena.size()-(address-start))return false;std::memcpy(output,reinterpret_cast<void*>(address),size);return true;};
        put(0,image+0x1000);put(16,unsigned(5));put(32,start+64);put(40,unsigned(1));put(64,start+128);
        put(136,start+256);put(144,start+512);put(152,start+160);
        put(168,start+288);put(176,start+576);put(184,uintptr_t(0));
        std::memcpy(arena.data()+256,"layout",6);arena[271]=9;
        std::memcpy(arena.data()+288,"extra",5);arena[303]=10;
        put(512,image+0x2000);put(528,unsigned(4)); // Native array value
        put(576,image+0x3000);put(592,unsigned(5)); // Nested native object
        auto fields=social::hubtab::references(start,image,read);
        require(fields&&fields->size()==2&&fields->at("layout")==start+512&&fields->at("extra")==start+576);
        put(184,start+128);require(!social::hubtab::references(start,image,read)); // Cyclic map
        put(184,uintptr_t(0));put(168,start+256);require(!social::hubtab::references(start,image,read)); // Duplicate key
        put(168,start+288);put(576,uintptr_t(1));require(!social::hubtab::references(start,image,read)); // Foreign value
    }
    {
        using namespace social::embedded::lifecycle;
        const auto emitted=social::embedded::lifecycle::programs();
        for(const auto& p:emitted){
            std::array<unsigned char,definitionHeader> header{};
            auto put=[&](size_t at,auto value){memcpy(header.data()+at,&value,sizeof(value));};
            put(0,uintptr_t(0x300000));put(8,p.argc);put(12,static_cast<unsigned short>(p.registers));put(14,static_cast<unsigned short>(p.flags));put(16,uintptr_t(0x310000));put(24,static_cast<unsigned>(p.original.size()));put(32,unsigned(41));put(40,uintptr_t(0x320000));
            const auto before=header;const auto owned=clone(p,header);require(owned&&owned->size()==definitionHeader+p.body.size()&&header==before);
            require(std::equal(p.body.begin(),p.body.end(),owned->begin()+definitionHeader));
            for(size_t i=0;i<definitionHeader;++i)if(i<24||i>=28)require(owned->at(i)==header[i]);
            require(field<unsigned>(owned->data(),24)==p.body.size());put(8,p.argc+1);require(!clone(p,header));
        }
        std::array<unsigned char,0x60> object{};const auto owner=reinterpret_cast<uintptr_t>(object.data()),image=uintptr_t(0x140000000),definition=uintptr_t(0x400000);
        auto put=[&](size_t at,uintptr_t value){memcpy(object.data()+at,&value,8);};put(0,image+functionVtable);object[11]=0x46;put(definitionField,definition);
        auto read=[&](uintptr_t at,void* out,size_t size){if(at!=owner||size!=object.size())return false;memcpy(out,object.data(),size);return true;};
        require(ownerMatches(owner,image,definition,read));put(definitionField,definition+8);require(!ownerMatches(owner,image,definition,read));put(definitionField,definition);object[11]=0x45;require(!ownerMatches(owner,image,definition,read));
    }
    {
        auto patches=social::dropdown::patches();const auto before=patches.front().changed;social::embedded::scopeTemplateFlow(patches);const auto& after=patches.front().changed;
        for(size_t i=0;i<after.size();++i)if(!(i>=0xcd&&i<0xcd+41)&&i!=0x118)require(after[i]==before[i]);
        require(after[0x118]==0x73);size_t at=0xcd;std::vector<std::pair<std::string,int>> fields;
        while(at<0xcd+41&&after[at]==0xb9){require(after[at++]==0xb9&&after[at++]==5);std::string key;if(after[at]==0xa1){++at;at=(at+7)&~size_t(7);uintptr_t pointer=0;memcpy(&pointer,after.data()+at,8);at+=8;key=reinterpret_cast<const char*>(pointer);}else{require(after[at++]==0xa2&&after[at++]==60);key="BlockSize";}require(after[at++]==0xb5);const int value=after[at++];require(after[at++]==0x4f);fields.emplace_back(key,value);}
        while(at<0xcd+41){require(after[at++]==0x76&&after[at++]==0x17);}
        require(fields==std::vector<std::pair<std::string,int>>{{"FillDirection",2},{"ExpandDirection",8},{"BlockSize",80}});
    }
    {
        using J=nlohmann::json;
        std::vector<J> rows={J{{"id","CM_ACTIONHOME"},{"linkage",social::embedded::linkage},{"priority",0}},J{{"id","cm_team"},{"priority",4},{"isVisible",false}},J{{"id","CM_LEAGUE"},{"priority",5}},J{{"id","DynastyCentral"},{"priority",6}}};
        auto plan=social::embedded::plan(rows);require(plan&&plan->donor==0&&plan->position==2&&plan->priority==4.5);
        rows.erase(rows.begin()+1);plan=social::embedded::plan(rows);require(plan&&plan->position==1&&plan->priority==4.5);
        rows.push_back(J{{"id",social::embedded::panelId}});require(!social::embedded::plan(rows));rows.pop_back();
        rows[0]["linkage"]="foreign";require(!social::embedded::plan(rows));
        const auto scroll=social::embeddedNewsScroll();auto target=[&](size_t at){int32_t n=0;std::memcpy(&n,scroll.data()+at,4);return int64_t(at+4)+n;};require(target(0xc8)==0x3ec&&target(0xd8)==0x3ec&&target(0x100)==0x2f4);require(std::string(social::embeddedTypeKey)=="CODE_R3");require(scroll[0x141]==social::newsScrollSmooth[0x141]&&scroll[0x199]==social::newsScrollSmooth[0x199]);
        require(std::string(social::embedded::screenKey)=="screen_news");
    }
    std::cout<<"Passed: 17-byte native insertion/existing-key writes fit a 24-byte result; adjacent stack canaries preserved.\n";
    std::cout<<"Passed: year-round placement without Team, duplicate/foreign donor rejection, registered News screen key and bumper-bubbling scroll.\n";
    std::cout<<"Passed: descriptor traversal preserves native arrays/objects by reference and rejects cycles, duplicate keys and foreign values.\n";
    std::cout<<"Passed: owned script definitions preserve relocated headers and reject foreign owners/metadata.\n";
}
