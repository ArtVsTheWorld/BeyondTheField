"""Execute isolated overlay display suffix without a game or gameplay changes."""
from pathlib import Path
import copy
import math
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_ingame_ui import (FIELDS,player_ratings_suffix,key_player_suffix,
                                  playcall_player_suffix,substitution_player_suffix,depth_panel_player_suffix,SPECS)
from recruit_notes_vm import Machine,UNDEFINED


def widget(value):
    result={'mData':{'display':value,'ExtraInfo':{'fontColor':0xFFFFFF,'font':'native'}}}
    result['SetLabel']=lambda label:result['mData'].update(display=label)
    result['SetExtraInfo']=lambda extra:result['mData']['ExtraInfo'].update(extra)
    return result


a=Assembler();player_ratings_suffix(a);program=a.finish()
for rating in range(101):
    grade='A' if rating>=90 else 'B' if rating>=80 else 'C' if rating>=70 else 'D' if rating>=60 else 'F'
    extra={field:rating for field,_ in FIELDS};extra.update(overallrating=rating,x=128,y=256,jersey=99,score=42)
    original=copy.deepcopy(extra);receiver={'mData':{'ExtraInfo':extra}}
    for _,name in FIELDS:receiver[name]=widget(rating)
    ovr={'mData':{'value':rating,'ExtraInfo':{}},'mcValue':widget(rating)};receiver['mcOvr']=ovr
    Machine({},[]).run(program,{1:receiver})
    assert extra==original and ovr['mData']['value']==rating
    for target in [receiver[name] for _,name in FIELDS]+[ovr['mcValue']]:
        assert target['mData']['display']==grade
        assert target['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade]
        assert target['mData']['ExtraInfo']['font']=='native'
for hidden in [None,'?',-1,101,'85']:
    receiver={'mData':{'ExtraInfo':{field:hidden for field,_ in FIELDS}},'mcOvr':{'mData':{'value':hidden},'mcValue':widget(hidden)}}
    for _,name in FIELDS:receiver[name]=widget(hidden)
    Machine({},[]).run(program,{1:receiver})
    assert all(receiver[name]['mData']['display']==hidden for _,name in FIELDS)
    assert receiver['mcOvr']['mcValue']['mData']['display']==hidden
receiver={'mData':{'ExtraInfo':{}},'mcOvr':{'mData':{'value':85},'mcValue':widget(85),'_visible':False}}
Machine({},[]).run(program,{1:receiver})
assert receiver['mcOvr']['mcValue']['mData']['display']==85 and receiver['mcOvr']['_visible'] is False
print('Passed: all101 coach-camera grade/color boundaries; hidden values, model values, fonts, coordinates, jerseys and scores preserved.')

for suffix,field,name,colored,tail in [
        (key_player_suffix,'overall','mcOVR',True,' OVR'),
        (playcall_player_suffix,'PrimaryTargetOVR','mcOvrStat',False,''),
        (substitution_player_suffix,'overallRating','mcOvrStat',False,''),
        (depth_panel_player_suffix,'PlayerOvr','mcOvr',False,'')]:
    a=Assembler();suffix(a);program=a.finish()
    for visible in [True,False,UNDEFINED]:
        for value in [*range(101),UNDEFINED,None,'?',-1,101,'85',math.nan,math.inf]:
            child=widget('native');child['_visible']=visible
            child['mData']['ExtraInfo']['fontColor']=0 # Native focused black
            extra={field:value,'PrimaryTargetPlayerId':42,'jersey':11,'numPlays':7,
                   'avgYards':7.6,'goToPercent':20,'Ovr':85}
            receiver={'mData':{'ExtraInfo':extra},name:child}
            Machine({},[]).run(program,{1:receiver})
            assert receiver['mData']['ExtraInfo'] is extra and extra[field] is value
            assert extra['jersey']==11 and extra['numPlays']==7 and extra['avgYards']==7.6 and extra['goToPercent']==20 and extra['Ovr']==85
            if visible is True and isinstance(value,int) and 0<=value<=100:
                grade='A' if value>=90 else 'B' if value>=80 else 'C' if value>=70 else 'D' if value>=60 else 'F'
                assert child['mData']['display']==grade+tail
                assert child['mData']['ExtraInfo']['fontColor']==(GRADE_COLORS[grade] if colored else 0)
            else:assert child['mData']['display']=='native' and child['mData']['ExtraInfo']['fontColor']==0
    for receiver in [{},{'mData':{}},{'mData':{'ExtraInfo':{field:90}}}]:
        Machine({},[]).run(program,{1:receiver})
    # A recycled row must not reuse its prior grade when the player changes.
    child=widget('native');child['_visible']=True
    extra={field:92};receiver={'mData':{'ExtraInfo':extra},name:child}
    Machine({},[]).run(program,{1:receiver});assert child['mData']['display']=='A'+tail
    extra[field]=63;child['mData']['display']='63';child['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    Machine({},[]).run(program,{1:receiver});assert child['mData']['display']=='D'+tail
    if not colored:assert child['mData']['ExtraInfo']['fontColor']==0xFFFFFF
    # This suffix never touches a group-only play-count/yards/percentage row.
    group={'numPlays':20,'avgYards':17.7,'goToPercent':30}
    child=widget(20);child['_visible']=True
    Machine({},[]).run(program,{1:{'mData':{'ExtraInfo':group},name:child}})
    assert child['mData']['display']==20 and group=={'numPlays':20,'avgYards':17.7,'goToPercent':30}

assert all(newregs==regs for off,argc,regs,flags,size,expected,newregs,suffix in SPECS[1:]), 'Playcall labels must attach safely on fixed-frame dispatch'
class BoundedAssembler(Assembler):
    def __init__(self,limit):super().__init__();self.limit=limit
    def reg(self,n):assert 0<=n<self.limit,(n,self.limit);super().reg(n)
    def store(self,n):assert 0<=n<self.limit,(n,self.limit);super().store(n)
for off,argc,regs,flags,size,expected,newregs,suffix in SPECS:
    a=BoundedAssembler(newregs);suffix(a);a.finish()
print('Passed:4 in-game player label paths,101 boundaries each, hidden/invalid/absent fields, recycled players, native focus colors and non-rating playcall statistics.')
