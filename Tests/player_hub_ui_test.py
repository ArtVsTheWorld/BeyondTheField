from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_hub_ui import formation_suffix,ovr_template_suffix
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
print('Passed: player-only hub labels, all101 grade boundaries/colors, source Ovr unchanged, ordinary numbers/team ratings preserved and hidden previews untouched.')
