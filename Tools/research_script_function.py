"""Read-only APT ScriptFunction owner/header capture for the direct-hub prototype.

Example:
  python Tools/research_script_function.py --pid 27496 --model-base 15848636416 \
    --output Evidence/DirectHub/script-function-runtime.json

Only OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ),
VirtualQueryEx, and ReadProcessMemory access the target process. Output files
are local research evidence; this helper never changes process memory.
"""
import argparse
import ctypes
import json
from pathlib import Path
import struct
import time


class MemoryInfo(ctypes.Structure):
    _fields_ = [
        ("base", ctypes.c_uint64), ("allocation", ctypes.c_uint64),
        ("allocation_protect", ctypes.c_uint32), ("pad", ctypes.c_uint32),
        ("size", ctypes.c_uint64), ("state", ctypes.c_uint32),
        ("protect", ctypes.c_uint32), ("type", ctypes.c_uint32),
        ("pad2", ctypes.c_uint32),
    ]


class ReadOnlyProcess:
    def __init__(self, pid, budget):
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        self.kernel.OpenProcess.restype = ctypes.c_void_p
        self.kernel.VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                               ctypes.c_void_p, ctypes.c_size_t]
        self.kernel.VirtualQueryEx.restype = ctypes.c_size_t
        self.kernel.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                                  ctypes.c_void_p, ctypes.c_size_t,
                                                  ctypes.POINTER(ctypes.c_size_t)]
        self.kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        self.handle = self.kernel.OpenProcess(0x410, False, pid)
        if not self.handle:
            raise OSError(ctypes.get_last_error(), "Read-only OpenProcess failed")
        self.budget = budget
        self.bytes_read = 0

    def read(self, address, size):
        if size < 0 or self.bytes_read + size > self.budget:
            raise RuntimeError("Read budget exceeded")
        buffer = ctypes.create_string_buffer(size)
        actual = ctypes.c_size_t()
        ok = self.kernel.ReadProcessMemory(self.handle, address, buffer, size,
                                           ctypes.byref(actual))
        self.bytes_read += actual.value
        if not ok or actual.value != size:
            raise OSError(ctypes.get_last_error(), f"Read failed at {address:#x}")
        return buffer.raw

    def query(self, address):
        info = MemoryInfo()
        if not self.kernel.VirtualQueryEx(self.handle, address, ctypes.byref(info),
                                          ctypes.sizeof(info)):
            raise OSError(ctypes.get_last_error(), f"Query failed at {address:#x}")
        return info

    def close(self):
        self.kernel.CloseHandle(self.handle)


U64 = lambda data, offset=0: struct.unpack_from("<Q", data, offset)[0]
U32 = lambda data, offset=0: struct.unpack_from("<I", data, offset)[0]
FUNCTIONS = {
    "Init": dict(definition=0x24940, argc=3, registers=7, flags=0x19, size=91),
    "Shutdown": dict(definition=0x24B38, argc=1, registers=5, flags=0x19, size=68),
}
ACCESSORS = {
    "body": (0xA8, 0x7C34E10, "488b41584883c030c3"),
    "length": (0xB0, 0x7C34E40, "488b41588b4018c3"),
    "pool": (0xB8, 0x7C34EB0, "488b4158c5f8104020c5f81102488bc2c3"),
    "parameter": (0xC0, 0x7C34DD0, "488b41584863ca4803c9488b4010488b44c808c3"),
}


def header_record(memory, address):
    data = memory.read(address, 0x30)
    size = U32(data, 0x18)
    return {
        "address": address, "header_hex": data.hex(),
        "name_pointer": U64(data), "argc": U32(data, 8),
        "registers": struct.unpack_from("<H", data, 0xC)[0],
        "flags": struct.unpack_from("<H", data, 0xE)[0],
        "parameter_pointer": U64(data, 0x10), "size": size,
        "pool_count": U32(data, 0x20), "pool_pointer": U64(data, 0x28),
        "body": address + 0x30,
        "body_hex": memory.read(address + 0x30, size).hex(),
    }


def disassemble(data, address):
    try:
        from capstone import Cs, CS_ARCH_X86, CS_MODE_64
    except ImportError:
        # Existing local research dependency; no packages are installed.
        import sys
        vendor = Path("C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools/_vendor")
        sys.path.insert(0, str(vendor))
        try:
            from capstone import Cs, CS_ARCH_X86, CS_MODE_64
        except ImportError:
            return []
    return [f"{i.address:#x} {i.mnemonic} {i.op_str}" for i in
            Cs(CS_ARCH_X86, CS_MODE_64).disasm(data, address)]


def capture(args):
    memory = ReadOnlyProcess(args.pid, args.read_budget_mb * 1048576)
    try:
        report = {"pid": args.pid, "image_base": args.image_base,
                  "model_base": args.model_base, "process_access": "read/query only",
                  "functions": {}, "accessors": {}, "owners": []}
        for name, expected in FUNCTIONS.items():
            record = header_record(memory, args.model_base + expected["definition"])
            record["expected"] = expected
            record["original_metadata_matches"] = all(
                record[k] == expected[k] for k in ("argc", "registers", "flags", "size"))
            if not record["original_metadata_matches"]:
                raise RuntimeError(f"Unexpected {name} definition metadata")
            report["functions"][name] = record
        vt = args.image_base + 0xBC42FE8
        for name, (slot, rva, prefix) in ACCESSORS.items():
            actual = U64(memory.read(vt + slot, 8))
            code = memory.read(args.image_base + rva, 32)
            report["accessors"][name] = dict(slot=slot, rva=rva, pointer=actual,
                bytes32_hex=code.hex(), expected_prefix_hex=prefix,
                gate_matches=(actual == args.image_base + rva and
                              code.startswith(bytes.fromhex(prefix))),
                disassembly=disassemble(code, rva))
        if not all(v["gate_matches"] for v in report["accessors"].values()):
            raise RuntimeError("Unexpected native accessor gate")
        caller = memory.read(args.image_base + 0x7C07A86, 0x35)
        report["invocation"] = dict(rva=0x7C07A86, bytes_hex=caller.hex(),
            disassembly=disassemble(caller, 0x7C07A86))
        report["lifetime"] = {}
        for name, slot, rva, amount in (
                ("clone", 0x90, 0x7C34D30, 0x80),
                ("cleanup", 0x60, 0x7C34BE0, 0x60),
                ("destructor", 0x80, 0x7C337F0, 0x80)):
            code = memory.read(args.image_base + rva, amount)
            report["lifetime"][name] = dict(slot=slot, rva=rva,
                vtable_pointer=U64(memory.read(vt + slot, 8)),
                bytes_hex=code.hex(), disassembly=disassemble(code, rva))

        # Apt strings/objects occupy nearby arenas in the verified session.
        # This is a bounded search heuristic, not a guaranteed allocator API.
        pool = report["functions"]["Init"]["pool_pointer"]
        string_object = U64(memory.read(pool, 8))
        scan_start = args.scan_start or memory.query(string_object).allocation
        scan_end = scan_start + args.scan_mb * 1048576
        targets = {v["address"]: name for name, v in report["functions"].items()}
        report["search"] = dict(start=scan_start, end=scan_end,
            heuristic="Apt object arenas near first dictionary-string allocation",
            completed=True)
        address = scan_start
        deadline = time.monotonic() + args.timeout
        while address < scan_end:
            if time.monotonic() > deadline:
                report["search"].update(completed=False, stopped_at=address, reason="time bound")
                break
            info = memory.query(address)
            low, high = max(address, info.base), min(scan_end, info.base + info.size)
            if (info.state == 0x1000 and info.type == 0x20000 and
                    info.protect & 0xFF in (4, 8, 0x40, 0x80) and
                    not info.protect & 0x100):
                cursor = low
                while cursor < high:
                    amount = min(8 * 1048576, high - cursor)
                    data = memory.read(cursor, amount)
                    for target, name in targets.items():
                        pointer = struct.pack("<Q", target)
                        offset = data.find(pointer)
                        while offset >= 0:
                            field = cursor + offset
                            owner = field - 0x58
                            if owner % 8 == 0:
                                obj = memory.read(owner, 0x60)
                                if U64(obj) == vt and obj[0xB] == 0x46 and U64(obj, 0x58) == target:
                                    report["owners"].append(dict(function=name, address=owner,
                                        vtable=vt, definition_field=field, definition=target,
                                        tag_word_at_8=U32(obj, 8), tag_byte_at_0b=obj[0xB],
                                        object_hex=obj.hex(), allocation=info.allocation))
                            offset = data.find(pointer, offset + 1)
                    cursor += amount
            address = info.base + info.size
        # Recheck all owner pointers after the scan to reject stale discoveries.
        for owner in report["owners"]:
            owner["recheck_matches"] = (
                U64(memory.read(owner["address"], 8)) == vt and
                U64(memory.read(owner["definition_field"], 8)) == owner["definition"])
        report["bytes_read"] = memory.bytes_read
        report["layout"] = dict(object_size=0x60, definition_pointer_offset=0x58,
            observed_tag_byte_offset=0xB, observed_tag_byte=0x46,
            tag_note="Observed packed header byte, not an independently resolved enum.",
            header_size=0x30, argc_offset=8, registers_offset=0xC, flags_offset=0xE,
            parameters_offset=0x10, size_offset=0x18, pool_offset=0x20)
        return report
    finally:
        memory.close()


def number(value):
    return int(value, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--model-base", type=number, required=True)
    parser.add_argument("--image-base", type=number, default=0x140000000)
    parser.add_argument("--scan-start", type=number)
    parser.add_argument("--scan-mb", type=int, default=256)
    parser.add_argument("--read-budget-mb", type=int, default=512)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    if not (1 <= options.scan_mb <= 512 and 1 <= options.read_budget_mb <= 1024):
        parser.error("Search/read bounds are outside the supported range")
    result = capture(options)
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(output=str(options.output), owners=result["owners"],
                         search=result["search"], bytes_read=result["bytes_read"]), indent=2))
