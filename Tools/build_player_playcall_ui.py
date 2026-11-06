"""Presentation-only labels in explicitly identified playcall panel methods."""
from pathlib import Path
import json
import sys
from build_recruit_notes_ui import Assembler, fnv
from build_player_card_ui import path, numeric_grade, numeric_display_grade as display_grade


def native_label(a, target, label, done, prefix):
    # Keep native presentation/comparison foreground and all font/layout styles.
    a.missing(target, done)
    path(a, target, 'mData'); a.raw(0x76, 0x49); a.branch(prefix+'set')
    path(a, target, 'mData', 'display'); a.reg(label); a.raw(0x66); a.branch(done)
    a.label(prefix+'set'); a.reg(label); a.number(1); a.reg(target); a.call('SetLabel')


def individual_suffix(a):
    # Original method retains its resolved numeric panel mode in r7 and its
    # sorted/selected display entries in r3. Modes 0/1 are manual/statistics.
    a.reg(7); a.number(2); a.raw(0x66); a.branch('individualDone', 0xB8)
    for index in range(3):
        done='individualNext'+str(index)
        a.reg(3); a.number(index); a.raw(0x4E); a.store(0); a.missing(0,done)
        path(a,0,'value'); a.store(0)
        numeric_grade(a, 0, 4, done, 'individualGrade'+str(index))
        path(a, 1, 'mcStat'+str(index)); a.store(2)
        native_label(a, 2, 4, done, 'individualLabel'+str(index))
        a.label(done)
    a.label('individualDone'); a.ret()


def comparison_suffix(a):
    # Native comparisons and arrow visibility have already used the true
    # numeric leftNum/rightNum. Only final text widgets change, in rating mode.
    a.reg(14); a.number(2); a.raw(0x66); a.branch('comparisonDone', 0xB8)
    for index in range(3):
        for side,field in [('Left','leftNum'),('Right','rightNum')]:
            tag='comparison'+side+str(index); done=tag+'Done'
            a.reg(3); a.number(index); a.raw(0x4E); a.store(0); a.missing(0,done)
            path(a,0,field); a.store(0)
            numeric_grade(a, 0, 4, done, tag+'Grade')
            path(a, 1, 'mcNum'+side+str(index)); a.store(2)
            native_label(a, 2, 4, done, tag+'Label')
            a.label(done)
    a.label('comparisonDone'); a.ret()


def impact_suffix(a):
    # ImpactPlayerDepth is the explicit rating-only panel. The similarly named
    # ImpactPlayer panel displays generic statistics and is deliberately absent.
    for index in range(3):
        done='impactDone'+str(index)
        a.reg(4); a.number(index); a.raw(0x4E); a.store(0); a.missing(0,done)
        path(a,0,'value'); a.store(0)
        numeric_grade(a, 0, 3, done, 'impactGrade'+str(index))
        path(a, 1, 'mcValue'+str(index)); a.store(2)
        native_label(a, 2, 3, done, 'impactLabel'+str(index))
        a.label(done)
    a.ret()



def provider_labels(a, providers, field):
    # These providers contain freshly constructed presentation WidgetData, not
    # player database records. Every other cell and its native style stay intact.
    for index,name in enumerate(providers):
        tag='provider'+str(index); done=tag+'Done'
        path(a, 1, name); a.store(0); a.missing(0, done)
        a.number(0); a.reg(0); a.string('GetNumItems'); a.raw(0x52); a.store(3)
        a.reg(3); a.raw(0x44); a.string('number'); a.raw(0x66); a.branch(done,0xB8)
        a.reg(3); a.number(0); a.raw(0x48); a.branch(done)
        a.reg(3); a.number(64); a.raw(0x67); a.branch(done)
        a.number(0); a.store(2); a.label(tag+'Loop')
        a.reg(2); a.reg(3); a.raw(0x48); a.branch(done,0xB8)
        a.reg(2); a.number(1); a.reg(0); a.string('GetItemData'); a.raw(0x52); a.store(4)
        a.missing(4,tag+'Next');path(a,4,'ExtraInfo');a.store(5);a.missing(5,tag+'Next')
        path(a,5,field); a.store(5)
        display_grade(a,5,5,tag+'Next',tag+'Grade')
        # SetDataProvider has already bound the native rows. Direct dictionary
        # mutation skips list notification. A field-specific UpdateProperty
        # updates only this presentation cell; its VirtualItemAdapter copies
        # the renderer's ExtraInfo and calls SetExtraInfo to invalidate it.
        # Formal parameters: index(r2), propertyName(r4), value(r3).
        a.reg(5);a.string(field);a.reg(2);a.number(3);a.reg(0);a.call('UpdateProperty')
        a.label(tag+'Next'); a.reg(2); a.number(1); a.raw(0x47); a.store(2); a.branch(tag+'Loop',0x99)
        a.label(done)
    a.ret()


def lineup_suffix(a): provider_labels(a, ['mDataProvider'], 'OverallText')
def lineup_stat_suffix(a): provider_labels(a, ['mDataProvider'], 'ConferenceText')
def trench_suffix(a): provider_labels(a, ['mLeftDataProvider','mRightDataProvider'], 'OverallText')


ASSETS=[
    ('individualPrograms','individualpositionstats.ast',[(0xF00,1,8,41,568,0xAAFCF14B1496DDDD,individual_suffix)]),
    ('comparisonPrograms','playervsplayer.ast',[(0x1048,1,15,41,820,0x567EA0C435169D4E,comparison_suffix)]),
    ('impactPrograms','impactplayerdepth.ast',[(0xBF0,1,11,41,601,0x259CAE7688E485F8,impact_suffix)]),
    ('lineupPrograms','teampositiongroups.ast',[(0x10E0,1,34,41,612,0x0CEFFD054D66A3FC,lineup_suffix),
                                             (0x1380,1,10,41,668,0x458D0B14010C332D,lineup_stat_suffix)]),
    ('trenchPrograms','trench.ast',[(0x14F0,1,28,41,1368,0x28CE9EBE211C65E5,trench_suffix)])]


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Custom presentation suffixes only; native bodies verified/copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::playerplaycallui {']
    for name,asset,specs in ASSETS:
        apt=load(Path('Evidence/PlayerFog/PlaycallPanels')/asset)
        lines.append(f'inline std::vector<notesui::Program> {name}(){{std::vector<notesui::Program> result;')
        for offset,argc,regs,flags,size,expected,suffix in specs:
            if fnv(apt.data[offset+48:offset+48+size])!=expected:
                raise ValueError(f'Unsupported playcall panel {asset}/{offset:x}')
            a=Assembler();a.code.extend(bytes(size));suffix(a);p=a.finish()
            code='{'+','.join(hex(b) for b in p.code)+'}'
            lines.append(f'result.push_back({{{offset},{argc},{regs},{flags},{size},{expected}ull,{regs},0,{size},{code}}});')
            for at in p.color_offsets:lines.append(f"result.back().colorOffsets.push_back({at});")
            for at in p.scale_offsets:lines.append(f"result.back().scaleOffsets.push_back({at});")
            for at in p.team_scale_offsets:lines.append(f"result.back().teamScaleOffsets.push_back({at});")
            for at in p.fog_offsets:lines.append(f"result.back().fogOffsets.push_back({at});")
            for at in p.team_offsets:lines.append(f"result.back().teamOffsets.push_back({at});")
            for at in p.dollar_offsets:lines.append(f"result.back().dollarOffsets.push_back({at});")
            for at,text in p.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}');destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'playcallPanelAssets':len(ASSETS),'methods':sum(len(s) for _,_,s in ASSETS),'nativeModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerPlaycallUiPrograms.h'))
