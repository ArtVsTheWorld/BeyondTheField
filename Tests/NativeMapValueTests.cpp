#include "../Source/NativeMapValue.h"
#include "../Source/HubTab.h"
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
    std::cout<<"Passed: 17-byte native insertion/existing-key writes fit a 24-byte result; adjacent stack canaries preserved.\n";
    std::cout<<"Passed: descriptor traversal preserves native arrays/objects by reference and rejects cycles, duplicate keys and foreign values.\n";
}
