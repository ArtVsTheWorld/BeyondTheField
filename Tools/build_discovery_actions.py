"""Native News-only jersey compositor and bottom-right engagement; exact gates."""
from pathlib import Path
import sys,struct,json
sys.path.insert(0,r'C:/Apps/CFB 27/MMC/SocialMedia/Research')
from build_dropdown_actions import load,Asm,arr
src=load(Path(r'C:/Apps/CFB 27/MMC/SocialMedia/Research/assets/common/ui/node_fe/scriptpodart.ast'))
a=Asm(0x2ce74)
def member(name):a.string(name);a.op(0x4e)
def prop(name):a.string(name)
def extra(name):a.reg(1);a.raw(bytes([0xac,2,90,30]));member(name)
def setprop(child,propidx,value):a.child(child);a.idx(propidx);a.num(value);a.op(0x4f)
# DateText keeps category/index. Reuse the native tertiary text for likes.
a.child(60);a.idx(164);a.reg(1);a.raw(bytes([0xac,2,90,160]));a.num(14);a.op(0x0b);a.op(0x4f)
a.child(60);a.idx(165);a.reg(1);a.raw(bytes([0xac,2,90,159]));a.num(32);a.op(0x0b);a.op(0x4f)
a.idx(55);a.glob(43,44,56);a.idx(54);a.num(22);a.num(2);a.op(0x43);a.num(1);a.child(60);a.call(92)
# Reuse the two native CustomSingleGeneric layers already owned by the tile.
# This is the same head + TeamJerseys image pairing used by PortraitWithJersey.
a.reg(1);a.raw(bytes([0xac,3,90,30,140]));a.jump('done',0xb8)
# Explicit native image update; use the same AssetLibrary/SetValue contract as the roster.
a.idx(134);a.num(92);a.num(1);a.op(0x43);a.num(1);a.child(64);a.call(92)
a.reg(1);a.raw(bytes([0xac,3,90,30,140]));a.num(1);a.child(64);a.call(111)
# News' alternate image can sit behind the opaque torso; ensure the jersey is in front.
a.num(0);a.child(64);a.string('getDepth');a.op(0x52)
a.num(0);a.child(63);a.string('getDepth');a.op(0x52);a.op(0x48);a.jump('front',0xb8)
a.child(63);a.num(1);a.child(64);a.string('swapDepths');a.op(0x52);a.op(0x17);a.label('front')
for propidx,v in [(164,13),(165,13),(184,100)]:setprop(64,propidx,v)
for method in [118,121]:a.num(95);a.num(1);a.child(64);a.call(method)
a.child(64);a.idx(38);a.op(0x73);a.op(0x4f)
a.label('done');a.void()
body,used,fixups=a.finish(0x2d161-0x2ce74)
# Twitter style's terminal jump now runs the custom tail. Other style branches remain untouched.
branch=src.data[0x2ce69:0x2ce74];changed=bytearray(branch);struct.pack_into('<i',changed,7,0)
header=['#pragma once','#include <vector>','#include <cstdint>','#include <cstring>','namespace social::discoveryui {','struct Patch {uintptr_t offset;std::vector<unsigned char> original,changed;};','inline std::vector<Patch> patches(){std::vector<Patch> r;']
# Give account name + handle enough width without the old 350px compression.
headerStyle=bytearray(src.data[0x2cc94:0x2ccd2]);struct.pack_into('<H',headerStyle,0x2ccaf-0x2cc94,850);headerStyle[0x2ccb3-0x2cc94]=0x74 # Preserve natural handle casing.
for off,orig,new in [(0x2cc94,src.data[0x2cc94:0x2ccd2],headerStyle),(0x2ce69,branch,changed),(0x2ce74,src.data[0x2ce74:0x2d161],body)]:header.append(f'r.push_back({{0x{off:x},{arr(orig)},{arr(new)}}});')
for off,s in fixups:header.append(f'{{const auto p=reinterpret_cast<uintptr_t>({json.dumps(s)});memcpy(r.back().changed.data()+{off},&p,8);}}')
header+=['return r;}','}']
Path('Source/NewsDiscovery.h').write_text('\n'.join(header)+'\n')
print({'tailUsed':used,'tailAvailable':len(body)})
