"""Verified Scholarship detail money, caching, and same-widget Off recovery."""
from dataclasses import replace
from pathlib import Path
import copy
import math
import re
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from build_recruit_notes_ui import Assembler,fnv
from build_currency_recruitdetail_ui import ASSET,OFFSET,ARGC,REGISTERS,FLAGS,SIZE,HASH,STATE,suffix,generate
from recruit_notes_vm import Machine,UNDEFINED

GLOBALS={'Math':{'round':lambda n:math.floor(n+.5),'floor':math.floor},
         'shared_enum':{'fblibraries':{'global':{'Icons':{'ASSETID_ICON_CURRENCY_PROGRAMPOINTS':1234,'LIBRARY_ID':71}}}}}


def program(enabled):
    a=Assembler();suffix(a);p=a.finish();code=bytearray(p.code)
    for at in p.dollar_offsets:code[at]=int(enabled)
    return replace(p,code=bytes(code))


class Tracked(dict):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.writes=[]
    def __setitem__(self,k,v):self.writes.append((k,v));super().__setitem__(k,v)


def text(display):
    row=Tracked({'mData':{'display':display,'ExtraInfo':{'fontColor':'native','resizeWidth':90}},
                 '_x':480,'_y':28,'_visible':True,'calls':[],'measures':[]})
    def set_label(label):row['mData']['display']=label;row['calls'].append(label)
    def width():row['measures'].append('width');return len(str(row['mData']['display']))*row['mData']['ExtraInfo'].get('fontSize',7)
    row.update({'SetLabel':set_label,'GetWidth':width});return row


def fixture(points=40,*,icon=1234,library=71,body=None):
    extra={'Body':points,'Text':'Offer','Icon':icon,'IconLibrary':library,'IconSize':16,
           'Triangles':5,'Percentage':'20%','Grade':'A','TextExtraInfo':{'font':'native'}}
    label=text(points if body is None else body)
    graphic=Tracked({'_x':480-len(str(label['mData']['display']))*7-16-10,'_y':20,'mData':{'Width':16,'Height':16},
                     'measures':[],'_visible':True,'Id':icon})
    def width():graphic['measures'].append('width');return graphic['mData']['Width']
    def height():graphic['measures'].append('height');return graphic['mData']['Height']
    graphic.update({'GetWidth':width,'GetHeight':height})
    return {'mData':{'ExtraInfo':extra,'Width':540},'mcBody':label,'mcIcon':graphic,
            'mcText':text('Offer'),'mcPercentage':text('20%'),
            'mcIncrementalSliderPos':{'Value':5},'mcIncrementalSliderNeg':{'Value':0},
            'mcGradeItem':{'Grade':'A'},'eligibility':{'offered':True,'hours':40}}


def run(row,enabled=True):return Machine(GLOBALS,[]).run(program(enabled),{1:row})


for enabled in (True,False):
    for points,expected in [(0,'0'),(40,'160K'),(95,'380K'),(250,'1.0M'),(1475,'5.9M'),(-40,'-160K'),('1,475','5.9M')]:
        row=fixture(points);extra_before=copy.deepcopy(row['mData']['ExtraInfo']);eligibility_before=copy.deepcopy(row['eligibility'])
        source_style=row['mcBody']['mData']['ExtraInfo'];icon=row['mcIcon'];old_xy=(icon['_x'],icon['_y'])
        run(row,enabled)
        label=row['mcBody'];assert label['mData']['display']==(expected if enabled else points)
        assert icon['_x']==(480-len(expected)*7-16-10 if enabled else old_xy[0])
        assert icon['_y']==old_xy[1] and icon['_visible'] and label['_visible']
        assert label['mData']['ExtraInfo'] is source_style and source_style=={'fontColor':'native','resizeWidth':90}
        assert row['mData']['ExtraInfo']==extra_before and row['eligibility']==eligibility_before
        assert row['mcIncrementalSliderPos']=={'Value':5} and row['mcIncrementalSliderNeg']=={'Value':0} and row['mcGradeItem']=={'Grade':'A'}
        assert not row['mcText']['calls'] and not row['mcPercentage']['calls']
        if not enabled:
            assert not label['calls'] and not label['measures'] and not icon['measures'] and not icon.writes and STATE not in label
        else:
            # Draw with no invalidation must not SetLabel, measure, write icon
            # positions or replace its small private state again.
            state=label[STATE];counts=(len(label['calls']),len(label['measures']),len(icon['measures']),len(icon.writes),len(label.writes))
            for _ in range(100):run(row)
            assert label[STATE] is state
            assert counts==(len(label['calls']),len(label['measures']),len(icon['measures']),len(icon.writes),len(label.writes))
            run(row,False)
            assert label['mData']['display']==points and icon['_x']==old_xy[0] and icon['_y']==old_xy[1]
            assert label[STATE] is UNDEFINED
            counts=(len(label['calls']),len(label['measures']),len(icon['measures']),len(icon.writes),len(label.writes))
            for _ in range(20):run(row,False)
            assert counts==(len(label['calls']),len(label['measures']),len(icon['measures']),len(icon.writes),len(label.writes))
            run(row);assert label['mData']['display']==expected

# Both summary rows consume their own Body. Never substitute Expected NIL for
# the user's current offer (or vice versa), even when both currently equal40.
record={'CurrentNILOffer':40,'ExpectedNILValue':95,'Hours':40,'ScholarshipOffered':True}
offer=fixture(record['CurrentNILOffer']);valuation=fixture(record['ExpectedNILValue'])
run(offer);run(valuation)
assert offer['mcBody']['mData']['display']=='160K' and valuation['mcBody']['mData']['display']=='380K'
assert record=={'CurrentNILOffer':40,'ExpectedNILValue':95,'Hours':40,'ScholarshipOffered':True}

# On -> native source change without a dirty render -> On/Off must use the
# fresh source, not a stale baseline from the previous recruit's summary row.
for enabled in (True,False):
    row=fixture(40);run(row);row['mData']['ExtraInfo']['Body']=100
    run(row,enabled)
    assert row['mcBody']['mData']['display']==('400K' if enabled else 100)
    assert row['mcIcon']['_x']==480-len(str(row['mcBody']['mData']['display']))*7-16-10
    assert row['mData']['ExtraInfo']['Body']==100

# Native dirty rendering, style changes, moving/resizing native controls, or
# replacing an icon invalidates the fast path without overwriting new state.
row=fixture(40);run(row);row['mcBody']['SetLabel'](95);row['mData']['ExtraInfo']['Body']=95
row['mcBody']['_x']=520;row['mcBody']['_y']=48
row['mcBody']['mData']['ExtraInfo']={'fontColor':'new native','resizeWidth':85}
run(row);assert row['mcBody']['mData']['display']=='380K'
assert row['mcIcon']['_x']==520-28-16-10 and row['mcIcon']['_y']==40
row['mcIcon']['_x']=-77;row['mcIcon']['_y']=-31
run(row,False)
assert row['mcBody']['mData']['display']==95 and row['mcIcon']['_x']==-77 and row['mcIcon']['_y']==-31
assert row['mcBody']['mData']['ExtraInfo']=={'fontColor':'new native','resizeWidth':85}
row=fixture(40);run(row);row['mcIcon']['mData'].update({'Width':24,'Height':20})
run(row);assert row['mcIcon']['_x']==480-28-24-10 and row['mcIcon']['_y']==18
counts=(len(row['mcBody']['calls']),len(row['mcIcon'].writes))
for _ in range(10):run(row)
assert counts==(len(row['mcBody']['calls']),len(row['mcIcon'].writes))
row=fixture(40);run(row)
style=row['mcBody']['mData']['ExtraInfo'];style['fontSize']=10 # in-place native style merge
run(row);assert row['mcBody']['mData']['ExtraInfo'] is style
assert row['mcIcon']['_x']==480-40-16-10
counts=(len(row['mcBody']['calls']),len(row['mcBody']['measures']),len(row['mcIcon'].writes))
style['fontColor']='selected black'
for _ in range(20):run(row)
assert counts==(len(row['mcBody']['calls']),len(row['mcBody']['measures']),len(row['mcIcon'].writes))
assert style['fontColor']=='selected black'

# Hours/coins/XP/pitch grades and messages are never money merely because Body
# is numeric or the text says Offer/Expected NIL. Both icon fields must match.
for icon,library in [(9999,71),(1234,9999),(None,71),(1234,None)]:
    row=fixture(40,icon=icon,library=library);run(row)
    assert row['mcBody']['mData']['display']==40 and not row['mcBody']['calls'] and not row['mcIcon'].writes
row=fixture(40);run(row);row['mData']['ExtraInfo']['Icon']=9999;row['mData']['ExtraInfo']['Body']='No offer'
run(row);assert row['mcBody']['mData']['display']=='No offer' and row['mcBody'][STATE] is UNDEFINED
for bad in (None,UNDEFINED,'','Hidden','NaN','Infinity','-Infinity','$0','$40K','160K','1.0M','40%'):
    row=fixture(bad);run(row)
    assert not row['mcBody']['calls'] and not row['mcBody']['measures'] and not row['mcIcon'].writes
for row in ({},{'mcBody':text(40)},{'mcBody':text(40),'mData':{}},
            {'mcBody':text(40),'mData':{'ExtraInfo':{}}}):run(row)

sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load
apt=load(ASSET);h=apt.data[OFFSET:OFFSET+48];body=apt.data[OFFSET+48:OFFSET+48+SIZE]
assert struct.unpack_from('<IHH',h,8)==(ARGC,REGISTERS,FLAGS) and struct.unpack_from('<I',h,24)[0]==SIZE and fnv(body)==HASH
assert bytes.fromhex('b901ac03862d72') in body # mData.ExtraInfo.Body
assert bytes.fromhex('b901af3fb295') in body # mcBody.SetLabel
assert bytes.fromhex('b901ac03862d81') in body and bytes.fromhex('b901ac03862d82') in body # Icon + IconLibrary
assert bytes.fromhex('b901af6db2') in body # native icon rendering remains in copied body
model=apt.data[0x111E8:0x111E8+1736];assert fnv(model)==0x61B616824D7E381A
assert bytes.fromhex('b903a37e02b902a3e3014e4f') in model # Offer Body <- CurrentNILOffer
assert bytes.fromhex('a37e02b902a3e2014e') in model # valuation Body <- ExpectedNILValue
assert bytes.fromhex('a381024e') in model # exact ASSETID_ICON_CURRENCY_PROGRAMPOINTS
pool=apt.decode(0xB320,0xB320+24)[0][2]
assert pool[482]=='ExpectedNILValue' and pool[483]=='CurrentNILOffer' and pool[638]=='Body'
assert pool[641]=='ASSETID_ICON_CURRENCY_PROGRAMPOINTS' and pool[642]=='IconLibrary' and pool[643]=='LIBRARY_ID'

class Bounded(Assembler):
    def reg(self,n):assert n<REGISTERS;super().reg(n)
    def store(self,n):assert n<REGISTERS;super().store(n)
a=Bounded();suffix(a);assert len(a.finish().code)+SIZE<32768
with tempfile.TemporaryDirectory() as folder:
    out=Path(folder)/'recruitdetail.h';generate(out)
    assert out.read_bytes()==(ROOT/'Source/CurrencyRecruitDetailUiPrograms.h').read_bytes()
owners=[]
for file in (ROOT/'Source').glob('*UiPrograms.h'):
    for match in re.finditer(r'result\.push_back\(\{([^\n]*?)\}\);',file.read_text(encoding='utf8')):
        fields=match.group(1).split(',',9)
        if len(fields)<10:continue
        try:
            numeric=lambda value:int(value.removesuffix('ull'),0)
            if numeric(fields[0])==OFFSET and numeric(fields[5])==HASH:owners.append(file.name)
        except ValueError:pass
assert owners==['CurrencyRecruitDetailUiPrograms.h'],owners
print('Passed: exact Scholarship Offer/Expected NIL Body money, independent sources, default-Off no-op, unchanged On fast path, same-widget On/Off cleanup, fresh source/native style changes, exact icon/library gate, untouched hours/eligibility/influence/grades, native icon placement and frame, deterministic source-backed unique callback.')
