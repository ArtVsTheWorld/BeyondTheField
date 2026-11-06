"""Grade roster-only Program Overview badges; leave budget/recruit data native."""
from pathlib import Path
import hashlib
import json
import struct
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade,palette,text_label


def blueprint_suffix(a):
    done='blueprintDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','LayoutStyle');a.number(1);a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mData','ExtraInfo','OVRValue');a.store(0)
    numeric_grade(a,0,2,done,'blueprintGrade')
    path(a,1,'mcRatingValueItem');a.store(4);a.missing(4,done)
    path(a,4,'_visible');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,4,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,4,'mData','value');a.reg(0);a.raw(0x66);a.branch(done,0xB8)
    path(a,4,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('blueprintExtra',0xB8)
    path(a,4,'mData');a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
    a.label('blueprintExtra')
    path(a,4,'mData','ExtraInfo');a.string('DEPlayerRating');a.raw(0x73,0x4F)
    palette(a,2,3,done,'blueprintPalette')
    path(a,4,'mcValue');a.store(4)
    text_label(a,4,2,3,0,done,'blueprintText')
    a.label(done);a.ret()


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    source=Path('Evidence/PlayerFog/program-points-core.ast')
    if hashlib.sha256(source.read_bytes()).hexdigest()!='ec6978cac9f5a8bf0c51ad4f3509d00c30e1167c248a80d8aa7b936aa2f472ae':
        raise ValueError('Unsupported Program Overview asset')
    apt=load(source);off,size,expected=0x7340,1258,0xA2B7CD2AD4D8862E
    h=apt.data[off:off+48]
    if (struct.unpack_from('<I',h,8)[0],struct.unpack_from('<H',h,12)[0],struct.unpack_from('<H',h,14)[0])!=(0,5,25):
        raise ValueError('Unsupported Program Overview frame')
    if fnv(apt.data[off+48:off+48+size])!=expected:raise ValueError('Unsupported Program Overview Draw')
    a=Assembler();a.code.extend(bytes(size));blueprint_suffix(a);p=a.finish()
    lines=['// Custom roster badge presentation. Native source bodies are copied only after attachment gates.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::playerblueprintui {',
           'inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;']
    code='{'+','.join(hex(b) for b in p.code)+'}'
    lines.append(f'result.push_back({{{off},0,5,25,{size},{expected}ull,5,0,{size},{code}}});')
    for at in p.color_offsets:lines.append(f"result.back().colorOffsets.push_back({at});")
    for at in p.scale_offsets:lines.append(f"result.back().scaleOffsets.push_back({at});")
    for at in p.team_scale_offsets:lines.append(f"result.back().teamScaleOffsets.push_back({at});")
    for at in p.fog_offsets:lines.append(f"result.back().fogOffsets.push_back({at});")
    for at in p.team_offsets:lines.append(f"result.back().teamOffsets.push_back({at});")
    for at in p.dollar_offsets:lines.append(f"result.back().dollarOffsets.push_back({at});")
    for at,value in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(value)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}'];destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'blueprintPlayerMethods':1,'budgetModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerBlueprintUiPrograms.h'))
