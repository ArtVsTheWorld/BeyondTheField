"""Execute final display suffixes; numeric mode/data/comparisons remain native."""
from pathlib import Path
import copy
import math
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler
from build_player_playcall_ui import (ASSETS,individual_suffix,comparison_suffix,impact_suffix,
                                     lineup_suffix,lineup_stat_suffix,trench_suffix)
from recruit_notes_vm import Machine,UNDEFINED


def program(suffix):
    a=Assembler();suffix(a);return a.finish()


def text(value='native',color=0xFFFFFF):
    target={'mData':{'display':value,'ExtraInfo':{'fontColor':color,'font':'native','size':48}}}
    target['SetLabel']=lambda label:target['mData'].update(display=label)
    return target


def expected(value):return 'A' if value>=90 else 'B' if value>=80 else 'C' if value>=70 else 'D' if value>=60 else 'F'
values=[*range(101),UNDEFINED,None,'?',-1,101,'85',math.nan,math.inf]
for value in values:
    valid=isinstance(value,int) and 0<=value<=100
    rows=[{'value':value,'valueStr':str(value),'label':'Acceleration'},
          {'value':85,'valueStr':'85','label':'Change of Direction'},
          {'value':85,'valueStr':'85','label':'Speed'}]
    row_values=[dict(r) for r in rows]
    for mode in [0,1,2,UNDEFINED,None,'2',3]:
        receiver={f'mcStat{i}':text() for i in range(3)}
        receiver['mcLabel0']=text('ACCELERATION');receiver['mPlayerId']=901
        Machine({},[]).run(program(individual_suffix),{1:receiver,3:rows,7:mode})
        assert receiver['mcStat0']['mData']['display']==(expected(value) if mode==2 and valid else 'native')
        assert receiver['mcStat1']['mData']['display']==('B' if mode==2 else 'native')
        assert all(receiver[f'mcStat{i}']['mData']['ExtraInfo']=={'fontColor':0xFFFFFF,'font':'native','size':48} for i in range(3))
        assert receiver['mcLabel0']['mData']['display']=='ACCELERATION' and receiver['mPlayerId']==901
    assert rows[0]['value'] is value and rows[0]['valueStr']==row_values[0]['valueStr'] and rows[1:]==row_values[1:]

# Actual pictured panel must read B/B/B. Reusing the same widgets for statistics
# later must restore their native numeric labels without inheriting new colors.
receiver={f'mcStat{i}':text() for i in range(3)}
rows=[{'value':v} for v in [89,85,85]]
Machine({},[]).run(program(individual_suffix),{1:receiver,3:rows,7:2})
assert [receiver[f'mcStat{i}']['mData']['display'] for i in range(3)]==['B','B','B']
for i,v in enumerate(['95','7.6','3/4']):receiver[f'mcStat{i}']['mData']['display']=v
Machine({},[]).run(program(individual_suffix),{1:receiver,3:rows,7:1})
assert [receiver[f'mcStat{i}']['mData']['display'] for i in range(3)]==['95','7.6','3/4']
print('Passed: individual ratings101 boundaries, strict mode2/unknown gates, original source/order/labels/fonts preserved and statistics-mode reentry stays numeric.')

for mode in [0,1,2,UNDEFINED,None,'2']:
    for value in values:
        valid=isinstance(value,int) and 0<=value<=100
        rows=[{'leftNum':value,'rightNum':80,'leftNumStr':str(value),'rightNumStr':'80','reverseArrow':False}]
        receiver={f'mcNum{s}{i}':text(color=0x888888 if s=='Right' else 0xFFFFFF) for i in range(3) for s in ['Left','Right']}
        receiver['mcArrowLeft0']={'_visible':True};receiver['mcArrowRight0']={'_visible':False}
        Machine({},[]).run(program(comparison_suffix),{1:receiver,3:rows,14:mode})
        assert receiver['mcNumLeft0']['mData']['display']==(expected(value) if mode==2 and valid else 'native')
        assert receiver['mcNumRight0']['mData']['display']==('B' if mode==2 else 'native')
        assert rows[0]['leftNum'] is value and rows[0]['rightNum']==80 and rows[0]['reverseArrow'] is False
        assert receiver['mcNumRight0']['mData']['ExtraInfo']['fontColor']==0x888888
        assert receiver['mcArrowLeft0']=={'_visible':True} and receiver['mcArrowRight0']=={'_visible':False}
for value in values:
    receiver={f'mcValue{i}':text() for i in range(3)}
    rows=[{'value':value},{'value':92}]
    Machine({},[]).run(program(impact_suffix),{1:receiver,4:rows})
    assert receiver['mcValue0']['mData']['display']==(expected(value) if isinstance(value,int) and 0<=value<=100 else 'native')
    assert receiver['mcValue1']['mData']['display']=='A' and rows[0]['value'] is value
print('Passed: comparison ratings101 boundaries and mode guards, native numeric comparison/arrow/foreground preservation; impact rating-only labels and source values preserved.')


def provider(rows,count=None):
    return {'GetNumItems':lambda:len(rows) if count is None else count,
            'GetItemData':lambda index:rows[int(index)]}


for suffix,field,providers in [(lineup_suffix,'OverallText',['mDataProvider']),
                               (lineup_stat_suffix,'ConferenceText',['mDataProvider']),
                               (trench_suffix,'OverallText',['mLeftDataProvider','mRightDataProvider'])]:
    for value in values:
        rows=[{'display':'A. Player','value':101,'ExtraInfo':{'OverallText':85,'ConferenceText':92,
                 'StadiumText':99,'PositionText':'QB','weight':215,'ShowBottomDivider':True,
                 'OverallUnfocusedStyle':{'fontColor':0xFFFFFF},'ConferenceUnFocusedStyle':{'fontColor':0x888888},field:value}},
              {'display':'B. Player','value':102,'ExtraInfo':{field:60}}]
        before=copy.deepcopy(rows)
        receiver={name:provider(rows) for name in providers}
        receiver.update(mcLeftNumber=text('315'),mcRightNumber=text('287'))
        Machine({},[]).run(program(suffix),{1:receiver})
        valid=isinstance(value,int) and 0<=value<=100
        assert rows[0]['ExtraInfo'][field]==expected(value) if valid else rows[0]['ExtraInfo'][field] is value
        assert rows[1]['ExtraInfo'][field]=='D'
        for index,row in enumerate(rows):
            for key,v in row.items():
                if key!='ExtraInfo':assert v==before[index][key]
            assert {k:v for k,v in row['ExtraInfo'].items() if k!=field}=={k:v for k,v in before[index]['ExtraInfo'].items() if k!=field}
        assert receiver['mcLeftNumber']['mData']['display']=='315' and receiver['mcRightNumber']['mData']['display']=='287'
    for count in [-1,65,'2',math.nan]:
        rows=[{'ExtraInfo':{field:90}}];receiver={name:provider(rows,count) for name in providers}
        Machine({},[]).run(program(suffix),{1:receiver});assert rows==[{'ExtraInfo':{field:90}}]
    for receiver in [{},{providers[0]:None},{providers[0]:provider([])},
                     {providers[0]:provider([None,{}, {'ExtraInfo':{}}])}]:
        Machine({},[]).run(program(suffix),{1:receiver})
print('Passed: lineup/key-stat/trench all101 OVR boundaries, only method-specific display cells change; key stats, records, jerseys, years, weights, native styles and source IDs preserved.')

left=[{'value':701,'ExtraInfo':{'OverallText':92,'weight':315,'PositionText':'LT'}}]
right=[{'value':809,'ExtraInfo':{'OverallText':63,'weight':287,'PositionText':'RE'}},
       {'value':810,'ExtraInfo':{'OverallText':78,'weight':302,'PositionText':'DT'}}]
receiver={'mLeftDataProvider':provider(left),'mRightDataProvider':provider(right)}
Machine({},[]).run(program(trench_suffix),{1:receiver})
assert left==[{'value':701,'ExtraInfo':{'OverallText':'A','weight':315,'PositionText':'LT'}}]
assert right==[{'value':809,'ExtraInfo':{'OverallText':'D','weight':287,'PositionText':'RE'}},
               {'value':810,'ExtraInfo':{'OverallText':'C','weight':302,'PositionText':'DT'}}]
print('Passed: distinct left/right Trench providers, unequal row counts and different grade bands; weights/IDs/positions preserved.')

class BoundedAssembler(Assembler):
    def __init__(self,limit):super().__init__();self.limit=limit
    def reg(self,n):assert 0<=n<self.limit,(n,self.limit);super().reg(n)
    def store(self,n):assert 0<=n<self.limit,(n,self.limit);super().store(n)
for _,_,specs in ASSETS:
    for _,_,registers,_,_,_,suffix in specs:
        a=BoundedAssembler(registers);suffix(a);a.finish()
print('Passed: all six native fixed frames; separate program sets preserve asset isolation.')
