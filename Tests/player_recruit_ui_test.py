"""Exercise only player Overall labels, preserving risk/header/scouting data."""
import copy
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_recruit_ui import risk_player_suffix
from recruit_notes_vm import Machine,UNDEFINED


def widget(label):
    item={'mData':{'display':label,'ExtraInfo':{'fontColor':0xFFFFFF,'font':'native'}}}
    item['SetLabel']=lambda value:item['mData'].update(display=value)
    item['SetExtraInfo']=lambda extra:item['mData']['ExtraInfo'].update(extra)
    return item


a=Assembler();risk_player_suffix(a);program=a.finish()
for value in range(101):
    extra={'OVR':value,'RiskValue':87,'Position':'QB','IsHeader':False,'jersey':99}
    original=copy.deepcopy(extra);target=widget(value)
    receiver={'mData':{'ExtraInfo':extra},'mcOVR':target,'mcRiskText':widget('87%')}
    Machine({},[]).run(program,{1:receiver})
    grade='A' if value>=90 else 'B' if value>=80 else 'C' if value>=70 else 'D' if value>=60 else 'F'
    assert extra==original and receiver['mcRiskText']['mData']['display']=='87%'
    assert target['mData']['display']==grade
    assert target['mData']['ExtraInfo']=={'fontColor':GRADE_COLORS[grade],'font':'native'}
    # Native focus/reentry can repaint the value white; restore the same label.
    target['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    Machine({},[]).run(program,{1:receiver})
    assert target['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade]
for value in [UNDEFINED,None,'?','OVR','92',-1,101,float('nan'),float('inf')]:
    target=widget('?');receiver={'mData':{'ExtraInfo':{'OVR':value}},'mcOVR':target}
    Machine({},[]).run(program,{1:receiver})
    assert target['mData']['display']=='?' and target['mData']['ExtraInfo']['fontColor']==0xFFFFFF
target=widget('OVR')
Machine({},[]).run(program,{1:{'mData':{'ExtraInfo':{'OVR':95,'IsHeader':True}},'mcOVR':target}})
assert target['mData']['display']=='OVR'
for receiver in [{},{'mData':{}},{'mData':{'ExtraInfo':{'OVR':80}}}]:
    Machine({},[]).run(program,{1:receiver})
print('Passed: My School risk-player Overall101 boundaries/colors/reentry; headers, unknowns, risk percentages and numeric source data preserved.')
