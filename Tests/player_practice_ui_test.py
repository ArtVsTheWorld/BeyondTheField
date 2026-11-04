"""Practice row grade presentation must preserve health, XP and plan decisions."""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_practice_ui import practice_draw_suffix,practice_unfocus_suffix,SPECS
from recruit_notes_vm import Machine,UNDEFINED


def program(suffix):
    a=Assembler();suffix(a);return a.finish()
def grade(n):return 'A' if n>=90 else 'B' if n>=80 else 'C' if n>=70 else 'D' if n>=60 else 'F'
def fixture(value,visible=True,group=False,injured=False,selected=False):
    t={'_visible':visible,'mData':{'display':value,'ExtraInfo':{'font':'native','fontColor':0x707070 if injured else 0 if selected else 0xFFFFFF}},'calls':[]}
    t['SetLabel']=lambda v:(t['mData'].update(display=v),t['calls'].append('label'))
    t['SetExtraInfo']=lambda v:(t['mData']['ExtraInfo'].update(v),t['calls'].append('color'))
    extra={'Ovr':value,'IsGroupPlan':group,'IsInjured':injured,'IsResults':True,'Xp':85,'Impacts':90,'InjuryRisk':80,'PlanValue':2,'HealthPenalty':-4}
    return {'mData':{'ExtraInfo':extra},'mcOvr':t,'mcHighlight':{'_visible':selected},'mcHighlightCenter':{'_visible':True}},extra,t


for n in range(101):
    receiver,extra,t=fixture(n);before=copy.deepcopy(extra)
    Machine({},[]).run(program(practice_draw_suffix),{1:receiver})
    assert t['mData']['display']==grade(n) and t['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)] and extra==before
    t['calls'].clear();Machine({},[]).run(program(practice_draw_suffix),{1:receiver});assert not t['calls']
    t['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    Machine({},[]).run(program(practice_unfocus_suffix),{1:receiver})
    assert t['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)] and extra==before
    for options in ({'selected':True},{'injured':True}):
        receiver,extra,t=fixture(n,**options);color=t['mData']['ExtraInfo']['fontColor']
        Machine({},[]).run(program(practice_draw_suffix),{1:receiver})
        assert t['mData']['display']==grade(n) and t['mData']['ExtraInfo']['fontColor']==color
        Machine({},[]).run(program(practice_unfocus_suffix),{1:receiver})
        assert t['mData']['ExtraInfo']['fontColor']==color
for options in ({'group':True},{'visible':False}):
    for suffix in (practice_draw_suffix,practice_unfocus_suffix):
        receiver,extra,t=fixture(0,**options);Machine({},[]).run(program(suffix),{1:receiver});assert not t['calls']
for value in (None,UNDEFINED,'?',-1,101,'85',float('nan')):
    for suffix in (practice_draw_suffix,practice_unfocus_suffix):
        receiver,extra,t=fixture(value);Machine({},[]).run(program(suffix),{1:receiver});assert not t['calls']
class FixedFrame(Assembler):
    def __init__(self,limit):super().__init__();self.limit=limit
    def reg(self,n):assert 0<=n<self.limit;super().reg(n)
    def store(self,n):assert 0<=n<self.limit;super().store(n)
for _,_,regs,_,_,_,suffix in SPECS:
    a=FixedFrame(regs);suffix(a);a.finish()
print('Passed: Practice Plans101 grades, selected/disabled styles, native6/2-register frames, hidden/group layouts and health/XP/plan models preserved.')
