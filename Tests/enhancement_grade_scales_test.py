"""Execute each configurable display path; original player models stay numeric."""
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,grade_colors,grade_palette
from build_player_card_ui import header_suffix,numeric_display_grade,team_module_suffix,ovr_item_suffix,rating_value_draw_suffix
from recruit_notes_vm import Machine,UNDEFINED
from grade_scales import label,COLORS

def program(builder,scale,colors=True,fog=True,team=True):
    a=Assembler();builder(a);p=a.finish();code=bytearray(p.code)
    for at in p.scale_offsets+p.team_scale_offsets:code[at]=scale
    for at in p.color_offsets:code[at]=int(colors)
    for at in p.fog_offsets:code[at]=int(fog)
    for at in p.team_offsets:code[at]=int(team)
    return replace(p,code=bytes(code))

for scale in range(4):
    for colors in [True,False]:
        for value in range(101):
            seen=[];styles=[]
            child={'mData':{'display':str(value),'ExtraInfo':{}},'SetLabel':lambda text:seen.append(text),'SetExtraInfo':lambda extra:styles.append(extra)}
            data={'value':value};receiver={'mcRatingValueItem':{'mData':data,'mcValue':child}}
            Machine({'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9}}},[]).run(program(header_suffix,scale,colors),{1:receiver})
            assert seen==[label(value,scale)] and data['value']==value
            assert styles[0]['fontColor']==(COLORS[label(value,scale)] if colors else 0xF3F0E7)
            if scale in (1,3):assert styles[0]['resize']==9 and styles[0]['maxNumLines']==1
            def converter(a):
                numeric_display_grade(a,0,0,'end','display');a.label('end');a.reg(0);a.raw(0x3E)
            assert Machine({},[]).run(program(converter,scale,colors),{0:str(value)})==label(value,scale)
        for value in ['?',None,UNDEFINED,-1,101,' 64','64 ','064','64.0','+64','64 yards','Hidden']:
            p=program(converter,scale,colors)
            result=Machine({},[]).run(p,{0:value})
            assert result is value or result==value,(scale,value,result)
        # Midpoint range colors use only the revealed range, including ranges
        # crossing multiple plus/minus bands. Unknown ratings stay hidden.
        for text,expected in grade_palette(scale).items():
            style={};child={'mData':{'ExtraInfo':style},'SetExtraInfo':lambda extra:style.update(extra)}
            widget={'mData':{'ExtraInfo':{'Points':text}},'mcPoints':child}
            globals_={'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9},'Color':{'UNFOCUS_BUTTON_FONT_COLOR':0xABCDEF}}}
            Machine(globals_,[]).run(program(grade_colors,scale,colors),{1:widget})
            assert style['fontColor']==(expected if colors else 0xABCDEF)

# Changing the setting must invalidate a reused widget's cached grade style.
style={};child={'mData':{'ExtraInfo':style},'SetExtraInfo':lambda extra:style.update(extra)}
widget={'mData':{'ExtraInfo':{'Points':'A'}},'mcPoints':child}
globals_={'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9},'Color':{'UNFOCUS_BUTTON_FONT_COLOR':0xABCDEF}}}
for colors in [True,False,True]:
    Machine(globals_,[]).run(program(grade_colors,0,colors),{1:widget})
    assert style['fontColor']==(COLORS['A'] if colors else 0xABCDEF)
def text_widget(value):
    child={'mData':{'display':str(value),'ExtraInfo':{'fontColor':0x123456,'font':'native'}}}
    child['SetLabel']=lambda text:child['mData'].update(display=text)
    child['SetExtraInfo']=lambda style:child['mData']['ExtraInfo'].update(style)
    return child

for scale in range(4):
    for fog in [True,False]:
        for team in [True,False]:
            for colors in [True,False]:
                for value in [0,59,60,69,70,79,80,89,90,94,95,96,97,100]:
                    child=text_widget(value);model={'value':value};receiver={'mcRatingValueItem':{'mData':model,'mcValue':child}}
                    Machine({'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9}}},[]).run(program(header_suffix,scale,colors,fog,team),{1:receiver})
                    assert child['mData']['display']==(label(value,scale) if fog else str(value))
                    expected=COLORS[label(value,scale)] if colors else 0xF3F0E7 if fog else 0x123456
                    assert child['mData']['ExtraInfo']['fontColor']==expected and model['value']==value
                    badges={name:{'mData':{'value':value,'ExtraInfo':{}},'mcValue':text_widget(value)} for name in ['mcOVRRating','mcOFFRating','mcDEFRating']}
                    Machine({'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9}}},[]).run(program(team_module_suffix,scale,colors,fog,team),{1:badges})
                    for badge in badges.values():
                        assert badge['mcValue']['mData']['display']==(label(value,scale) if team else str(value))
                        assert badge['mData']['value']==value
                        # Its own native Draw can repaint after its parent's Draw.
                        badge['mcValue']['mData']['display']=str(value)
                        Machine({'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9}}},[]).run(program(rating_value_draw_suffix,scale,colors,fog,team),{1:badge})
                        assert badge['mcValue']['mData']['display']==(label(value,scale) if team else str(value))
                    child=text_widget(value);model={'value':value,'display':'OVR'}
                    Machine({'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9}}},[]).run(program(ovr_item_suffix,scale,colors,fog,team),{1:{'mData':model,'mcValue':child}})
                    assert child['mData']['display']==(label(value,scale) if fog else str(value)) and model['value']==value
                child=text_widget(96);widget={'mData':{'ExtraInfo':{'Points':96}},'mcPoints':child}
                Machine({'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9},'Color':{'UNFOCUS_BUTTON_FONT_COLOR':0x123456}}},[]).run(program(grade_colors,scale,colors,fog,team),{1:widget})
                assert child['mData']['ExtraInfo']['fontColor']==(COLORS[label(96,scale)] if colors else 0x123456)
                assert widget['mData']['ExtraInfo']['Points']==96
print('Passed: four scales, independent player/team fog and colors, numeric colors, six-option semantics, native child repaint, Select Your Team Top Players, scouting colors, hidden values and unchanged source ratings.')
