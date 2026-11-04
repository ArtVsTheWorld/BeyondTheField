"""Execute custom presentation suffixes; preserve native model/progression values."""
import copy
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler, GRADE_COLORS
from build_player_card_ui import (header_suffix,badge_suffix,attributes_suffix,
                                 template_suffix,group_suffix,level_suffix,attribute_slots_suffix,
                                 skill_slots_suffix,rating_value_draw_suffix,subskills_suffix,
                                 SPECS,append_program,fnv)
from recruit_notes_vm import Machine,UNDEFINED


def program(suffix):
    a=Assembler();suffix(a);a.ret();return a.finish()


def text_widget(label='old',color=0xFFFFFF):
    target={'mData':{'display':label,'ExtraInfo':{'fontColor':color,'font':'preserve','size':24}},'calls':[]}
    def set_label(value):target['mData']['display']=value;target['calls'].append(('label',value))
    def set_style(value):target['mData']['ExtraInfo'].update(value);target['calls'].append(('style',value))
    target.update(SetLabel=set_label,SetExtraInfo=set_style)
    return target


def expected(value):
    return 'A' if value>=90 else 'B' if value>=80 else 'C' if value>=70 else 'D' if value>=60 else 'F'


for value in range(101):
    child=text_widget(str(value));data={'value':value,'unrelated':17}
    item={'mData':data,'mcValue':child}
    receiver={'mcRatingValueItem':item,'mOVRValue':value,'delta':3}
    Machine({},[]).run(program(header_suffix),{1:receiver})
    grade=expected(value)
    assert data=={'value':value,'unrelated':17,'ExtraInfo':{'DEPlayerRating':True}} and receiver['mOVRValue']==value and receiver['delta']==3
    assert child['mData']['display']==grade and child['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade]
    child['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    Machine({},[]).run(program(rating_value_draw_suffix),{1:item})
    assert child['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade] and data['value']==value
    assert child['mData']['ExtraInfo']['font']=='preserve' and child['mData']['ExtraInfo']['size']==24
    child['calls'].clear();Machine({},[]).run(program(header_suffix),{1:receiver})
    assert child['calls']==[], 'Unchanged draw reapplied styles or label'
    # Native reentry/focus can restore white and the numeric text. Restore both.
    child['mData']['display']=str(value);child['mData']['ExtraInfo']['fontColor']=0xFFFFFF
    Machine({},[]).run(program(header_suffix),{1:receiver})
    assert child['mData']['display']==grade and child['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade]

for value in [UNDEFINED,None,'?','--','Hidden','92',-1,101,float('nan'),float('inf')]:
    child=text_widget('?');receiver={'mcRatingValueItem':{'mData':{'value':value},'mcValue':child}}
    Machine({},[]).run(program(header_suffix),{1:receiver})
    assert child['calls']==[],'Hidden/invalid rating was disclosed'
for receiver in [{},{'mcRatingValueItem':{}},{'mcRatingValueItem':{'mData':{'value':90}}}]:
    Machine({},[]).run(program(header_suffix),{1:receiver})

for value in ['A','B','C','D','F',92,0,45000,'NIL','B+','C–A','?',None]:
    child=text_widget(value);item={'mData':{'value':value},'mcValue':child}
    Machine({},[]).run(program(badge_suffix),{1:{'mcStat':item}})
    if isinstance(value,str) and value in GRADE_COLORS:
        assert child['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[value]
    else:assert child['calls']==[], 'Shared module recolored an unrelated statistic or value'
    assert item['mData']['value']==value

for marked in [True,False]:
    for current,maximum in [(59,90),(60,79),(80,100),(0,0),(UNDEFINED,UNDEFINED),('?',-1)]:
        child=text_widget(current);max_child=text_widget(maximum)
        data={'value':current,'ExtraInfo':{'DEPlayerRating':marked,'MaxValue':maximum,'ShowMaxValue':False,'ShowSlider':False},'sliderValue':current}
        receiver={'mData':data,'mcValue':child,'mcMaxValue':max_child}
        before_extra=dict(data['ExtraInfo'])
        Machine({},[]).run(program(attributes_suffix),{1:receiver})
        assert data['ExtraInfo']==before_extra and data['value']==current and data['sliderValue']==current
        for value,target in [(current,child),(maximum,max_child)]:
            if marked and isinstance(value,int) and 0<=value<=100:
                grade=expected(value);assert target['mData']['display']==grade and target['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade]
            else:assert target['calls']==[]

globals_={'fb_shared_enum':{'BindingType':{'ATTRIBUTES':'attributes','INFO':'info'}}}
for binding in ['attributes','skills','stats']:
    for kind in ['info','container']:
        data={'ExtraInfo':{'Width':150,'ShowSlider':False}}
        result=Machine(globals_,[]).run(program(template_suffix),{1:data,2:binding,3:kind})
        assert result is data
        assert data['ExtraInfo'].get('DEPlayerRating',False)==(binding=='attributes' and kind=='info')
        assert data['ExtraInfo']['Width']==150 and data['ExtraInfo']['ShowSlider'] is False

for rating in [0,59,60,79,80,90,100]:
    styles={}
    for name in ['FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle']:
        style={'font':'native-font','fontColor':0xFFFFFF,'size':28}
        style['CloneAndModify']=lambda changes,original=style:{**original,**changes}
        styles[name]=style
    clip={'mData':{'value':4,'ExtraInfo':styles},'calls':[]}
    def update(value):clip['calls'].append(value);clip['mData']['ExtraInfo'].update(value)
    clip['SetExtraInfo']=update
    data={'ExtraInfo':{'Rating':rating,'Level':4,'MaxSkillGroupCap':10}}
    old_data=copy.deepcopy(data)
    Machine({},[]).run(program(group_suffix),{1:data,2:clip})
    assert data==old_data and clip['mData']['value']==4
    assert clip['mData']['ExtraInfo']['RightLabelDisplayOverride']==expected(rating)
    for name in ['FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle']:
        style=clip['mData']['ExtraInfo'][name]
        assert style['fontColor']==GRADE_COLORS[expected(rating)] and style['font']=='native-font' and style['size']==28
    updates=[];receiver={'mSkillLevelDataProvider':{'UpdateProperty':lambda *args:updates.append(args)}}
    Machine({},[]).run(program(level_suffix),{1:receiver,4:rating,5:3})
    assert updates==[(0,'display',expected(rating))], 'Upgrade bonus/cost was altered'

for revealed in [True,False]:
    widgets=[text_widget() for _ in range(6)]
    entries=[{'ratingValue':grade,'isFullyScouted':revealed,'ratingName':'Speed'} for grade in ['A','B','C','D','F','?']]
    receiver={'mData':{'ExtraInfo':{'AttributesData'+str(i):entry for i,entry in enumerate(entries)}}}
    receiver.update({'mcValueSlotText'+str(i):widget for i,widget in enumerate(widgets)})
    before=copy.deepcopy(entries)
    Machine({},[]).run(program(attribute_slots_suffix),{1:receiver})
    assert entries==before
    for grade,widget in zip(['A','B','C','D','F','?'],widgets):
        if revealed and grade!='?':assert widget['mData']['ExtraInfo']['fontColor']==GRADE_COLORS[grade]
        else:assert widget['calls']==[]
for rating in [59,70,90]:
    entry={'Rating':rating,'Level':3,'SkillGroupCap':8,'MaxSkillGroupCap':10}
    gauge={'mData':{'value':3,'ExtraInfo':{}},'calls':[]}
    gauge['SetExtraInfo']=lambda extra:gauge['calls'].append(extra)
    receiver={'mData':{'ExtraInfo':{'SkillData0':entry}},'mcSkill0':gauge}
    before=copy.deepcopy(entry)
    Machine({},[]).run(program(skill_slots_suffix),{1:receiver})
    assert entry==before and gauge['mData']['value']==3
    assert gauge['calls']==[{'RightLabelDisplayOverride':expected(rating)}]
for suffix in [attribute_slots_suffix,skill_slots_suffix]:
    for receiver in [{},{'mData':{}},{'mData':{'ExtraInfo':{}}}]:Machine({},[]).run(program(suffix),{1:receiver})

for rating in range(101):
    style={'font':'native','size':26,'fontColor':0xFFFFFF}
    style['CloneAndModify']=lambda patch,original=style:{**original,**patch}
    original_extra={'UnfocusValueTextStyle':style,'MinValue':0,'MaxValue':100,'IncreaseValue':2,'CanIncrease':True}
    rows=[{'value':rating,'display':'Speed','ExtraInfo':original_extra}];updates=[]
    def update(i,key,value):rows[i][key]=value;updates.append((i,key))
    provider={'GetNumItems':lambda:len(rows),'GetItemData':lambda i:rows[i],'UpdateProperty':update}
    globals_={'cafe':{'utility':{'ObjectUtil':{'MergeInto':lambda target,source:target.update(source)}}}}
    Machine(globals_,[]).run(program(subskills_suffix),{1:{'mSubskillsDataProvider':provider}})
    assert rows[0]['value']==rating and rows[0]['display']=='Speed' and updates==[(0,'ExtraInfo')]
    extra=rows[0]['ExtraInfo'];assert extra is not original_extra and extra['RightLabelDisplayOverride']==expected(rating)
    assert 'RightLabelDisplayOverride' not in original_extra and style['fontColor']==0xFFFFFF
    for key in ['MinValue','MaxValue','IncreaseValue','CanIncrease']:assert extra[key]==original_extra[key]
    assert extra['UnfocusValueTextStyle']['font']=='native' and extra['UnfocusValueTextStyle']['fontColor']==GRADE_COLORS[expected(rating)]

sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load
for asset,specs in SPECS.values():
    apt=load(Path(asset))
    for off,argc,regs,flags,size,hash_,newregs,suffix,count in specs:
        original=apt.data[off+48:off+48+size]
        assert fnv(original)==hash_ and newregs>=regs and newregs<=64
        emitted=append_program(size,suffix,count)
        copy_count=size if count is None else count
        assert emitted.code[:copy_count]==bytes(copy_count), 'Native game bytes were emitted'
        assert len(emitted.code)<32768
        if count is not None:assert original[count:]==bytes([0xB9,1,0x3E])
print('Passed: all 101 card grade boundaries/colors, hidden values, marker gating, native model/slider/progression preservation, focus resets, style cloning and private-asset fingerprint gates.')
