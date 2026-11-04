"""Execute isolated overlay display suffix without a game or gameplay changes."""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_ingame_ui import FIELDS,player_ratings_suffix
from recruit_notes_vm import Machine


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
