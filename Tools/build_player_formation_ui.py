"""Formation Subs labels only; never alter substitution data or commands."""
from pathlib import Path
import json
import sys
from build_recruit_notes_ui import Assembler, fnv
from build_player_card_ui import path, numeric_grade, palette, text_label


def mark_item(a, register, prefix):
    path(a, register, 'mData', 'ExtraInfo');a.raw(0x76,0x49);a.branch(prefix+'extra',0xB8)
    path(a, register, 'mData');a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
    a.label(prefix+'extra')
    path(a, register, 'mData', 'ExtraInfo');a.string('DEPlayerRating');a.raw(0x73,0x4F)


def module_suffix(a):
    # The native _UpdatePlayer leaves its selected WidgetData in r2.
    done='moduleDone'
    a.missing(2,done);path(a,2,'key');a.raw(0x76,0x49);a.branch(done)
    path(a,2,'ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,2,'ExtraInfo','Ovr');a.store(0)
    numeric_grade(a,0,0,done,'moduleGrade');palette(a,0,3,done,'modulePalette')
    path(a,1,'mcOvrData');a.store(6);a.missing(6,done)
    path(a,6,'mData');a.raw(0x76,0x49);a.branch(done)
    mark_item(a,6,'moduleMark')
    path(a,6,'mcValue');a.store(4)
    text_label(a,4,0,3,5,done,'moduleText')
    a.label(done);a.ret()


def list_suffix(a):
    # Retain the native black selected foreground; only unfocused grades get
    # the palette. A separate unfocus suffix restores it after native resets.
    done='listDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','Ovr');a.store(0)
    numeric_grade(a,0,0,done,'listGrade')
    path(a,1,'mcTxt2');a.store(3);a.missing(3,done)
    path(a,3,'mData');a.raw(0x76,0x49);a.branch('listSetLabel')
    path(a,3,'mData','display');a.reg(0);a.raw(0x66);a.branch('listLabelReady')
    a.label('listSetLabel')
    a.reg(0);a.number(1);a.reg(3);a.call('SetLabel')
    a.label('listLabelReady')
    path(a,1,'mcHighlight','_visible');a.raw(0x73,0x66);a.branch(done)
    palette(a,0,2,done,'listPalette')
    text_label(a,3,0,2,0,done,'listText')
    a.label(done);a.ret()


def detail_suffix(a):
    done='detailDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','Ovr');a.store(0)
    numeric_grade(a,0,3,done,'detailGrade');palette(a,3,4,done,'detailPalette')
    # Legacy player-info and modern PlayerModule are distinct native branches.
    path(a,1,'mcPlayerInfo');a.store(5);a.missing(5,'detailModern')
    path(a,5,'_visible');a.raw(0x73,0x66);a.branch('detailModern',0xB8)
    path(a,5,'mcOvr');a.store(5);a.missing(5,done)
    path(a,5,'mData');a.raw(0x76,0x49);a.branch(done)
    mark_item(a,5,'detailLegacyMark')
    path(a,5,'mcValue');a.store(6)
    text_label(a,6,3,4,7,done,'detailLegacyText')
    a.branch(done,0x99)
    a.label('detailModern')
    path(a,1,'mcPlayerModule');a.store(5);a.missing(5,done)
    path(a,5,'_visible');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,5,'mcStat');a.store(5);a.missing(5,done)
    path(a,5,'mData');a.raw(0x76,0x49);a.branch(done)
    mark_item(a,5,'detailModernMark')
    path(a,5,'mcValue');a.store(6)
    text_label(a,6,3,4,7,done,'detailModernText')
    a.label(done);a.ret()


def legacy_ovr_suffix(a):
    # OVRItem also renders team OVR/OFF/DEF: opt in only the private marker
    # placed on the legacy Formation Subs player child above.
    done='legacyOvrDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DEPlayerRating');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mData','value');a.store(0)
    numeric_grade(a,0,2,done,'legacyOvrGrade');palette(a,2,3,done,'legacyOvrPalette')
    path(a,1,'mcValue');a.store(4)
    text_label(a,4,2,3,5,done,'legacyOvrText')
    a.label(done);a.ret()


SPECS=[(0x3E70,1,7,41,348,0x18D00AA7087BBB23,module_suffix),
       (0x8AF0,0,4,25,120,0x36C9D322B6943FAF,list_suffix),
       (0x8E60,1,5,25,97,0x7B062866513012A9,list_suffix),
       (0x5740,0,21,25,1126,0xD9C74E57CF9721C9,detail_suffix)]


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Custom presentation suffixes; verified native bodies copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::playerformationui {']
    for name,asset,specs in [('programs','formationsubs.ast',SPECS),
                             ('legacyPrograms','art-control-scriptpod.ast',[(0x1CEC0,0,9,25,549,0x4D2C777B5AE1ECA7,legacy_ovr_suffix)])]:
        apt=load(Path('Evidence/PlayerFog')/asset)
        lines.append(f'inline std::vector<notesui::Program> {name}(){{std::vector<notesui::Program> result;')
        for offset,argc,regs,flags,size,expected,suffix in specs:
            if fnv(apt.data[offset+48:offset+48+size])!=expected:
                raise ValueError(f'Unsupported native Formation Subs method {offset:x}')
            a=Assembler();a.code.extend(bytes(size));suffix(a);p=a.finish()
            code='{'+','.join(hex(b) for b in p.code)+'}'
            lines.append(f'result.push_back({{{offset},{argc},{regs},{flags},{size},{expected}ull,{regs},0,{size},{code}}});')
            for at,text in p.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}')
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'formationRatingMethods':len(SPECS),'substitutionModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerFormationUiPrograms.h'))
