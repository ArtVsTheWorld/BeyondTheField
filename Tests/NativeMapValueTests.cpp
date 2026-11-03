#include "../Source/NativeMapValue.h"
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
    std::cout<<"Passed: 17-byte native insertion/existing-key writes fit a 24-byte result; adjacent stack canaries preserved.\n";
}
