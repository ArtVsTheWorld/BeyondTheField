#pragma once
#include <cstddef>
#include <cstdint>
#include <type_traits>
namespace social::native {
// Map insertion returns a two-word iterator AND an insertion flag. Native
// 0x8aeba90 writes the flag at output+0x10; two pointers alone underallocate it.
// This contract is shared by the existing-key and inserted-key paths.
struct InsertResult {
    void* node=nullptr;
    void* bucket=nullptr;
    bool inserted=false;
    unsigned char padding[7]{};
};
static_assert(std::is_standard_layout_v<InsertResult>);
static_assert(offsetof(InsertResult,inserted)==0x10);
static_assert(sizeof(InsertResult)==0x18);
using Lookup=void*(__fastcall*)(void*,InsertResult*,const char*);
inline InsertResult findOrInsert(Lookup fn,void* target,const char* key){
    InsertResult result{};fn(target,&result,key);return result;
}
}
