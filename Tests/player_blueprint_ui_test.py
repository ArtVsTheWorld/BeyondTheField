"""Program Overview roster badges must not alter budgets or recruit widgets."""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_blueprint_ui import blueprint_suffix
from build_player_card_ui import rating_value_draw_suffix
from recruit_notes_vm import Machine,UNDEFINED


class FixedFrame(Assembler):
    def reg(self,n):
        assert 0<=n<5
        super().reg(n)
    def store(self,n):
        assert 0<=n<5
        super().store(n)


a=FixedFrame();blueprint_suffix(a);program=a.finish()
def grade(n):return 'A' if n>=90 else 'B' if n>=80 else 'C' if n>=70 else 'D' if n>=60 else 'F'
def fixture(value,layout=1,visible=True,badge_value=None):
    label={'mData':{'display':value,'ExtraInfo':{'font':'native','fontColor':0xFFFFFF}},'calls':[]}
    label['SetLabel']=lambda v:(label['mData'].update(display=v),label['calls'].append('label'))
    label['SetExtraInfo']=lambda v:(label['mData']['ExtraInfo'].update(v),label['calls'].append('color'))
    extra={'LayoutStyle':layout,'OVRValue':value,'ProgramPtsValue':85,'Position':'QB','StarRating':5}
    badge={'_visible':visible,'mData':{'value':value if badge_value is None else badge_value,'ExtraInfo':{}},'mcValue':label}
    receiver={'mData':{'ExtraInfo':extra},'mcRatingValueItem':badge,'mcProgramPtsValue':{'display':85}}
    return receiver,extra,badge,label


for n in range(101):
    receiver,extra,badge,label=fixture(n);before=copy.deepcopy(extra)
    Machine({},[]).run(program,{1:receiver})
    assert label['mData']['display']==grade(n)
    assert label['mData']['ExtraInfo']=={'font':'native','fontColor':GRADE_COLORS[grade(n)]}
    assert badge['mData']['value']==n and badge['mData']['ExtraInfo']['DEPlayerRating'] is True
    assert extra==before and receiver['mcProgramPtsValue']['display']==85
    label['calls'].clear();Machine({},[]).run(program,{1:receiver});assert not label['calls']
    # A later native RatingValueItem repaint must recover the grade from its
    # numeric value while keeping compensation and original model unchanged.
    label['mData']['display']=n;label['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    repaint=Assembler();rating_value_draw_suffix(repaint);repaint.ret()
    Machine({},[]).run(repaint.finish(),{1:badge})
    assert label['mData']['display']==grade(n) and extra==before and badge['mData']['value']==n
for layout in (0,2,None,UNDEFINED,'1'):
    receiver,extra,badge,label=fixture(85,layout=layout)
    Machine({},[]).run(program,{1:receiver});assert not label['calls'] and not badge['mData']['ExtraInfo']
for value in (UNDEFINED,None,'?',-1,101,'85',float('nan')):
    receiver,extra,badge,label=fixture(value)
    Machine({},[]).run(program,{1:receiver});assert not label['calls']
for receiver in ({},{'mData':{}},{'mData':{'ExtraInfo':{}}}):
    Machine({},[]).run(program,{1:receiver})
for kwargs in ({'visible':False},{'badge_value':75}):
    receiver,extra,badge,label=fixture(85,**kwargs)
    Machine({},[]).run(program,{1:receiver});assert not label['calls'] and not badge['mData']['ExtraInfo']
print('Passed: Blueprint roster badges101 boundaries/colors/repaint/fixed5frame; recruits, unknowns, compensation and source models preserved.')
