"""AIO dollar input normalization and source-preserving callback suffixes."""
import sys,math,copy
from pathlib import Path
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_aio_currency_ui import aio_money
from build_recruit_notes_ui import Assembler
from recruit_notes_vm import Machine

def program():
    a=Assembler();aio_money(a,'done','aio');a.reg(1);a.string('result');a.reg(2);a.raw(0x4F);a.label('done');a.ret();return a.finish()
p=program()
g={'Math':{'round':lambda x:math.floor(x+.5),'floor':math.floor}}
for value,expected in [(0,'0'),(150,'600K'),('$0','0'),('$600,000','600K'),('$4,720,000','4.7M'),('$2.1M','2.1M'),('$1.0M','1.0M'),('$40K','40K'),('$-40,000','-40K')]:
    m=Machine(g,[]);out={};m.run(p,{0:value,1:out});assert out.get('result')==expected,(value,out)
for invalid in ['$NaN','$Infinity','$1e6','$abc','$','$1$2']:
    m=Machine(g,[]);out={};m.run(p,{0:invalid,1:out,2:'unchanged'});assert 'result' not in out,(invalid,out)
print('Passed: AIO explicit dollars/K/M normalization, raw points, invalid rejection and no double multiplication.')

import build_currency_budget_ui as cb
import build_currency_topbar_ui as ct
cb.money=aio_money;ct.money=aio_money
for enabled in [False,True]:
    a=Assembler();cb.budget_suffix(a);base=a.finish();code=bytearray(base.code)
    for at in base.dollar_offsets:code[at]=int(enabled)
    calls=[];data={'display':'$4,720,000'};before=copy.deepcopy(data)
    receiver={'mcProgramPtsValue':{'mData':data,'SetLabel':calls.append}}
    Machine(g,[]).run(replace(base,code=bytes(code)),{1:receiver})
    assert calls==(['4.7M'] if enabled else []) and data==before
    a=Assembler();ct.suffix(a);base=a.finish();code=bytearray(base.code)
    for at in base.dollar_offsets:code[at]=int(enabled)
    calls=[];data={'ExtraInfo':{'isCoach':True,'remainingProgramPoints':2185}}
    before=copy.deepcopy(data);receiver={'mData':data,'mcProgramPoints':{'SetLabel':calls.append}}
    Machine(g,[]).run(replace(base,code=bytes(code)),{1:receiver})
    assert calls==(['8.7M'] if enabled else []) and data==before
print('Passed: Blueprint and topbar output, Off no-op, unchanged source data.')
