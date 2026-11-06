"""Execute exact gap suffixes and independently verify their native sources."""
from dataclasses import replace
from pathlib import Path
import copy
import inspect
import math
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from build_recruit_notes_ui import Assembler,fnv
from build_fog_gap_ui import (GROUPS,TEAM_CAPTIONS,TEAM_RATING_CAPTIONS,MODERN_STAT_BINDINGS,RATING_NAMES,generate,
    FixedFrameAssembler,assembler_for,
    vertical_team_suffix,select_team_suffix,top_players_suffix,
    award_attributes_suffix,by_numbers_suffix,weekly_school_suffix,
    weekly_playing_time_suffix,display_grade,modern_by_numbers_suffix)
from build_player_card_ui import rating_value_draw_suffix
from recruit_notes_vm import Machine,UNDEFINED,ScriptFunction
from grade_scales import label,COLORS


GLOBALS={'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':9}}}


class GapMachine(Machine):
    pass

# Execute the same function-local scratch operations as the Draft verifier.
# Each invocation gets its own locals, including recursive widget callbacks.
namespace=dict(math=math,struct=struct,UNDEFINED=UNDEFINED,ScriptFunction=ScriptFunction)
machine_source=inspect.getsource(Machine.run).replace('    def run(','def run(',1).replace('\n    ','\n')
machine_source=machine_source.replace('pc, stack = begin, []','pc, stack = begin, []; locals_ = {}')
machine_source=machine_source.replace('stack.append(self.globals[stack.pop()])','stack.append((lambda key: locals_.get(key,self.globals.get(key,UNDEFINED)))(stack.pop()))')
machine_source=machine_source.replace('elif op == 0x4F:', 'elif op == 0x4D:\n                stack[-1],stack[-2]=stack[-2],stack[-1]\n            elif op == 0x3C:\n                value,key=stack.pop(),stack.pop();locals_[key]=value\n            elif op == 0x4F:')
exec(machine_source,namespace)
GapMachine.run=namespace['run']


class NativeFrame(dict):
    """An accessor cannot enlarge this already allocated native register file."""
    def __init__(self, count, receiver):
        self.count=count
        super().__init__({1:receiver})
    def get(self, key, default=None):
        assert 0 <= key < self.count, ('read outside native frame',key,self.count)
        return super().get(key,default)
    def __setitem__(self, key, value):
        assert 0 <= key < self.count, ('write outside native frame',key,self.count)
        super().__setitem__(key,value)


def program(builder,scale=0,colors=True,player=True,team=True):
    a=assembler_for(builder);builder(a);p=a.finish();code=bytearray(p.code)
    for offsets,value in [(p.scale_offsets+p.team_scale_offsets,scale),(p.color_offsets,colors),
                          (p.fog_offsets,player),(p.team_offsets,team)]:
        for at in offsets:code[at]=int(value)
    return replace(p,code=bytes(code))


def text(value='native'):
    t={'mData':{'display':value,'ExtraInfo':{'font':'native','fontColor':0x123456}},
       '_width':80,'calls':[]}
    def set_label(v):t['mData']['display']=v;t['calls'].append(('label',v))
    def set_style(v):t['mData']['ExtraInfo'].update(v);t['calls'].append(('style',v))
    t.update(SetLabel=set_label,SetExtraInfo=set_style)
    return t


def badge(value):return {'mData':{'value':value,'ExtraInfo':{'CircleColor':42}},'mcValue':text(str(value))}


def run(builder,receiver,**options):
    assembler=assembler_for(builder)
    registers=NativeFrame(assembler.native_registers,receiver) if isinstance(assembler,FixedFrameAssembler) else {1:receiver}
    return GapMachine(GLOBALS,[]).run(program(builder,**options),registers)


def verify_text(t,value,scale,colors,enabled):
    expected_label=label(value,scale) if enabled else str(value)
    assert t['mData']['display']==expected_label,(value,scale,colors,enabled,t)
    expected_color=COLORS[label(value,scale)] if colors else 0xF3F0E7 if enabled else 0x123456
    assert t['mData']['ExtraInfo']['fontColor']==expected_color
    assert t['mData']['ExtraInfo']['font']=='native'


TEAM_BADGES=('mcStatOVR','mcStatOFF','mcStatDEF')
SELECT_BADGES=tuple('mc'+s+'Rating'+k for s in ('Home','Away') for k in ('Ovr','Off','Def'))

# Every boundary and scale, with independent player/team toggles. The other
# models carry values in the same range to catch over-broad numeric scanning.
for scale in range(4):
    for enabled in (True,False):
        for colors in (True,False):
            for value in range(101):
                for builder,names in ((vertical_team_suffix,TEAM_BADGES),(select_team_suffix,SELECT_BADGES)):
                    receiver={name:badge(value) for name in names}
                    receiver.update(TeamStars=5,Rank=1,Record='12-1',CoachOVR=90,TeamOVR=value)
                    run(builder,receiver,scale=scale,colors=colors,player=not enabled,team=enabled)
                    for name in names:
                        item=receiver[name];verify_text(item['mcValue'],value,scale,colors,enabled)
                        assert item['mData']['value']==value
                        assert item['mData']['ExtraInfo']=={'CircleColor':42,'DETeamRating':True}
                    assert [receiver[n] for n in ('TeamStars','Rank','Record','CoachOVR','TeamOVR')]==[5,1,'12-1',90,value]
                source={'PlayersList':[{'playerOVR':value,'playerPos':'QB','number':12}]}
                receiver={'mPlayerOverallArray':[badge(value)],'TeamOVR':value,'NIL':85,'mData':{'ExtraInfo':source}}
                original=copy.deepcopy(source)
                run(top_players_suffix,receiver,scale=scale,colors=colors,player=enabled,team=not enabled)
                verify_text(receiver['mPlayerOverallArray'][0]['mcValue'],value,scale,colors,enabled)
                assert source==original and receiver['TeamOVR']==value and receiver['NIL']==85
                item=receiver['mPlayerOverallArray'][0]
                assert item['mData']['value']==value and item['mData']['ExtraInfo']['DEPlayerRating'] is True
                receiver={'mData':{'ExtraInfo':{'OVRRow1':str(value),'OVRRow2':'', 'Grade':'A+', 'RiskBarRow1':77}},'mcOVRRow1':text(str(value))}
                original=copy.deepcopy(receiver['mData'])
                run(weekly_school_suffix,receiver,scale=scale,colors=colors,player=enabled,team=not enabled)
                verify_text(receiver['mcOVRRow1'],value,scale,colors,enabled)
                assert receiver['mData']==original

# Native deferred child repaints retain the badge's exact role. A team badge
# must not follow Roster Fog, and a player badge must not follow Team Fog.
for builder,names,role in ((vertical_team_suffix,TEAM_BADGES,'team'),(select_team_suffix,SELECT_BADGES,'team'),(top_players_suffix,None,'player')):
    for enabled in (True,False):
        receiver={n:badge(96) for n in names} if names else {'mPlayerOverallArray':[badge(96)]}
        run(builder,receiver,scale=2,player=enabled if role=='player' else not enabled,team=enabled if role=='team' else not enabled)
        item=receiver[names[0]] if names else receiver['mPlayerOverallArray'][0]
        item['mcValue']['mData']['display']='96'
        def repaint(a):rating_value_draw_suffix(a);a.ret()
        run(repaint,item,scale=2,player=enabled if role=='player' else not enabled,team=enabled if role=='team' else not enabled)
        assert item['mcValue']['mData']['display']==('S' if enabled else '96')

# Multiple populated rows must not clobber the loop index/style register or
# accidentally repeat the first player's value in every visible slot.
receiver={'mPlayerOverallArray':[badge(v) for v in (96,84,70,55)]}
run(top_players_suffix,receiver,scale=2)
assert [b['mcValue']['mData']['display'] for b in receiver['mPlayerOverallArray']]==['S','B','C','F']
receiver={'mData':{'ExtraInfo':{'OVRRow1':74,'OVRRow2':'0','OVRRow3':'Hidden','OVRRow4':100}},
          **{'mcOVRRow'+str(i):text(v) for i,v in enumerate((74,'0','Hidden',100),1)}}
run(weekly_school_suffix,receiver)
assert [receiver['mcOVRRow'+str(i)]['mData']['display'] for i in range(1,5)]==['C','F','Hidden','A']

# Both late-accessor callbacks use only native r0..r3, even though their loop
# state formerly required r4/r5. Inspect stores as well as register reads.
for specs in GROUPS.values():
    for s in specs:
        if s.suffix not in (weekly_school_suffix,select_team_suffix):continue
        assert s.registers==4 and (s.new_registers or s.registers)==4
        a=assembler_for(s.suffix);assert isinstance(a,FixedFrameAssembler)
        s.suffix(a);p=a.finish();pc=0;used=[]
        while pc<len(p.code):
            op=p.code[pc];pc+=1
            if op==0xB9:used.append(p.code[pc]);pc+=1
            elif op==0xB5:pc+=1
            elif op==0xB6:pc+=2
            elif op==0xA1:pc=((pc+7)&~7)+8
            elif op in (0x87,0x9D,0xB8,0x99):
                pc=(pc+7)&~7
                if op==0x87:used.append(struct.unpack_from('<I',p.code,pc)[0])
                pc+=4
        assert used and all(n<s.registers for n in used),(s.name,used)
        assert any(v=='_DEFogGapLocal4' for _,v in p.literals)
        assert not any(v.startswith('_DEDraftLocal') for _,v in p.literals)
        # A leaked old r4 store must fail under the same caller fixture.
        old=Assembler();old.number(0);old.store(4);old.ret()
        try:GapMachine(GLOBALS,[]).run(old.finish(),NativeFrame(4,{}))
        except AssertionError as error:assert error.args[0][0]=='write outside native frame'
        else:raise AssertionError('The bounded native-frame fixture accepted r4')

# A nested callback on the SAME VM must not overwrite the outer callback's
# local loop index or badge array. Neither this nor globals receive scratch.
for builder in (weekly_school_suffix,select_team_suffix):
    def receiver_for(values):
        if builder is select_team_suffix:
            return {name:badge(value) for name,value in zip(SELECT_BADGES,values)}
        return {'mData':{'ExtraInfo':{'OVRRow'+str(i):value for i,value in enumerate(values,1)}},
                **{'mcOVRRow'+str(i):text(value) for i,value in enumerate(values,1)}}
    outer_values=(96,84,70,55,91,65) if builder is select_team_suffix else (96,84,70,55)
    inner_values=(60,90,80,70,50,100) if builder is select_team_suffix else (60,90,80,70)
    outer,inner=receiver_for(outer_values),receiver_for(inner_values)
    target=outer[SELECT_BADGES[0]]['mcValue'] if builder is select_team_suffix else outer['mcOVRRow1']
    native_set_label=target['SetLabel'];entered=[];machine=GapMachine(GLOBALS,[]);p=program(builder)
    def nested_label(value):
        if not entered:
            entered.append(True);machine.run(p,NativeFrame(4,inner))
        native_set_label(value)
    target['SetLabel']=nested_label
    machine.run(p,NativeFrame(4,outer))
    def displayed(receiver):
        if builder is select_team_suffix:return [receiver[n]['mcValue']['mData']['display'] for n in SELECT_BADGES]
        return [receiver['mcOVRRow'+str(i)]['mData']['display'] for i in range(1,5)]
    assert displayed(outer)==[label(v,0) for v in outer_values]
    assert displayed(inner)==[label(v,0) for v in inner_values]
    assert not any(key.startswith('_DEFogGapLocal') for key in outer)
    assert not any(key.startswith('_DEFogGapLocal') for key in GLOBALS)

# The shared award card mixes rating fields and real football statistics.
for scale in range(4):
    for enabled in (True,False):
        for colors in (True,False):
            for stat_name in RATING_NAMES:
                stats=[{'StatName':stat_name,'StatValue':'85'},
                       {'StatName':'Passing Yards','StatValue':85},
                       {'StatName':'Passing TD','StatValue':'12'}]
                receiver={'mTeamListItem':{'PlayerStats':stats},**{'mcStatNumber'+str(i):text(s['StatValue']) for i,s in enumerate(stats)}}
                original=copy.deepcopy(stats)
                run(award_attributes_suffix,receiver,scale=scale,colors=colors,player=enabled,team=not enabled)
                verify_text(receiver['mcStatNumber0'],85,scale,colors,enabled)
                assert receiver['mcStatNumber1']['mData']['display']==85 and receiver['mcStatNumber1']['calls']==[]
                assert receiver['mcStatNumber2']['mData']['display']=='12' and receiver['mcStatNumber2']['calls']==[]
                assert stats==original

# By the Numbers: team ratings only when the native header says OVR/OFF/DEF.
# PPG and yards in the same numeric range remain untouched.
for scale in range(4):
    for enabled in (True,False):
        for colors in (True,False):
            for is_ratings in (True,False):
                receiver={'mData':{'ExtraInfo':[{'StatValue':85,'DisplayRank':12}]}}
                for (header,captions,ending),stat_caption in zip(TEAM_CAPTIONS,('PASS YPG','RUSH YPG','PPG')):
                    receiver[header]=text(captions[0] if is_ratings else stat_caption)
                    for side in ('Home','Away'):receiver['mc'+side+ending]=text('85')
                original=copy.deepcopy(receiver['mData'])
                run(by_numbers_suffix,receiver,scale=scale,colors=colors,player=not enabled,team=enabled)
                assert receiver['mData']==original
                for _,_,ending in TEAM_CAPTIONS:
                    for side in ('Home','Away'):
                        t=receiver['mc'+side+ending]
                        if is_ratings:verify_text(t,85,scale,colors,enabled)
                        else:assert t['mData']['display']=='85' and t['calls']==[]

# Actual p90 path: InfoPanelPregameTeamStats model.BindWidget, whose native
# parameters are r4 bindName/r3 widget. Values come from StatDisplay; StatValue
# remains numeric for the independently executed native comparison/arrows.
MODERN_ENUMS={name:310+index*7 for index,(name,_,_) in enumerate(MODERN_STAT_BINDINGS)}
MODERN_ENUMS.update(STATS=900,HOME_STATS_RANKING_0=901,AWAY_STATS_RANKING_3=902,TITLE=903)
def modern_fixture():
    return {'FIRST_ROW_ARRAY_INDEX':0,'SECOND_ROW_ARRAY_INDEX':1,
            'THIRD_ROW_ARRAY_INDEX':2,'FOURTH_ROW_ARRAY_INDEX':3,
            'mHomeTeamStatsData':[{'StatName':n,'StatDisplay':str(v),'StatValue':99-i,'StatRanking':12+i}
                                  for i,(n,v) in enumerate(zip(('OVR','OFF','DEF','PPG'),(67,64,63,24)))],
            'mAwayTeamStatsData':[{'StatName':n,'StatDisplay':str(v),'StatValue':95-i,'StatRanking':20+i}
                                  for i,(n,v) in enumerate(zip(('OVR','OFF','DEF','PASS YPG'),(80,90,70,85)))],
            'NIL':85,'Record':'4-0','Rank':12,'Stars':5}
def run_modern(receiver,binding,widget,**options):
    registers=NativeFrame(5,receiver);registers[3]=widget;registers[4]=MODERN_ENUMS.get(binding,binding)
    return GapMachine({**GLOBALS,'fb_shared_enum':{'BindingType':MODERN_ENUMS}},[]).run(
        program(modern_by_numbers_suffix,**options),registers)
for scale in range(4):
    for enabled in (True,False):
        for colors in (True,False):
            for binding,array,constant in MODERN_STAT_BINDINGS:
                receiver=modern_fixture();source=copy.deepcopy(receiver)
                row=receiver[array][receiver[constant]];widget=text(row['StatDisplay'])
                run_modern(receiver,binding,widget,scale=scale,colors=colors,team=enabled,player=not enabled)
                if row['StatName'] in TEAM_RATING_CAPTIONS:verify_text(widget,int(row['StatDisplay']),scale,colors,enabled)
                else:assert widget['mData']['display']==row['StatDisplay'] and widget['calls']==[]
                assert receiver==source
            for value in range(101):
                for binding,array,constant in (MODERN_STAT_BINDINGS[0],MODERN_STAT_BINDINGS[-1]):
                    receiver=modern_fixture();row=receiver[array][receiver[constant]]
                    row.update(StatName='Overall',StatDisplay=str(value),StatValue=100-value)
                    source=copy.deepcopy(receiver);widget=text(str(value))
                    run_modern(receiver,binding,widget,scale=scale,colors=colors,team=enabled,player=not enabled)
                    verify_text(widget,value,scale,colors,enabled);assert receiver==source
# Native ordinal constants need not equal our loop indexes. No title, caption,
# rank, or unrelated binding is allowed to masquerade as a ratings value.
receiver=modern_fixture();receiver['FIRST_ROW_ARRAY_INDEX']=2
widget=text('63');run_modern(receiver,'HOME_STATS_0',widget)
assert widget['mData']['display']=='D'
for binding in ('STATS','HOME_STATS_RANKING_0','AWAY_STATS_RANKING_3','TITLE',123456):
    receiver=modern_fixture();widget=text('85');run_modern(receiver,binding,widget)
    assert widget['calls']==[] and widget['mData']['display']=='85'
for caption in ('PPG','Passing Yards','Total Yards','Rush YPG','Turnovers','Rank','Winning Percentage','OVR rank',''):
    receiver=modern_fixture();receiver['mHomeTeamStatsData'][0].update(StatName=caption,StatDisplay='85',StatValue=85)
    widget=text('85');run_modern(receiver,'HOME_STATS_0',widget);assert widget['calls']==[]
for value in (UNDEFINED,None,'?','Hidden','',' 85','85 ','085','+85','85.0','85%','85 yards','1,000',-1,101,float('nan'),float('inf')):
    receiver=modern_fixture();receiver['mHomeTeamStatsData'][0]['StatDisplay']=value
    widget=text(value);run_modern(receiver,'HOME_STATS_0',widget);assert widget['calls']==[]
for receiver in ({},{'mHomeTeamStatsData':[]},{'FIRST_ROW_ARRAY_INDEX':0,'mHomeTeamStatsData':[{}]}):
    widget=text('85');run_modern(receiver,'HOME_STATS_0',widget);assert widget['calls']==[]

# Playing Time mask is exact and source-independent: other motivations and all
# eligibility/Have/Need inputs stay native. The bank is enabled by Recruiting
# Fog at runtime, rather than following Roster Fog/Team Fog/color options.
for motivation in ('Playing Time','Proximity to Home','Championship Contender','Academic Prestige','playing time',''):
    source={'playingTime':motivation,'Have':'A+','HaveText':'A+','Need':'C-','NeedText':'C-', 'MatchId':123,'IsBoostedByTalents':True,'Eligible':True}
    receiver={'mData':{'ExtraInfo':source},'mcHaveNeed':text('Have: A+ | Need: C-'),'mcPlayingTime':text(motivation),'mcArrow':{'_visible':True}}
    original=copy.deepcopy(source)
    run(weekly_playing_time_suffix,receiver)
    assert source==original
    if motivation=='Playing Time':
        assert receiver['mcHaveNeed']['mData']['display']=='Have: ? | Need: ?'
        assert receiver['mcArrow']['_visible'] is False
    else:assert receiver['mcHaveNeed']['calls']==[] and receiver['mcArrow']['_visible'] is True
    assert receiver['mcPlayingTime']['mData']['display']==motivation

INVALID=(UNDEFINED,None,'?','Hidden','',' 85','85 ','085','+85','85.0','85%','85 yards','1,000',-1,101,float('nan'),float('inf'))
for value in INVALID:
    for builder,receiver,target in (
        (vertical_team_suffix,{'mcStatOVR':badge(value)},lambda r:r['mcStatOVR']['mcValue']),
        (select_team_suffix,{'mcHomeRatingOvr':badge(value)},lambda r:r['mcHomeRatingOvr']['mcValue']),
        (top_players_suffix,{'mPlayerOverallArray':[badge(value)]},lambda r:r['mPlayerOverallArray'][0]['mcValue']),
        (weekly_school_suffix,{'mData':{'ExtraInfo':{'OVRRow1':value}},'mcOVRRow1':text(value)},lambda r:r['mcOVRRow1']),
        (award_attributes_suffix,{'mTeamListItem':{'PlayerStats':[{'StatName':'Awareness','StatValue':value}]},'mcStatNumber0':text(value)},lambda r:r['mcStatNumber0']),
        (by_numbers_suffix,{'mcPassYPGHeader':text('OVR'),'mcHomePassYPGText':text(value)},lambda r:r['mcHomePassYPGText']),
    ):
        run(builder,receiver)
        assert target(receiver)['calls']==[],(builder.__name__,value,target(receiver))
for builder in (vertical_team_suffix,select_team_suffix,top_players_suffix,weekly_school_suffix,award_attributes_suffix,by_numbers_suffix,weekly_playing_time_suffix):
    run(builder,{})
    assert len(program(builder).code)<32768

# Deterministic generation and native descriptors. Check exact member names
# inside the native bodies, not only the hand-built mocks used above.
sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load,walk
ASSETS={s.asset:load(Path(s.asset)) for specs in GROUPS.values() for s in specs}
expected_keys={
 'TeamModule.Draw':{'mcStatOVR','mcStatOFF','mcStatDEF','TeamOVR','TeamOFF','TeamDEF'},
 'OverviewModule._FillListPlayerData':{'mPlayerOverallArray','playerOVR','PlayersList'},
 'MySchoolGradePerWeek.Draw':{'mcOVRRow1','mcOVRRow2','mcOVRRow3','mcOVRRow4'},
 'InfoPanelPOTW._SetAttributesParams':{'mcStatNumber0','mcStatNumber1','mcStatNumber2','StatName','StatValue'},
 'InfoPanelPregameStats.Init':{'mcPassYPGHeader','mcRushYPGHeader','mcPPGHeader','mcHomePassYPGText','mcAwayPassYPGText','StatName','StatValue'},
 'InfoPanelPregameTeamStats.BindWidget':{'BindWidget','mHomeTeamStatsData','mAwayTeamStatsData','StatName','StatDisplay',
                                       'FIRST_ROW_ARRAY_INDEX','FOURTH_ROW_ARRAY_INDEX','HOME_STATS_0','AWAY_STATS_3'},
 'DealBreakerInfoSlot.Draw':{'mcHaveNeed','mcPlayingTime','mcArrow','HaveText','NeedText','playingTime'},
 'TeamSelect._UpdateStatBoxes':set(SELECT_BADGES)|{'ratingOVR','ratingOFF','ratingDEF'},
}
for specs in GROUPS.values():
    for s in specs:
        apt=ASSETS[s.asset];header=apt.data[s.offset:s.offset+48]
        assert (struct.unpack_from('<I',header,8)[0],struct.unpack_from('<H',header,12)[0],struct.unpack_from('<H',header,14)[0])==(s.argc,s.registers,s.flags)
        assert fnv(apt.data[s.offset+48:s.offset+48+s.size])==s.hash
        found=set()
        for _,off in apt.root_streams():
            try:items=apt.decode(off)
            except Exception:continue
            for item in items:
                if item[1]!=0x8E or int(item[2][3],16)!=s.offset+48:continue
                for _,_,op in walk(item[3]):
                    if isinstance(op[2],tuple) and len(op[2])==2 and isinstance(op[2][1],str):found.add(op[2][1])
        # Some compiler fast-member opcodes encode the field through the root
        # constant pool; require that exact class's pool, not a whole-file hit.
        if not expected_keys[s.name]<=found:
            for _,off in apt.root_streams():
                try:items=apt.decode(off)
                except Exception:continue
                if any(i[1]==0x8E and int(i[2][3],16)==s.offset+48 for i in items):found.update(items[0][2])
        assert expected_keys[s.name]<=found,(s.name,expected_keys[s.name]-found)
        if s.name=='InfoPanelPregameTeamStats.BindWidget':
            assert s.registers==5 and (s.new_registers or s.registers)==5
            params=struct.unpack_from('<Q',header,16)[0]
            assert [struct.unpack_from('<Q',apt.data,params+16*i)[0] for i in range(2)]==[4,3]
        # All loops are local UI work; no provider/native query is introduced.
        literals=[text for _,text in program(s.suffix).literals]
        assert not any('Adapter' in x or 'Provider' in x or x=='onEnterFrame' for x in literals)
with tempfile.TemporaryDirectory() as td:
    output=Path(td)/'Gap.h';generate(output)
    assert output.read_bytes()==(ROOT/'Source/FogGapUiPrograms.h').read_bytes()

print('Passed: eight exact native gap callbacks; modern hub binding frame/args/StatDisplay and real-stat preservation; native four-slot late-accessor frames and nested local scratch isolation; every grade boundary and independent fog/colors; canonical hidden values; award/stat discrimination; Playing Time-only mask; unchanged sources; deterministic bounded bytecode and no provider polling.')
