"""Assemble a scoped News.Init body; never reads/writes a running process.

The result needs a verified runtime function-body owner before it can be used.
It is deliberately not an in-place patch of the 91-byte original function.
"""
from dataclasses import dataclass, field
from pathlib import Path
import argparse
import json
import struct

# Exact supported-game gates captured independently from the live definitions.
ORIGINAL_INIT = bytes.fromhex('5959b904a20b52a20c52870000000000030000001776b90349b800000000000009000000594387000300000017b903a20dad040e0f10114fb9035a59b904a20b52b212b905b904b906b503b902b20ab901a213744fb901a214744f')
ORIGINAL_SHUTDOWN = bytes.fromhex('b901af14b800000031000000b901af23ad03161c1d4eb901af244e8700000000030000001759b903b22559b903b2227687000000000000000300000017b9045ab902b222')


@dataclass
class Program:
    code: bytes
    literals: list[tuple[int, str]]
    references: list[tuple[int, str]] = field(default_factory=list)


class Assembler:
    def __init__(self):
        self.code = bytearray()
        self.literals = []
        self.labels = {}
        self.branches = []
        self.references = []

    def raw(self, *values):
        self.code.extend(values)

    def align(self):
        while len(self.code) % 8:
            self.raw(0)

    def reg(self, value):
        self.raw(0xB9, value)

    def idx(self, value):
        self.raw(0xA2, value)

    def string(self, value):
        self.raw(0xA1)
        self.align()
        self.literals.append((len(self.code), value))
        self.code.extend(bytes(8))

    def member(self, value):
        self.string(value)
        self.raw(0x4E)

    def store(self, value):
        self.raw(0x87)
        self.align()
        self.code.extend(struct.pack('<I', value))
        self.raw(0x17)

    def branch(self, label, opcode):
        self.raw(opcode)
        self.align()
        self.branches.append((len(self.code), label))
        self.code.extend(bytes(4))

    def label(self, name):
        self.labels[name] = len(self.code)

    def set_field(self, reg, key, value):
        self.reg(reg)
        self.string(key)
        if isinstance(value, bool):
            self.raw(0x73 if value else 0x74)
        else:
            self.string(value)
        self.raw(0x4F)

    def function(self, program, *, argc=0, registers=2):
        if argc not in (0, 1):
            raise ValueError('Only the verified zero/one argument nested layouts are used')
        self.raw(0x8E)
        self.align()
        header = len(self.code)
        self.code.extend(bytes(48))
        self.literals.append((header, ''))
        struct.pack_into('<IHH', self.code, header + 8, argc, registers, 0x29)
        if argc:
            self.references.append((header + 16, 'focusParameters'))
        struct.pack_into('<I', self.code, header + 24, len(program.code))
        struct.pack_into('<I', self.code, header + 32, 0x98765432)
        struct.pack_into('<Q', self.code, header + 40, 0x12345678)
        body = len(self.code)
        self.code.extend(program.code)
        self.literals.extend((body + at, value) for at, value in program.literals)
        self.references.extend((body + at, value) for at, value in program.references)

    def header_facade(self):
        # Keep the shared hub header out of the embedded News view's ownership.
        self.reg(4)
        self.string('mDynastySocialRealHeader')
        self.number(0)
        self.reg(4)
        self.string('GetHeader')
        self.raw(0x52, 0x4F)
        self.set_field(4, 'mHideHeaderOnTransitionOut', False)
        self.number(0)
        self.raw(0x43)
        self.store(0)
        for name in ('SetState', 'SetTitle', 'Show', 'Hide'):
            self.reg(0)
            self.string(name)
            self.reg(1)
            self.member('_OnServiceTileFocusChanged')
            self.raw(0x4F)
        empty = Assembler()
        empty.string('')
        empty.raw(0x3E)
        self.reg(0)
        self.string('GetValidDisplayString')
        self.function(empty.finish())
        self.raw(0x4F)
        self.reg(4)
        self.string('mDynastySocialHeaderProxy')
        self.reg(0)
        self.raw(0x4F)
        getter = Assembler()
        getter.reg(1)
        getter.member('mDynastySocialHeaderProxy')
        getter.raw(0x3E)
        self.reg(4)
        self.string('GetHeader')
        self.function(getter.finish())
        self.raw(0x4F)

    def missing(self, register, label):
        self.raw(0x76)
        self.reg(register)
        self.raw(0x49)
        self.branch(label, 0x9D)

    def increment(self, register):
        self.reg(register)
        self.number(1)
        self.raw(0x47)
        self.store(register)

    def context_service(self, *names):
        self.reg(1)
        self.member('mDynastySocialContext')
        self.number(1)
        self.global_object(*names)
        self.string('Get')
        self.raw(0x52)

    def view_method(self, name, program, *, argc=0, registers=8):
        self.reg(4)
        self.string(name)
        self.function(program, argc=argc, registers=registers)
        self.raw(0x4F)

    def call_self(self, method):
        self.number(0)
        self.reg(1)
        self.call(method, 0)

    def presentation(self):
        self.set_field(4, 'mDynastySocialAlive', True)
        self.reg(4)
        self.string('mDynastySocialContext')
        self.reg(6)
        self.raw(0x4F)
        # PanelData.mMovie is populated before SubScreenPanel.SetData, which
        # supplies that PanelData to the child's initialization parameters.
        self.reg(3)
        self.member('Panel')
        self.store(0)
        self.missing(0, 'no_outer')
        self.reg(0)
        self.member('mId')
        self.string('CM_DYNASTY_SOCIAL')
        self.raw(0x66)
        self.branch('no_outer', 0xB8)
        self.reg(4)
        self.string('mDynastySocialOuter')
        self.reg(0)
        self.member('mMovie')
        self.raw(0x4F)
        self.label('no_outer')
        for name in ('Focus', 'Unfocus'):
            self.reg(4)
            self.string('mDynastySocialOriginal' + name)
            self.reg(4)
            self.member(name)
            self.raw(0x4F)
        for name, program in (
                ('mDynastySocialAlignMount', align_mount()),
                ('mDynastySocialHidePreview', hide_preview()),
                ('mDynastySocialRestorePreview', restore_preview()),
                ('mDynastySocialTick', presentation_tick())):
            self.view_method(name, program)
        for name in ('Focus', 'Unfocus'):
            self.view_method(name, focus_wrapper(name), argc=1)

    def number(self, value):
        if value in (0, 1):
            self.raw(0x59 + value)
        elif -128 <= value < 128:
            self.raw(0xB5)
            self.code.extend(struct.pack('<b', value))
        elif -32768 <= value < 32768:
            self.raw(0xB6)
            self.code.extend(struct.pack('<h', value))
        else:
            self.raw(0xB7)
            self.code.extend(struct.pack('<i', value))

    def global_object(self, *names):
        self.string(names[0])
        self.raw(0x1C)
        for name in names[1:]:
            self.member(name)

    def call(self, name, count):
        # Arguments and receiver are already on the stack, with count below
        # the receiver, matching native CallMethod. Discard its return value.
        self.string(name)
        self.raw(0x52, 0x17)

    def adapter(self):
        self.number(0)
        self.global_object('madden', 'Adapters')
        self.string('GetPanelMenuAdapter')
        self.raw(0x52)

    def signal(self, kind):
        self.number(0)
        self.string(kind)
        self.string('CM_DYNASTY_SOCIAL_FEED')
        self.number(3)
        self.adapter()
        self.call('SetFilterChanged', 3)

    def intervals(self):
        self.reg(1)
        self.member('mParentNode')
        self.number(1)
        self.global_object('cafe', 'manager', 'IntervalManagerService')
        self.string('Get')
        self.raw(0x52)

    def clear_timer(self):
        self.reg(1)
        self.member('mDynastySocialTimerName')
        self.number(1)
        self.intervals()
        self.call('ClearInterval', 1)

    def start_timer(self):
        self.clear_timer()
        self.number(250)
        self.reg(1)
        self.member('mView')
        self.member('mDynastySocialTick')
        self.reg(1)
        self.member('mView')
        self.number(2)
        self.global_object('cafe', 'utility', 'Delegate')
        self.string('Create')
        self.raw(0x52)
        self.reg(1)
        self.member('mDynastySocialTimerName')
        self.number(3)
        self.intervals()
        self.call('SetInterval', 3)

    def timer_name(self):
        self.global_object('cafe')
        self.member('DynastyEnhancerSocialTimerSerial')
        self.store(0)
        self.raw(0x76)
        self.reg(0)
        self.raw(0x49)
        self.branch('have_serial', 0xB8)
        self.number(0)
        self.store(0)
        self.label('have_serial')
        self.reg(0)
        self.number(1)
        self.raw(0x47)
        self.store(0)
        self.global_object('cafe')
        self.string('DynastyEnhancerSocialTimerSerial')
        self.reg(0)
        self.raw(0x4F)
        self.reg(1)
        self.string('mDynastySocialTimerName')
        self.string('DYNASTY_SOCIAL_SYNC_')
        self.reg(0)
        self.raw(0x47, 0x4F)

    def finish(self):
        for at, label in self.branches:
            struct.pack_into('<i', self.code, at, self.labels[label] - at - 4)
        return Program(bytes(self.code), self.literals, self.references)


def align_mount():
    a = Assembler()
    a.reg(1)
    a.member('mDynastySocialRealHeader')
    a.store(3)
    a.missing(3, 'done')
    a.reg(3)
    a.member('mcTabs')
    a.store(3)
    a.missing(3, 'done')
    a.reg(1)
    a.member('mDynastySocialOuter')
    a.store(4)
    a.missing(4, 'done')
    a.reg(4)
    a.member('mcMount')
    a.store(6)
    a.missing(6, 'done')
    a.reg(6)
    a.member('_parent')
    a.store(5)
    a.missing(5, 'done')
    a.number(0)
    a.raw(0x43)
    a.store(0)
    a.reg(0)
    a.string('x')
    a.number(0)
    a.raw(0x4F)
    a.number(0)
    a.reg(3)
    a.string('GetHeight')
    a.raw(0x52)
    a.store(7)
    a.reg(7)
    a.number(0)
    a.raw(0x67)
    a.branch('done', 0xB8)
    a.reg(0)
    a.string('y')
    a.reg(7)
    a.raw(0x4F)
    a.reg(0)
    a.number(1)
    a.reg(3)
    a.call('localToGlobal', 1)
    a.number(0)
    a.raw(0x43)
    a.store(2)
    a.reg(2)
    a.string('x')
    a.reg(6)
    a.member('_x')
    a.raw(0x4F)
    a.reg(2)
    a.string('y')
    a.number(0)
    a.raw(0x4F)
    a.reg(2)
    a.number(1)
    a.reg(5)
    a.call('localToGlobal', 1)
    a.reg(0)
    a.string('x')
    a.reg(2)
    a.member('x')
    a.raw(0x4F)
    a.reg(0)
    a.string('y')
    a.reg(0)
    a.member('y')
    a.number(16)
    a.raw(0x47, 0x4F)
    a.reg(0)
    a.member('y')
    a.reg(2)
    a.member('y')
    a.raw(0x48)
    a.branch('body_floor_ready', 0xB8)
    a.reg(0)
    a.string('y')
    a.reg(2)
    a.member('y')
    a.raw(0x4F)
    a.label('body_floor_ready')
    a.reg(0)
    a.number(1)
    a.reg(5)
    a.call('globalToLocal', 1)
    for field_name in ('x', 'y'):
        for limit, operation in ((-32768, 0x67), (32767, 0x48)):
            a.reg(0)
            a.member(field_name)
            a.number(limit)
            a.raw(operation)
            a.branch('done', 0xB8)
    a.reg(0)
    a.member('y')
    a.number(138)
    a.raw(0x0B)
    a.reg(0)
    a.member('x')
    a.number(2)
    a.reg(4)
    a.call('SetScreenMountPosition', 2)
    a.label('done')
    a.raw(0x76, 0x3E)
    return a.finish()


def hide_preview():
    a = Assembler()
    a.reg(1)
    a.member('mDynastySocialSavedPreviews')
    a.store(3)
    a.raw(0x76)
    a.reg(3)
    a.raw(0x49)
    a.branch('have_saved', 0xB8)
    a.number(0)
    a.raw(0x42)
    a.store(3)
    a.reg(1)
    a.string('mDynastySocialSavedPreviews')
    a.reg(3)
    a.raw(0x4F)
    a.label('have_saved')
    a.context_service('logic_cfm', 'service', 'HubInfoPanelsService')
    a.store(4)
    a.missing(4, 'done')
    a.reg(4)
    a.member('mHidePanelHandler')
    a.store(4)
    a.missing(4, 'done')
    a.reg(4)
    a.member('mListeners')
    a.store(4)
    a.missing(4, 'done')
    a.number(0)
    a.store(0)
    a.label('loop')
    for maximum in (16, None):
        a.reg(0)
        if maximum is None:
            a.reg(4)
            a.member('length')
        else:
            a.number(maximum)
        a.raw(0x48)
        a.branch('done', 0xB8)
    a.reg(4)
    a.reg(0)
    a.raw(0x4E)
    a.store(5)
    a.missing(5, 'next')
    a.reg(5)
    a.member('Callback')
    a.store(5)
    a.missing(5, 'next')
    a.reg(5)
    a.member('scope')
    a.store(6)
    a.missing(6, 'next')
    a.global_object('art_screen', 'panel', 'career', 'HubPanelSwitcher')
    a.store(2)
    a.missing(2, 'next')
    a.reg(6)
    a.reg(2)
    a.raw(0x54)
    a.branch('next', 0xB8)
    a.reg(5)
    a.member('func')
    a.reg(6)
    a.member('_HideAllScreens')
    a.raw(0x66)
    a.branch('next', 0xB8)
    a.number(0)
    a.number(0)
    a.reg(6)
    a.string('GetScreenInfo')
    a.raw(0x52)
    a.string('GetHolderMovie')
    a.raw(0x52)
    a.store(6)
    a.missing(6, 'next')
    a.reg(6)
    a.member('_visible')
    a.store(5)
    a.missing(5, 'next')
    a.number(0)
    a.store(7)
    a.label('saved_loop')
    a.reg(7)
    a.reg(3)
    a.member('length')
    a.raw(0x48)
    a.branch('save', 0xB8)
    a.reg(3)
    a.reg(7)
    a.raw(0x4E)
    a.member('holder')
    a.reg(6)
    a.raw(0x66)
    a.branch('hide', 0x9D)
    a.increment(7)
    a.branch('saved_loop', 0x99)
    a.label('save')
    a.reg(3)
    a.member('length')
    a.number(16)
    a.raw(0x48)
    a.branch('next', 0xB8)
    a.reg(6)
    a.member('mDynastySocialHideCount')
    a.store(2)
    a.raw(0x76)
    a.reg(2)
    a.raw(0x49)
    a.branch('have_count', 0xB8)
    a.number(0)
    a.store(2)
    a.label('have_count')
    a.reg(2)
    a.number(0)
    a.raw(0x66)
    a.branch('already_hidden', 0xB8)
    a.reg(6)
    a.string('mDynastySocialOriginalVisible')
    a.reg(6)
    a.member('_visible')
    a.raw(0x4F)
    a.label('already_hidden')
    a.reg(6)
    a.string('mDynastySocialHideCount')
    a.reg(2)
    a.number(1)
    a.raw(0x47, 0x4F)
    a.number(0)
    a.raw(0x43)
    a.store(5)
    for name in ('holder', 'visible'):
        a.reg(5)
        a.string(name)
        a.reg(6)
        if name == 'visible':
            a.member('_visible')
        a.raw(0x4F)
    a.reg(5)
    a.number(1)
    a.reg(3)
    a.call('push', 1)
    a.label('hide')
    a.set_field(6, '_visible', False)
    a.label('next')
    a.increment(0)
    a.branch('loop', 0x99)
    a.label('done')
    a.raw(0x76, 0x3E)
    return a.finish()


def restore_preview():
    a = Assembler()
    a.reg(1)
    a.member('mDynastySocialSavedPreviews')
    a.store(3)
    a.missing(3, 'done')
    a.number(0)
    a.store(0)
    a.label('loop')
    for maximum in (16, None):
        a.reg(0)
        if maximum is None:
            a.reg(3)
            a.member('length')
        else:
            a.number(maximum)
        a.raw(0x48)
        a.branch('clear', 0xB8)
    a.reg(3)
    a.reg(0)
    a.raw(0x4E)
    a.store(4)
    a.missing(4, 'next')
    a.reg(4)
    a.member('holder')
    a.store(5)
    a.missing(5, 'next')
    a.reg(5)
    a.member('mDynastySocialHideCount')
    a.store(2)
    a.missing(2, 'next')
    a.reg(2)
    a.number(0)
    a.raw(0x67)
    a.branch('next', 0xB8)
    a.reg(2)
    a.number(1)
    a.raw(0x0B)
    a.store(2)
    a.reg(5)
    a.string('mDynastySocialHideCount')
    a.reg(2)
    a.raw(0x4F)
    a.reg(2)
    a.number(0)
    a.raw(0x66)
    a.branch('next', 0xB8)
    a.reg(5)
    a.string('_visible')
    a.reg(5)
    a.member('mDynastySocialOriginalVisible')
    a.raw(0x4F)
    a.label('next')
    a.increment(0)
    a.branch('loop', 0x99)
    a.label('clear')
    a.reg(1)
    a.string('mDynastySocialSavedPreviews')
    a.number(0)
    a.raw(0x42, 0x4F)
    a.label('done')
    a.raw(0x76, 0x3E)
    return a.finish()


def focus_wrapper(name):
    a = Assembler()
    if name == 'Unfocus':
        a.call_self('mDynastySocialRestorePreview')
    a.reg(2)
    a.number(1)
    a.reg(1)
    a.call('mDynastySocialOriginal' + name, 1)
    if name == 'Focus':
        a.call_self('mDynastySocialAlignMount')
        a.call_self('mDynastySocialHidePreview')
    a.raw(0x76, 0x3E)
    return a.finish()


def presentation_tick():
    a = Assembler()
    a.reg(1)
    a.member('mDynastySocialAlive')
    a.raw(0x73, 0x66)
    a.branch('done', 0xB8)
    a.number(0)
    a.context_service('panelmenu', 'service', 'PanelMenuDataService')
    a.string('GetCurrentPanelFocus')
    a.raw(0x52)
    a.string('CM_DYNASTY_SOCIAL')
    a.raw(0x66)
    a.branch('inactive', 0xB8)
    a.call_self('mDynastySocialAlignMount')
    a.call_self('mDynastySocialHidePreview')
    a.signal('SOCIAL_SYNC')
    a.branch('done', 0x99)
    a.label('inactive')
    a.call_self('mDynastySocialRestorePreview')
    a.label('done')
    a.raw(0x76, 0x3E)
    return a.finish()


def scoped_init(*, timer=False):
    a = Assembler()
    # Original News.Init register allocation and constant pool are retained.
    # view.GetScreenInfo().GetInitParams() -> r3; undefined -> {}.
    a.raw(0x59, 0x59)
    a.reg(4)
    a.idx(11)
    a.raw(0x52)
    a.idx(12)
    a.raw(0x52)
    a.store(3)
    a.raw(0x76)
    a.reg(3)
    a.raw(0x49)
    a.branch('have_params', 0xB8)
    a.raw(0x59, 0x43)
    a.store(3)
    a.label('have_params')

    # Only the embedded Social Media child changes behavior. Ordinary News
    # keeps its native focus, Back and visibility lifecycle.
    a.reg(3)
    a.member('IsSubscreen')
    a.raw(0x73, 0x66)
    a.branch('native_init', 0xB8)
    a.reg(3)
    a.member('PanelId')
    a.string('CM_DYNASTY_SOCIAL')
    a.raw(0x66)
    a.branch('native_init', 0xB8)

    for reg in (3, 0):
        if reg == 0:
            a.reg(3)
            a.member('BackupState')
            a.store(0)
            a.raw(0x76)
            a.reg(0)
            a.raw(0x49)
            a.branch('no_backup', 0x9D)
        a.set_field(reg, 'PanelId', 'CM_DYNASTY_SOCIAL_FEED')
        a.set_field(reg, 'AllowFocus', False)
        a.set_field(reg, 'AllowBack', False)
    a.label('no_backup')
    # SinglePanel queues _SetMenuVisible on both Init and Shutdown. Replace
    # only this instance's handler with the inherited verified empty method.
    a.reg(1)
    a.string('_SetMenuVisible')
    a.reg(1)
    a.member('_OnServiceTileFocusChanged')
    a.raw(0x4F)
    a.set_field(1, 'mDynastySocialEmbedded', True)
    a.header_facade()
    a.presentation()
    if timer:
        a.timer_name()
    a.signal('SOCIAL_CHILD_ATTACH')

    a.label('native_init')
    a.reg(3)
    a.idx(13)  # MenuInstanceName
    a.raw(0xAD, 4, 14, 15, 16, 17)  # MENU_CAREER
    a.raw(0x4F)
    a.reg(3)
    a.raw(0x5A, 0x59)
    a.reg(4)
    a.idx(11)
    a.raw(0x52, 0xB2, 18)  # SetInitParams
    a.reg(5)
    a.reg(4)
    a.reg(6)
    a.raw(0xB5, 3)
    a.reg(2)
    a.raw(0xB2, 10)  # super.Init
    for field in (19, 20):
        a.reg(1)
        a.idx(field)
        a.raw(0x74, 0x4F)
    if timer:
        a.reg(1)
        a.member('mDynastySocialEmbedded')
        a.raw(0x73, 0x66)
        a.branch('done', 0xB8)
        a.start_timer()
        a.label('done')
    a.raw(0x76, 0x3E)
    return a.finish()


def scoped_shutdown(*, timer=False):
    a = Assembler()
    a.reg(1)
    a.member('mDynastySocialEmbedded')
    a.raw(0x73, 0x66)
    a.branch('native_shutdown', 0xB8)
    if timer:
        a.clear_timer()
    a.reg(1)
    a.member('mView')
    a.store(0)
    a.missing(0, 'native_shutdown')
    a.set_field(0, 'mDynastySocialAlive', False)
    a.number(0)
    a.reg(0)
    a.call('mDynastySocialRestorePreview', 0)
    a.label('native_shutdown')
    a.reg(1)
    a.raw(0xAF, 20)  # mAddedFilter
    a.branch('super_shutdown', 0xB8)
    a.reg(1)
    a.raw(0xAF, 35, 0xAD, 3, 22, 28, 29, 0x4E)
    a.reg(1)
    a.raw(0xAF, 36, 0x4E)
    a.store(3)
    a.number(0)
    a.reg(3)
    a.raw(0xB2, 37)  # ClearAllItems
    a.number(0)
    a.reg(3)
    a.raw(0xB2, 34)  # Shutdown
    a.raw(0x76)
    a.store(3)
    a.label('super_shutdown')
    a.reg(4)
    a.number(1)
    a.reg(2)
    a.raw(0xB2, 34)
    a.reg(1)
    a.member('mDynastySocialEmbedded')
    a.raw(0x73, 0x66)
    a.branch('done', 0xB8)
    a.signal('SOCIAL_CHILD_DETACH')
    a.set_field(1, 'mDynastySocialEmbedded', False)
    a.label('done')
    a.raw(0x76, 0x3E)
    return a.finish()


def generate_header(destination):
    result = ['// Generated by Tools/build_hub_lifecycle.py; prototype only.',
              '#pragma once', '#include <vector>', '#include <cstdint>',
              '#include <cstring>', 'namespace social::embedded::lifecycle {',
              'struct Parameter {uint64_t reg;const char* name;};',
              'static_assert(sizeof(Parameter)==16);',
              'inline const Parameter focusParameters[]={{2,"method"}};',
              'struct Program {uintptr_t definition;unsigned argc,registers,flags;',
              'std::vector<unsigned char> original,body;};',
              'inline std::vector<Program> programs(){std::vector<Program> result;']
    array = lambda b: '{' + ','.join(f'0x{x:02x}' for x in b) + '}'
    for definition, argc, registers, original, program in (
            (0x24940, 3, 7, ORIGINAL_INIT, scoped_init(timer=True)),
            (0x24b38, 1, 5, ORIGINAL_SHUTDOWN, scoped_shutdown(timer=True))):
        result.append(f'result.push_back({{0x{definition:x},{argc},{registers},25,'
                      f'{array(original)},{array(program.code)}}});')
        for at, literal in program.literals:
            result.append('{const auto p=reinterpret_cast<uintptr_t>('
                          f'{json.dumps(literal)});memcpy(result.back().body.data()+{at},&p,8);}}')
        for at, reference in program.references:
            result.append('{const auto p=reinterpret_cast<uintptr_t>('
                          f'{reference});memcpy(result.back().body.data()+{at},&p,8);}}')
    result += ['return result;}', '}']
    Path(destination).write_text('\n'.join(result) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--header', type=Path)
    args = parser.parse_args()
    if args.header:
        generate_header(args.header)
    else:
        p = scoped_init(timer=True)
        print(json.dumps({
            'status': 'offline assembly only; runtime redirect structurally verified, not live tested',
            'originalBodyOffset': '0x24970',
            'originalBodyBytes': 91,
            'registerCount': 7,
            'bytes': len(p.code),
            'code': p.code.hex(),
            'literals': p.literals,
        }, indent=2))
