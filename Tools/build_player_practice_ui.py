"""Weekly Practice Plans/Wear & Tear player labels, without plan/model edits."""
from pathlib import Path
import hashlib
import json
import struct
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade,palette,text_label


def practice_guards(a,done):
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','IsGroupPlan');a.raw(0x73,0x66);a.branch(done)
    path(a,1,'mcOvr');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcOvr','_visible');a.raw(0x73,0x66);a.branch(done,0xB8)


def practice_draw_suffix(a):
    done='practiceDone';practice_guards(a,done)
    path(a,1,'mData','ExtraInfo','Ovr');a.store(0)
    numeric_grade(a,0,2,done,'practiceGrade')
    path(a,1,'mcOvr');a.store(4)
    path(a,4,'mData');a.raw(0x76,0x49);a.branch('practiceSetLabel')
    path(a,4,'mData','display');a.reg(2);a.raw(0x66);a.branch('practiceLabelReady')
    a.label('practiceSetLabel');a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    a.label('practiceLabelReady')
    # Keep injured rows' native disabled style and selected rows' black text.
    path(a,1,'mData','ExtraInfo','IsInjured');a.raw(0x73,0x66);a.branch(done)
    path(a,1,'mcHighlight','_visible');a.raw(0x73,0x66);a.branch(done)
    palette(a,2,3,done,'practicePalette')
    text_label(a,4,2,3,5,done,'practiceText')
    a.label(done);a.ret()


def practice_unfocus_suffix(a):
    done='practiceUnfocusDone';practice_guards(a,done)
    path(a,1,'mData','ExtraInfo','IsInjured');a.raw(0x73,0x66);a.branch(done)
    path(a,1,'mcHighlight','_visible');a.raw(0x73,0x66);a.branch(done)
    path(a,1,'mData','ExtraInfo','Ovr');a.store(0)
    numeric_grade(a,0,0,done,'practiceUnfocusGrade')
    palette(a,0,0,done,'practiceUnfocusPalette')
    a.string('fontColor');a.reg(0);a.number(1);a.raw(0x43)
    a.number(1);path(a,1,'mcOvr');a.call('SetExtraInfo')
    a.label(done);a.ret()


SPECS=[(0x7B7C0,0,6,25,1856,0xA9F158B809556E8E,practice_draw_suffix),
       (0x7C0A0,1,2,41,208,0xB782BAE79E0A136E,practice_unfocus_suffix)]


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    source=Path('Evidence/PlayerFog/wear-tear-core.ast')
    if hashlib.sha256(source.read_bytes()).hexdigest()!='6e1d534eeefbbc0f810b7b5e983e6f7bcec73aff3140760e217f65da13996716':
        raise ValueError('Unsupported Practice Plans asset')
    apt=load(source)
    lines=['// Custom player text only; verified native definitions are copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::playerpracticeui {',
           'inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;']
    for off,argc,regs,flags,size,expected,suffix in SPECS:
        h=apt.data[off:off+48]
        if (struct.unpack_from('<I',h,8)[0],struct.unpack_from('<H',h,12)[0],struct.unpack_from('<H',h,14)[0])!=(argc,regs,flags):
            raise ValueError('Unsupported Practice Plans frame')
        if fnv(apt.data[off+48:off+48+size])!=expected:raise ValueError('Unsupported Practice Plans method')
        a=Assembler();a.code.extend(bytes(size));suffix(a);p=a.finish()
        code='{'+','.join(hex(b) for b in p.code)+'}'
        lines.append(f'result.push_back({{{off},{argc},{regs},{flags},{size},{expected}ull,{regs},0,{size},{code}}});')
        for at,value in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(value)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}'];destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'practicePlayerMethods':len(SPECS),'planModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerPracticeUiPrograms.h'))
