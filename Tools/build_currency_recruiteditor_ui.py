"""ScholarshipToggle's plain value label, with native numeric editing retained."""
from pathlib import Path
import json,struct,sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path
from build_currency_ui import money

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'Evidence/PlayerFog/Gaps/current-cfm-currency.ast'
STATE='mDECurrencyRecruitEditor'
SPECS=[('Draw',0x7f540,0,4,25,390,0xa3d02aead352a9d8),
       ('_AddCurrentValue',0x7fcb0,1,3,41,96,0x3df176f9cdf7ad5a),
       ('_SetCurrentValueToMax',0x7fdd8,0,2,41,36,0xcec9e00239ebad5a),
       ('_SetCurrentValueToMin',0x7fe38,0,2,41,36,0x864cc49684a5c545),
       ('_SetCurrentValueToDefault',0x7fe98,0,2,41,39,0x20f40259dbb99d88)]

class FixedFrameAssembler(Assembler):
    def __init__(self,registers):super().__init__();self.native_registers=registers
    def reg(self,n):
        if n<self.native_registers:super().reg(n)
        else:self.string('_DERecruitEditorLocal'+str(n));self.raw(0x1c)
    def store(self,n):
        if n<self.native_registers:super().store(n)
        else:self.string('_DERecruitEditorLocal'+str(n));self.raw(0x4d,0x3c)

def field(a,obj,name,value):a.reg(obj);a.string(name);a.reg(value);a.raw(0x4f)

def call_label(a,label):a.reg(label);a.number(1);a.reg(4);a.call('SetLabel')

def current_style(a,name):path(a,4,'mData','ExtraInfo',name)

def restore_fit(a,prefix):
    # Only undo fields that still equal this adapter's applied values. Native
    # focus/style updates and unrelated font/color fields must survive.
    a.missing(5,prefix+'Done');path(a,5,'fit');a.raw(0x73,0x66);a.branch(prefix+'Done',0xb8)
    a.empty_object(8);a.number(0);a.store(9)
    for name,saved in [('resize','beforeResize'),('resizeWidth','beforeWidth'),('maxNumLines','beforeLines')]:
        skip=prefix+name
        current_style(a,name)
        if name=='resize':a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN')
        elif name=='resizeWidth':path(a,5,'bound')
        else:a.number(1)
        a.raw(0x66);a.branch(skip,0xb8)
        a.reg(8);a.string(name);path(a,5,saved);a.raw(0x4f)
        a.reg(9);a.raw(0x50);a.store(9);a.label(skip)
    a.reg(9);a.number(0);a.raw(0x67);a.branch(prefix+'Done',0xb8)
    a.reg(8);a.number(1);a.reg(4);a.call('SetExtraInfo')
    a.label(prefix+'Done')

def geometry(a):
    # Native SetWidth positions the field inside mcBackground. Bound the text
    # to its existing right edge; never move/widen the control, icon or arrows.
    a.raw(0x76);a.store(6)
    path(a,1,'mcBackground');a.store(7);a.missing(7,'geometryDone')
    for obj,names,minimum,maximum in [(7,('_x',),-16384,16384),(7,('_width',),1,4096),
                                        (4,('_x',),-16384,16384),(1,('SPACING_OFFSET',),0,256)]:
        path(a,obj,*names);a.raw(0x44);a.string('number');a.raw(0x66);a.branch('geometryDone',0xb8)
        path(a,obj,*names);a.number(minimum);a.raw(0x48);a.branch('geometryDone')
        path(a,obj,*names);a.number(maximum);a.raw(0x48);a.branch('geometryDone',0xb8)
    path(a,7,'_x');path(a,7,'_width');a.raw(0x47);path(a,4,'_x');a.raw(0x0b)
    path(a,1,'SPACING_OFFSET');a.raw(0x0b);a.store(7)
    a.reg(7);a.number(1);a.raw(0x67);a.branch('geometryDone',0xb8)
    a.reg(7);a.number(4096);a.raw(0x48);a.branch('geometryDone',0xb8)
    a.reg(7);a.store(6);a.label('geometryDone')

def fit_matches(a,failed):
    path(a,5,'fit');a.raw(0x73,0x66);a.branch(failed,0xb8)
    path(a,5,'bound');a.reg(6);a.raw(0x66);a.branch(failed,0xb8)
    for name in ['resize','resizeWidth','maxNumLines']:
        current_style(a,name)
        if name=='resize':a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN')
        elif name=='resizeWidth':a.reg(6)
        else:a.number(1)
        a.raw(0x66);a.branch(failed,0xb8)

def suffix(a):
    path(a,1,'mcValue');a.store(4);a.missing(4,'done')
    for names in [('mData',),('mData','ExtraInfo')]:
        path(a,4,*names);a.raw(0x76,0x49);a.branch('done')
    path(a,1,STATE);a.store(5);a.missing(5,'noState')
    path(a,5,'child');a.reg(4);a.raw(0x66);a.branch('noState',0xb8)
    a.branch('stateReady',0x99)
    a.label('noState');a.raw(0x76);a.store(5)
    a.label('stateReady');a.dollars_enabled();a.number(1);a.raw(0x66);a.branch('enabled')
    a.missing(5,'done')
    path(a,4,'mData','display');path(a,5,'display');a.raw(0x66);a.branch('offFit',0xb8)
    path(a,1,'mValue');a.raw(0x4b);a.store(2)
    path(a,4,'mData','display');a.reg(2);a.raw(0x66);a.branch('offFit')
    call_label(a,2)
    a.label('offFit');restore_fit(a,'offRestore')
    a.reg(1);a.string(STATE);a.raw(0x76,0x4f);a.branch('done',0x99)
    a.label('enabled');geometry(a)
    # Unchanged callbacks do no formatting/setter/style allocation. The native
    # body may reset the numeric label on an actual change, which fails this.
    a.missing(5,'format')
    path(a,5,'value');path(a,1,'mValue');a.raw(0x66);a.branch('format',0xb8)
    path(a,5,'display');path(a,4,'mData','display');a.raw(0x66);a.branch('format',0xb8)
    path(a,5,'bound');a.reg(6);a.raw(0x66);a.branch('format',0xb8)
    a.reg(6);a.raw(0x76,0x49);a.branch('done')
    fit_matches(a,'format');a.branch('done',0x99)
    a.label('format');path(a,1,'mValue');a.store(0);money(a,'done','recruitEditorMoney');a.reg(2);a.store(10)
    path(a,4,'mData','display');a.reg(10);a.raw(0x66);a.branch('labelReady')
    call_label(a,10);a.label('labelReady')
    a.missing(5,'newState')
    a.reg(6);a.raw(0x76,0x49);a.branch('reuseNoFit')
    fit_matches(a,'newState');a.branch('cache',0x99)
    a.label('reuseNoFit');path(a,5,'fit');a.raw(0x73,0x66);a.branch('newState')
    a.branch('cache',0x99)
    a.label('newState');restore_fit(a,'onRestore');a.empty_object(5)
    field(a,5,'child',4);a.set_field(5,'fit',False)
    a.reg(6);a.raw(0x76,0x49);a.branch('cache')
    for name,saved in [('resize','beforeResize'),('resizeWidth','beforeWidth'),('maxNumLines','beforeLines')]:
        a.reg(5);a.string(saved);current_style(a,name);a.raw(0x4f)
    a.empty_object(8);a.reg(8);a.string('resize');a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN');a.raw(0x4f)
    field(a,8,'resizeWidth',6);a.set_field(8,'maxNumLines',1)
    a.reg(8);a.number(1);a.reg(4);a.call('SetExtraInfo');a.set_field(5,'fit',True)
    a.label('cache');a.reg(5);a.string('value');path(a,1,'mValue');a.raw(0x4f)
    field(a,5,'display',10);field(a,5,'bound',6);field(a,1,STATE,5)
    a.label('done');a.ret()

def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools');from inspect_tb_ast import load
    apt=load(ASSET);class_items=apt.decode(0x7ea98)
    assert class_items[0][2][4]=='ScholarshipToggle'
    lines=['// Specialized ScholarshipToggle currency labels; native numeric editor retained.','#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::currencyrecruiteditorui {','inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;']
    for name,offset,argc,registers,flags,size,expected in SPECS:
        definitions=[i for i,item in enumerate(class_items) if len(item)>3 and item[2][3]==hex(offset+48)]
        assert len(definitions)==1 and class_items[definitions[0]-1][2][1]==name
        h=apt.data[offset:offset+48];original=apt.data[offset+48:offset+48+size]
        assert struct.unpack_from('<IHH',h,8)==(argc,registers,flags) and struct.unpack_from('<I',h,24)[0]==size and fnv(original)==expected
        for at in range(0,size-47,8):assert not (struct.unpack_from('<I',original,at+32)[0]==0x98765432 and struct.unpack_from('<Q',original,at+40)[0]==0x12345678)
        a=FixedFrameAssembler(registers);a.code.extend(bytes(size));suffix(a);p=a.finish();assert len(p.code)<32768
        code='{'+','.join(hex(v) for v in p.code)+'}'
        lines.append(f'// {name}\nresult.push_back({{{offset},{argc},{registers},{flags},{size},{expected}ull,{registers},0,{size},{code}}});')
        for at in p.dollar_offsets:lines.append(f'result.back().dollarOffsets.push_back({at});')
        for at,literal in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(literal)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}'];destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'recruitEditorCallbacks':len(SPECS),'nativeFramesPreserved':True,'numericEditingUnchanged':True}))

if __name__=='__main__':generate(ROOT/'Source/CurrencyRecruitEditorUiPrograms.h')
