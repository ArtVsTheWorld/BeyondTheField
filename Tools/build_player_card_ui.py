"""Build scoped player-card label adapters, preserving numeric progression data.

Only custom instructions, native fingerprints and zeroed copy regions are emitted.
Private extracted game assets are read at development time and never distributed.
"""
from pathlib import Path
import json
import sys
from build_recruit_notes_ui import Assembler, fnv, GRADE_COLORS


def path(a, register, *members):
    a.reg(register)
    for member in members:
        a.member(member)


def numeric_grade(a, value, label, done, prefix):
    # A strict numeric guard leaves unknown strings/sentinels untouched. Neither
    # the underlying WidgetData.value nor any progression input is replaced.
    a.reg(value); a.raw(0x44); a.string('number'); a.raw(0x66); a.branch(done, 0xB8)
    a.reg(value); a.reg(value); a.raw(0x66); a.branch(done, 0xB8)
    a.reg(value); a.number(0); a.raw(0x48); a.branch(done)
    a.reg(value); a.number(100); a.raw(0x67); a.branch(done)
    for upper, grade in [(60, 'F'), (70, 'D'), (80, 'C'), (90, 'B')]:
        a.reg(value); a.number(upper); a.raw(0x48); a.branch(prefix+grade)
    a.string('A'); a.store(label); a.branch(prefix+'ready', 0x99)
    for grade in 'FDCB':
        a.label(prefix+grade); a.string(grade); a.store(label); a.branch(prefix+'ready', 0x99)
    a.label(prefix+'ready')


def palette(a, label, color, done, prefix):
    for grade, rgb in GRADE_COLORS.items():
        a.reg(label); a.string(grade); a.raw(0x66); a.branch(prefix+grade)
    a.branch(done, 0x99)
    for grade, rgb in GRADE_COLORS.items():
        a.label(prefix+grade); a.number(rgb); a.store(color); a.branch(prefix+'ready', 0x99)
    a.label(prefix+'ready')


def text_label(a, target, label, color, style, done, prefix):
    a.missing(target, done)
    path(a, target, 'mData'); a.raw(0x76, 0x49); a.branch(prefix+'setlabel')
    path(a, target, 'mData', 'display'); a.reg(label); a.raw(0x66); a.branch(prefix+'color')
    a.label(prefix+'setlabel'); a.reg(label); a.number(1); a.reg(target); a.call('SetLabel')
    a.label(prefix+'color')
    path(a, target, 'mData'); a.raw(0x76, 0x49); a.branch(prefix+'setcolor')
    path(a, target, 'mData', 'ExtraInfo'); a.raw(0x76, 0x49); a.branch(prefix+'setcolor')
    path(a, target, 'mData', 'ExtraInfo', 'fontColor'); a.reg(color); a.raw(0x66); a.branch(done)
    a.label(prefix+'setcolor')
    a.empty_object(style); a.reg(style); a.string('fontColor'); a.reg(color); a.raw(0x4F)
    a.reg(style); a.number(1); a.reg(target); a.call('SetExtraInfo')


def value_item_suffix(a, container, scratch, prefix, numeric=True, mark=False):
    # container is a RatingValueItem, whose mcValue is its real text child.
    value, label, color, target, style = range(scratch, scratch+5)
    done = prefix+'done'
    a.missing(container, done)
    path(a, container, 'mData'); a.raw(0x76, 0x49); a.branch(done)
    path(a, container, 'mData', 'value'); a.store(value)
    if numeric:
        numeric_grade(a, value, label, done, prefix+'grade')
    else:
        a.reg(value); a.store(label)
    palette(a, label, color, done, prefix+'palette')
    if mark:
        path(a,container,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(prefix+'extra',0xB8)
        path(a,container,'mData');a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
        a.label(prefix+'extra');path(a,container,'mData','ExtraInfo');a.string('DEPlayerRating');a.raw(0x73,0x4F)
    path(a, container, 'mcValue'); a.store(target)
    text_label(a, target, label, color, style, done, prefix+'text')
    a.label(done)


def header_suffix(a):
    path(a, 1, 'mcRatingValueItem'); a.store(24)
    value_item_suffix(a, 24, 25, 'header',mark=True)


def header_event_suffix(a):
    path(a, 1, 'mcRatingValueItem'); a.store(12)
    value_item_suffix(a, 12, 13, 'headerEvent',mark=True)


def rating_value_draw_suffix(a):
    done='ratingDrawDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DEPlayerRating');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mData','value');a.store(0)
    a.reg(0);a.raw(0x44);a.string('number');a.raw(0x66);a.branch('ratingDrawNumeric')
    a.reg(0);a.store(2);a.branch('ratingDrawLabel',0x99)
    a.label('ratingDrawNumeric');numeric_grade(a,0,2,done,'ratingDrawGrade')
    a.label('ratingDrawLabel');palette(a,2,3,done,'ratingDrawPalette')
    path(a,1,'mcValue');a.store(4);text_label(a,4,2,3,5,done,'ratingDrawText')
    a.label(done)


def generic_slider_draw_suffix(a):
    # GenericSlider is shared with progression/settings. Recolor only a
    # private-marked, already-converted player display override; never infer
    # a rating from the shared numeric slider value or skill-group level.
    done='sliderDrawDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DEPlayerRating');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mData','ExtraInfo','RightLabelDisplayOverride');a.store(2)
    palette(a,2,3,done,'sliderDrawPalette')
    path(a,1,'mcRightValue');a.store(4)
    text_label(a,4,2,3,5,done,'sliderDrawText')
    a.label(done)


def badge_suffix(a):
    path(a, 1, 'mcStat'); a.store(17)
    # Shared PlayerModule may show NIL/stat values. Only an already-converted
    # exact grade is recolored; this adapter never converts its numeric values.
    value_item_suffix(a, 17, 18, 'badge', numeric=False)


def attributes_suffix(a):
    done='attributesDone'
    path(a, 1, 'mData'); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, 'mData', 'ExtraInfo'); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, 'mData', 'ExtraInfo', 'DEPlayerRating'); a.raw(0x73, 0x66); a.branch(done, 0xB8)
    for index, (source, widget) in enumerate([(('mData', 'value'), 'mcValue'), (('mData', 'ExtraInfo', 'MaxValue'), 'mcMaxValue')]):
        prefix='attribute'+str(index)
        path(a, 1, *source); a.store(0)
        numeric_grade(a, 0, 2, prefix+'done', prefix+'grade')
        palette(a, 2, 3, prefix+'done', prefix+'palette')
        path(a, 1, widget); a.store(4)
        text_label(a, 4, 2, 3, 0, prefix+'done', prefix+'text')
        a.label(prefix+'done')
    a.label(done)


def template_suffix(a):
    # The original function returns WidgetData in r1. Mark only the Skills
    # attributes/info template, not its containers, headers or unrelated UI.
    a.reg(2); a.global_object('fb_shared_enum', 'BindingType', 'ATTRIBUTES'); a.raw(0x66); a.branch('return', 0xB8)
    a.reg(3); a.global_object('fb_shared_enum', 'BindingType', 'INFO'); a.raw(0x66); a.branch('return', 0xB8)
    a.missing(1, 'return')
    path(a, 1, 'ExtraInfo'); a.raw(0x76, 0x49); a.branch('extra', 0xB8)
    a.reg(1); a.string('ExtraInfo'); a.number(0); a.raw(0x43, 0x4F)
    a.label('extra'); path(a, 1, 'ExtraInfo'); a.string('DEPlayerRating'); a.raw(0x73, 0x4F)
    a.label('return'); a.reg(1); a.raw(0x3E)


def group_suffix(a):
    done='groupDone'
    a.missing(1, done); a.missing(2, done)
    path(a, 1, 'ExtraInfo'); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, 'ExtraInfo', 'Rating'); a.store(3)
    numeric_grade(a, 3, 4, done, 'groupGrade')
    palette(a, 4, 6, done, 'groupPalette')
    a.empty_object(5); a.reg(5); a.string('RightLabelDisplayOverride'); a.reg(4); a.raw(0x4F)
    a.set_field(5,'DEPlayerRating',True)
    # Native slider applies these style objects again on focus changes. Clone
    # each available style and alter only its color, retaining fonts/layout.
    path(a, 2, 'mData'); a.raw(0x76, 0x49); a.branch('groupApply')
    path(a, 2, 'mData', 'ExtraInfo'); a.raw(0x76, 0x49); a.branch('groupApply')
    for index, name in enumerate(('FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle')):
        path(a, 2, 'mData', 'ExtraInfo', name); a.store(7); a.missing(7, 'groupStyle'+str(index))
        a.empty_object(8); a.reg(8); a.string('fontColor'); a.reg(6); a.raw(0x4F)
        a.reg(5); a.string(name); a.reg(8); a.number(1); a.reg(7); a.string('CloneAndModify'); a.raw(0x52, 0x4F)
        a.label('groupStyle'+str(index))
    a.label('groupApply')
    a.reg(5); a.number(1); a.reg(2); a.call('SetExtraInfo')
    a.label(done)


def level_suffix(a):
    numeric_grade(a, 4, 6, 'levelDone', 'levelGrade')
    a.reg(6); a.string('display'); a.number(0); a.number(3)
    path(a, 1, 'mSkillLevelDataProvider'); a.call('UpdateProperty')
    palette(a,6,7,'levelDone','levelPalette')
    a.number(0);a.number(1);path(a,1,'mSkillLevelDataProvider');a.string('GetItemData');a.raw(0x52);a.store(8);a.missing(8,'levelDone')
    path(a,8,'ExtraInfo');a.store(9);a.missing(9,'levelDone')
    a.empty_object(10);a.reg(10);a.string('fontColor');a.reg(7);a.raw(0x4F)
    a.reg(10);a.number(1);a.reg(9);a.string('CloneAndModify');a.raw(0x52);a.store(10)
    a.reg(10);a.string('fontColor');a.reg(7);a.raw(0x4F)
    a.set_field(10,'DEPlayerRating',True)
    a.reg(10);a.string('ExtraInfo');a.number(0);a.number(3)
    path(a,1,'mSkillLevelDataProvider');a.call('UpdateProperty')
    a.label('levelDone')


def subskills_suffix(a):
    # Verified active Ratings renderer: GenericSlider. Leave numeric values,
    # min/max/boost/costs and progression records untouched. Set only its
    # existing right-label display override and cloned value font styles.
    path(a,1,'mSubskillsDataProvider');a.raw(0x76,0x49);a.branch('subskillsDone')
    a.number(0);a.store(2)
    a.label('subskillsLoop')
    a.reg(2);a.number(128);a.raw(0x48);a.branch('subskillsDone',0xB8)
    a.reg(2);a.number(0);path(a,1,'mSubskillsDataProvider');a.string('GetNumItems');a.raw(0x52,0x48);a.branch('subskillsDone',0xB8)
    a.reg(2);a.number(1);path(a,1,'mSubskillsDataProvider');a.string('GetItemData');a.raw(0x52);a.store(3);a.missing(3,'subskillsNext')
    path(a,3,'value');a.store(4);numeric_grade(a,4,5,'subskillsNext','subskillsGrade');palette(a,5,6,'subskillsNext','subskillsPalette')
    path(a,3,'ExtraInfo');a.store(8);a.missing(8,'subskillsNext');a.empty_object(7)
    a.reg(8);a.reg(7);a.number(2);a.global_object('cafe','utility','ObjectUtil');a.call('MergeInto')
    a.reg(7);a.string('RightLabelDisplayOverride');a.reg(5);a.raw(0x4F)
    a.set_field(7,'DEPlayerRating',True)
    for index,name in enumerate(('FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle')):
        path(a,7,name);a.store(8);a.missing(8,'subskillsStyle'+str(index))
        a.empty_object(9);a.reg(9);a.string('fontColor');a.reg(6);a.raw(0x4F)
        a.reg(7);a.string(name);a.reg(9);a.number(1);a.reg(8);a.string('CloneAndModify');a.raw(0x52,0x4F)
        a.label('subskillsStyle'+str(index))
    a.reg(7);a.string('ExtraInfo');a.reg(2);a.number(3);path(a,1,'mSubskillsDataProvider');a.call('UpdateProperty')
    a.label('subskillsNext');a.reg(2);a.raw(0x50);a.store(2);a.branch('subskillsLoop',0x99)
    a.label('subskillsDone')


def attribute_slots_suffix(a):
    a.number(0);a.store(3)
    a.label('slotsLoop');a.reg(3);a.number(6);a.raw(0x48);a.branch('slotsDone',0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch('slotsDone')
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('slotsDone')
    path(a,1,'mData','ExtraInfo');a.string('AttributesData');a.reg(3);a.raw(0x47,0x4E);a.store(4);a.missing(4,'slotsNext')
    path(a,4,'isFullyScouted');a.raw(0x73,0x66);a.branch('slotsNext',0xB8)
    path(a,4,'ratingValue');a.store(5)
    palette(a,5,6,'slotsNext','slotsPalette')
    a.reg(1);a.string('mcValueSlotText');a.reg(3);a.raw(0x47,0x4E);a.store(7)
    text_label(a,7,5,6,8,'slotsNext','slotsText')
    a.label('slotsNext');a.reg(3);a.raw(0x50);a.store(3);a.branch('slotsLoop',0x99)
    a.label('slotsDone')


def skill_slots_suffix(a):
    a.number(0);a.store(12)
    a.label('skillSlotsLoop');a.reg(12);a.number(6);a.raw(0x48);a.branch('skillSlotsDone',0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch('skillSlotsDone')
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('skillSlotsDone')
    path(a,1,'mData','ExtraInfo');a.string('SkillData');a.reg(12);a.raw(0x47,0x4E);a.store(13);a.missing(13,'skillSlotsNext')
    path(a,13,'Rating');a.store(14)
    numeric_grade(a,14,15,'skillSlotsNext','skillSlotsGrade')
    palette(a,15,16,'skillSlotsNext','skillSlotsPalette')
    a.reg(1);a.string('mcSkill');a.reg(12);a.raw(0x47,0x4E);a.store(17);a.missing(17,'skillSlotsNext')
    a.empty_object(18);a.reg(18);a.string('RightLabelDisplayOverride');a.reg(15);a.raw(0x4F)
    a.set_field(18,'DEPlayerRating',True)
    path(a,17,'mData');a.raw(0x76,0x49);a.branch('skillSlotsApply')
    path(a,17,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('skillSlotsApply')
    for index,name in enumerate(('FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle')):
        path(a,17,'mData','ExtraInfo',name);a.store(19);a.missing(19,'skillSlotsStyle'+str(index))
        a.empty_object(20);a.reg(20);a.string('fontColor');a.reg(16);a.raw(0x4F)
        a.reg(18);a.string(name);a.reg(20);a.number(1);a.reg(19);a.string('CloneAndModify');a.raw(0x52,0x4F)
        a.label('skillSlotsStyle'+str(index))
    a.label('skillSlotsApply');a.reg(18);a.number(1);a.reg(17);a.call('SetExtraInfo')
    a.label('skillSlotsNext');a.reg(12);a.raw(0x50);a.store(12);a.branch('skillSlotsLoop',0x99)
    a.label('skillSlotsDone')


def append_program(size, suffix, copy_bytes=None):
    a=Assembler(); a.code.extend(bytes(size if copy_bytes is None else copy_bytes))
    suffix(a); a.ret()
    return a.finish()


SPECS={
    'controlPrograms': ('C:/Apps/CFB 27/MMC/AbilityColors/Research/assets/common/ui/art_control/scriptpod.ast', [
        (0x36EB0,0,23,25,6675,0x27B53CDB6D8B7673,23,badge_suffix,None),
        (0x18CC0,0,5,25,1233,0x9DCA6F0E09D88CDA,5,attributes_suffix,None),
        (0x327E8,0,9,25,388,0x45B4DB9AE855957E,9,attribute_slots_suffix,None),
        (0x44BF8,0,12,25,204,0xC3220200E8D796CA,21,skill_slots_suffix,None),
        (0x22150,0,9,25,1730,0x444360923A963AB5,9,rating_value_draw_suffix,None)]),
    'sliderPrograms': ('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_com/scriptpod.ast', [
        (0x3EEB0,0,10,25,2587,0xF364EAE7B6CB59CA,10,generic_slider_draw_suffix,None)]),
    'cardPrograms': ('Evidence/PlayerFog/manageplayerart.ast', [
        (0x3038,1,30,41,2224,0xA6909B15969FC597,30,header_suffix,None),
        (0x3EF0,6,18,41,876,0x944C06B02B868F03,18,header_event_suffix,None)]),
    'templatePrograms': ('Evidence/PlayerFog/manageplayer-skills.ast', [
        (0x860,3,4,42,414,0x351678A392FC9086,4,template_suffix,411)]),
    'skillPrograms': ('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_cfm/corenode.ast', [
        (0x54C20,4,3,42,240,0x1A7E5A93BC79FFE4,9,group_suffix,None),
        (0x54E20,2,6,41,100,0x3C700A570F7C0AA9,11,level_suffix,None),
        (0x54EC0,1,8,41,164,0xC40A11F67BBBC449,10,subskills_suffix,None)])}


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Generated custom label adapters. Native bodies are verified/copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::playercardui {']
    methods=0
    for name,(asset,specs) in SPECS.items():
        apt=load(Path(asset)); lines.append(f'inline std::vector<notesui::Program> {name}(){{std::vector<notesui::Program> result;')
        for off,argc,regs,flags,size,expected,newregs,suffix,copy_bytes in specs:
            original=apt.data[off+48:off+48+size]
            if fnv(original)!=expected:raise ValueError(f'Unsupported native player method {asset}:{off:x}')
            count=size if copy_bytes is None else copy_bytes
            program=append_program(size,suffix,copy_bytes)
            code='{'+','.join(hex(b) for b in program.code)+'}'
            lines.append(f'result.push_back({{{off},{argc},{regs},{flags},{size},{expected}ull,{newregs},0,{count},{code}}});')
            if name=='cardPrograms' and off==0x3EF0:
                # Only loader metadata is normalized for the parent-body hash.
                # Every callback instruction/header semantic remains checked.
                for at,name_rva,param_rva in [(0x90,0x61D0,0x61D8),(0x108,0x61F8,0x6200),(0x180,0x6220,0x6228)]:
                    lines.append(f'result.back().nestedDefinitions.push_back({{{at},{name_rva},{param_rva}}});')
            for at,text in program.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
            methods+=1
        lines.append('return result;}')
    lines.append('}')
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'playerCardMethods':methods,'numericProgressionPreserved':True}))


if __name__=='__main__':generate(Path('Source/PlayerCardUiPrograms.h'))
