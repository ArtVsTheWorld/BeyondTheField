"""Assemble a scoped News.Init body; never reads/writes a running process.

The result needs a verified runtime function-body owner before it can be used.
It is deliberately not an in-place patch of the 91-byte original function.
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
    literals: list[tuple[int, str]]


class Assembler:
    def __init__(self):
        self.code = bytearray()
        self.literals = []
        self.labels = {}
        self.branches = []

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

    def number(self, value):
        if value in (0, 1):
            self.raw(0x59 + value)
        elif value < 128:
            self.raw(0xB5, value)
        else:
            self.raw(0xB6)
            self.code.extend(struct.pack('<H', value))

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
        self.adapter()
        self.store(0)
        self.number(250)
        self.number(0)
        self.string('SOCIAL_SYNC')
        self.string('CM_DYNASTY_SOCIAL_FEED')
        self.reg(0)
        self.member('SetFilterChanged')
        self.reg(0)
        self.number(5)
        self.global_object('cafe', 'utility', 'Delegate')
        self.string('Bind')
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
        return Program(bytes(self.code), self.literals)


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
    sys.path.insert(0, 'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    root = Path(__file__).resolve().parents[1]
    model = load(root.parent / 'SocialMedia/Research/assets/common/ui/node_cfm/corenode.ast')
    result = ['// Generated by Tools/build_hub_lifecycle.py; prototype only.',
              '#pragma once', '#include <vector>', '#include <cstdint>',
              '#include <cstring>', 'namespace social::embedded::lifecycle {',
              'struct Program {uintptr_t definition;unsigned argc,registers,flags;',
              'std::vector<unsigned char> original,body;};',
              'inline std::vector<Program> programs(){std::vector<Program> result;']
    array = lambda b: '{' + ','.join(f'0x{x:02x}' for x in b) + '}'
    for definition, argc, registers, offset, count, program in (
            (0x24940, 3, 7, 0x24970, 91, scoped_init(timer=True)),
            (0x24b38, 1, 5, 0x24b68, 68, scoped_shutdown(timer=True))):
        result.append(f'result.push_back({{0x{definition:x},{argc},{registers},25,'
                      f'{array(model.data[offset:offset + count])},{array(program.code)}}});')
        for at, literal in program.literals:
            result.append('{const auto p=reinterpret_cast<uintptr_t>('
                          f'{json.dumps(literal)});memcpy(result.back().body.data()+{at},&p,8);}}')
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
