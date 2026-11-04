"""Assemble the read-only Notes view in the native recruit profile.

Only custom instructions and hashes are emitted. Original game method bodies
are verified and copied at runtime; no extracted AST is shipped in the DLL.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import struct
import sys


@dataclass
class Program:
    code: bytes
    literals: list
    references: list


class Assembler:
    def __init__(self):
        self.code = bytearray()
        self.literals, self.references, self.branches = [], [], []
        self.labels = {}

    def raw(self, *values): self.code.extend(values)
    def reg(self, n): self.raw(0xB9, n)
    def align(self):
        while len(self.code) % 8: self.raw(0)
    def string(self, value):
        self.raw(0xA1); self.align()
        self.literals.append((len(self.code), value)); self.code.extend(bytes(8))
    def number(self, n):
        if n in (0, 1): self.raw(0x59+n)
        elif -128 <= n < 128: self.raw(0xB5); self.code.extend(struct.pack('<b', n))
        else: self.raw(0xB6); self.code.extend(struct.pack('<h', n))
    def member(self, name): self.string(name); self.raw(0x4E)
    def store(self, n):
        self.raw(0x87); self.align(); self.code.extend(struct.pack('<I', n)); self.raw(0x17)
    def branch(self, name, op=0x9D):
        self.raw(op); self.align(); self.branches.append((len(self.code), name)); self.code.extend(bytes(4))
    def label(self, name): self.labels[name] = len(self.code)
    def global_object(self, *parts):
        self.string(parts[0]); self.raw(0x1C)
        for part in parts[1:]: self.member(part)
    def call(self, method): self.string(method); self.raw(0x52, 0x17)
    def ret(self): self.raw(0x76, 0x3E)
    def missing(self, reg, label):
        self.raw(0x76); self.reg(reg); self.raw(0x49); self.branch(label)
    def set_value(self, value):
        if isinstance(value, bool): self.raw(0x73 if value else 0x74)
        elif isinstance(value, int): self.number(value)
        else: self.string(value)
    def set_field(self, reg, name, value):
        self.reg(reg); self.string(name); self.set_value(value); self.raw(0x4F)
    def empty_object(self, reg): self.number(0); self.raw(0x43); self.store(reg)
    def notes_flag(self): self.global_object('cafe', 'DynastyEnhancerRecruitNotesSelected')
    def pad_code(self):
        # Align executable code with balanced operations, never ActionEnd bytes.
        n = (-len(self.code)) % 8
        if n == 1: n = 9
        if n % 2: self.raw(0x59, 0x50, 0x17); n -= 3
        for _ in range(n//2): self.raw(0x76, 0x17)
    def finish(self):
        for at, label in self.branches: struct.pack_into('<i', self.code, at, self.labels[label]-at-4)
        return Program(bytes(self.code), self.literals, self.references)


HIDDEN = ('mcCircularBar', 'mcBarIcon', 'mcScoutBtn', 'mcTotalHours',
          'mcAttributesTitle', 'mcAbilitiesTitle', 'mcMentalsTitle',
          'mcDevelopmentTitle', 'mcDevelopmentDesc', 'mcDevTrait', 'mcList',
          'mcLineMid', 'mcLineLeft', 'mcLineRight')
ALL = HIDDEN + ('mcTitle', 'mcDescription')


def append_tab(a):
    # The native method's register 1 contains the three-element return array.
    # The navigation builder assigns a fresh screen-layer key to every row.
    # Native tabs cache their widths before the board replaces the Scouting
    # label with its percentage. Reserve its longest label before adding Notes.
    a.reg(1); a.number(2); a.raw(0x4E); a.store(8)
    a.reg(8); a.string('display'); a.reg(8); a.member('display'); a.string(' (100%)'); a.raw(0x47, 0x4F)
    a.empty_object(0)
    a.set_field(0, 'display', 'Notes')
    a.set_field(0, 'DENotes', True)
    a.set_field(0, 'isDefault', False)
    a.reg(0); a.string('StateMachineKey')
    a.global_object('shared_enum_career', 'recruitinghub', 'StateMachine', 'STATE_SCOUTING_TAB'); a.raw(0x4F)
    a.reg(0); a.string('ScreenKey')
    a.global_object('shared_enum_career', 'recruitinghub', 'ScreenKey', 'SUBSCREEN_RECRUITINGHUB_BOARD_SCOUTING'); a.raw(0x4F)
    a.reg(0); a.number(1); a.reg(1); a.call('push')
    a.reg(1); a.raw(0x3E)


def category_changed(a):
    a.reg(2); a.member('Data'); a.store(3)
    a.reg(3); a.member('WidgetData'); a.member('ExtraInfo'); a.store(4)
    a.global_object('cafe'); a.string('DynastyEnhancerRecruitNotesSelected')
    a.reg(4); a.member('DENotes'); a.raw(0x73, 0x66, 0x4F)
    a.reg(1); a.string('mCurrentTabIndex'); a.reg(3); a.member('Index'); a.raw(0x4F)
    a.reg(4); a.member('StateMachineKey'); a.store(5)
    a.number(0); a.reg(1); a.member('mRecruitingBoardService'); a.member('mStateMachine'); a.string('GetCurrentStateKey'); a.raw(0x52)
    a.reg(5); a.raw(0x66); a.branch('change_state', 0xB8)
    # Notes and Scouting intentionally share the read-only/presentation donor
    # state. Do not acquire an input lock waiting for a no-op state transition.
    a.ret()
    a.label('change_state')
    a.global_object('logic_cfm', 'service', 'RecruitingBoardServiceImpl', 'INPUT_LOCK_TAB')
    a.number(1)
    a.reg(1); a.member('mParentNode'); a.number(1)
    a.global_object('cafe', 'manager', 'InputLockManagerService'); a.string('Get'); a.raw(0x52)
    a.call('LockInput')
    a.reg(5); a.number(1); a.reg(1); a.member('mRecruitingBoardService'); a.call('TransitionToState')
    a.ret()


def description_style(a, width, color):
    a.empty_object(7); a.set_field(7, 'resizeWidth', width)
    a.reg(7); a.string('fontColor'); a.global_object('art_styleguide', 'Color', color); a.raw(0x4F)
    a.reg(7); a.number(1); a.reg(4); a.member('mcDescription'); a.call('SetExtraInfo')


def clear_refresh(a):
    a.string('DynastyEnhancerRecruitNotesRefresh'); a.number(1)
    a.reg(1); a.number(1); a.global_object('cafe', 'manager', 'IntervalManagerService'); a.string('Get'); a.raw(0x52)
    a.call('ClearDelay')


def refresh_if_loading(a):
    # The native flag setter produces 0/1. Only a loading report schedules a
    # bounded retry; settled reports have no polling timer.
    a.reg(3); a.member('DENotesLoading'); a.number(1); a.raw(0x49); a.branch('not_loading',0xB8)
    a.reg(1); a.member('mDENotesRetries'); a.store(6); a.reg(6); a.raw(0x76,0x49); a.branch('have_retries',0xB8)
    a.number(0); a.store(6); a.label('have_retries')
    a.reg(6); a.number(20); a.raw(0x48); a.branch('done',0xB8)
    a.reg(1); a.string('mDENotesRetries'); a.reg(6); a.raw(0x50,0x4F)
    clear_refresh(a)
    a.raw(0x76); a.number(500)
    a.reg(1); a.member('_PopulateData'); a.reg(1); a.number(2)
    a.global_object('cafe','utility','Delegate'); a.string('Create'); a.raw(0x52)
    a.string('DynastyEnhancerRecruitNotesRefresh'); a.number(4)
    a.reg(1); a.number(1); a.global_object('cafe','manager','IntervalManagerService'); a.string('Get'); a.raw(0x52)
    a.call('SetDelay'); a.ret()
    a.label('not_loading'); clear_refresh(a); a.set_field(1,'mDENotesRetries',0)


def draw_notes(a):
    a.reg(1); a.member('mView'); a.store(4); a.missing(4, 'done')
    a.reg(4); a.member('mcDescription'); a.store(6); a.missing(6, 'done')
    # GetActiveRecruit returns a RecordId, not the recruit object. Match it in
    # the same native response used by Scouting, retaining our DENotesBody.
    a.number(0); a.reg(1); a.member('mRecruitingBoardService'); a.string('GetActiveRecruit'); a.raw(0x52); a.store(8)
    a.number(0); a.reg(1); a.member('mRecruitingBoardAdapter'); a.string('GetTeamRecruitList'); a.raw(0x52); a.store(9)
    a.missing(9, 'done')
    a.string('RecordId'); a.reg(8); a.reg(9); a.number(3)
    a.global_object('cafe', 'utility', 'ArrayUtil'); a.string('Search'); a.raw(0x52); a.store(0)
    a.reg(0); a.global_object('cafe', 'utility', 'ArrayUtil', 'SEARCH_FAIL'); a.raw(0x49); a.branch('found_recruit', 0xB8)
    a.empty_object(3); a.branch('recruit_ready', 0x99)
    a.label('found_recruit'); a.reg(9); a.reg(0); a.raw(0x4E); a.store(3)
    a.label('recruit_ready')
    a.reg(1); a.string('mCurrentRecruit'); a.reg(3); a.raw(0x4F)
    a.reg(4); a.member('mDENotesSaved'); a.raw(0x76, 0x49); a.branch('hide_widgets', 0xB8)
    a.empty_object(5)
    for index, name in enumerate(ALL):
        a.reg(4); a.member(name); a.store(6); a.missing(6, f'capture_skip{index}')
        a.reg(5); a.string(name); a.reg(6); a.member('_visible'); a.raw(0x4F)
        if name in ('mcTitle', 'mcDescription'):
            for axis in ('_x', '_y'):
                a.reg(5); a.string(name+axis); a.reg(6); a.member(axis); a.raw(0x4F)
        a.label(f'capture_skip{index}')
    a.reg(4); a.string('mDENotesSaved'); a.reg(5); a.raw(0x4F)
    a.label('hide_widgets')
    for index, name in enumerate(HIDDEN):
        a.reg(4); a.member(name); a.store(6); a.missing(6, f'hide_skip{index}')
        a.set_field(6, '_visible', False)
        if name == 'mcScoutBtn': a.number(0); a.reg(6); a.call('Unfocus')
        a.label(f'hide_skip{index}')
    # These native widgets use stage coordinates, not coordinates relative to
    # their visible panel. Anchor to their original positions and lift them
    # into the now-empty body, preserving the game's resolution/safe-zone work.
    for name, lift in [('mcTitle', 140), ('mcDescription', 154)]:
        a.reg(4); a.member(name); a.store(6)
        for axis in ('_x', '_y'):
            a.reg(6); a.string(axis); a.reg(4); a.member('mDENotesSaved'); a.member(name+axis)
            if axis=='_y': a.number(lift); a.raw(0x0B)
            a.raw(0x4F)
        a.set_field(6, '_visible', True)
    a.string('Recruit Notes'); a.number(1); a.reg(4); a.member('mcTitle'); a.call('SetLabel')
    description_style(a, 1180, 'PRIMARY_LIGHT_COLOR')
    a.reg(3); a.member('DENotesBody'); a.store(6)
    a.reg(6); a.raw(0x76, 0x49); a.branch('have_text', 0xB8)
    a.string('The staff is gathering the first background and film notes on this prospect.'); a.store(6)
    a.label('have_text')
    a.reg(6); a.number(1); a.reg(4); a.member('mcDescription'); a.call('SetLabel')
    refresh_if_loading(a)
    a.label('done'); a.ret()


def restore_layout(a):
    clear_refresh(a); a.set_field(1,'mDENotesRetries',0)
    a.reg(1); a.member('mView'); a.store(4); a.missing(4, 'native')
    a.reg(4); a.member('mDENotesSaved'); a.store(5); a.missing(5, 'native')
    for index, name in enumerate(ALL):
        a.reg(4); a.member(name); a.store(6); a.missing(6, f'restore_skip{index}')
        a.reg(6); a.string('_visible'); a.reg(5); a.member(name); a.raw(0x4F)
        if name in ('mcTitle', 'mcDescription'):
            for axis in ('_x', '_y'):
                a.reg(6); a.string(axis); a.reg(5); a.member(name+axis); a.raw(0x4F)
        a.label(f'restore_skip{index}')
    description_style(a, 256, 'UNFOCUS_FONT_COLOR')
    for widget, key in [('mcTitle', 'SCOUT'), ('mcDescription', 'SCOUT_DESCRIPTION')]:
        a.global_object('loc', 'career', 'Recruiting', key); a.number(1); a.reg(4); a.member(widget); a.call('SetLabel')
    a.reg(4); a.string('mDENotesSaved'); a.raw(0x76, 0x4F)


def fnv(data):
    n=14695981039346656037
    for b in data: n=((n^b)*1099511628211)&0xffffffffffffffff
    return n


def generate_header(destination, evidence):
    root=Path(__file__).resolve().parents[1]
    methods=json.loads((evidence/'notes-methods.json').read_text(encoding='utf8'))+json.loads((evidence/'notes-navigation.json').read_text(encoding='utf8'))
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    apt=load(evidence/'Assets/common__ui__node_cfm__recruitinghub__corenode.ast')
    specs=[('Navigation.', 'GetSubscreenDataAtBoardLevel', 'tabs'),('recruitinghub.Board.', 'Init', 'reset'),('recruitinghub.Board.', '_OnCategoryChanged', 'category'),('board.Scouting.', '_PopulateData', 'draw'),('board.Scouting.', '_InitializeFocus', 'guard'),('board.Scouting.', '_UpdateScoutButton', 'guard'),('board.Scouting.', '_OnScout', 'guard'),('board.Scouting.', '_OnRecruitUpdated', 'refresh'),('board.Scouting.','ModelHidden','cancel'),('board.Scouting.','Shutdown','cancel')]
    programs=[];report=[]
    for cls,name,mode in specs:
        item=next(x for x in methods if cls in x.get('class',x.get('cls','')) and x['method']==name)
        _,argc,registers,body,size=item['definition'];offset=int(body,16);original=apt.data[offset:offset+size]
        a=Assembler();copy_at=0;copy_size=0
        if mode=='tabs':
            assert original[-3:]==bytes.fromhex('b9013e')
            copy_size=size-3;a.code.extend(bytes(copy_size));append_tab(a)
        elif mode=='category':category_changed(a)
        elif mode=='cancel':
            clear_refresh(a);a.set_field(1,'mDENotesRetries',0);a.pad_code();copy_at=len(a.code);copy_size=size;a.code.extend(bytes(size))
        elif mode=='reset':
            a.global_object('cafe');a.string('DynastyEnhancerRecruitNotesSelected');a.raw(0x74,0x4F);a.pad_code()
            copy_at=len(a.code);copy_size=size;a.code.extend(bytes(size))
        else:
            a.notes_flag();a.raw(0x73,0x66);a.branch('normal',0xB8)
            if mode=='draw':draw_notes(a)
            elif mode=='refresh':a.number(0);a.reg(1);a.call('_PopulateData');a.ret()
            else:a.ret()
            a.label('normal')
            if mode=='draw':restore_layout(a)
            a.label('native');a.pad_code();copy_at=len(a.code);copy_size=size;a.code.extend(bytes(size))
        p=a.finish();newregs=max(registers[0],10)
        programs.append((offset-0x30,argc,registers[0],registers[1],size,fnv(original),newregs,copy_at,copy_size,p))
        report.append(dict(name=cls+name,definition=offset-0x30,argc=argc,registers=registers[0],flags=registers[1],size=size,hash=fnv(original),customBytes=len(p.code),copyAt=copy_at,copyBytes=copy_size))
    lines=['// Generated by Tools/build_recruit_notes_ui.py; custom bytecode only.','#pragma once','#include <vector>','#include <cstdint>','#include <cstring>','namespace recruitingfog::notesui {','struct Program {uintptr_t offset;unsigned argc,registers,flags,size;uint64_t hash;unsigned newRegisters,copyAt,copyBytes;std::vector<unsigned char> code;};','inline std::vector<Program> programs(){std::vector<Program> result;']
    for offset,argc,regs,flags,size,hash_,newregs,copy_at,copy_size,p in programs:
        array='{'+','.join(hex(b) for b in p.code)+'}'
        lines.append(f'result.push_back({{{offset},{argc},{regs},{flags},{size},{hash_}ull,{newregs},{copy_at},{copy_size},{array}}});')
        for at,text in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}']
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    (evidence/'notes-programs.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps({'programs':len(programs),'customBytes':sum(len(x[-1].code) for x in programs),'header':str(destination)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--header',type=Path,default=Path('Source/RecruitNotesUiPrograms.h'))
    parser.add_argument('--evidence',type=Path,default=Path('Evidence/RecruitingFog'))
    args=parser.parse_args();generate_header(args.header,args.evidence)
