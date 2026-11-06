"""Player/team scales, Blind native colors, and reused native text widgets."""
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from build_recruit_notes_ui import Assembler,grade_colors
from build_player_card_ui import header_suffix,team_module_suffix,rating_value_draw_suffix,ovr_item_suffix
from recruit_notes_vm import Machine,UNDEFINED
from grade_scales import label,COLORS,BLIND_LABEL

GLOBALS={'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9},'Color':{'UNFOCUS_BUTTON_FONT_COLOR':0x123456}}}
@lru_cache(None)
def program(builder,player_scale,team_scale,player=True,team=True,colors=True):
    a=Assembler();builder(a);p=a.finish();code=bytearray(p.code)
    for offsets,value in [(p.scale_offsets,player_scale),(p.team_scale_offsets,team_scale),
                          (p.fog_offsets,int(player)),(p.team_offsets,int(team)),(p.color_offsets,int(colors))]:
        for at in offsets:code[at]=value
    return replace(p,code=bytes(code))

def text(value):
    t={'mData':{'display':str(value),'ExtraInfo':{'fontColor':0x123456,'font':'native'}},'_width':80}
    t['SetLabel']=lambda v:t['mData'].update(display=v)
    t['SetExtraInfo']=lambda v:t['mData']['ExtraInfo'].update(v)
    return t
def badge(value,team=False):return {'mData':{'value':value,'ExtraInfo':{'DETeamRating':team,'DEPlayerRating':not team}},'mcValue':text(value)}
def color(value,scale,fog,colors):
    return 0x123456 if scale==4 or (not fog and not colors) else COLORS[label(value,scale)] if colors else 0xF3F0E7

for ps in range(5):
    for ts in range(5):
        for pf in [False,True]:
            for tf in [False,True]:
                for colors in [False,True]:
                    for n in [0,59,60,62,63,69,70,79,80,89,90,94,95,96,97,100]:
                        player=badge(n);team=badge(n,True)
                        Machine(GLOBALS,[]).run(program(header_suffix,ps,ts,pf,tf,colors),{1:{'mcRatingValueItem':player}})
                        Machine(GLOBALS,[]).run(program(team_module_suffix,ps,ts,pf,tf,colors),{1:{'mcOVRRating':team}})
                        for item,scale,fog in [(player,ps,pf),(team,ts,tf)]:
                            assert item['mcValue']['mData']['display']==(label(n,scale) if fog else str(n))
                            assert item['mcValue']['mData']['ExtraInfo']['fontColor']==color(n,scale,fog,colors)
                            assert item['mData']['value']==n
                            item['mcValue']['mData']['display']=str(n)
                            Machine(GLOBALS,[]).run(program(rating_value_draw_suffix,ps,ts,pf,tf,colors),{1:item})
                            assert item['mcValue']['mData']['display']==(label(n,scale) if fog else str(n))

# Real scale transitions reuse the same text child. Blind must restore the
# original native tint, including a native focus repaint between callbacks.
b=badge(95);receiver={'mcRatingValueItem':b}
for scale,expected in [(3,COLORS['Elite']),(4,0x123456),(1,COLORS['A']),(4,0x123456)]:
    Machine(GLOBALS,[]).run(program(header_suffix,scale,0),{1:receiver})
    assert b['mcValue']['mData']['ExtraInfo']['fontColor']==expected
b['mcValue']['mData']['ExtraInfo']['fontColor']=0x654321
Machine(GLOBALS,[]).run(program(header_suffix,4,0),{1:receiver})
assert b['mcValue']['mData']['ExtraInfo']['fontColor']==0x654321
for team in [False,True]:
    b=badge(96,team);b['mData']['display']='OVR'
    Machine(GLOBALS,[]).run(program(ovr_item_suffix,4 if not team else 1,4 if team else 1),{1:b})
    assert b['mcValue']['mData']['display']==BLIND_LABEL
    assert b['mcValue']['mData']['ExtraInfo']['fontColor']==0x123456
child=text('–');widget={'mData':{'ExtraInfo':{'Points':'–'}},'mcPoints':child}
Machine(GLOBALS,[]).run(program(grade_colors,4,0),{1:widget})
assert child['mData']['ExtraInfo']['fontColor']==0x123456
for source in ['Elite','A+','C–A','?','–']:
    b=badge(source)
    Machine(GLOBALS,[]).run(program(rating_value_draw_suffix,4,0),{1:b})
    assert b['mcValue']['mData']['display']==BLIND_LABEL
    assert b['mcValue']['mData']['ExtraInfo']['fontColor']==0x123456
    assert b['mData']['value']==source
print('Passed: all25 independent player/team scale combinations, Blind numeric/color-only and fog modes, native tint/focus restoration, marked child repaint, and unchanged rating sources.')
