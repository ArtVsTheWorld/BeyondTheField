"""Find and verify native recruit-profile script owners with read/query access.

Writes a session-specific private manifest. This helper never modifies memory.
"""
import argparse
import json
from pathlib import Path
import struct
import time
from recruit_notes_memory import ReadOnlyProcess,U32,U64
from build_recruit_notes_ui import fnv


def inspect(pid,output):
    evidence=Path(__file__).resolve().parents[1]/'Evidence/RecruitingFog'
    programs=json.loads((evidence/'notes-programs.json').read_text(encoding='utf8'))
    memory=ReadOnlyProcess(pid,768*1048576)
    report={'pid':pid,'asset':0,'owners':[],'access':'read/query only','programs':programs}
    observed=Path('Build/recruit-notes-observed.json')
    if observed.exists():
        candidate=json.loads(observed.read_text(encoding='utf8'))
        if candidate.get('pid')==pid:report['asset']=candidate['asset']
    deadline=time.monotonic()+20
    try:
        # Large CoreNode APT data streams use aligned native allocations. Every
        # candidate must match all eight complete method bodies and headers.
        cursor=0x10000;probe=programs[0]
        while cursor<0x7fffffff0000 and not report['asset']:
            if time.monotonic()>deadline:raise RuntimeError('Bounded APT discovery timed out')
            region=memory.query(cursor);end=region.base+region.size
            if end<=cursor:break
            if region.state==0x1000 and region.type==0x20000 and region.protect&0xff in (2,4,8,0x40,0x80) and not region.protect&0x100:
                at=(cursor+0xffff)&~0xffff
                while at<end:
                    if time.monotonic()>deadline:raise RuntimeError('Bounded APT discovery timed out')
                    try:
                        if not memory.read(at,14).startswith(b'Apt Data:1:'):at+=0x10000;continue
                        matched=True;checks=[]
                        for p in programs:
                            h=memory.read(at+p['definition'],0x30)
                            if (U32(h,8)!=p['argc'] or struct.unpack_from('<HH',h,12)!=(p['registers'],p['flags']) or U32(h,24)!=p['size'] or fnv(memory.read(at+p['definition']+0x30,p['size']))!=p['hash']):matched=False;break
                        if matched:report['asset']=at;break
                    except OSError:pass
                    at+=0x10000
            cursor=end
        if not report['asset']:raise RuntimeError('Recruiting CoreNode is not currently available; open Recruiting before discovery')
        for p in programs:
            h=memory.read(report['asset']+p['definition'],0x30)
            if U32(h,8)!=p['argc'] or struct.unpack_from('<HH',h,12)!=(p['registers'],p['flags']) or U32(h,24)!=p['size'] or fnv(memory.read(report['asset']+p['definition']+0x30,p['size']))!=p['hash']:raise RuntimeError('The observed CoreNode does not match every complete Notes method')
        if not observed.exists() or not candidate.get('owner'):raise RuntimeError('The updated pass-through probe needs one recruit-selection refresh to observe an executing method owner')
        executing=candidate['owner'];obj=memory.read(executing,0x60)
        if U64(obj)!=0x140000000+0xbc42fe8 or U64(obj,0x58) not in {report['asset']+p['definition'] for p in programs}:raise RuntimeError('The observed executing function is no longer valid')
        region=memory.query(executing);start=max(region.allocation,(executing-64*1048576)&~0xffff);end=start+256*1048576
        report['arena']=start;report['executingOwner']=executing;targets={report['asset']+p['definition']:i for i,p in enumerate(programs)}
        cursor=start;deadline=time.monotonic()+15
        while cursor<end:
            if time.monotonic()>deadline:raise RuntimeError('Bounded script-owner search timed out')
            region=memory.query(cursor);high=min(end,region.base+region.size)
            if high<=cursor:break
            if region.state==0x1000 and region.type==0x20000 and region.protect&0xff in (4,8,0x40,0x80) and not region.protect&0x100:
                while cursor<high:
                    amount=min(4*1048576,high-cursor);data=memory.read(cursor,amount)
                    for target,index in targets.items():
                        needle=struct.pack('<Q',target);offset=data.find(needle)
                        while offset>=0:
                            owner=cursor+offset-0x58
                            if owner%8==0 and owner>=0x10000:
                                obj=memory.read(owner,0x60)
                                if U64(obj)==0x140000000+0xbc42fe8 and U64(obj,0x58)==target:
                                    report['owners'].append({'address':owner,'program':index})
                            offset=data.find(needle,offset+1)
                    cursor+=amount
            cursor=high
        if len(report['owners'])>128 or any(not any(o['program']==i for o in report['owners']) for i in range(len(programs))):
            (evidence/'notes-owner-search.json').write_text(json.dumps(report,indent=2),encoding='utf8')
            raise RuntimeError('Not every Notes method has a verified live script owner: '+str({p['name']:sum(o['program']==i for o in report['owners']) for i,p in enumerate(programs)}))
        for owner in report['owners']:
            obj=memory.read(owner['address'],0x60)
            if U64(obj)!=0x140000000+0xbc42fe8 or U64(obj,0x58)!=report['asset']+programs[owner['program']]['definition']:raise RuntimeError('A script owner changed during discovery')
        report['bytesRead']=memory.bytes_read
        output.write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps({'asset':report['asset'],'owners':len(report['owners']),'bytesRead':memory.bytes_read,'manifest':str(output)}))
    finally:memory.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pid',type=int,required=True);p.add_argument('--output',type=Path,default=Path('Build/recruit-notes-runtime.json'));a=p.parse_args();inspect(a.pid,a.output)
