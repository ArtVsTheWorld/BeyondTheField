"""Compare the settings preflight bytes with the independent native capture."""
from pathlib import Path
import re
import mmap

root=Path(__file__).resolve().parents[1]
source=(root/'Source/RecruitingFog.cpp').read_text()
snapshot=root.parent/'SocialMedia/Evidence/live-module.pe.bin'
with snapshot.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as image:
    for name,offset in [('listPrefix',0x7998C00),('writerPrefix',0x79A5C30)]:
        match=re.search(r'constexpr unsigned char '+name+r'\[\]=\{([^}]+)\}',source)
        assert match, f'Missing native settings guard: {name}'
        expected=bytes(int(x.strip(),0) for x in match[1].split(','))
        actual=image[offset:offset+len(expected)]
        assert expected==actual, f'{name}: source {expected.hex()} differs from native {actual.hex()}'
print('Passed: settings callback prefixes match the independent native capture, including instruction prefixes.')
