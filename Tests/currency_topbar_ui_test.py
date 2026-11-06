"""Exact native topbar binding, source preservation and dollar edge cases."""
from dataclasses import replace
from pathlib import Path
import copy
import math
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from build_recruit_notes_ui import Assembler,fnv
from build_currency_topbar_ui import suffix,generate,ASSET,OFFSET,SIZE,HASH,ARGC,REGISTERS,FLAGS
from recruit_notes_vm import Machine,UNDEFINED


def program(enabled):
    a=Assembler();suffix(a);p=a.finish();code=bytearray(p.code)
    for at in p.dollar_offsets:code[at]=int(enabled)
    return replace(p,code=bytes(code))


GLOBALS={'Math':{'round':lambda n:math.floor(n+.5),'floor':math.floor}}
cases=[(0,'0'),(0.0,'0'),('0','0'),(1,'4K'),(25,'100K'),(75,'300K'),
       (150,'600K'),(249,'996K'),(250,'1.0M'),(1000,'4.0M'),(10_630,'42.5M'),
       ('10,630','42.5M'),(-75,'-300K')]
for source,expected in cases:
    for enabled in (True,False):
        for coach in (True,False):
            target={'mData':{'display':str(source),'ExtraInfo':{'font':'native','fontColor':0xF3F0E7}},'calls':[]}
            target['SetLabel']=lambda label:target['calls'].append(label)
            data={'ExtraInfo':{'isCoach':coach,'remainingProgramPoints':source,'CoachPoints':75,
                               'StaffPoints':250,'coachLevel':52,'jobSecurityPercentage':60}}
            before=copy.deepcopy(data)
            receiver={'mData':data,'mcProgramPoints':target,'mcStaffPoints':{'SetLabel':lambda value:(_ for _ in ()).throw(AssertionError('Staff points changed'))},
                      'mcCharacterXP':{'SetLabel':lambda value:(_ for _ in ()).throw(AssertionError('Coach XP changed'))}}
            Machine(GLOBALS,[]).run(program(enabled),{1:receiver})
            assert target['calls']==([expected] if enabled and coach else [])
            assert data==before and target['mData']['ExtraInfo']=={'font':'native','fontColor':0xF3F0E7}

for source in (UNDEFINED,None,'',' ','Hidden','?','NaN','Infinity','-Infinity','$0','$40K','$1.0M','75%','75 points',float('nan'),float('inf'),1_000_000_001):
    calls=[];receiver={'mData':{'ExtraInfo':{'isCoach':True,'remainingProgramPoints':source}},'mcProgramPoints':{'SetLabel':calls.append}}
    Machine(GLOBALS,[]).run(program(True),{1:receiver})
    assert calls==[],(source,calls)
for receiver in ({},{'mData':{}},{'mData':{'ExtraInfo':{'isCoach':True,'remainingProgramPoints':75}}}):
    Machine(GLOBALS,[]).run(program(True),{1:receiver})

class Bounded(Assembler):
    def reg(self,n):assert n<REGISTERS;super().reg(n)
    def store(self,n):assert n<REGISTERS;super().store(n)
a=Bounded();suffix(a);assert len(a.finish().code)+SIZE<32768

sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load
apt=load(ASSET);header=apt.data[OFFSET:OFFSET+48];body=apt.data[OFFSET+48:OFFSET+48+SIZE]
assert struct.unpack_from('<IHH',header,8)==(ARGC,REGISTERS,FLAGS)
assert struct.unpack_from('<I',header,24)[0]==SIZE and fnv(body)==HASH
pool=apt.decode(0xB298)[0][2]
assert pool[:5]==['_global','art_screen','Object','infocenter','CareerInfoModule']
# Native optimized MultiGetMember reads exactly this.mData.ExtraInfo before
# fetching remainingProgramPoints; it sends the formatted result to the exact
# mcProgramPoints child. Do not infer a binding from a whole-file string hit.
assert pool.index('mData')==110 and pool.index('ExtraInfo')==111
assert pool.index('remainingProgramPoints')==257 and pool.index('mcProgramPoints')==81
assert bytes.fromhex('b901ac026e6fa301014e') in body
assert bytes.fromhex('b901af51b261') in body # this.mcProgramPoints.SetLabel
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'topbar.h';generate(out)
    assert out.read_bytes()==(ROOT/'Source/CurrencyTopbarUiPrograms.h').read_bytes()
print('Passed: native Dynasty topbar $4K conversion, exact merged source/target, unchanged numeric budgets and coach/staff points, numeric/string zero and nonzero cases, preformatted-dollar rejection, native frame and deterministic generation.')
