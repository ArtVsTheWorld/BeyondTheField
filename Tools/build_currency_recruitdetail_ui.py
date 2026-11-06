"""Format the recruiting Scholarship detail's exact monetary summary rows."""
from pathlib import Path
import json
import struct
import sys

from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path
from build_currency_ui import money

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'Evidence/PlayerFog/Gaps/current-recruitinghub.ast'
OFFSET=0x16160
ARGC,REGISTERS,FLAGS,SIZE,HASH=0,8,25,1727,0xC06366D67CE77475
STATE='mDERecruitDetailCurrency'
METRIC_STYLE_FIELDS=('fontSize','fontId','fontFace','fontName','resize','resizeWidth',
                     'hAlign','maxNumLines','letterSpacing','lineSpacing')


def currency_scope(a,done):
    for parts in [('mData',),('mData','ExtraInfo')]:
        path(a,1,*parts);a.raw(0x76,0x49);a.branch(done)
    # This summary renderer also displays hours, influence, percentages and
    # pitch grades. Only the exact native program-points icon/library pair
    # identifies the monetary Offer and Expected NIL Body fields.
    for field,constant in [('Icon','ASSETID_ICON_CURRENCY_PROGRAMPOINTS'),('IconLibrary','LIBRARY_ID')]:
        path(a,1,'mData','ExtraInfo',field)
        a.global_object('shared_enum','fblibraries','global','Icons',constant)
        a.raw(0x66);a.branch(done,0xB8)


def icon_x(a):
    a.reg(6);a.string('_x');path(a,4,'_x')
    a.number(0);a.reg(4);a.string('GetWidth');a.raw(0x52,0x0B)
    a.number(0);a.reg(6);a.string('GetWidth');a.raw(0x52,0x0B)
    a.number(10);a.raw(0x0B,0x4F)


def icon_y(a):
    a.reg(6);a.string('_y');path(a,4,'_y')
    a.number(0);a.reg(6);a.string('GetHeight');a.raw(0x52)
    a.number(2);a.raw(0x0D,0x0B,0x4F)


def suffix(a):
    # Always dispatch this bank, including Dollars Off, to clean up only state
    # owned by a previous converted Draw. Fresh Off draws remain inert.
    done='recruitDetailMoneyDone';apply='recruitDetailMoneyApply';restore='recruitDetailMoneyRestore'
    path(a,1,'mcBody');a.store(4);a.missing(4,done)
    path(a,4,STATE);a.store(5);a.missing(5,apply)
    path(a,4,'mData');a.raw(0x76,0x49);a.branch('recruitDetailMoneyClear')
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(restore,0xB8)
    currency_scope(a,restore)
    # A stable draw needs no text setter, measurements, geometry or allocation.
    for register,parts,saved in [
            (1,('mData','ExtraInfo','Body'),'source'),
            (1,('mData','Width'),'parentWidth'),
            (4,('mData','display'),'display'),(4,('mData','ExtraInfo'),'style'),
            (4,('_x',),'bodyX'),(4,('_y',),'bodyY'),
            (1,('mcIcon',),'icon')]:
        path(a,register,*parts);path(a,5,saved);a.raw(0x66);a.branch(restore,0xB8)
    path(a,1,'mcIcon');a.store(6);a.missing(6,restore)
    path(a,6,'mData');a.raw(0x76,0x49);a.branch(restore)
    for parts,saved in [(('_x',),'iconX'),(('_y',),'iconY')]:
        path(a,6,*parts);path(a,5,saved);a.raw(0x66);a.branch(restore,0xB8)
    for parts,saved in [(('mData','Width'),'iconWidth'),(('mData','Height'),'iconHeight')]:
        path(a,6,*parts);path(a,5,saved);a.raw(0x66);a.branch(restore,0xB8)
    path(a,4,'mData','ExtraInfo');a.store(7);a.missing(7,'recruitDetailMoneyCacheStyleDone')
    # Native SetExtraInfo can merge layout fields into the same style object.
    # Compare primitive metrics as well as identity; color-only edits are inert.
    for prop in METRIC_STYLE_FIELDS:
        path(a,7,prop);path(a,5,'metric_'+prop);a.raw(0x66);a.branch(restore,0xB8)
    a.label('recruitDetailMoneyCacheStyleDone')
    a.branch(done,0x99)

    a.label(restore)
    # Native Draw may have already replaced a reused row's text. Only replace
    # our own last applied text; a new native value/style remains its baseline.
    path(a,4,'mData','display');path(a,5,'display');a.raw(0x66);a.branch('recruitDetailMoneyRestoreIcon',0xB8)
    for parts in [('mData',),('mData','ExtraInfo')]:
        path(a,1,*parts);a.raw(0x76,0x49);a.branch('recruitDetailMoneyRestoreIcon')
    path(a,1,'mData','ExtraInfo','Body');a.store(7);a.missing(7,'recruitDetailMoneyRestoreIcon')
    a.reg(7);path(a,5,'source');a.raw(0x66);a.branch('recruitDetailMoneyRestoreFresh',0xB8)
    path(a,5,'nativeDisplay');a.store(7)
    a.label('recruitDetailMoneyRestoreFresh')
    path(a,4,'SetLabel');a.raw(0x76,0x49);a.branch('recruitDetailMoneyRestoreIcon')
    a.reg(7);a.number(1);a.reg(4);a.call('SetLabel')
    a.label('recruitDetailMoneyRestoreIcon')
    path(a,1,'mcIcon');a.store(6);a.missing(6,'recruitDetailMoneyClear')
    a.reg(6);path(a,5,'icon');a.raw(0x66);a.branch('recruitDetailMoneyClear',0xB8)
    for register,method in [(4,'GetWidth'),(6,'GetWidth'),(6,'GetHeight')]:
        path(a,register,method);a.raw(0x76,0x49);a.branch('recruitDetailMoneyClear')
    path(a,6,'_x');path(a,5,'iconX');a.raw(0x66);a.branch('recruitDetailMoneyRestoreY',0xB8)
    icon_x(a)
    a.label('recruitDetailMoneyRestoreY')
    path(a,6,'_y');path(a,5,'iconY');a.raw(0x66);a.branch('recruitDetailMoneyClear',0xB8)
    icon_y(a)
    a.label('recruitDetailMoneyClear');a.reg(4);a.string(STATE);a.raw(0x76,0x4F)

    a.label(apply)
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    currency_scope(a,done)
    path(a,4,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcIcon');a.store(6);a.missing(6,done)
    path(a,6,'mData');a.raw(0x76,0x49);a.branch(done)
    for register,method in [(4,'SetLabel'),(4,'GetWidth'),(6,'GetWidth'),(6,'GetHeight')]:
        path(a,register,method);a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','Body');a.store(0)
    money(a,done,'recruitDetailMoney')
    a.string('source');path(a,1,'mData','ExtraInfo','Body')
    a.string('nativeDisplay');path(a,4,'mData','display')
    a.string('display');a.reg(2)
    a.string('style');path(a,4,'mData','ExtraInfo')
    a.string('parentWidth');path(a,1,'mData','Width')
    a.string('bodyX');path(a,4,'_x');a.string('bodyY');path(a,4,'_y')
    a.string('icon');a.reg(6)
    a.string('iconWidth');path(a,6,'mData','Width');a.string('iconHeight');path(a,6,'mData','Height')
    path(a,4,'mData','ExtraInfo');a.store(7)
    for prop in METRIC_STYLE_FIELDS:
        a.string('metric_'+prop);a.missing(7,'recruitDetailMoneyMetricMissing'+prop)
        path(a,7,prop);a.branch('recruitDetailMoneyMetricReady'+prop,0x99)
        a.label('recruitDetailMoneyMetricMissing'+prop);a.raw(0x76)
        a.label('recruitDetailMoneyMetricReady'+prop)
    a.number(10+len(METRIC_STYLE_FIELDS));a.raw(0x43);a.store(5)
    a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    # Native icon placement for the new right-aligned amount; never resize or
    # restyle the body, the icon, or adjacent influence/percentage widgets.
    icon_x(a);icon_y(a)
    for name in ('_x','_y'):
        a.reg(5);a.string('iconX' if name=='_x' else 'iconY');path(a,6,name);a.raw(0x4F)
    a.reg(4);a.string(STATE);a.reg(5);a.raw(0x4F)
    a.label(done);a.ret()


def generate(destination=None):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    apt=load(ASSET);header=apt.data[OFFSET:OFFSET+48];native=apt.data[OFFSET+48:OFFSET+48+SIZE]
    if struct.unpack_from('<IHH',header,8)!=(ARGC,REGISTERS,FLAGS) or struct.unpack_from('<I',header,24)[0]!=SIZE or fnv(native)!=HASH:
        raise ValueError('Unsupported recruiting summary renderer')
    a=Assembler();a.code.extend(bytes(SIZE));suffix(a);p=a.finish()
    if len(p.code)>32768:raise ValueError('Recruiting currency detail exceeds bytecode bound')
    code='{'+','.join(hex(v) for v in p.code)+'}'
    lines=['// Exact program-points summary rows only; numeric sources remain native.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::currencyrecruitdetailui {',
           'inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;',
           f'result.push_back({{{OFFSET},{ARGC},{REGISTERS},{FLAGS},{SIZE},{HASH}ull,{REGISTERS},0,{SIZE},{code}}});']
    for at in p.dollar_offsets:lines.append(f'result.back().dollarOffsets.push_back({at});')
    for at,literal in p.literals:
        lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(literal)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines.extend(['return result;}','}'])
    (destination or ROOT/'Source/CurrencyRecruitDetailUiPrograms.h').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'recruitDetailCurrencyMethods':1,'nativeRegisterFramePreserved':True,'sourceAmountsUnchanged':True}))


if __name__=='__main__':generate()
