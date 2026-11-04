"""Read the installed MMC v6 cache without changing it; retain requested GUIDs."""
import json
import sys
import uuid
from pathlib import Path


def read_cache(file, wanted, toolkit):
    sys.path.insert(0, str(toolkit/'FbmodMigrationResearch'))
    from compression import zstd
    raw = file.read_bytes()
    if int.from_bytes(raw[:8], 'little') != 144213406785688134 or int.from_bytes(raw[8:12], 'little') != 6:
        raise ValueError('Unsupported MMC cache format; no stale metadata fallback')
    data = zstd.decompress(raw[40:])
    pos = 0

    def take(n):
        nonlocal pos
        if n < 0 or n > len(data)-pos:
            raise ValueError('Cache field exceeds bounds')
        value = data[pos:pos+n]
        pos += n
        return value

    def number(n=4): return int.from_bytes(take(n), 'little')

    def string():
        end = data.index(0, pos)
        return take(end-pos+1)[:-1].decode('utf8')

    def array(n=4): take(number()*n)

    def extra():
        if not number(1): return None
        delta = number(1)
        if delta: take(40)
        offset, sb, patch, path_id = number(8), number(), number(1), number()
        return {'offset': offset, 'sb': sb, 'patch': patch, 'path': paths[path_id]}

    counts = [number() for _ in range(5)]
    for _ in range(counts[0]): string()
    for _ in range(counts[1]): string(); number()
    paths = [string() for _ in range(number())]
    for _ in range(counts[2]):
        string(); take(20+8+8+4+1); string(); take(16); extra(); array(); array(16)
    for _ in range(counts[3]):
        string(); take(20+8+8+4+1+8+4); take(number()); extra(); array()
    chunks = {}
    for _ in range(counts[4]):
        guid = str(uuid.UUID(bytes_le=take(16)))
        item = {'sha': take(20).hex(), 'size': number(8), 'location': number(), 'inline': number(1)}
        take(20); array(); item['extra'] = extra(); array()
        if guid in wanted: chunks[guid] = item
    if pos != len(data) or set(chunks) != set(wanted):
        raise ValueError('Cache parse incomplete or requested asset GUID unavailable')
    return {'cache': str(file), 'head': int.from_bytes(raw[16:20], 'little'), 'chunks': chunks}
