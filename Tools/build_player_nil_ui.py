"""Display-only NIL roster grades. Compensation and roster model stay numeric."""
from pathlib import Path
import json
import hashlib
import struct
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade,palette,text_label


def nil_draw_suffix(a):
    done='nilDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','Ovr');a.store(0)
    numeric_grade(a,0,2,done,'nilGrade')
    path(a,1,'mcOvr');a.store(4);a.missing(4,done)
    path(a,4,'mData');a.raw(0x76,0x49);a.branch('nilSetLabel')
    path(a,4,'mData','display');a.reg(2);a.raw(0x66);a.branch('nilLabelReady')
    a.label('nilSetLabel');a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    a.label('nilLabelReady')
    path(a,1,'mcHighlight','_visible');a.raw(0x73,0x66);a.branch(done)
    palette(a,2,3,done,'nilPalette');text_label(a,4,2,3,5,done,'nilText')
    a.label(done);a.ret()


def nil_unfocus_suffix(a):
    # Native focus callbacks have two registers and can bypass setup. Keep that
    # frame unchanged; construct the tiny color patch directly on the stack.
    done='nilUnfocusDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcOvr');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','Ovr');a.store(0)
    numeric_grade(a,0,0,done,'nilUnfocusGrade');palette(a,0,0,done,'nilUnfocusPalette')
    a.reg(0);a.number(0);a.raw(0x48);a.branch(done)
    a.string('fontColor');a.reg(0);a.number(1);a.raw(0x43)
    a.number(1);path(a,1,'mcOvr');a.call('SetExtraInfo')
    a.label(done);a.ret()


SPECS=[(0x1A90,0,6,25,665,0x14CEAC0385098E7D,nil_draw_suffix),
       (0x1FC0,1,2,41,104,0xD0ACDF397686B473,nil_unfocus_suffix)]
EMBEDDED_SPECS=[(0x2610,0,6,25,665,0x14CEAC0385098E7D,nil_draw_suffix),
                (0x2B40,1,2,41,104,0xD0ACDF397686B473,nil_unfocus_suffix)]


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Custom player-label suffixes; native NIL model/body is not redistributed.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::playernilui {']
    for name,filename,sha,specs in [
        ('programs','rosternilrowitem.ast','5605ede3f7ed7d945dc574b56fbb17413f5c12ecd647ac126306de455798443f',SPECS),
        ('embeddedPrograms','rosternil-screen.ast','0851ae84bdb0e21bd0c264530aaa0731e10d37d95d09b7d9644e2b76489b5d54',EMBEDDED_SPECS)]:
        source=Path('Evidence/PlayerFog')/filename
        if hashlib.sha256(source.read_bytes()).hexdigest()!=sha:raise ValueError('Unsupported NIL player source asset')
        apt=load(source)
        lines.append(f'inline std::vector<notesui::Program> {name}(){{std::vector<notesui::Program> result;')
        for off,argc,regs,flags,size,expected,suffix in specs:
            h=apt.data[off:off+48]
            if (struct.unpack_from('<I',h,8)[0],struct.unpack_from('<H',h,12)[0],struct.unpack_from('<H',h,14)[0])!=(argc,regs,flags):raise ValueError('Unsupported NIL player frame')
            if fnv(apt.data[off+48:off+48+size])!=expected:raise ValueError('Unsupported native NIL player row')
            a=Assembler();a.code.extend(bytes(size));suffix(a);p=a.finish()
            code='{'+','.join(hex(b) for b in p.code)+'}'
            lines.append(f'result.push_back({{{off},{argc},{regs},{flags},{size},{expected}ull,{regs},0,{size},{code}}});')
            for at in p.color_offsets:lines.append(f"result.back().colorOffsets.push_back({at});")
            for at in p.scale_offsets:lines.append(f"result.back().scaleOffsets.push_back({at});")
            for at in p.team_scale_offsets:lines.append(f"result.back().teamScaleOffsets.push_back({at});")
            for at in p.fog_offsets:lines.append(f"result.back().fogOffsets.push_back({at});")
            for at in p.team_offsets:lines.append(f"result.back().teamOffsets.push_back({at});")
            for at in p.dollar_offsets:lines.append(f"result.back().dollarOffsets.push_back({at});")
            for at,text in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}');destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'nilPlayerRatingMethods':len(SPECS)+len(EMBEDDED_SPECS),'budgetModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerNilUiPrograms.h'))
