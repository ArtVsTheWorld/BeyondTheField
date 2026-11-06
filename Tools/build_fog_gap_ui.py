"""Scoped native adapters for the remaining team, award and weekly-summary gaps.

The emitted programs contain custom suffixes and zeroed native-copy regions.
Extracted game assets remain private evidence. No rating/model source is edited.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import struct
import sys

from build_recruit_notes_ui import Assembler, fnv
from build_player_card_ui import path, numeric_grade, palette, text_label
from build_player_hub_ui import ATTRIBUTE_NAMES


class FixedFrameAssembler(Assembler):
    """Store overflow scratch as AS2 locals, never enlarge a native frame."""
    def __init__(self, registers):
        super().__init__()
        self.native_registers = registers

    def reg(self, n):
        if n < self.native_registers:
            super().reg(n)
        else:
            self.string('_DEFogGapLocal' + str(n)); self.raw(0x1C)

    def store(self, n):
        if n < self.native_registers:
            super().store(n)
        else:
            self.string('_DEFogGapLocal' + str(n)); self.raw(0x4D, 0x3C)


def display_grade(a, value, label, done, prefix, team=False):
    """Admit numbers or canonical 0..100 integer text in a known rating slot."""
    a.reg(value); a.raw(0x44); a.string('string'); a.raw(0x66)
    a.branch(prefix+'strings')
    numeric_grade(a, value, label, done, prefix+'number', team=team)
    a.branch(prefix+'ready', 0x99)
    a.label(prefix+'strings')
    for number in range(101):
        a.reg(value); a.string(str(number)); a.raw(0x66); a.branch(prefix+'convert')
    a.branch(done, 0x99)
    a.label(prefix+'convert'); a.reg(value); a.raw(0x4A); a.store(label)
    numeric_grade(a, label, label, done, prefix+'text', team=team)
    a.label(prefix+'ready')


def named_rating(a, value_path, target_path, done, prefix, *, team=False,
                 value=0, label=0, color=2, target=3, style=0):
    """Read a scoped source and change only the widget's rendered text/style."""
    path(a, 1, *value_path); a.store(value)
    display_grade(a, value, label, done, prefix+'grade', team=team)
    palette(a, label, color, done, prefix+'palette',team=team)
    path(a, 1, *target_path); a.store(target)
    text_label(a, target, label, color, style, done, prefix+'text',team=team)


def mark_badge(a, widget, done, *, team=False):
    # RatingValueItem.Draw can run after its parent's draw/SetValue, so mark
    # its role as well as repainting its current text. The numeric value stays.
    path(a, 1, *widget); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, *widget, 'mData'); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, *widget, 'mData', 'ExtraInfo'); a.raw(0x76, 0x49)
    a.branch(done+'extra', 0xB8)
    path(a, 1, *widget, 'mData'); a.string('ExtraInfo'); a.number(0); a.raw(0x43, 0x4F)
    a.label(done+'extra')
    path(a, 1, *widget, 'mData', 'ExtraInfo')
    a.string('DETeamRating' if team else 'DEPlayerRating'); a.raw(0x73, 0x4F)


def team_badges(a, widgets, prefix):
    # Keep one conversion loop, rather than duplicating a full configurable
    # grade palette for every badge. r4/r5 retain only index/widget names.
    for widget in reversed(widgets):a.string(widget)
    a.number(len(widgets));a.raw(0x42);a.store(5)
    a.number(0);a.store(4)
    a.label(prefix+'loop')
    a.reg(4);a.number(len(widgets));a.raw(0x48);a.branch(prefix+'done',0xB8)
    a.reg(1);a.reg(5);a.reg(4);a.raw(0x4E,0x4E);a.store(0)
    a.missing(0,prefix+'next')
    path(a,0,'mData');a.raw(0x76,0x49);a.branch(prefix+'next')
    path(a,0,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(prefix+'extra',0xB8)
    path(a,0,'mData');a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
    a.label(prefix+'extra')
    path(a,0,'mData','ExtraInfo');a.string('DETeamRating');a.raw(0x73,0x4F)
    path(a,0,'mData','value');a.store(2)
    display_grade(a,2,2,prefix+'next',prefix+'grade',team=True)
    palette(a,2,3,prefix+'next',prefix+'palette',team=True)
    path(a,0,'mcValue');a.store(0)
    text_label(a,0,2,3,2,prefix+'next',prefix+'text',team=True)
    a.label(prefix+'next');a.reg(4);a.raw(0x50);a.store(4);a.branch(prefix+'loop',0x99)
    a.label(prefix+'done')


def vertical_team_suffix(a):
    team_badges(a,('mcStatOVR','mcStatOFF','mcStatDEF'),'verticalTeam')
    a.ret()


def select_team_suffix(a):
    # TeamSelect._UpdateStatBoxes owns these six badges, not player cards.
    team_badges(a,tuple('mc'+side+'Rating'+kind for side in ('Home','Away')
                       for kind in ('Ovr','Off','Def')),'selectTeam')
    a.ret()


def top_players_suffix(a):
    # The Choose Team and coach-carousel overview share the four exact player
    # badges. Native PlayersList/playerOVR and team ratings remain numeric.
    a.number(0);a.store(6)
    a.label('topPlayerLoop')
    a.reg(6);a.number(4);a.raw(0x48);a.branch('topPlayerDone',0xB8)
    path(a,1,'mPlayerOverallArray');a.store(0);a.missing(0,'topPlayerDone')
    a.reg(0);a.reg(6);a.raw(0x4E);a.store(0);a.missing(0,'topPlayerNext')
    path(a,0,'mData');a.raw(0x76,0x49);a.branch('topPlayerNext')
    path(a,0,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('topPlayerExtra',0xB8)
    path(a,0,'mData');a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
    a.label('topPlayerExtra')
    path(a,0,'mData','ExtraInfo');a.string('DEPlayerRating');a.raw(0x73,0x4F)
    path(a,0,'mData','value');a.store(2)
    display_grade(a,2,3,'topPlayerNext','topPlayerGrade')
    palette(a,3,4,'topPlayerNext','topPlayerPalette')
    path(a,0,'mcValue');a.store(5)
    text_label(a,5,3,4,0,'topPlayerNext','topPlayerText')
    a.label('topPlayerNext');a.reg(6);a.raw(0x50);a.store(6);a.branch('topPlayerLoop',0x99)
    a.label('topPlayerDone')
    a.ret()


RATING_NAMES=tuple(dict.fromkeys(v for n in ('Overall', 'OVR', *ATTRIBUTE_NAMES)
                              for v in (n, n.upper(), n.lower())))


def award_attributes_suffix(a):
    # POTW is also used for preseason All-American cards. Gate each of its
    # three values by the actual StatName so passing yards/TDs stay numeric.
    a.number(0);a.store(4)
    a.label('awardStatLoop');a.reg(4);a.number(3);a.raw(0x48);a.branch('awardStatDone',0xB8)
    path(a,1,'mTeamListItem');a.store(0);a.missing(0,'awardStatDone')
    path(a,0,'PlayerStats');a.store(0);a.missing(0,'awardStatDone')
    a.reg(0);a.reg(4);a.raw(0x4E);a.store(0);a.missing(0,'awardStatNext')
    path(a,0,'StatName');a.store(2)
    for name in RATING_NAMES:
        a.reg(2);a.string(name);a.raw(0x66);a.branch('awardStatRating')
    a.branch('awardStatNext',0x99)
    a.label('awardStatRating');path(a,0,'StatValue');a.store(0)
    display_grade(a,0,0,'awardStatNext','awardStatGrade')
    palette(a,0,2,'awardStatNext','awardStatPalette')
    a.reg(1);a.string('mcStatNumber');a.reg(4);a.raw(0x47,0x4E);a.store(3)
    text_label(a,3,0,2,0,'awardStatNext','awardStatText')
    a.label('awardStatNext');a.reg(4);a.raw(0x50);a.store(4);a.branch('awardStatLoop',0x99)
    a.label('awardStatDone')
    a.ret()


TEAM_CAPTIONS=(('mcPassYPGHeader', ('OVR', 'Overall', 'OVERALL'), 'PassYPGText'),
               ('mcRushYPGHeader', ('OFF', 'Offense', 'OFFENSE'), 'RushYPGText'),
               ('mcPPGHeader', ('DEF', 'Defense', 'DEFENSE'), 'PPGText'))

TEAM_RATING_CAPTIONS=tuple(dict.fromkeys(
    alias for caption in ('OVR','Overall','OFF','Offense','DEF','Defense')
    for alias in (caption,caption.lower(),caption.upper(),caption.title())))
MODERN_STAT_BINDINGS=tuple(
    ('HOME_STATS_' + str(index) if side=='Home' else 'AWAY_STATS_' + str(index),
     'm'+side+'TeamStatsData',constant)
    for side in ('Home','Away')
    for index,constant in enumerate(('FIRST_ROW_ARRAY_INDEX','SECOND_ROW_ARRAY_INDEX',
                                     'THIRD_ROW_ARRAY_INDEX','FOURTH_ROW_ARRAY_INDEX')))


def modern_by_numbers_suffix(a):
    # Live p90 trace proves this model binding path, not the older panel Init.
    # Native formal parameters: r4 bindName, r3 widget; preserve frame5. Every
    # stats value is displayed from row.StatDisplay, while arrows/comparisons
    # continue to consume the separate numeric row.StatValue.
    done='modernNumbersDone'
    for index,(binding,array,constant) in enumerate(MODERN_STAT_BINDINGS):
        a.reg(4);a.global_object('fb_shared_enum','BindingType',binding)
        a.raw(0x66);a.branch('modernNumbersRow'+str(index))
    a.branch(done,0x99)
    for index,(_,array,constant) in enumerate(MODERN_STAT_BINDINGS):
        a.label('modernNumbersRow'+str(index))
        path(a,1,array);a.store(0);a.missing(0,done)
        a.reg(0);path(a,1,constant);a.raw(0x4E);a.store(0);a.missing(0,done)
        a.branch('modernNumbersRowReady',0x99)
    a.label('modernNumbersRowReady')
    path(a,0,'StatName');a.store(2)
    for caption in TEAM_RATING_CAPTIONS:
        a.reg(2);a.string(caption);a.raw(0x66);a.branch('modernNumbersRating')
    a.branch(done,0x99)
    a.label('modernNumbersRating')
    path(a,0,'StatDisplay');a.store(0)
    display_grade(a,0,0,done,'modernNumbersGrade',team=True)
    palette(a,0,2,done,'modernNumbersPalette',team=True)
    # r4's binding discriminator is no longer needed after dispatch. Reuse it
    # only for the temporary style object; native r3 remains the bound widget.
    text_label(a,3,0,2,4,done,'modernNumbersText',team=True)
    a.label(done);a.ret()


def by_numbers_suffix(a):
    # This generic panel can show actual passing/rushing/PPG statistics too.
    # The rendered native caption identifies team ratings; arbitrary numbers
    # beneath a statistics caption are never interpreted as ratings.
    for index, (header, captions, ending) in enumerate(TEAM_CAPTIONS):
        group='byNumbers'+str(index)
        path(a, 1, header); a.store(0); a.missing(0, group+'done')
        path(a, 0, 'mData'); a.raw(0x76,0x49); a.branch(group+'done')
        path(a, 0, 'mData', 'display'); a.store(0)
        for caption in captions:
            a.reg(0); a.string(caption); a.raw(0x66); a.branch(group+'rating')
        a.branch(group+'done',0x99)
        a.label(group+'rating')
        for side in ('Away','Home'):a.string('mc'+side+ending)
        a.number(2);a.raw(0x42);a.store(4)
        a.number(0);a.store(5)
        a.label(group+'loop');a.reg(5);a.number(2);a.raw(0x48);a.branch(group+'done',0xB8)
        a.reg(1);a.reg(4);a.reg(5);a.raw(0x4E,0x4E);a.store(6);a.missing(6,group+'next')
        path(a,6,'mData');a.raw(0x76,0x49);a.branch(group+'next')
        path(a,6,'mData','display');a.store(0)
        display_grade(a,0,0,group+'next',group+'grade',team=True)
        palette(a,0,2,group+'next',group+'palette',team=True)
        text_label(a,6,0,2,0,group+'next',group+'text',team=True)
        a.label(group+'next');a.reg(5);a.raw(0x50);a.store(5);a.branch(group+'loop',0x99)
        a.label(group+'done')
    a.ret()


def weekly_school_suffix(a):
    path(a,1,'mData');a.raw(0x76,0x49);a.branch('weeklyRiskDone')
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('weeklyRiskDone')
    a.number(1);a.store(4)
    a.label('weeklyRiskLoop');a.reg(4);a.number(5);a.raw(0x48);a.branch('weeklyRiskDone',0xB8)
    path(a,1,'mData','ExtraInfo');a.string('OVRRow');a.reg(4);a.raw(0x47,0x4E);a.store(0)
    display_grade(a,0,0,'weeklyRiskNext','weeklyRiskGrade')
    palette(a,0,2,'weeklyRiskNext','weeklyRiskPalette')
    a.reg(1);a.string('mcOVRRow');a.reg(4);a.raw(0x47,0x4E);a.store(3)
    text_label(a,3,0,2,0,'weeklyRiskNext','weeklyRiskText')
    a.label('weeklyRiskNext');a.reg(4);a.raw(0x50);a.store(4);a.branch('weeklyRiskLoop',0x99)
    a.label('weeklyRiskDone')
    a.ret()


def weekly_playing_time_suffix(a):
    # The runtime enables this bank only for Recruiting Fog. This slot also
    # displays other dealbreakers, whose Have/Need grades must remain intact.
    done='weeklyPlayingTimeDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','playingTime');a.string('Playing Time');a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mcHaveNeed');a.store(0);a.missing(0,done)
    a.string('Have: ? | Need: ?');a.number(1);a.reg(0);a.call('SetLabel')
    path(a,1,'mcArrow');a.store(0);a.missing(0,done)
    a.reg(0);a.string('_visible');a.raw(0x74,0x4F)
    a.label(done);a.ret()


def assembler_for(builder):
    # These two callbacks may reach the body accessor after native register
    # allocation. Their loop scratch must fit an already allocated 4-slot frame.
    if builder in (weekly_school_suffix, select_team_suffix):
        return FixedFrameAssembler(4)
    return Assembler()


@dataclass(frozen=True)
class Spec:
    name: str
    asset: str
    offset: int
    size: int
    hash: int
    argc: int
    registers: int
    flags: int
    suffix: object
    new_registers: int = 0


CFM='C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_cfm/corenode.ast'
HUB='C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_cfm/hub/corenode.ast'
CONTROL='C:/Apps/CFB 27/MMC/AbilityColors/Research/assets/common/ui/art_control/scriptpod.ast'
# Read-only extraction from the installed MMC v6 cache's current collector.
# GUID e00c1ddb-d9b4-10e6-1e94-a914719bea18, cache head 4338538.
SELECT=str(Path(__file__).resolve().parents[1]/'Evidence/PlayerFog/Gaps/current-teamselect.ast')

GROUPS={
    'corePrograms':[
        Spec('TeamModule.Draw',CFM,0x95890,853,0x342CB01E56D46555,0,6,25,vertical_team_suffix),
        Spec('OverviewModule._FillListPlayerData',CFM,0x6F040,220,0xF9C6C492DA4DF66F,1,10,41,top_players_suffix),
        Spec('MySchoolGradePerWeek.Draw',CFM,0xC7338,793,0x5F67472EB5A034D3,0,4,25,weekly_school_suffix),
    ],
    'hubPrograms':[
        Spec('InfoPanelPOTW._SetAttributesParams',HUB,0x35960,440,0xFC18560C7622340A,0,6,41,award_attributes_suffix),
        Spec('InfoPanelPregameStats.Init',HUB,0x38588,1869,0xB49C571125C7ADA0,1,23,25,by_numbers_suffix),
        Spec('InfoPanelPregameTeamStats.BindWidget',HUB,0x114F8,1284,0x6347B3585977D943,2,5,25,modern_by_numbers_suffix),
    ],
    'recruitingPrograms':[
        Spec('DealBreakerInfoSlot.Draw',CONTROL,0x33780,332,0x2A313B07269AF3F1,0,4,25,weekly_playing_time_suffix),
    ],
    'teamSelectPrograms':[
        Spec('TeamSelect._UpdateStatBoxes',SELECT,0x6AE8,1230,0xBEE478BBB75CD395,2,4,41,select_team_suffix),
    ],
}


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Generated native rating display suffixes. Source values remain numeric.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::gapui {']
    report=[]
    assets={}
    for group,specs in GROUPS.items():
        lines.append('inline std::vector<notesui::Program> '+group+'(){std::vector<notesui::Program> result;')
        for s in specs:
            if s.asset not in assets:assets[s.asset]=load(Path(s.asset))
            apt=assets[s.asset]
            header=apt.data[s.offset:s.offset+48]
            frame=(struct.unpack_from('<I',header,8)[0],struct.unpack_from('<H',header,12)[0],struct.unpack_from('<H',header,14)[0])
            if frame!=(s.argc,s.registers,s.flags):raise ValueError('Unsupported native frame '+s.name)
            original=apt.data[s.offset+48:s.offset+48+s.size]
            if fnv(original)!=s.hash:raise ValueError('Unsupported native fingerprint '+s.name)
            a=assembler_for(s.suffix)
            if isinstance(a,FixedFrameAssembler) and a.native_registers!=s.registers:
                raise ValueError('Fixed-frame scratch differs from native frame '+s.name)
            a.code.extend(bytes(s.size));s.suffix(a);p=a.finish()
            if len(p.code)>32768:raise ValueError('Native adapter bytecode bound exceeded: '+s.name)
            code='{'+','.join(hex(b) for b in p.code)+'}'
            lines.append(f'// {s.name}')
            lines.append(f'result.push_back({{{s.offset},{s.argc},{s.registers},{s.flags},{s.size},{s.hash}ull,{s.new_registers or s.registers},0,{s.size},{code}}});')
            for field,offsets in [('colorOffsets',p.color_offsets),('scaleOffsets',p.scale_offsets),('teamScaleOffsets',p.team_scale_offsets),('fogOffsets',p.fog_offsets),('teamOffsets',p.team_offsets),('dollarOffsets',p.dollar_offsets)]:
                for at in offsets:lines.append(f'result.back().{field}.push_back({at});')
            for at,literal in p.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(literal)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
            report.append({'group':group,'name':s.name,'nativeBytes':s.size,'customBytes':len(p.code)-s.size,'registers':s.registers})
        lines.append('return result;}')
    lines.append('}')
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(report))


if __name__=='__main__':generate(Path('Source/FogGapUiPrograms.h'))
