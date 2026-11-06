"""Scoped plain-text budget/offer labels and tagged budget animation output.

Animation inputs, timing and budget values stay native. Only the known budget
row's text child receives the private money marker; other TextUtil animations
run their original formatter unchanged.
"""
from pathlib import Path
import json
import struct
import sys

from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path
from build_currency_ui import money,money_or_ratio

ROOT=Path(__file__).resolve().parents[1]
CFM=ROOT/'Evidence/PlayerFog/Gaps/current-cfm-currency.ast'
CONTROL=Path('C:/Apps/CFB 27/MMC/AbilityColors/Research/assets/common/ui/art_control/scriptpod.ast')
ART=ROOT/'Evidence/PlayerFog/Gaps/current-scriptpodart.ast'
MARKER='mDECurrencyPoints'


def mark_budget_value(a):
    done='markBudgetDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mcProgramPtsValue');a.store(0);a.missing(0,done)
    a.reg(0);a.string(MARKER);a.raw(0x73,0x4F)
    a.label(done)


def budget_money(a,done,prefix):
    """Known budget slots can contain a complete ratio or one split half."""
    a.reg(0);a.raw(0x44);a.string('string');a.raw(0x66);a.branch(prefix+'check')
    a.branch(prefix+'single',0x99)
    a.label(prefix+'check');a.string('/');a.number(1);a.reg(0);a.string('split');a.raw(0x52);a.store(3)
    path(a,3,'length');a.number(2);a.raw(0x66);a.branch(prefix+'parts')
    a.branch(prefix+'single',0x99)
    a.label(prefix+'parts')
    a.reg(3);a.number(0);a.raw(0x4E);a.string('');a.raw(0x66);a.branch(prefix+'leading')
    a.reg(3);a.number(1);a.raw(0x4E);a.string('');a.raw(0x66);a.branch(prefix+'trailing')
    money_or_ratio(a,done,prefix+'ratio');a.branch(prefix+'ready',0x99)
    a.label(prefix+'leading');a.reg(3);a.number(1);a.raw(0x4E);a.store(0)
    money(a,done,prefix+'leadValue');a.string('/');a.reg(2);a.raw(0x47);a.store(2)
    a.branch(prefix+'ready',0x99)
    a.label(prefix+'trailing');a.reg(3);a.number(0);a.raw(0x4E);a.store(0)
    money(a,done,prefix+'tailValue');a.reg(2);a.string('/');a.raw(0x47);a.store(2)
    a.branch(prefix+'ready',0x99)
    a.label(prefix+'single');money(a,done,prefix+'value')
    a.label(prefix+'ready')


def plain_text_suffix(a,names,prefix,formatter=money):
    done=prefix+'Done'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    for index,name in enumerate(names):
        skip=prefix+'Skip'+str(index)
        path(a,1,name);a.store(4);a.missing(4,skip)
        path(a,4,'SetLabel');a.raw(0x76,0x49);a.branch(skip)
        path(a,4,'mData');a.raw(0x76,0x49);a.branch(skip)
        # Native code has already applied its own value/discount/initial-state
        # choice to this exact monetary text slot. Its model remains untouched.
        path(a,4,'mData','display');a.store(0);formatter(a,skip,prefix+str(index))
        a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
        a.label(skip)
    a.label(done);a.ret()


def budget_suffix(a):plain_text_suffix(a,('mcProgramPtsValue','mcProgramPtsMax'),'budgetText',budget_money)
def popup_suffix(a):plain_text_suffix(a,('mcProgramPoints','mcNIL'),'offerPopupText')


def source_label(a,source,target,done,prefix,*,trailing=''):
    path(a,1,*target);a.store(4);a.missing(4,done)
    path(a,4,'SetLabel');a.raw(0x76,0x49);a.branch(done)
    for count in range(1,len(source)):
        path(a,1,*source[:count]);a.raw(0x76,0x49);a.branch(done)
    path(a,1,*source);a.store(0);money(a,done,prefix)
    if trailing:a.reg(2);a.string(trailing);a.raw(0x47);a.store(2)
    a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')


def split_budget_labels(a,budget_path,prefix):
    """Native headers use separate Remaining+slash and total text children."""
    for index,(field,target,trailing) in enumerate([
        ('Remaining','mcRemainingBudget','/'),('Budget','mcTotalBudget','')]):
        skip=prefix+'Skip'+str(index)
        source_label(a,(*budget_path,field),(target,),skip,prefix+str(index),trailing=trailing)
        a.label(skip)


def school_budget_suffix(a):
    done='schoolBudgetDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    source_label(a,('mData','ExtraInfo','SchoolInfo','DynastyPointsBudget'),('mcDynastyPointsValue',),
                 'schoolBudgetAvailableDone','schoolBudgetAvailable')
    a.label('schoolBudgetAvailableDone')
    split_budget_labels(a,('mData','ExtraInfo','Budget'),'schoolBudgetHeader')
    # Repeat only the exact native grade-adjacent position formula after the
    # amount's displayed width changes. Grades, historical stats and records
    # keep their own native values and rendering.
    for widget in ('mcDynastyPointsGrade','mcDynastyPointsValue'):
        path(a,1,widget);a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcDynastyPointsValue','GetWidth');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'DYNASTY_POINTS_GRADE_OFFSET');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcDynastyPointsGrade');a.string('_x')
    path(a,1,'mcDynastyPointsValue','_x')
    a.number(0);path(a,1,'mcDynastyPointsValue');a.string('GetWidth');a.raw(0x52,0x47)
    path(a,1,'DYNASTY_POINTS_GRADE_OFFSET');a.raw(0x47,0x4F)
    a.label(done);a.ret()


def overview_budget_suffix(a):
    done='overviewBudgetDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    split_budget_labels(a,('mData','ExtraInfo','BudgetData'),'overviewBudgetHeader')
    # Preserve the native wallet sizing/centering calculation for the newly
    # formatted split labels, without changing the pie or allocation sources.
    for widget in ('mcRemainingBudget','mcTotalBudget','mcBudgetBG','mcBudgetTitle'):
        path(a,1,widget);a.raw(0x76,0x49);a.branch(done)
    for widget in ('mcRemainingBudget','mcTotalBudget','mcBudgetBG'):
        path(a,1,widget,'GetWidth');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcBudgetBG','SetWidth');a.raw(0x76,0x49);a.branch(done)
    a.global_object('art_control','coachcarousel','ProgramPointsModule','BUDGET_BG_PADDING')
    a.raw(0x76,0x49);a.branch(done)
    a.number(0);path(a,1,'mcRemainingBudget');a.string('GetWidth');a.raw(0x52)
    a.number(0);path(a,1,'mcTotalBudget');a.string('GetWidth');a.raw(0x52,0x47)
    a.global_object('art_control','coachcarousel','ProgramPointsModule','BUDGET_BG_PADDING');a.raw(0x47)
    a.number(1);path(a,1,'mcBudgetBG');a.call('SetWidth')
    path(a,1,'mcBudgetBG');a.string('_x');path(a,1,'mcBudgetTitle','_x')
    a.number(0);path(a,1,'mcBudgetBG');a.string('GetWidth');a.raw(0x52);a.number(2);a.raw(0x0D,0x0B,0x4F)
    a.label(done);a.ret()


def allocation_suffix(a):
    done='allocationMoneyDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    for parts in [('mData',),('mData','ExtraInfo')]:
        path(a,1,*parts);a.raw(0x76,0x49);a.branch(done)
    # The native SingleRow variation renders SpentTotal as a percentage.
    # Only its normal money variation is eligible for currency formatting.
    path(a,1,'mData','ExtraInfo','SingleRow');a.raw(0x73,0x66);a.branch(done)
    source_label(a,('mData','ExtraInfo','SpentTotal'),('mcSpentTotal',),done,'allocationMoney')
    a.label(done);a.ret()


def pie_currency_suffix(a):
    done='pieCurrencyDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    for key,target,trailing in [('UpperData','mcBudgetCurrency',''),('LowerData','mcRemainingCurrency','/')]:
        skip='pieCurrency'+key+'Done'
        source_label(a,('mData','ExtraInfo',key,'Currency'),(target,),skip,'pieCurrency'+key,trailing=trailing)
        a.label(skip)
    a.label(done);a.ret()


def animation_suffix(a):
    # TextUtil._SetLabel is static: target=r3, numeric current value=r2.
    # Its native formatter can use r1 as a local output string, so no implicit
    # `this` assumption is allowed here. Preserve target before money uses r3.
    done='budgetAnimationDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    a.missing(3,done);path(a,3,MARKER);a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,3,'SetLabel');a.raw(0x76,0x49);a.branch(done)
    a.reg(3);a.store(4);a.reg(2);a.store(0)
    money(a,done,'budgetAnimation')
    a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    a.label(done);a.ret()


# group, offset, argc, registers, flags, size, hash, prefix, suffix
SPECS=[
    ('corePrograms',0x38A28,0,2,41,61,0x6E4DA88D33277C7E,mark_budget_value,None),
    ('corePrograms',0x39048,0,5,25,3377,0x82F8F4005CE31B3B,mark_budget_value,budget_suffix),
    ('corePrograms',0x7C470,0,20,41,3922,0x95C711A6AA2835DB,None,popup_suffix),
    ('corePrograms',0x7E6D0,1,11,41,554,0xB7BAF5949354DCFF,None,popup_suffix),
    ('corePrograms',0x70228,0,12,25,1024,0x12E088669C41063C,None,school_budget_suffix),
    ('corePrograms',0x710F0,0,9,25,526,0x527E120C5CA99BE4,None,overview_budget_suffix),
    ('animationPrograms',0x66DB0,7,10,42,227,0x412593C510D7428E,None,animation_suffix),
    ('artPrograms',0x43F08,0,6,25,942,0xD328FBFD7790DB47,None,allocation_suffix),
    ('artPrograms',0x45750,0,10,41,310,0xA3F103B82B2B5F21,None,pie_currency_suffix),
]


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Plain monetary labels and private-marker-only budget animation formatting.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::currencybudgetui {']
    for group,source in [('corePrograms',CFM),('animationPrograms',CONTROL),('artPrograms',ART)]:
        apt=load(source)
        lines.append(f'inline std::vector<notesui::Program> {group}(){{std::vector<notesui::Program> result;')
        for key,offset,argc,registers,flags,size,hash_,prefix,suffix in SPECS:
            if key!=group:continue
            h=apt.data[offset:offset+48];original=apt.data[offset+48:offset+48+size]
            if struct.unpack_from('<IHH',h,8)!=(argc,registers,flags) or struct.unpack_from('<I',h,24)[0]!=size or fnv(original)!=hash_:
                raise ValueError('Unsupported native budget method '+hex(offset))
            a=Assembler()
            if prefix:prefix(a);a.pad_code()
            copy_at=len(a.code);a.code.extend(bytes(size))
            if suffix:suffix(a)
            else:a.ret()
            p=a.finish()
            if len(p.code)>32768:raise ValueError('Budget adapter exceeds bytecode bound')
            code='{'+','.join(hex(v) for v in p.code)+'}'
            lines.append(f'result.push_back({{{offset},{argc},{registers},{flags},{size},{hash_}ull,{registers},{copy_at},{size},{code}}});')
            for at in p.dollar_offsets:lines.append(f'result.back().dollarOffsets.push_back({at});')
            for at,literal in p.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(literal)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}')
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'budgetCurrencyMethods':len(SPECS),'newTimers':False,'nativeAnimationInputsPreserved':True}))


if __name__=='__main__':generate(ROOT/'Source/CurrencyBudgetUiPrograms.h')
