from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_hub_ui import formation_suffix,ovr_template_suffix,comparison_stat_suffix,ATTRIBUTE_NAMES,SPECS
from build_player_card_ui import rating_value_draw_suffix
from recruit_notes_vm import Machine,UNDEFINED


def program(suffix):
    a=Assembler();suffix(a);return a.finish()


def grade(n):return 'A' if n>=90 else 'B' if n>=80 else 'C' if n>=70 else 'D' if n>=60 else 'F'


for n in range(101):
    player={'Ovr':n,'JerseyNumber':n,'PlayerSurname':'Player','Position':'QB'}
    text={'mData':{'display':str(n),'ExtraInfo':{'font':'unchanged'}}}
    text['SetLabel']=lambda value:text['mData'].update(display=value)
    text['SetExtraInfo']=lambda value:text['mData']['ExtraInfo'].update(value)
    receiver={'FIELDED_PLAYERS':1,'mcPlayerOVRValue0':text,'teamOverall':n,'teamOffense':n,'teamDefense':n}
    Machine({},[]).run(program(formation_suffix),{1:receiver,3:[player]})
    assert text['mData']['display']==grade(n) and text['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)]
    assert text['mData']['ExtraInfo']['font']=='unchanged'
    assert player['Ovr']==n and player['JerseyNumber']==n and receiver['teamOverall']==n and receiver['teamOffense']==n and receiver['teamDefense']==n
    style={'font':'native','size':28,'fontColor':0xFFFFFF}
    style['CloneAndModify']=lambda patch:{**style,**patch}
    data={'value':n,'display':'OVR','ExtraInfo':{'ValueTextStyle':style,'unrelated':12}}
    result=Machine({},[]).run(program(ovr_template_suffix),{2:data})
    assert result is data and data['value']==grade(n) and data['display']=='OVR' and data['ExtraInfo']['unrelated']==12
    assert data['ExtraInfo']['ValueTextStyle']['font']=='native' and data['ExtraInfo']['ValueTextStyle']['fontColor']==GRADE_COLORS[grade(n)]
    # Player-watch templates omit ValueTextStyle. Its private marker lets the
    # shared badge Draw recolor the existing native text without inventing a font.
    default_data={'value':n};Machine({},[]).run(program(ovr_template_suffix),{2:default_data})
    assert default_data['ExtraInfo']['DEPlayerRating'] is True
    child={'mData':{'display':grade(n),'ExtraInfo':{'font':'native-default','fontColor':0xFFFFFF}}}
    child['SetLabel']=lambda value:child['mData'].update(display=value)
    child['SetExtraInfo']=lambda value:child['mData']['ExtraInfo'].update(value)
    suffix=Assembler();rating_value_draw_suffix(suffix);suffix.ret()
    Machine({},[]).run(suffix.finish(),{1:{'mData':default_data,'mcValue':child}})
    assert child['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)] and child['mData']['ExtraInfo']['font']=='native-default'
for n in ['?','Hidden',-1,101,UNDEFINED,None]:
    data={'value':n};Machine({},[]).run(program(ovr_template_suffix),{2:data});assert data=={'value':n}
for receiver in [{},{'FIELDED_PLAYERS':11}]:
    Machine({},[]).run(program(formation_suffix),{1:receiver,3:[]})

comparison=program(comparison_stat_suffix)
assert len(comparison.code)<32768
assert SPECS[-1][3:6]==(2,5,5) # native argc and fixed register frame
def comparison_result(name,value):
    entry={'StatName':name,'StatValue':value}
    team={'Stats':[{'StatName':'Passing Yards','StatValue':312},entry]}
    receiver={'mTeamList':[{'Stats':[]},team]}
    style={'font':'native','fontColor':0xFFFFFF,'resizeWidth':84,'hAlign':'CENTER'}
    data={'display':value,'ExtraInfo':style}
    result=Machine({},[]).run(comparison,{1:receiver,2:data,3:1,4:1})
    assert result is data and entry=={'StatName':name,'StatValue':value}
    assert team['Stats'][0]['StatValue']==312
    assert all(style[k]==v for k,v in {'font':'native','resizeWidth':84,'hAlign':'CENTER'}.items())
    return result
for n in range(101):
    for name in ('Awareness','SPEED','acceleration','Catching'):
        for value in (n,str(n)):
            data=comparison_result(name,value)
            assert data['display']==grade(n) and data['ExtraInfo']['fontColor']==GRADE_COLORS[grade(n)]
for name in ATTRIBUTE_NAMES:
    for form in (name,name.upper(),name.lower()):
        assert comparison_result(form,85)['display']=='B'
for name in ('Passing Yards','Rushing Yards','Completions','Passing TD','INT','REC','TKL','Yards','Rank','NIL','Unknown'):
    for n in range(101):
        for value in (n,str(n)):
            data=comparison_result(name,value)
            assert data['display']==value and data['ExtraInfo']['fontColor']==0xFFFFFF
for value in ('?', 'Hidden', '', ' 85', '85 ', '+85', '085', '85%', '85.0', '85 yards', '1,000', -1,101,None,UNDEFINED,float('nan')):
    data=comparison_result('Awareness',value)
    assert data['ExtraInfo']['fontColor']==0xFFFFFF
print('Passed: player-only hub labels/comparison attributes, all101 grade boundaries/colors, source values unchanged, ordinary statistics/team ratings preserved and hidden previews untouched.')
