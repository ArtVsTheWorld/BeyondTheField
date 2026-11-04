"""Native player-only Dynasty hub previews. Team ratings/statistics untouched."""
from pathlib import Path
import json
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade,palette,text_label


def formation_suffix(a):
    a.missing(3,'formationDone');path(a,1,'FIELDED_PLAYERS');a.raw(0x44);a.string('number');a.raw(0x66);a.branch('formationDone',0xB8)
    a.number(0);a.store(4)
    a.label('formationLoop')
    a.reg(4);a.reg(1);a.member('FIELDED_PLAYERS');a.raw(0x48);a.branch('formationDone',0xB8)
    a.reg(4);a.reg(3);a.member('length');a.raw(0x48);a.branch('formationDone',0xB8)
    a.reg(3);a.reg(4);a.raw(0x4E);a.store(5);a.missing(5,'formationNext')
    path(a,5,'Ovr');a.store(5);numeric_grade(a,5,6,'formationNext','formationGrade')
    palette(a,6,7,'formationNext','formationPalette')
    a.reg(1);a.string('mcPlayerOVRValue');a.reg(4);a.raw(0x47,0x4E);a.store(8)
    text_label(a,8,6,7,9,'formationNext','formationText')
    a.label('formationNext');a.reg(4);a.raw(0x50);a.store(4);a.branch('formationLoop',0x99)
    a.label('formationDone');a.ret()


def ovr_template_suffix(a):
    a.missing(2,'templateReturn');path(a,2,'value');a.store(4)
    numeric_grade(a,4,5,'templateReturn','previewGrade');palette(a,5,6,'templateReturn','previewPalette')
    a.reg(2);a.string('value');a.reg(5);a.raw(0x4F)
    path(a,2,'ExtraInfo');a.raw(0x76,0x49);a.branch('previewExtra',0xB8)
    a.reg(2);a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
    a.label('previewExtra')
    path(a,2,'ExtraInfo');a.string('DEPlayerRating');a.raw(0x73,0x4F)
    # Clone an existing ValueTextStyle; absence leaves the native default style
    # intact rather than inventing an unverified default font or widget type.
    path(a,2,'ExtraInfo','ValueTextStyle');a.store(7);a.missing(7,'templateReturn')
    a.empty_object(8);a.reg(8);a.string('fontColor');a.reg(6);a.raw(0x4F)
    path(a,2,'ExtraInfo');a.string('ValueTextStyle');a.reg(8);a.number(1);a.reg(7);a.string('CloneAndModify');a.raw(0x52,0x4F)
    a.label('templateReturn');a.reg(2);a.raw(0x3E)


SPECS=[(0x1FF18,156,0xCE87BAC7B2804856,10,formation_suffix,156),
       (0x33368,102,0xE30E56A3B41D133E,9,ovr_template_suffix,99),
       (0x33EA0,38,0x7AB09F632B3E07B6,9,ovr_template_suffix,35)]


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    apt=load(Path('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_cfm/hub/corenode.ast'))
    lines=['// Generated custom player preview labels; original game bodies are verified and copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::playerhubui {',
           'inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;']
    for off,size,expected,regs,suffix,count in SPECS:
        original=apt.data[off+48:off+48+size]
        if fnv(original)!=expected:raise ValueError(f'Unsupported native hub method {off:x}')
        if count<size and original[count:]!=bytes([0xB9,2,0x3E]):raise ValueError('Unsupported native hub return')
        a=Assembler();a.code.extend(bytes(count));suffix(a);p=a.finish()
        code='{'+','.join(hex(b) for b in p.code)+'}'
        lines.append(f'result.push_back({{{off},1,4,41,{size},{expected}ull,{regs},0,{count},{code}}});')
        for at,text in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}'];destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'playerHubMethods':len(SPECS),'teamRatingFieldsChanged':False}))


if __name__=='__main__':generate(Path('Source/PlayerHubUiPrograms.h'))
