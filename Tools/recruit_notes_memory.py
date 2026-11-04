"""Bounded read-only process access reused from Dynasty Enhancer UI research."""
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
