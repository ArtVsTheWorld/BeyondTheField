"""Minimal Draft Results OVR display adapter; all stock UI behavior is retained.

Exactly two fingerprinted methods are copied unchanged: a Draft strategy marks
its own provider, then shared native row data receives a display-only suffix.
No custom table, data capture, filter, row key, sidebar or navigation code.
"""
from pathlib import Path
import argparse
import json
import struct
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade

ASSETS={'strategy':'common/ui/node_cfm/hub/corenode.ast','rows':'common/ui/node_com/scriptpod.ast'}
SPECS=[('strategy','_GetTeamModule',0x49ac8,0,3,41,207,0x9489B6FCC2AB8C9C),
       ('rows','GetRowData',0x108a40,2,6,41,72,0x692F2D8E6C46500D)]

class FixedFrameAssembler(Assembler):
    def __init__(self,registers):super().__init__();self.native_registers=registers
    def reg(self,n):
        if n<self.native_registers:super().reg(n)
        else:self.string('_DEDraftOvrLocal'+str(n));self.raw(0x1C)
    def store(self,n):
        if n<self.native_registers:super().store(n)
        else:self.string('_DEDraftOvrLocal'+str(n));self.raw(0x4D,0x3C)

def strategy_prefix(a):
    # This definition belongs to PlayersLeavingStrategy. The CFM base
    # _GetColumnData callback is shared and MUST NOT mark all Ucm providers.
    path(a,1,'mSpreadsheetDataProvider');a.store(2);a.missing(2,'stock')
    a.reg(2);a.string('mDEDraftOvr');path(a,1,'mIsDraftClass');a.raw(0x73,0x66,0x4F)
    a.label('stock');a.pad_code()

def rows_suffix(a):
    # Native r2 is the returned cell array; native r4 is the requested column
    # key array. Only column4 (Draft Results OVR) display text can be changed.
    path(a,1,'mDEDraftOvr');a.raw(0x73,0x66);a.branch('return',0xB8)
    a.missing(2,'return');a.missing(4,'return');a.number(0);a.store(8)
    a.label('loop');a.reg(8);path(a,4,'length');a.raw(0x48);a.branch('return',0xB8)
    a.reg(4);a.reg(8);a.raw(0x4E);a.number(4);a.raw(0x66);a.branch('next',0xB8)
    a.reg(2);a.reg(8);a.raw(0x4E);a.store(10);a.missing(10,'next')
    path(a,10,'display');a.store(11)
    a.reg(11);a.raw(0x44);a.string('number');a.raw(0x66);a.branch('number')
    a.reg(11);a.raw(0x44);a.string('string');a.raw(0x66);a.branch('next',0xB8)
    a.reg(11);a.raw(0x4A);a.store(12)
    # Only canonical numeric strings qualify; unknown/sentinel/trend strings
    # keep their exact stock text. The grade helper bounds numbers0..100.
    a.reg(12);a.raw(0x4B);a.reg(11);a.raw(0x66);a.branch('next',0xB8);a.branch('grade',0x99)
    a.label('number');a.reg(11);a.store(12)
    a.label('grade');numeric_grade(a,12,11,'next','draft_ovr_grade')
    a.reg(10);a.string('display');a.reg(11);a.raw(0x4F)
    a.label('next');a.reg(8);a.raw(0x50);a.store(8);a.branch('loop',0x99)
    a.label('return');a.reg(2);a.raw(0x3E)

def emit(mode):
    a=FixedFrameAssembler(3 if mode=='strategy' else 6)
    if mode=='strategy':strategy_prefix(a)
    elif mode=='rows':rows_suffix(a)
    else:raise ValueError(mode)
    return a

def generate(root,header,evidence):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Generated minimal Draft OVR adapter; stock UI bodies remain intact.','#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::draftovrui {']
    report=[]
    for mode,name,body,argc,regs,flags,size,expected in SPECS:
        asset=load(root/ASSETS[mode]);original=asset.data[body:body+size];descriptor=asset.data[body-48:body]
        assert struct.unpack_from('<IHH',descriptor,8)==(argc,regs,flags)
        assert struct.unpack_from('<I',descriptor,24)[0]==size
        assert fnv(original)==expected,(mode,hex(fnv(original)),hex(expected))
        if mode=='strategy':
            # Exact source class proof, rather than relying on a shared method
            # name: the definition is in PlayersLeavingStrategy's class pool.
            class_items=asset.decode(298176)
            assert class_items[0][2][6]=='PlayersLeavingStrategy'
            definitions=[i for i,item in enumerate(class_items) if len(item)>3 and item[2][3]==hex(body)]
            assert len(definitions)==1
            assert class_items[definitions[0]-1][2][1]=='_GetTeamModule'
            a=emit(mode);copy_at=len(a.code);copy_bytes=size;a.code.extend(bytes(size))
        else:
            assert original[-3:]==bytes.fromhex('b9023e')
            a=FixedFrameAssembler(regs);copy_at=0;copy_bytes=size-3;a.code.extend(bytes(copy_bytes));rows_suffix(a)
        p=a.finish();code='{'+','.join(hex(b) for b in p.code)+'}'
        method='strategyPrograms' if mode=='strategy' else 'rowPrograms'
        lines.append(f'inline std::vector<notesui::Program> {method}(){{std::vector<notesui::Program> result;')
        lines.append(f'result.push_back({{{body-48},{argc},{regs},{flags},{size},{expected}ull,{regs},{copy_at},{copy_bytes},{code}}});')
        for field,offsets in [('scaleOffsets',p.scale_offsets),('teamScaleOffsets',p.team_scale_offsets),('fogOffsets',p.fog_offsets),('colorOffsets',p.color_offsets)]:
            for at in offsets:lines.append(f'result.back().{field}.push_back({at});')
        for at,value in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(value)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
        report.append(dict(mode=mode,asset=ASSETS[mode],method=name,definition=body-48,argc=argc,registers=regs,flags=flags,size=size,hash=expected,copyAt=copy_at,copyBytes=copy_bytes,customBytes=len(p.code)-copy_bytes))
    lines.append('}');header.write_text('\n'.join(lines)+'\n',encoding='utf8')
    evidence.parent.mkdir(parents=True,exist_ok=True);evidence.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'callbacks':2,'customBytes':sum(r['customBytes'] for r in report),'header':str(header)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assets',type=Path,default=Path('../PlayerAnalytics/Research/assets'));parser.add_argument('--header',type=Path,default=Path('Source/DraftOvrUiPrograms.h'));parser.add_argument('--evidence',type=Path,default=Path('Evidence/PlayerFog/Draft/minimal-ovr-programs.json'));args=parser.parse_args();generate(args.assets,args.header,args.evidence)
