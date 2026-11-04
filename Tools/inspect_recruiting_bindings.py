"""Map recruiting getter registrations and live vtable ownership, read-only.

Input: an RVA-indexed module snapshot plus its capture JSON from capture_image.py.
No getters are called, no hooks installed, and no remote memory is written.
"""
import argparse
import ctypes as c
import json
import mmap
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--image', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
capture = json.loads(args.image.with_suffix('.json').read_text(encoding='utf8'))
base, pid = capture['base'], capture['pid']
k = c.WinDLL('kernel32', use_last_error=True)
k.OpenProcess.argtypes = [c.c_uint32, c.c_int, c.c_uint32]
k.OpenProcess.restype = c.c_void_p
k.ReadProcessMemory.argtypes = [c.c_void_p, c.c_void_p, c.c_void_p, c.c_size_t, c.c_void_p]
k.CloseHandle.argtypes = [c.c_void_p]
handle = k.OpenProcess(0x1010, False, pid)
if not handle: raise OSError(c.get_last_error(), 'Read-only OpenProcess failed')


def read(address, size):
    data, got = c.create_string_buffer(size), c.c_size_t()
    if not k.ReadProcessMemory(handle, address, data, size, c.byref(got)) or got.value != size:
        raise OSError(c.get_last_error(), f'Cannot read {address:#x}')
    return data.raw


def q(address): return struct.unpack('<Q', read(address, 8))[0]


decoder = Cs(CS_ARCH_X86, CS_MODE_64)
decoder.detail = True
targets = {'GetTeamRecruitList': 0x40, 'GetMotivationsForRecruit': 0x90,
           'GetPitchInfo': 0x60, 'GetRecruitInfoData': 0x30}
report = []
try:
    with args.image.open('rb') as file:
        image = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        if read(base, 0x200) != image[:0x200]: raise ValueError('Snapshot process header differs')
        for name, slot in targets.items():
            string_at = image.find(name.encode()+b'\0')
            if string_at < 0: raise ValueError(f'Native name unavailable: {name}')
            reference = image.find(struct.pack('<Q', base+string_at))
            if reference < 8: raise ValueError(f'Native registration unavailable: {name}')
            registration = struct.unpack_from('<Q', image, reference-8)[0]-base
            code = list(decoder.disasm(image[registration:registration+0x40], registration))
            thunk = next(i.address+i.size+i.operands[1].mem.disp for i in code
                         if i.mnemonic == 'lea' and i.op_str.startswith('r8, [rip'))
            code = list(decoder.disasm(image[thunk:thunk+0x70], thunk))
            name_pointer = next(i.address+i.size+i.operands[1].mem.disp for i in code
                                if i.mnemonic == 'lea' and i.op_str.startswith('rcx, [rip'))
            if name_pointer != string_at: raise ValueError(f'Getter name verification failed: {name}')
            global_at = next(i.address+i.size+i.operands[1].mem.disp for i in code
                             if i.mnemonic == 'mov' and 'qword ptr [rip' in i.op_str)
            obj = q(base+global_at)
            vtable = q(obj)
            function = q(vtable+slot)
            if not base <= vtable < base+len(image) or not base <= function < base+len(image):
                raise ValueError(f'Getter has an unsupported or already-owned binding: {name}')
            prefix = read(function, 32)
            if prefix != image[function-base:function-base+32]: raise ValueError('Live getter differs from snapshot')
            report.append({'name': name, 'registrationRva': hex(registration), 'thunkRva': hex(thunk),
                           'globalRva': hex(global_at), 'vtableRva': hex(vtable-base), 'slot': hex(slot),
                           'functionRva': hex(function-base), 'prefix': prefix.hex(), 'nameVerified': True})
        image.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'pid': pid, 'base': base, 'bindings': report,
                                       'access': 'read-only; getters not invoked'}, indent=2), encoding='utf8')
    print(json.dumps({'verifiedBindings': len(report), 'pid': pid, 'output': str(args.output)}))
finally:
    k.CloseHandle(handle)
