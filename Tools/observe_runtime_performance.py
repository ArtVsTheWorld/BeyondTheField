"""Bounded, query-only Windows process/thread observation. Never suspends threads.

Records CPU-time deltas, memory and I/O counters plus thread start modules.
No debug attach, ETW policy change, game calls or process-memory writes.
"""
import argparse
import ctypes as c
from ctypes import wintypes as w
import json
from pathlib import Path
import time


class ThreadEntry(c.Structure):
    _fields_ = [('size', w.DWORD), ('usage', w.DWORD), ('tid', w.DWORD),
                ('pid', w.DWORD), ('base_priority', w.LONG),
                ('delta_priority', w.LONG), ('flags', w.DWORD)]


class Memory(c.Structure):
    _fields_ = [('size', w.DWORD), ('faults', w.DWORD)] + [
        (name, c.c_size_t) for name in ('peak_working_set', 'working_set',
        'peak_paged_pool', 'paged_pool', 'peak_nonpaged_pool', 'nonpaged_pool',
        'pagefile', 'peak_pagefile', 'private_bytes')]


class Io(c.Structure):
    _fields_ = [(name, c.c_uint64) for name in (
        'read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--seconds', type=int, default=45, choices=range(1, 61))
    parser.add_argument('--modules', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    kernel = c.WinDLL('kernel32', use_last_error=True)
    psapi = c.WinDLL('psapi', use_last_error=True)
    ntdll = c.WinDLL('ntdll')
    kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    kernel.OpenProcess.restype = w.HANDLE
    kernel.OpenThread.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    kernel.OpenThread.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.GetProcessTimes.argtypes = [w.HANDLE] + [c.POINTER(w.FILETIME)] * 4
    kernel.GetThreadTimes.argtypes = kernel.GetProcessTimes.argtypes
    kernel.GetThreadPriority.argtypes = [w.HANDLE]
    kernel.GetThreadPriority.restype = c.c_int
    kernel.GetProcessIoCounters.argtypes = [w.HANDLE, c.POINTER(Io)]
    kernel.CreateToolhelp32Snapshot.argtypes = [w.DWORD, w.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = w.HANDLE
    for name in ('Thread32First', 'Thread32Next'):
        getattr(kernel, name).argtypes = [w.HANDLE, c.POINTER(ThreadEntry)]
    kernel.GetTickCount64.restype = c.c_uint64
    psapi.GetProcessMemoryInfo.argtypes = [w.HANDLE, c.POINTER(Memory), w.DWORD]
    ntdll.NtQueryInformationThread.argtypes = [w.HANDLE, w.ULONG, w.LPVOID,
                                              w.ULONG, w.LPVOID]
    modules = json.loads(args.modules.read_text(encoding='utf-8-sig'))
    def location(address):
        for item in modules:
            if item['base'] <= address < item['base'] + item['ModuleMemorySize']:
                return f"{item['ModuleName']}+0x{address-item['base']:x}"
        return hex(address)
    def cpu(handle, fn):
        times = [w.FILETIME() for _ in range(4)]
        if not fn(handle, *(c.byref(t) for t in times)):
            return None
        return sum((t.dwHighDateTime << 32) | t.dwLowDateTime
                   for t in times[2:]) / 10_000_000
    process = kernel.OpenProcess(0x410, False, args.pid)  # query + read only
    if not process:
        raise c.WinError(c.get_last_error())
    handles, starts, priorities, previous, totals = {}, {}, {}, {}, {}
    previous_cpu = cpu(process, kernel.GetProcessTimes)
    previous_at = time.monotonic()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with args.output.open('w', encoding='utf-8') as out:
            for sample in range(args.seconds + 1):
                at = time.monotonic()
                snapshot = kernel.CreateToolhelp32Snapshot(4, 0)
                if snapshot == c.c_void_p(-1).value:
                    raise c.WinError(c.get_last_error())
                try:
                    entry = ThreadEntry(size=c.sizeof(ThreadEntry))
                    ok = kernel.Thread32First(snapshot, c.byref(entry))
                    present = set()
                    while ok:
                        if entry.pid == args.pid:
                            present.add(entry.tid)
                            if entry.tid not in handles:
                                handle = kernel.OpenThread(0x40, False, entry.tid)
                                if handle:
                                    handles[entry.tid] = handle
                                    start = c.c_void_p()
                                    if ntdll.NtQueryInformationThread(handle, 9, c.byref(start), c.sizeof(start), None) == 0:
                                        starts[entry.tid] = location(start.value or 0)
                                    priorities[entry.tid] = kernel.GetThreadPriority(handle)
                        ok = kernel.Thread32Next(snapshot, c.byref(entry))
                finally:
                    kernel.CloseHandle(snapshot)
                deltas = {}
                for tid in list(handles):
                    if tid not in present:
                        kernel.CloseHandle(handles.pop(tid))
                        previous.pop(tid, None)
                        continue
                    value = cpu(handles[tid], kernel.GetThreadTimes)
                    if value is None:
                        continue
                    delta = max(0, value - previous.get(tid, value))
                    previous[tid] = value
                    if delta:
                        deltas[tid] = round(delta, 6)
                        totals[tid] = totals.get(tid, 0) + delta
                proc_cpu = cpu(process, kernel.GetProcessTimes)
                if proc_cpu is None:
                    raise RuntimeError('Target process no longer queryable')
                memory = Memory(size=c.sizeof(Memory))
                psapi.GetProcessMemoryInfo(process, c.byref(memory), c.sizeof(memory))
                io = Io()
                kernel.GetProcessIoCounters(process, c.byref(io))
                row = dict(sample=sample, tick=kernel.GetTickCount64(),
                    elapsed=round(at-previous_at, 3), cpu_seconds=round(proc_cpu-previous_cpu, 5),
                    private_bytes=memory.private_bytes, working_set=memory.working_set,
                    threads=len(present), thread_cpu=deltas,
                    io={name: getattr(io, name) for name, _ in Io._fields_})
                out.write(json.dumps(row)+'\n')
                out.flush()
                previous_at, previous_cpu = at, proc_cpu
                if sample < args.seconds:
                    time.sleep(max(0, 1-(time.monotonic()-at)))
        summary=dict(pid=args.pid, output=str(args.output), seconds=args.seconds,
            top_threads=[dict(tid=tid, cpu_seconds=round(total, 3),
                              start=starts.get(tid), priority=priorities.get(tid))
                         for tid, total in sorted(totals.items(), key=lambda p: -p[1])[:15]],
            thread_info=[dict(tid=tid,start=start,priority=priorities.get(tid)) for tid,start in starts.items()])
        args.output.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2))
        print(json.dumps({key:value for key,value in summary.items() if key!='thread_info'}))
    finally:
        for handle in handles.values():
            kernel.CloseHandle(handle)
        kernel.CloseHandle(process)


if __name__ == '__main__':
    main()
