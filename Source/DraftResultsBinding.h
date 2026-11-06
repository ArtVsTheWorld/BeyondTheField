#pragma once
#include <cstdint>
namespace recruitingfog::draftresults {
// Name-verified from the PlayersLeavingFlowAdapterClass registration and its
// GetTeamInfo script thunk. The loader must additionally verify live ownership
// and all32 prefix bytes before replacing this single native vtable slot.
inline constexpr uintptr_t teamInfoTable=0xc751ea0;
inline constexpr uintptr_t teamInfoSlot=0x60;
inline constexpr uintptr_t teamInfoRva=0xa0db8e0;
inline constexpr char teamInfoPrefix[]="48895c2410574883ec60488bfa488bd9e8dbe8e2f9488bd7488bc8e88010a1fe";
// Exactly two native arguments. Do not reuse a four-argument player-detail ABI.
using TeamInfoGetter=void*(__fastcall*)(void*,void**);
}
