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


def machine():return Machine({},[])


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
    def update(index,property_name,value):rows[int(index)]['ExtraInfo'][property_name]=value
    return {'GetNumItems':lambda:len(rows) if count is None else count,
            'GetItemData':lambda index:rows[int(index)],'UpdateProperty':update}


for suffix,field,providers in [(lineup_suffix,'OverallText',['mDataProvider']),
                               (lineup_stat_suffix,'ConferenceText',['mDataProvider']),
                               (trench_suffix,'OverallText',['mLeftDataProvider','mRightDataProvider'])]:
    for value in [*values,*map(str,range(101)),'',' 85','85 ','085','85.0','85%','+85','-1','101']:
        rows=[{'display':'A. Player','value':101,'ExtraInfo':{'OverallText':85,'ConferenceText':92,
                 'StadiumText':99,'PositionText':'QB','weight':215,'ShowBottomDivider':True,
                 'OverallUnfocusedStyle':{'fontColor':0xFFFFFF},'ConferenceUnFocusedStyle':{'fontColor':0x888888},field:value}},
              {'display':'B. Player','value':102,'ExtraInfo':{field:60}}]
        before=copy.deepcopy(rows)
        receiver={name:provider(rows) for name in providers}
        receiver.update(mcLeftNumber=text('315'),mcRightNumber=text('287'))
        old_extra=rows[0]['ExtraInfo'];old_style=old_extra['OverallUnfocusedStyle']
        machine().run(program(suffix),{1:receiver})
        valid=isinstance(value,int) and 0<=value<=100 or isinstance(value,str) and value in set(map(str,range(101)))
        assert rows[0]['ExtraInfo'][field]==expected(int(value)) if valid else rows[0]['ExtraInfo'][field] is value
        assert rows[0]['ExtraInfo'] is old_extra
        assert rows[0]['ExtraInfo']['OverallUnfocusedStyle'] is old_style
        assert rows[1]['ExtraInfo'][field]=='D'
        for index,row in enumerate(rows):
            for key,v in row.items():
                if key!='ExtraInfo':assert v==before[index][key]
            assert {k:v for k,v in row['ExtraInfo'].items() if k!=field}=={k:v for k,v in before[index]['ExtraInfo'].items() if k!=field}
        assert receiver['mcLeftNumber']['mData']['display']=='315' and receiver['mcRightNumber']['mData']['display']=='287'
    for count in [-1,65,'2',math.nan]:
        rows=[{'ExtraInfo':{field:90}}];receiver={name:provider(rows,count) for name in providers}
        machine().run(program(suffix),{1:receiver});assert rows==[{'ExtraInfo':{field:90}}]
    for receiver in [{},{providers[0]:None},{providers[0]:provider([])},
                     {providers[0]:provider([None,{}, {'ExtraInfo':{}}])}]:
        machine().run(program(suffix),{1:receiver})
print('Passed: lineup/key-stat/trench all101 OVR boundaries, only method-specific display cells change; key stats, records, jerseys, years, weights, native styles and source IDs preserved.')

left=[{'value':701,'ExtraInfo':{'OverallText':92,'weight':315,'PositionText':'LT'}}]
right=[{'value':809,'ExtraInfo':{'OverallText':63,'weight':287,'PositionText':'RE'}},
       {'value':810,'ExtraInfo':{'OverallText':78,'weight':302,'PositionText':'DT'}}]
receiver={'mLeftDataProvider':provider(left),'mRightDataProvider':provider(right)}
machine().run(program(trench_suffix),{1:receiver})
assert left==[{'value':701,'ExtraInfo':{'OverallText':'A','weight':315,'PositionText':'LT'}}]
assert right==[{'value':809,'ExtraInfo':{'OverallText':'D','weight':287,'PositionText':'RE'}},
               {'value':810,'ExtraInfo':{'OverallText':'C','weight':302,'PositionText':'DT'}}]
print('Passed: distinct left/right Trench providers, unequal row counts and different grade bands; weights/IDs/positions preserved.')

# Native list binding copies ExtraInfo into a renderer. A raw provider mutation
# cannot update that renderer; UpdateProperty -> SetExtraInfo does. Model that
# distinction instead of testing only the final backing dictionaries. This is
# the verified native field-specific UpdateProperty -> VirtualItemAdapter path.
for suffix,field,names in [(trench_suffix,'OverallText',['mLeftDataProvider','mRightDataProvider']),
                          (lineup_suffix,'OverallText',['mDataProvider']),
                          (lineup_stat_suffix,'ConferenceText',['mDataProvider'])]:
    for value in [*range(101),*map(str,range(101))]:
        receiver={};visible=[];notifications=[];source_rows=[]
        for name in names:
            original={'OverallText':64,'ConferenceText':89,'StadiumText':5,'PositionText':'LT',field:value,
                      'OverallUnfocusedStyle':{'fontColor':0xFFFFFF},'callback':lambda:None}
            row={'value':812,'display':'A. Lineman','ExtraInfo':original};source_rows.append((row,original))
            cached=dict(original);visible.append(cached)
            def update(index,prop,new,old=original,cache=cached,row=row):
                assert index==0 and prop==field and old[prop] is value
                # DataItemUtil.SetProperty updates the provider's one cell.
                old[prop]=new
                # VirtualItemAdapter then copies the bound renderer's ExtraInfo
                # and invokes SetExtraInfo, whose merge invalidates the label.
                fresh=dict(cache);fresh[prop]=new
                assert fresh['OverallUnfocusedStyle'] is cache['OverallUnfocusedStyle']
                assert fresh['callback'] is cache['callback']
                assert cache[prop] is value
                notifications.append((index,prop));cache.update(fresh)
            receiver[name]={'GetNumItems':lambda:1,'GetItemData':lambda index,row=row:row,'UpdateProperty':update}
        machine().run(program(suffix),{1:receiver})
        assert len(notifications)==len(names)
        assert all(cache[field]==expected(int(value)) for cache in visible)
        assert all(row['value']==812 and row['ExtraInfo'] is old for row,old in source_rows)
        # Second pass sees a letter and must not notify or clone repeatedly.
        machine().run(program(suffix),{1:receiver});assert len(notifications)==len(names)
print('Passed: bound native-shaped row repaint via field-specific provider notification for numeric and canonical string ratings; unchanged style/function identities, source IDs and repeat-pass no-op.')

class BoundedAssembler(Assembler):
    def __init__(self,limit):super().__init__();self.limit=limit
    def reg(self,n):assert 0<=n<self.limit,(n,self.limit);super().reg(n)
    def store(self,n):assert 0<=n<self.limit,(n,self.limit);super().store(n)
for _,_,specs in ASSETS:
    for _,_,registers,_,_,_,suffix in specs:
        a=BoundedAssembler(registers);suffix(a);a.finish()
        assert len(a.code)+1368<32768
print('Passed: all six native fixed frames; separate program sets preserve asset isolation.')
