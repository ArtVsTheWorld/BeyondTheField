"""Execute isolated overlay display suffix without a game or gameplay changes."""
from pathlib import Path
import copy
import math
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,GRADE_COLORS
from build_player_ingame_ui import (FIELDS,player_ratings_suffix,key_player_suffix,
                                  playcall_player_suffix,substitution_player_suffix,depth_panel_player_suffix,
                                  preplay_sub_player_suffix,kicker_range_suffix,injury_module_suffix,SPECS,KICKER_SPECS,INJURY_SPECS)
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
        (depth_panel_player_suffix,'PlayerOvr','mcOvr',False,''),
        (preplay_sub_player_suffix,'Overall','mcOverall',False,'')]:
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
for off,argc,regs,flags,size,expected,newregs,suffix in [*SPECS,*KICKER_SPECS,*INJURY_SPECS]:
    a=BoundedAssembler(newregs);suffix(a);a.finish()
print('Passed:5 in-game player label paths,101 boundaries each, hidden/invalid/absent fields, recycled players, native focus colors and non-rating playcall statistics.')

# Actual pre-snap substitution shape: five visible player rows include the
# adjusted OVR plus a player-name toggle, wear-and-tear text and a status meter.
# Grade the adjusted value without changing base ratings, toggle selection,
# injury penalties, slider steps, composure or pending boost flags.
a=Assembler();preplay_sub_player_suffix(a);preplay=a.finish()
for adjusted,expected in [(66,'D'),(72,'C'),(67,'D'),(80,'B'),(59,'F'),(90,'A')]:
    extra={'Overall':adjusted,'BaseOverall':92,'Position':'QB','WearandTear':'-3',
           'Status':4,'IsCaptain':True,'IsHot':False,'IsCold':True,'IsPendingBoost':True}
    original=copy.deepcopy(extra)
    label=widget(str(adjusted));label['_visible']=True
    toggle={'mData':{'value':1,'display':'C. Whitaker - QB1'}}
    status={'mData':{'value':4,'ExtraInfo':{'Min':0,'Max':5,'NumberOfSteps':5}}}
    wear=widget('-3')
    receiver={'mData':{'ExtraInfo':extra},'mcOverall':label,
              'mcPlayerName':toggle,'mcStatus':status,'mcWearandTear':wear}
    siblings=copy.deepcopy([toggle,status,wear['mData']])
    Machine({},[]).run(preplay,{1:receiver})
    assert label['mData']['display']==expected and extra==original
    assert [toggle,status,wear['mData']]==siblings
    # A clean redraw with no rating invalidation must retain the label, then
    # a native update to a different player must replace it with a fresh grade.
    Machine({},[]).run(preplay,{1:receiver});assert label['mData']['display']==expected
    extra['Overall']=85;label['mData']['display']='85'
    Machine({},[]).run(preplay,{1:receiver});assert label['mData']['display']=='B'
print('Passed: pre-snap substitution adjusted OVR labels; player toggles, wear-and-tear, status meters, base ratings and composure preserved.')

a=Assembler();kicker_range_suffix(a);kicker=a.finish()
for rating in [*range(101),*map(str,range(101)),UNDEFINED,None,'?',-1,101,math.nan,math.inf,
               '',' 64','64 ','064','64.0','64%','64 ACC','+64','101']:
    def badge(value):
        return {'mData':{'value':value,'ExtraInfo':{'CircleColor':0x336633}},'mcValue':widget('native'),'_visible':True}
    accuracy,power=badge(rating),badge(92)
    stats=[{'value':rating},{'value':92},{'value':28},{'value':38}]
    receiver={'mcAccStat':accuracy,'mcPowStat':power,'mPlayerId':901,
              'stats':stats,'mcTargetText':widget('28 YARD LINE'),
              'mcDistanceText':widget('WITHIN RANGE!'),
              'mcTargetLine':{'_x':164},'mcEndLine':{'_x':356},'mcRange':{'_width':192}}
    original_stats=copy.deepcopy(stats)
    range_before=copy.deepcopy([receiver[k] for k in ['mcTargetLine','mcEndLine','mcRange']])
    Machine({},[]).run(kicker,{1:receiver})
    assert accuracy['mData']['value'] is rating and power['mData']['value']==92
    assert power['mcValue']['mData']['display']=='A'
    assert power['mData']['ExtraInfo']=={'CircleColor':0x336633,'DEPlayerRating':True,'DEPlayerRatingNumericText':True}
    valid=isinstance(rating,int) and 0<=rating<=100 or isinstance(rating,str) and rating in set(map(str,range(101)))
    if valid:
        n=int(rating);grade='A' if n>=90 else 'B' if n>=80 else 'C' if n>=70 else 'D' if n>=60 else 'F'
        assert accuracy['mcValue']['mData']['display']==grade
        assert accuracy['mcValue']['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade]
    else:assert accuracy['mcValue']['mData']['display']=='native'
    assert stats[0]['value'] is rating and stats[1:]==original_stats[1:]
    assert [receiver[k] for k in ['mcTargetLine','mcEndLine','mcRange']]==range_before
    assert receiver['mcTargetText']['mData']['display']=='28 YARD LINE'
    assert receiver['mcDistanceText']['mData']['display']=='WITHIN RANGE!' and receiver['mPlayerId']==901
    # Existing RatingValueItem.Draw honors the scoped marker after a native
    # redraw. Exercise that route instead of assuming initial paint persists.
    from build_player_card_ui import rating_value_draw_suffix
    draw_asm=Assembler();rating_value_draw_suffix(draw_asm)
    power['mcValue']['mData']['display']='92';power['mcValue']['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    Machine({},[]).run(draw_asm.finish(),{1:power})
    assert power['mcValue']['mData']['display']=='A' and power['mData']['value']==92
for receiver in [{},{'mcAccStat':{}},{'mcPowStat':{'mData':{'value':90}}}]:
    Machine({},[]).run(kicker,{1:receiver})
assert all(regs==newregs for _,_,regs,_,_,_,newregs,_ in KICKER_SPECS)
print('Passed: separate Kicker Range accuracy/power grade colors, unknowns, persistent redraw and fixed frames; native numeric yard lines, distances, range geometry and player data preserved.')

# The native source may be text; a late SetValue writes its raw label again.
# Check both the immediate SetValue suffix and subsequent style-reset Draw,
# including delayed child creation and reused badges receiving another kicker.
from build_player_card_ui import rating_value_draw_suffix,kicker_value_set_suffix
draw=Assembler();rating_value_draw_suffix(draw);draw=draw.finish()
set_value=BoundedAssembler(4);kicker_value_set_suffix(set_value);set_value=set_value.finish()
for initial in [UNDEFINED,'64',64]:
    badge={'mData':{'value':initial,'ExtraInfo':{'CircleColor':0x123456}}}
    Machine({},[]).run(kicker,{1:{'mcAccStat':badge}})
    assert badge['mData']['ExtraInfo']['DEPlayerRatingNumericText'] is True
    badge['mcValue']=widget('native')
    for value,label in [('64','D'),('91','A'),(80,'B'),('0','F'),('100','A'),('?', '?'),('64%', '64%')]:
        badge['mData']['value']=value
        badge['mcValue']['mData']['display']=value # native SetValue
        Machine({},[]).run(set_value,{1:badge})
        assert badge['mcValue']['mData']['display']==label
        assert badge['mData']['value'] is value
        badge['mcValue']['mData'].update(display=value,ExtraInfo={'fontColor':0xFFFFFF,'font':'native'})
        Machine({},[]).run(draw,{1:badge})
        assert badge['mcValue']['mData']['display']==label
        assert badge['mData']['ExtraInfo']['CircleColor']==0x123456
        assert badge['mData']['value'] is value
for extra in [{},{'DEPlayerRating':True},{'DEPlayerRatingNumericText':False}]:
    badge={'mData':{'value':'64','ExtraInfo':extra},'mcValue':widget('64')}
    Machine({},[]).run(set_value,{1:badge});Machine({},[]).run(draw,{1:badge})
    assert badge['mcValue']['mData']['display']=='64'
assert len(draw.code)+1730<32768 and len(set_value.code)+20<32768
print('Passed: kicker canonical numeric text at initial paint, deferred initialization, SetValue and Draw; reused kicker/unknown values, four-register frame and unmarked team/stat badges preserved.')

# Actual pause Injury Report: the legacy player module defaults roster=false,
# even for active players. Its skills normalize to AttributesData0..5. Only
# this screen's private marker permits raw values to be displayed as grades.
from build_player_card_ui import badge_suffix,attribute_slots_suffix
mark=Assembler();injury_module_suffix(mark);mark=mark.finish()
parent=Assembler();badge_suffix(parent);parent=parent.finish()
slots=Assembler();attribute_slots_suffix(slots);slots=slots.finish()
for raw in [[91,94,65,81,84,89],['91','94','65','81','84','89']]:
    source=[{'skillLabel':n,'skillValue':v} for n,v in zip(['Speed','Agility','Awareness','Medium Route','Catching','Spec Catch'],raw)]
    before=copy.deepcopy(source)
    extra={f'AttributesData{i}':{'ratingName':s['skillLabel'],'ratingValue':s['skillValue'],'isFullyScouted':True} for i,s in enumerate(source)}
    attributes={'mData':{'ExtraInfo':extra},**{f'mcValueSlotText{i}':widget(v) for i,v in enumerate(raw)}}
    info={'PlayerId':127,'roster':False,'overall':'B','injury':'Broken Collarbone','length':'Multiple Weeks',
          'attributesSubpanelInfo':source}
    module={'mData':{'ExtraInfo':info},'mcInfoSlotAttributes':attributes}
    Machine({},[]).run(mark,{1:{'mcModule':module}})
    Machine({},[]).run(parent,{1:module});Machine({},[]).run(slots,{1:attributes})
    assert [attributes[f'mcValueSlotText{i}']['mData']['display'] for i in range(6)]==['A','A','D','B','B','B']
    assert source==before and info['overall']=='B' and info['roster'] is False
    assert info['injury']=='Broken Collarbone' and info['length']=='Multiple Weeks'
    assert [extra[f'AttributesData{i}']['ratingValue'] for i in range(6)]==raw
    # A reused player selection replaces all six labels from fresh values.
    for i in range(6):extra[f'AttributesData{i}']['ratingValue']='72';attributes[f'mcValueSlotText{i}']['mData']['display']='72'
    Machine({},[]).run(slots,{1:attributes});assert all(attributes[f'mcValueSlotText{i}']['mData']['display']=='C' for i in range(6))
for revealed in [False,UNDEFINED]:
    attributes={'mData':{'ExtraInfo':{'DEInjuryPlayerRatings':True,'AttributesData0':{'isFullyScouted':revealed,'ratingValue':91}}},'mcValueSlotText0':widget('?')}
    Machine({},[]).run(slots,{1:attributes});assert attributes['mcValueSlotText0']['mData']['display']=='?'
for module in [{},{'mData':{}},{'mData':{'ExtraInfo':{'roster':False}}}]:
    Machine({},[]).run(mark,{1:{'mcModule':module}});Machine({},[]).run(parent,{1:module})
unmarked={'mData':{'ExtraInfo':{'AttributesData0':{'isFullyScouted':True,'ratingValue':91}}},'mcValueSlotText0':widget(91)}
Machine({},[]).run(slots,{1:unmarked});assert unmarked['mcValueSlotText0']['mData']['display']==91
assert len(slots.code)+388<32768
print('Passed: pause Injury Report six numeric/text attributes with native roster=false, private marker forwarding, unknowns/reused players; source skills, Overall, injury status/recovery and unmarked displays preserved.')
