"""Formation Subs display boundaries and substitution/model preservation."""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_formation_ui import module_suffix,list_suffix,detail_suffix,legacy_ovr_suffix,SPECS
from build_player_card_ui import rating_value_draw_suffix,badge_suffix,attribute_slots_suffix
from recruit_notes_vm import Machine,UNDEFINED


def program(suffix):
    a=Assembler();suffix(a);a.ret();return a.finish()


def text(value):
    t={'mData':{'display':value,'ExtraInfo':{'fontColor':0xFFFFFF,'font':'native','size':24}},'calls':[]}
    t['SetLabel']=lambda value:(t['mData'].update(display=value),t['calls'].append('label'))
    t['SetExtraInfo']=lambda style:(t['mData']['ExtraInfo'].update(style),t['calls'].append('color'))
    return t


def item(value):return {'mData':{'value':value,'ExtraInfo':{'circle':'native'}},'mcValue':text(value)}
def grade(n):return 'A' if n>=90 else 'B' if n>=80 else 'C' if n>=70 else 'D' if n>=60 else 'F'


for n in range(101):
    source={'key':0,'ExtraInfo':{'Ovr':n,'Jersey':n,'CommandId':n,'CommandParam2':n,'NavId':n,'Weight':n}}
    before=copy.deepcopy(source);badge=item(n)
    Machine({},[]).run(program(module_suffix),{1:{'mcOvrData':badge},2:source})
    assert source==before and badge['mData']['value']==n
    assert badge['mData']['ExtraInfo']['circle']=='native' and badge['mData']['ExtraInfo']['DEPlayerRating'] is True
    assert badge['mcValue']['mData']['display']==grade(n) and badge['mcValue']['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)]
    # Shared badge repaint is marker-gated and must retain the numeric model.
    badge['mcValue']['mData']['display']=n;badge['mcValue']['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    a=Assembler();rating_value_draw_suffix(a);a.ret()
    Machine({},[]).run(a.finish(),{1:badge})
    assert badge['mData']['value']==n and badge['mcValue']['mData']['display']==grade(n)
    for selected in [False,True]:
        label=text(n);label['mData']['ExtraInfo']['fontColor']=0 if selected else 0xFFFFFF
        receiver={'mData':source,'mcTxt2':label,'mcTxt0':text('name'),'mcTxt1':text('HB'),'mcHighlight':{'_visible':selected}}
        Machine({},[]).run(program(list_suffix),{1:receiver})
        assert label['mData']['display']==grade(n)
        assert label['mData']['ExtraInfo']['fontColor']==(0 if selected else GRADE_COLORS[grade(n)])
        assert receiver['mcTxt0']['mData']['display']=='name' and receiver['mcTxt1']['mData']['display']=='HB'
        assert source==before and receiver['mcHighlight']['_visible']==selected
    for legacy in [False,True]:
        old=item(n);new=item(n)
        receiver={'mData':source,'mcPlayerInfo':{'_visible':legacy,'mcOvr':old},'mcPlayerModule':{'_visible':not legacy,'mData':{'ExtraInfo':{'roster':True,'overall':n}},'mcStat':new}}
        Machine({},[]).run(program(detail_suffix),{1:receiver})
        active=old if legacy else new;inactive=new if legacy else old
        assert active['mcValue']['mData']['display']==grade(n) and active['mData']['value']==n
        assert inactive['mcValue']['mData']['display']==n and inactive['mData']['value']==n
        assert active['mcValue']['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)]
        assert source==before and active['mcValue']['mData']['ExtraInfo']['font']=='native'
    for marked in [False,True]:
        badge=item(n);badge['mData']['ExtraInfo']['DEPlayerRating']=marked
        before=copy.deepcopy(badge['mData'])
        Machine({},[]).run(program(legacy_ovr_suffix),{1:badge})
        assert badge['mData']==before
        assert badge['mcValue']['mData']['display']==(grade(n) if marked else n)
        assert badge['mcValue']['mData']['ExtraInfo']['fontColor']==(GRADE_COLORS[grade(n)] if marked else 0xFFFFFF)

for hidden in [UNDEFINED,None,'?',-1,101,'85',float('nan'),float('inf')]:
    for suffix in [module_suffix,list_suffix,detail_suffix]:
        badge=item(hidden);t=text(hidden)
        receiver={'mData':{'ExtraInfo':{'Ovr':hidden}},'mcOvrData':badge,'mcTxt2':t,'mcPlayerInfo':{'_visible':True,'mcOvr':badge}}
        source={'key':1,'ExtraInfo':{'Ovr':hidden}}
        Machine({},[]).run(program(suffix),{1:receiver,2:source})
        assert not badge['mcValue']['calls'] and not t['calls']
for receiver in [{},{'mData':{}},{'mData':{'ExtraInfo':{}}}]:
    for suffix in [module_suffix,list_suffix,detail_suffix]:Machine({},[]).run(program(suffix),{1:receiver})
for key in [UNDEFINED,None]:
    badge=item(90);Machine({},[]).run(program(module_suffix),{1:{'mcOvrData':badge},2:{'key':key,'ExtraInfo':{'Ovr':90}}})
    assert not badge['mcValue']['calls']

class BoundedAssembler(Assembler):
    def __init__(self,limit):super().__init__();self.limit=limit
    def reg(self,n):
        assert 0<=n<self.limit,f'Register read {n} exceeds native frame {self.limit}'
        return super().reg(n)
    def store(self,n):
        assert 0<=n<self.limit,f'Register write {n} exceeds native frame {self.limit}'
        return super().store(n)

# Assert actual emitted register references, including the four-register list.
for registers,suffix in [(spec[2],spec[-1]) for spec in SPECS]+[(9,legacy_ovr_suffix)]:
    a=BoundedAssembler(registers);suffix(a);a.finish()

label=text(90);receiver={'mData':{'ExtraInfo':{'Ovr':90}},'mcTxt2':label,'mcHighlight':{'_visible':False}}
Machine({},[]).run(program(list_suffix),{1:receiver})
assert label['mData']['ExtraInfo']['fontColor']==GRADE_COLORS['A']
# Simulate native focus/unfocus resets on the same recycled widget.
receiver['mcHighlight']['_visible']=True;label['mData']['ExtraInfo']['fontColor']=0
Machine({},[]).run(program(list_suffix),{1:receiver})
assert label['mData']['ExtraInfo']['fontColor']==0
receiver['mcHighlight']['_visible']=False;label['mData']['ExtraInfo']['fontColor']=0xFFFFFF
receiver['mData']['ExtraInfo']['Ovr']=59;label['mData']['display']=59
Machine({},[]).run(program(list_suffix),{1:receiver})
assert label['mData']['display']=='F' and label['mData']['ExtraInfo']['fontColor']==GRADE_COLORS['F']
label['calls'].clear();Machine({},[]).run(program(list_suffix),{1:receiver})
assert not label['calls'],'An unchanged list draw invalidated native text/style again'

# Reproduce the observed child-after-parent repaint, rather than testing only
# direct labels immediately after the formation parent's callback.
for marked in [False,True]:
    for n,values in [(67,[62,85,89,68,64,85]),(90,[90,59,60,79,80,100])]:
        records=[{'ratingValue':v,'isFullyScouted':True,'ratingName':str(i)} for i,v in enumerate(values)]
        source=copy.deepcopy(records)
        slots={'mData':{'ExtraInfo':{f'AttributesData{i}':v for i,v in enumerate(records)}}}
        for i,v in enumerate(values):slots[f'mcValueSlotText{i}']=text(v)
        badge=item(n)
        module={'_visible':True,'mData':{'ExtraInfo':{'roster':True,'overall':n,'attributesSubpanelInfo':records}},'mcStat':badge,'mcInfoSlotAttributes':slots}
        if marked:
            detail={'mData':{'ExtraInfo':{'Ovr':n}},'mcPlayerInfo':{'_visible':False},'mcPlayerModule':module}
            Machine({},[]).run(program(detail_suffix),{1:detail})
        for _ in range(2):
            badge['mcValue']['mData']['display']=n;badge['mcValue']['mData']['ExtraInfo']['fontColor']=0xFFFFFF
            for i,v in enumerate(values):
                slots[f'mcValueSlotText{i}']['mData']['display']=v
                slots[f'mcValueSlotText{i}']['mData']['ExtraInfo']['fontColor']=0xFFFFFF
            Machine({},[]).run(program(badge_suffix),{1:module})
            Machine({},[]).run(program(attribute_slots_suffix),{1:slots})
            assert badge['mcValue']['mData']['display']==grade(n), 'Native roster=true identifies the player badge even without the formation marker'
            for i,v in enumerate(values):
                target=slots[f'mcValueSlotText{i}']['mData']
                assert target['display']==(grade(v) if marked else v)
                assert target['ExtraInfo']['fontColor']==(GRADE_COLORS[grade(v)] if marked else 0xFFFFFF)
            assert module['mData']['ExtraInfo']['overall']==n and badge['mData']['value']==n and records==source
        # Unrevealed and unsupported values must not be disclosed by the marker.
        records[0]['isFullyScouted']=False;slots['mcValueSlotText0']['mData']['display']='?'
        records[1]['ratingValue']='?';slots['mcValueSlotText1']['mData']['display']='?'
        Machine({},[]).run(program(attribute_slots_suffix),{1:slots})
        assert slots['mcValueSlotText0']['mData']['display']=='?' and slots['mcValueSlotText1']['mData']['display']=='?'

# A stale marker cannot convert a non-roster/stat badge or a mismatched value.
for roster,value in [(False,67),(True,45)]:
    badge=item(value);module={'mData':{'ExtraInfo':{'DEFormationPlayerRatings':True,'roster':roster,'overall':67}},'mcStat':badge}
    Machine({},[]).run(program(badge_suffix),{1:module})
    assert badge['mcValue']['mData']['display']==value
for regs,suffix in [(23,badge_suffix),(9,attribute_slots_suffix)]:
    a=BoundedAssembler(regs);suffix(a);a.ret();a.finish()
print('Passed: Formation Subs101 grade boundaries, native selected contrast, hidden values, both detail branches, marker repaint, jersey/commands/models preserved.')
