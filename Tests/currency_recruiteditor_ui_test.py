"""Execute ScholarshipToggle's unchanged native writers plus display suffix."""
from dataclasses import replace
from pathlib import Path
import copy,inspect,math,struct,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from build_currency_recruiteditor_ui import ASSET,SPECS,STATE,FixedFrameAssembler,suffix,generate
from recruit_notes_vm import Machine,UNDEFINED,ScriptFunction
sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools');from inspect_tb_ast import load
apt=load(ASSET);pool=apt.decode(0x7ea98)[0][2];assert pool[4]=='ScholarshipToggle'

class EditorMachine(Machine):pass
namespace=dict(math=math,struct=struct,UNDEFINED=UNDEFINED,ScriptFunction=ScriptFunction)
source=inspect.getsource(Machine.run).replace('    def run(','def run(',1).replace('\n    ','\n')
source=source.replace('pc, stack = begin, []','pc, stack = begin, []; locals_ = {}')
source=source.replace('stack.append(self.globals[stack.pop()])','stack.append((lambda key: locals_.get(key,self.globals.get(key,UNDEFINED)))(stack.pop()))')
source=source.replace('elif op == 0xAF:',"elif op == 0xAC:\n                count=code[pc];pc+=1;names=[self.pool[n] for n in code[pc:pc+count]];pc+=count;value=stack.pop()\n                for name in names:value=self.member(value,name)\n                stack.append(value)\n            elif op == 0xAF:")
source=source.replace('elif op == 0x4F:',"elif op == 0x4D:\n                stack[-1],stack[-2]=stack[-2],stack[-1]\n            elif op == 0x3C:\n                value,key=stack.pop(),stack.pop();locals_[key]=value\n            elif op == 0x60:\n                right,left=stack.pop(),stack.pop();stack.append(int(left)&int(right))\n            elif op == 0x4F:")
source=source.replace('op in (0x47, 0x0B, 0x48, 0x67)','op in (0x47, 0x71, 0x0B, 0x48, 0x67)').replace('if op == 0x47:','if op in (0x47,0x71):')
exec(source,namespace);EditorMachine.run=namespace['run']
GLOBALS={'Math':{'round':lambda n:math.floor(n+.5),'floor':math.floor},'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':4}}}

def program(name='Draw',enabled=True,native=True):
    spec=next(s for s in SPECS if s[0]==name);_,offset,argc,registers,flags,size,expected=spec
    a=FixedFrameAssembler(registers)
    if native:a.code.extend(apt.data[offset+48:offset+48+size])
    suffix(a);p=a.finish();code=bytearray(p.code)
    for at in p.dollar_offsets:code[at]=int(enabled)
    if native:assert bytes(code[:size])==apt.data[offset+48:offset+48+size]
    return replace(p,code=bytes(code))

def fixture(value=40):
    calls=[];events=[];native_style={'fontColor':0xffffff,'size':24,'font':'native','resize':2,'resizeWidth':200,'maxNumLines':3}
    child={'mData':{'display':str(value),'ExtraInfo':dict(native_style)},'_x':260,'_y':17}
    def label(value):child['mData']['display']=value;calls.append(('label',value))
    def style(value):child['mData']['ExtraInfo'].update(value);calls.append(('style',dict(value)))
    child.update(SetLabel=label,SetExtraInfo=style)
    receiver={'mcValue':child,'mValue':value,'mMinValue':0,'mMaxValue':1000,'mData':{'ExtraInfo':{'DefaultValue':UNDEFINED,'MaxValue':UNDEFINED,'MinValue':UNDEFINED,'ShowLevelLabel':False}},
              'mcBackground':{'_x':200,'_width':150},'SPACING_OFFSET':8,'mcLevel':{'_x':0,'_visible':False},'mcIcon':{'SetValue':lambda v:calls.append(('icon',v))},
              'mcArrowLeft':{'GetWidth':lambda:20,'_x':0},'mcArrowRight':{'GetWidth':lambda:20,'_x':0},'ARROW_OFFSET':24,'LABEL_PADDING':56,
              'mDirtyBitFlags':0,'INVALIDATE_INFO':1,'_FireChangeEvent':lambda unused,event:events.append(dict(event))}
    def super_draw():receiver['mDirtyBitFlags']=0
    receiver['super']={'Draw':super_draw}
    return receiver,calls,events,native_style

def invoke(receiver,name='Draw',value=None,enabled=True,native=True):
    args={1:receiver}
    if name=='Draw':args[2]=receiver['super']
    elif name=='_AddCurrentValue':args[2]=value
    return EditorMachine(GLOBALS,pool).run(program(name,enabled,native),args)

for source_value,expected in [(0,'0'),(1,'4K'),(40,'160K'),(150,'600K'),(250,'1.0M'),(1000,'4.0M'),(-15,'-60K')]:
    receiver,calls,events,native_style=fixture(source_value);source={'ExtraInfo':dict(receiver['mData']['ExtraInfo'])}
    receiver['mDirtyBitFlags']=1;invoke(receiver)
    assert receiver['mcValue']['mData']['display']==expected and receiver['mValue']==source_value
    assert receiver['mData']==source and not events
    extra=receiver['mcValue']['mData']['ExtraInfo'];assert extra['resize']==4 and extra['resizeWidth']==82 and extra['maxNumLines']==1
    assert extra['fontColor']==native_style['fontColor'] and extra['size']==24 and receiver['mcValue']['_x']==260
    before=len(calls)
    for _ in range(50):invoke(receiver)
    assert len(calls)==before,'Unchanged native Draw caused another display/style setter'
    invoke(receiver,enabled=False)
    assert receiver['mcValue']['mData']['display']==str(source_value)
    assert receiver['mcValue']['mData']['ExtraInfo']==native_style and receiver[STATE] is UNDEFINED
    before=len(calls)
    for _ in range(10):invoke(receiver,enabled=False)
    assert len(calls)==before
    invoke(receiver);assert receiver['mcValue']['mData']['display']==expected

# Actual native clamps and event payloads run before the suffix. The money
# string is never fed into GetValue, _FireChangeEvent, min/max/default or math.
for name,initial,argument,minimum,maximum,default,actual,expected in [
    ('_AddCurrentValue',40,10,0,1000,0,50,'200K'),('_AddCurrentValue',40,5000,0,1000,0,1000,'4.0M'),
    ('_AddCurrentValue',40,-5000,10,1000,0,10,'40K'),('_SetCurrentValueToMax',40,None,0,250,0,250,'1.0M'),
    ('_SetCurrentValueToMin',40,None,10,250,0,10,'40K'),('_SetCurrentValueToDefault',40,None,0,250,75,75,'300K')]:
    for enabled in [False,True]:
        receiver,calls,events,_=fixture(initial);receiver.update(mMinValue=minimum,mMaxValue=maximum);receiver['mData']['ExtraInfo']['DefaultValue']=default
        before={'ExtraInfo':dict(receiver['mData']['ExtraInfo'])};invoke(receiver,name,argument,enabled)
        assert receiver['mValue']==actual and events==[{'value':actual}]
        assert receiver['mcValue']['mData']['display']==(expected if enabled else str(actual)) and receiver['mData']==before

# Native overwrites survive cleanup: restore only our own currently-applied
# three fit properties and our own display label on the same child.
receiver,calls,_,native_style=fixture();invoke(receiver)
receiver['mcValue']['mData']['ExtraInfo'].update(fontColor=0x123456,size=29,resize=7,resizeWidth=77,maxNumLines=2)
receiver['mcValue']['mData']['display']='native override';invoke(receiver,enabled=False)
assert receiver['mcValue']['mData']['display']=='native override'
assert receiver['mcValue']['mData']['ExtraInfo']['resize']==7 and receiver['mcValue']['mData']['ExtraInfo']['fontColor']==0x123456
receiver,calls,_,_=fixture();invoke(receiver);receiver['mcBackground']['_width']=180;invoke(receiver)
assert receiver['mcValue']['mData']['ExtraInfo']['resizeWidth']==112
before=len(calls)
for _ in range(50):invoke(receiver)
assert len(calls)==before
for value in [None,UNDEFINED,'Hidden','NaN','Infinity','$40K','40K',float('nan'),float('inf')]:
    receiver,calls,events,_=fixture();receiver['mValue']=value;invoke(receiver,native=False)
    assert not calls and not events
for bad in [None,UNDEFINED,'150',float('nan'),float('inf'),-1,4096]:
    receiver,calls,_,_=fixture();receiver['mcBackground']['_width']=bad;invoke(receiver)
    assert receiver['mcValue']['mData']['display']=='160K' and not [c for c in calls if c[0]=='style']
for enabled in [False,True]:
    assert EditorMachine(GLOBALS,pool).run(program(enabled=enabled,native=False),{1:{}}) is UNDEFINED

for name,offset,argc,registers,flags,size,expected in SPECS:
    h=apt.data[offset:offset+48];assert struct.unpack_from('<IHH',h,8)==(argc,registers,flags)
    a=FixedFrameAssembler(registers);suffix(a);p=a.finish();pc=0
    while pc<len(p.code):
        op=p.code[pc];pc+=1
        if op==0xb9:assert p.code[pc]<registers;pc+=1
        elif op==0xb5:pc+=1
        elif op==0xb6:pc+=2
        elif op==0xa1:pc=((pc+7)&~7)+8
        elif op in (0x87,0x9d,0xb8,0x99):pc=((pc+7)&~7)+4
    # These native data/member words are never assigned by custom bytecode.
    assert 'mMinValue' not in [v for _,v in p.literals] and 'mMaxValue' not in [v for _,v in p.literals]
with tempfile.TemporaryDirectory() as folder:
    output=Path(folder)/'editor.h';generate(output);assert output.read_bytes()==(ROOT/'Source/CurrencyRecruitEditorUiPrograms.h').read_bytes()
print('Recruit editor: five full native writers, numeric clamps/events, fixed2/3/4-register frames, K/M labels, unchanged-On zero setters, same-instance Off restoration and bounded native layout pass')
