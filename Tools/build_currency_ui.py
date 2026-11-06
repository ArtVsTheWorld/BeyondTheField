"""Native, presentation-only Dynasty dollar labels, never budget model values."""
from pathlib import Path
import json,sys,struct
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path

def money(a,done,prefix):
    # Four-register frame: this=r1, input=r0, output=r2, scratch=r3.
    # Only callers with verified currency semantics may use this formatter.
    a.reg(0);a.raw(0x44);a.string('string');a.raw(0x66);a.branch(prefix+'string')
    a.reg(0);a.raw(0x44);a.string('number');a.raw(0x66);a.branch(done,0xB8)
    a.branch(prefix+'number',0x99)
    a.label(prefix+'string');path(a,0,'length');a.number(0);a.raw(0x67);a.branch(done,0xB8)
    a.string(' ');a.number(1);a.reg(0);a.string('split');a.raw(0x52);a.store(3)
    a.string('');a.number(1);a.reg(3);a.string('join');a.raw(0x52);a.store(0)
    path(a,0,'length');a.number(0);a.raw(0x67);a.branch(done,0xB8)
    a.string(',');a.number(1);a.reg(0);a.string('split');a.raw(0x52);a.store(3)
    a.string('');a.number(1);a.reg(3);a.string('join');a.raw(0x52);a.store(3)
    # A native grid may already supply "$0"/"$600K". Reject noncanonical
    # numeric text before arithmetic; do not depend on APT NaN equality.
    for invalid in ['NaN','Infinity','-Infinity']:
        a.reg(3);a.string(invalid);a.raw(0x66);a.branch(done)
    a.reg(3);a.raw(0x4A);a.store(0)
    a.reg(0);a.raw(0x4B);a.reg(3);a.raw(0x66);a.branch(done,0xB8)
    a.label(prefix+'number')
    a.reg(0);a.raw(0x4B);a.store(3)
    for invalid in ['NaN','nan','Infinity','inf','-Infinity','-inf']:
        a.reg(3);a.string(invalid);a.raw(0x66);a.branch(done)
    a.reg(0);a.reg(0);a.raw(0x66);a.branch(done,0xB8)
    for edge,op in [(-1000000000,0x48),(1000000000,0x67)]:
        a.reg(0);a.number(1000000);a.number(1000);a.raw(0x0C);
        if edge<0:a.number(-1);a.raw(0x0C)
        a.raw(op);a.branch(done)
    a.string('');a.store(2)
    a.reg(0);a.number(0);a.raw(0x48);a.branch(prefix+'negative')
    a.branch(prefix+'positive',0x99)
    a.label(prefix+'negative');a.string('-');a.store(2);a.reg(0);a.number(-1);a.raw(0x0C);a.store(0)
    a.label(prefix+'positive');a.reg(0);a.number(0);a.raw(0x66);a.branch(prefix+'zero')
    a.reg(0);a.number(250);a.raw(0x48);a.branch(prefix+'thousands')
    a.reg(0);a.number(25);a.raw(0x0D);a.number(1);a.global_object('Math');a.string('round');a.raw(0x52);a.store(3)
    a.reg(3);a.number(10);a.raw(0x0D);a.number(1);a.global_object('Math');a.string('floor');a.raw(0x52);a.store(0)
    a.reg(2);a.reg(0);a.raw(0x4B,0x47);a.string('.');a.raw(0x47)
    a.reg(3);a.reg(0);a.number(10);a.raw(0x0C,0x0B,0x4B,0x47);a.string('M');a.raw(0x47);a.store(2)
    a.branch(prefix+'ready',0x99)
    a.label(prefix+'thousands');a.reg(2);a.reg(0);a.number(4);a.raw(0x0C);a.number(1);a.global_object('Math');a.string('round');a.raw(0x52,0x4B,0x47);a.string('K');a.raw(0x47);a.store(2)
    a.branch(prefix+'ready',0x99)
    a.label(prefix+'zero');a.string('0');a.store(2)
    a.label(prefix+'ready')

def money_or_ratio(a,done,prefix):
    a.reg(0);a.raw(0x44);a.string('string');a.raw(0x66);a.branch(prefix+'check')
    a.branch(prefix+'single',0x99)
    a.label(prefix+'check');a.string('/');a.number(1);a.reg(0);a.string('split');a.raw(0x52);a.store(2)
    path(a,2,'length');a.number(2);a.raw(0x66);a.branch(prefix+'ratio')
    path(a,2,'length');a.number(1);a.raw(0x66);a.branch(done,0xB8)
    a.branch(prefix+'single',0x99)
    a.label(prefix+'ratio');a.reg(1);a.string('mDEDollarParts');a.reg(2);a.raw(0x4F)
    a.reg(2);a.number(0);a.raw(0x4E);a.store(0);money(a,done,prefix+'left')
    a.reg(1);a.string('mDEDollarLeft');a.reg(2);a.raw(0x4F)
    path(a,1,'mDEDollarParts');a.number(1);a.raw(0x4E);a.store(0);money(a,done,prefix+'right')
    path(a,1,'mDEDollarLeft');a.string(' / ');a.raw(0x47);a.reg(2);a.raw(0x47);a.store(2)
    a.branch(prefix+'ready',0x99)
    a.label(prefix+'single');money(a,done,prefix+'value')
    a.label(prefix+'ready')

def icon_label_suffix(a):
    done='dollarIconDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    # Reproduce both verified native PROGRAMPOINTS expressions exactly:
    # ImageUtil's format-token:asset:library and PendingOfferListItem's
    # legacy asset:library. Coins, skill points and other libraries stay out.
    a.global_object('shared_enum','fblibraries','global','Icons','LIBRARY_ID')
    a.global_object('shared_enum','fblibraries','global','Icons','ASSETID_ICON_CURRENCY_PROGRAMPOINTS')
    a.number(2);a.global_object('art_utility','ImageUtil');a.string('BuildFbImageString');a.raw(0x52)
    path(a,1,'mData','value');a.raw(0x66);a.branch('dollarIconVerified')
    a.global_object('shared_enum','fblibraries','global','Icons','ASSETID_ICON_CURRENCY_PROGRAMPOINTS')
    a.string(':');a.raw(0x47)
    a.global_object('shared_enum','fblibraries','global','Icons','LIBRARY_ID');a.raw(0x47)
    path(a,1,'mData','value');a.raw(0x66);a.branch(done,0xB8)
    a.label('dollarIconVerified')
    path(a,1,'mData','display');a.store(0);money_or_ratio(a,done,'dollarIcon')
    path(a,1,'mcLabel');a.store(0);a.missing(0,done)
    a.reg(2);a.number(1);a.reg(0);a.call('SetLabel')
    a.label(done);a.ret()

def unchanged_info_slot_layout(a,done):
    # The common case is an unchanged cached slot. Do not call setters, clone
    # fonts or invalidate either widget when the displayed fit is still valid.
    slow='dollarSlotRefreshRequired'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(slow,0xB8)
    path(a,1,'mcCurrencyValue');a.store(0);a.missing(0,slow)
    path(a,0,'mDEDollarSlotState');a.store(2);a.missing(2,slow)
    path(a,2,'appliedStyle');a.store(3);a.missing(3,slow)
    for reg,parts in [(1,('mData',)),(1,('mData','ExtraInfo')),
                      (0,('mData',)),(0,('mData','ExtraInfo'))]:
        path(a,reg,*parts);a.store(3);a.missing(3,slow)
    path(a,1,'mData','ExtraInfo','UseCurrencyValue');a.raw(0x73,0x66);a.branch(slow,0xB8)
    for prop,constant in [('CurrencyIconId','ASSETID_ICON_CURRENCY_PROGRAMPOINTS'),('CurrencyIconLibrary','LIBRARY_ID')]:
        path(a,1,'mData','ExtraInfo',prop)
        a.global_object('shared_enum','fblibraries','global','Icons',constant)
        a.raw(0x66);a.branch(slow,0xB8)
    for reg,parts,saved in [
            (1,('mData','ExtraInfo','CurrencyValue'),'sourceValue'),
            (1,('mData','Width'),'parentWidth'),(0,('_x',),'currencyX'),
            (0,('mData','ExtraInfo','IconSize'),'iconSize'),
            (0,('mData','ExtraInfo','TextPadding'),'textPadding'),
            (0,('mData','Width'),'appliedWidth'),
            (0,('mData','ExtraInfo','LabelTextStyle'),'appliedStyle'),
            (0,('mData','display'),'appliedDisplay')]:
        path(a,reg,*parts);path(a,2,saved);a.raw(0x66);a.branch(slow,0xB8)
    path(a,0,'mData','ExtraInfo','FixedWidth');a.raw(0x73,0x66);a.branch(slow,0xB8)
    # A native change to the fitted style's resize fields also needs a refresh;
    # unrelated in-place font/color edits can keep the existing valid fit.
    path(a,2,'appliedStyle','resize');a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN');a.raw(0x66);a.branch(slow,0xB8)
    path(a,2,'appliedStyle','resizeWidth');path(a,2,'appliedResizeWidth');a.raw(0x66);a.branch(slow,0xB8)
    path(a,2,'appliedStyle','maxNumLines');a.number(1);a.raw(0x66);a.branch(slow,0xB8)
    a.branch(done,0x99);a.label(slow)


def restore_info_slot_layout(a):
    # This bank must remain dispatched while dollars are Off: it restores only
    # state owned by a previous dollar draw, then becomes a no-op. Restoring
    # before a changed draw also lets a legitimate native style/width replacement
    # become the next fit's baseline rather than keeping a stale saved style.
    done='restoreDollarSlotDone';clear='restoreDollarSlotClear'
    path(a,1,'mcCurrencyValue');a.store(0);a.missing(0,done)
    path(a,0,'mDEDollarSlotState');a.store(2);a.missing(2,done)
    path(a,0,'mData');a.store(3);a.missing(3,clear)
    path(a,0,'mData','display');path(a,2,'appliedDisplay');a.raw(0x66);a.branch('restoreDollarSlotStyle',0xB8)
    path(a,2,'display');a.number(1);a.reg(0);a.call('SetLabel')
    a.label('restoreDollarSlotStyle')
    path(a,2,'appliedStyle');a.store(3);a.missing(3,'restoreDollarSlotWidth')
    path(a,0,'mData','ExtraInfo');a.store(3);a.missing(3,'restoreDollarSlotWidth')
    path(a,0,'mData','ExtraInfo','LabelTextStyle');path(a,2,'appliedStyle');a.raw(0x66);a.branch('restoreDollarSlotWidth',0xB8)
    path(a,2,'appliedStyle','CloneAndModify');a.store(3);a.missing(3,'restoreDollarSlotWidth')
    # Restore only style properties that still match the values we applied.
    # Cloning the current style preserves native edits made in place too.
    for prop in ['resize','resizeWidth','maxNumLines']:
        keep='restoreDollarSlotKeep'+prop;ready='restoreDollarSlotReady'+prop
        a.string(prop);path(a,2,'appliedStyle',prop)
        if prop=='resize':a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN')
        elif prop=='resizeWidth':path(a,2,'appliedResizeWidth')
        else:a.number(1)
        a.raw(0x66);a.branch(keep,0xB8)
        path(a,2,'style',prop);a.branch(ready,0x99)
        a.label(keep);path(a,2,'appliedStyle',prop);a.label(ready)
    a.number(3);a.raw(0x43);a.number(1);path(a,2,'appliedStyle');a.string('CloneAndModify');a.raw(0x52);a.store(3)
    a.string('LabelTextStyle');a.reg(3);a.number(1);a.raw(0x43);a.number(1);a.reg(0);a.call('SetExtraInfo')
    a.label('restoreDollarSlotWidth')
    path(a,2,'appliedWidth');a.store(3);a.missing(3,clear)
    path(a,0,'mData','Width');a.reg(3);a.raw(0x66);a.branch(clear,0xB8)
    path(a,0,'mData','ExtraInfo');a.store(3);a.missing(3,'restoreDollarSlotNativeWidth')
    path(a,0,'mData','ExtraInfo','FixedWidth');a.raw(0x73,0x66);a.branch('restoreDollarSlotNativeWidth',0xB8)
    a.string('FixedWidth');path(a,2,'fixed');a.number(1);a.raw(0x43);a.number(1);a.reg(0);a.call('SetExtraInfo')
    a.label('restoreDollarSlotNativeWidth')
    path(a,2,'width');a.number(1);a.reg(0);a.call('SetWidth')
    a.label(clear);a.reg(0);a.string('mDEDollarSlotState');a.raw(0x76,0x4F)
    a.label(done)


def info_slot_suffix(a):
    done='dollarSlotDone'
    unchanged_info_slot_layout(a,done)
    restore_info_slot_layout(a)
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','UseCurrencyValue');a.raw(0x73,0x66);a.branch(done,0xB8)
    # SetData fills these defaults, but callers can override them for skill
    # points or other currencies. Never infer money from UseCurrencyValue alone.
    for prop,constant in [('CurrencyIconId','ASSETID_ICON_CURRENCY_PROGRAMPOINTS'),('CurrencyIconLibrary','LIBRARY_ID')]:
        path(a,1,'mData','ExtraInfo',prop)
        a.global_object('shared_enum','fblibraries','global','Icons',constant)
        a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mData','ExtraInfo','CurrencyValue');a.store(0);money(a,done,'dollarSlot')
    path(a,1,'mcCurrencyValue');a.store(0);a.missing(0,done)
    path(a,0,'mData');a.store(3);a.missing(3,'dollarSlotSetLabel')
    a.reg(0);a.string('mDEDollarSlotState')
    a.string('display');path(a,1,'mData','ExtraInfo','CurrencyValue');a.string('appliedDisplay');a.reg(2);a.number(2);a.raw(0x43,0x4F)
    a.label('dollarSlotSetLabel')
    a.reg(2);a.number(1);a.reg(0);a.call('SetLabel')
    # InfoSlotsItemWidget.Draw lays out the class and the currency icon, but
    # leaves the latter's label unconstrained.  A redshirt class plus a dollar
    # label can consequently flow into the adjacent Height & Weight slot.
    # Bound only this native currency child's text to the space remaining in
    # its own slot.  Clone the native font style so its color, size, alignment
    # and icon are retained, including when the child redraws after SetLabel.
    # All measurements come from the unscaled parent layout, never the last
    # rendered currency width (repeated draws must not progressively shrink).
    for parts in [('mData',),('mData','ExtraInfo'),('mData','ExtraInfo','LabelTextStyle'),
                  ('mData','ExtraInfo','LabelTextStyle','CloneAndModify')]:
        path(a,0,*parts);a.store(3);a.missing(3,done)
    for register,parts in [(1,('mData','Width')),(0,('_x',)),
                           (0,('mData','ExtraInfo','IconSize')),
                           (0,('mData','ExtraInfo','TextPadding'))]:
        path(a,register,*parts);a.raw(0x44);a.string('number');a.raw(0x66);a.branch(done,0xB8)
        path(a,register,*parts);a.number(0);a.raw(0x48);a.branch(done)
        path(a,register,*parts);a.number(4096);a.raw(0x48);a.branch(done,0xB8)
    path(a,1,'mData','Width');path(a,0,'_x');a.raw(0x0B);a.number(10);a.raw(0x0B);a.store(2)
    a.reg(2);path(a,0,'mData','ExtraInfo','IconSize');a.raw(0x0B)
    path(a,0,'mData','ExtraInfo','TextPadding');a.raw(0x0B);a.store(3)
    a.reg(3);a.number(0);a.raw(0x67);a.branch(done,0xB8)
    a.string('resize');a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN')
    a.string('resizeWidth');a.reg(3);a.string('maxNumLines');a.number(1);a.number(3);a.raw(0x43)
    a.number(1);path(a,0,'mData','ExtraInfo','LabelTextStyle');a.string('CloneAndModify');a.raw(0x52);a.store(3)
    for name,parts in [('width',('mData','Width')),('fixed',('mData','ExtraInfo','FixedWidth')),
                       ('style',('mData','ExtraInfo','LabelTextStyle'))]:
        path(a,0,'mDEDollarSlotState');a.string(name);path(a,0,*parts);a.raw(0x4F)
    path(a,0,'mDEDollarSlotState');a.string('appliedWidth');a.reg(2);a.raw(0x4F)
    path(a,0,'mDEDollarSlotState');a.string('appliedStyle');a.reg(3);a.raw(0x4F)
    path(a,0,'mDEDollarSlotState');a.string('appliedResizeWidth');path(a,3,'resizeWidth');a.raw(0x4F)
    for reg,parts,name in [
            (1,('mData','ExtraInfo','CurrencyValue'),'sourceValue'),
            (1,('mData','Width'),'parentWidth'),(0,('_x',),'currencyX'),
            (0,('mData','ExtraInfo','IconSize'),'iconSize'),
            (0,('mData','ExtraInfo','TextPadding'),'textPadding')]:
        path(a,0,'mDEDollarSlotState');a.string(name);path(a,reg,*parts);a.raw(0x4F)
    a.string('LabelTextStyle');a.reg(3);a.string('FixedWidth');a.raw(0x73);a.number(2);a.raw(0x43)
    a.number(1);a.reg(0);a.call('SetExtraInfo')
    a.reg(2);a.number(1);a.reg(0);a.call('SetWidth')
    a.label(done);a.ret()

def point_cell_suffix(a):
    done='dollarCellDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    a.missing(3,done);path(a,3,'display');a.store(0);money(a,done,'dollarCell')
    path(a,1,'mTextField');a.store(0);a.missing(0,done)
    a.reg(2);a.number(1);a.reg(0);a.call('SetText')
    a.label(done);a.ret()

def team_budget_suffix(a):
    done='dollarTeamDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    for parts in [('mData',),('mData','ExtraInfo'),('mData','ExtraInfo','ProgramPointsNILData')]:
        path(a,1,*parts);a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','IsProgramPointsNILData');a.raw(0x73,0x66);a.branch(done,0xB8)
    for i,(field,widget) in enumerate([
        ('RecruitNILValue','mcRecruitNILValue'),('RosterNILValue','mcRosterNILValue'),('UnspentValue','mcUnspentNILValue'),
        ('RecruitNILSuggestedValue','mcRecruitNILSubvalue'),('RosterNILSuggestedValue','mcRosterNILSubvalue'),('UnspentSuggestedValue','mcUnspentNILSubvalue')]):
        skip='dollarTeamSkip'+str(i)
        path(a,1,widget);a.store(4);a.missing(4,skip)
        path(a,1,'mData','ExtraInfo','ProgramPointsNILData',field);a.store(0);money(a,skip,'dollarTeam'+str(i))
        a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
        a.label(skip)
    a.label(done)

SPECS={
 'iconPrograms':('../PlayerAnalytics/Research/assets/common/ui/node_com/scriptpod.ast',[
     (0x49FE8,1,4,25,25,0xAB621E24163E3402,icon_label_suffix),
     (0x4A0D8,0,6,25,1618,0x153701423A0BB648,icon_label_suffix)]),
 'slotPrograms':('../AbilityColors/Research/assets/common/ui/art_control/scriptpod.ast',[
     (0x34730,0,7,25,702,0x9153EE615A8EF74A,info_slot_suffix)]),
 'cellPrograms':('../PlayerAnalytics/Research/assets/common/ui/node_cfm/corenode.ast',[
     (0xDBD68,1,4,25,37,0x49DB87F2EF0226AE,point_cell_suffix)])}

def generate():
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Custom currency labels only; native methods verified/copied at attachment.','#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::currencyui {']
    for name,(asset,specs) in SPECS.items():
        apt=load(Path(asset));lines.append(f'inline std::vector<notesui::Program> {name}(){{std::vector<notesui::Program> result;')
        for off,argc,regs,flags,size,expected,suffix in specs:
            header=apt.data[off:off+48]
            if (struct.unpack_from('<I',header,8)[0],struct.unpack_from('<H',header,12)[0],struct.unpack_from('<H',header,14)[0])!=(argc,regs,flags):raise ValueError('Unsupported native currency frame')
            if fnv(apt.data[off+48:off+48+size])!=expected:raise ValueError('Unsupported native currency method')
            a=Assembler();a.code.extend(bytes(size));suffix(a);p=a.finish()
            code='{'+','.join(hex(b) for b in p.code)+'}'
            lines.append(f'result.push_back({{{off},{argc},{regs},{flags},{size},{expected}ull,{regs},0,{size},{code}}});')
            for at in p.dollar_offsets:lines.append(f'result.back().dollarOffsets.push_back({at});')
            for at,text in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}');Path('Source/CurrencyUiPrograms.h').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':generate()
