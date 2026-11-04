"""NIL row grades preserve compensation, risk, identities and selected contrast."""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_nil_ui import nil_draw_suffix,nil_unfocus_suffix,SPECS
from recruit_notes_vm import Machine,UNDEFINED


def program(suffix):
    a=Assembler();suffix(a);return a.finish()


def text(value):
    t={'mData':{'display':value,'ExtraInfo':{'fontColor':0xFFFFFF,'font':'native','size':24}},'calls':[]}
    t['SetLabel']=lambda v:(t['mData'].update(display=v),t['calls'].append('label'))
    t['SetExtraInfo']=lambda v:(t['mData']['ExtraInfo'].update(v),t['calls'].append('style'))
    return t


def grade(n):return 'A' if n>=90 else 'B' if n>=80 else 'C' if n>=70 else 'D' if n>=60 else 'F'


for n in range(101):
    extra={'Ovr':n,'CurrentNIL':90,'NILValue':85,'RiskOfTransfer':80,'OfferMin':20,'OfferMax':100,'PlayerKey':n,'Position':'QB','Name':'Player','Year':3}
    before=copy.deepcopy(extra);label=text(n)
    receiver={'mData':{'ExtraInfo':extra},'mcOvr':label,'mcHighlight':{'_visible':False},'mcNILValue':text(85)}
    Machine({},[]).run(program(nil_draw_suffix),{1:receiver})
    assert extra==before and label['mData']['display']==grade(n)
    assert label['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)]
    assert label['mData']['ExtraInfo']['font']=='native' and label['mData']['ExtraInfo']['size']==24
    assert receiver['mcNILValue']['mData']['display']==85
    label['calls'].clear();Machine({},[]).run(program(nil_draw_suffix),{1:receiver});assert not label['calls']
    # Focus/reset/recycle the same row; preserve the native black selection.
    receiver['mcHighlight']['_visible']=True;label['mData']['ExtraInfo']['fontColor']=0
    Machine({},[]).run(program(nil_draw_suffix),{1:receiver})
    assert label['mData']['ExtraInfo']['fontColor']==0 and label['mData']['display']==grade(n)
    receiver['mcHighlight']['_visible']=False;label['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    Machine({},[]).run(program(nil_unfocus_suffix),{1:receiver})
    assert label['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)] and extra==before

for hidden in [UNDEFINED,None,'?',-1,101,'85',float('nan'),float('inf')]:
    for suffix in [nil_draw_suffix,nil_unfocus_suffix]:
        label=text(hidden);receiver={'mData':{'ExtraInfo':{'Ovr':hidden}},'mcOvr':label}
        Machine({},[]).run(program(suffix),{1:receiver});assert not label['calls']
for receiver in [{},{'mData':{}},{'mData':{'ExtraInfo':{}}}]:
    for suffix in [nil_draw_suffix,nil_unfocus_suffix]:Machine({},[]).run(program(suffix),{1:receiver})

class BoundedAssembler(Assembler):
    def __init__(self,limit):super().__init__();self.limit=limit
    def reg(self,n):
        assert 0<=n<self.limit
        return super().reg(n)
    def store(self,n):
        assert 0<=n<self.limit
        return super().store(n)

for _,_,regs,_,_,_,suffix in SPECS:
    a=BoundedAssembler(regs);suffix(a);a.finish()
print('Passed: NIL roster101 grades, two-register unfocus/recycled selection, hidden values, numeric compensation/risk/model preservation and unchanged redraw fast path.')
