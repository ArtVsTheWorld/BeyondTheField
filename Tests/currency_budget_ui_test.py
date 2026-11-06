"""Budget animation values remain numeric; only tagged monetary text changes."""
from dataclasses import replace
from pathlib import Path
import copy
import math
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from build_recruit_notes_ui import Assembler,fnv
from build_currency_budget_ui import (SPECS,CFM,CONTROL,ART,MARKER,mark_budget_value,
    budget_suffix,popup_suffix,animation_suffix,school_budget_suffix,overview_budget_suffix,
    allocation_suffix,pie_currency_suffix,generate)
from recruit_notes_vm import Machine,UNDEFINED

GLOBALS={'Math':{'round':lambda n:math.floor(n+.5),'floor':math.floor},
         'art_control':{'coachcarousel':{'ProgramPointsModule':{'BUDGET_BG_PADDING':24}}}}


def program(builder,enabled=True,ret=False):
    a=Assembler();builder(a)
    if ret:a.ret()
    p=a.finish();code=bytearray(p.code)
    for at in p.dollar_offsets:code[at]=int(enabled)
    return replace(p,code=bytes(code))


def native_label(value):
    return str(int(value)) if isinstance(value,float) and math.isfinite(value) and value.is_integer() else str(value)


def text(value):
    result={'mData':{'display':native_label(value),'ExtraInfo':{'font':'native','fontColor':123}},'calls':[]}
    def set_label(v):result['mData']['display']=v;result['calls'].append(v)
    result['SetLabel']=set_label
    return result


for enabled in (True,False):
    for points,expected in [(0,'0'),(0.0,'0'),(15,'60K'),(75,'300K'),(249,'996K'),(250,'1.0M'),(1000,'4.0M'),(-75,'-300K')]:
        data={'ExtraInfo':{'ProgramPtsValue':points,'PreviousProgramPtsValue':25,'MaxProgramPtsValue':points,
                           'Grade':'A+','ProgramPtsChange':10,'ShouldAnimate':True}}
        receiver={'mData':data,'mcProgramPtsValue':text(points),'mcProgramPtsMax':text(points),'mcTitle':text('Brand Exposure')}
        original=copy.deepcopy(data)
        Machine(GLOBALS,[]).run(program(mark_budget_value,enabled,ret=True),{1:receiver})
        assert receiver['mcProgramPtsValue'].get(MARKER,False)==enabled
        Machine(GLOBALS,[]).run(program(budget_suffix,enabled),{1:receiver})
        for key in ('mcProgramPtsValue','mcProgramPtsMax'):
            assert receiver[key]['mData']['display']==(expected if enabled else native_label(points)), (enabled,points,key,receiver[key]['mData']['display'],expected)
            assert receiver[key]['mData']['ExtraInfo']=={'font':'native','fontColor':123}
        assert receiver['mcTitle']['calls']==[] and data==original

        # Native TextUtil._Step keeps `current`/`start`/`end` in its own state
        # and supplies that numeric value to _SetLabel. It never reads the
        # formatted monetary string back into its arithmetic.
        state={'start':25,'current':points,'end':1000,'m':10,'asInt':True}
        state_before=copy.deepcopy(state)
        target=receiver['mcProgramPtsValue'];target['mData']['display']=native_label(points);target['calls'].clear()
        # Static callback register1 is a native formatted local string, not a
        # receiver. A wrong implicit-this assumption must fail this fixture.
        Machine(GLOBALS,[]).run(program(animation_suffix,enabled),{1:'native output',2:state['current'],3:target})
        assert target['mData']['display']==(expected if enabled else native_label(points))
        assert state==state_before and data==original

        popup={'mPopupInfo':{'CustomData':{'RemainingProgramPoints':1000,'NILValuation':points}},
               'mRemainingProgramPointsAfterCost':points,'mcProgramPoints':text(points),'mcNIL':text(points),
               'mcCurrentMaxOffer':text('native max'),'mcCoachPointsDescription':text('skill points')}
        before=copy.deepcopy(popup['mPopupInfo'])
        Machine(GLOBALS,[]).run(program(popup_suffix,enabled),{1:popup})
        assert popup['mcProgramPoints']['mData']['display']==(expected if enabled else native_label(points))
        assert popup['mcNIL']['mData']['display']==(expected if enabled else native_label(points))
        assert popup['mPopupInfo']==before and popup['mRemainingProgramPointsAfterCost']==points
        assert popup['mcCurrentMaxOffer']['calls']==[] and popup['mcCoachPointsDescription']['calls']==[]

# The shared animation helper is inert for ordinary numeric animations, coach
# XP, ratings, percentages, hours and any target without our private marker.
for marker in (None,False,'true',1):
    for value in (0,75,1000):
        target=text(value)
        if marker is not None:target[MARKER]=marker
        Machine(GLOBALS,[]).run(program(animation_suffix),{1:'native',2:value,3:target})
        assert target['calls']==[]
for value in (None,UNDEFINED,'',' ','?','Hidden','NaN','Infinity','-Infinity','$0','$40K','$1.0M','40K','1.0M','75%',float('nan'),float('inf')):
    target=text('native');target[MARKER]=True
    Machine(GLOBALS,[]).run(program(animation_suffix),{1:'native',2:value,3:target})
    assert target['calls']==[]
    for builder,names in [(budget_suffix,('mcProgramPtsValue','mcProgramPtsMax')),(popup_suffix,('mcProgramPoints','mcNIL'))]:
        receiver={key:text(value) for key in names}
        Machine(GLOBALS,[]).run(program(builder),{1:receiver})
        assert all(not receiver[key]['calls'] for key in names)
for builder in (budget_suffix,popup_suffix):
    Machine(GLOBALS,[]).run(program(builder),{1:{}})
Machine(GLOBALS,[]).run(program(mark_budget_value,ret=True),{1:{}})
Machine(GLOBALS,[]).run(program(animation_suffix),{1:'native',2:75,3:{}})

# Native rows accept slash-prefixed maximums and split remaining/total labels.
# Only verified budget slots use this extension, not arbitrary ratios/hours.
for enabled in (True,False):
    for value,expected in [('915/10,630','3.7M / 42.5M'),('915 / 10,630','3.7M / 42.5M'),
                           ('/10,630','/42.5M'),('915/','3.7M/'),('0/','0/'),('/0','/0'),
                           ('75/0','300K / 0'),('0/250','0 / 1.0M')]:
        receiver={'mcProgramPtsValue':text(value),'mcProgramPtsMax':text(value)}
        Machine(GLOBALS,[]).run(program(budget_suffix,enabled),{1:receiver})
        assert all(receiver[key]['mData']['display']==(expected if enabled else value) for key in ['mcProgramPtsValue','mcProgramPtsMax'])
for value in ('/','//','1/2/3','300K/10,630','915/42.5M','/$0','?/', '/Hidden'):
    receiver={'mcProgramPtsValue':text(value),'mcProgramPtsMax':text(value)}
    Machine(GLOBALS,[]).run(program(budget_suffix),{1:receiver})
    assert not receiver['mcProgramPtsValue']['calls'] and not receiver['mcProgramPtsMax']['calls']


def sized_text(value,x=0):
    result=text(value);result.update({'_x':x,'_y':17})
    result['GetWidth']=lambda:len(result['mData']['display'])*7
    return result


def budget_frame():
    result={'_x':33,'_y':47,'width':148,'calls':[]}
    def set_width(width):result['width']=width;result['calls'].append(width)
    result.update({'GetWidth':lambda:result['width'],'SetWidth':set_width})
    return result


for enabled in (True,False):
    for remaining,total,expected_remaining,expected_total in [(915,10630,'3.7M/','42.5M'),
            (0,0,'0/','0'),(-15,250,'-60K/','1.0M'),('915','10,630','3.7M/','42.5M')]:
        extra={'SchoolInfo':{'DynastyPointsBudget':remaining,'DynastyPointsBudgetGrade':'B+',
                            'StadiumCapacity':100119,'YearFounded':1883,'AllTimeRecord':'921-389-33 (.685)'},
               'Budget':{'Remaining':remaining,'Budget':total},
               'BudgetData':{'Remaining':remaining,'Budget':total},'Contract':{'Salary':45,'Years':3}}
        original=copy.deepcopy(extra)
        school={'mData':{'ExtraInfo':extra},'mcDynastyPointsValue':sized_text(remaining,100),
                'mcDynastyPointsGrade':{'_x':999,'mData':{'ExtraInfo':{'Grade':'B+'}}},
                'DYNASTY_POINTS_GRADE_OFFSET':9,'mcRemainingBudget':text(str(remaining)+'/'),
                'mcTotalBudget':text(total),'mcYearFoundedValue':text(1883)}
        Machine(GLOBALS,[]).run(program(school_budget_suffix,enabled),{1:school})
        assert school['mcDynastyPointsValue']['mData']['display']==(expected_remaining[:-1] if enabled else native_label(remaining))
        assert school['mcRemainingBudget']['mData']['display']==(expected_remaining if enabled else str(remaining)+'/')
        assert school['mcTotalBudget']['mData']['display']==(expected_total if enabled else native_label(total))
        grade=school['mcDynastyPointsGrade']
        assert grade['_x']==(100+school['mcDynastyPointsValue']['GetWidth']()+9 if enabled else 999)
        assert grade['mData']['ExtraInfo']['Grade']=='B+' and not school['mcYearFoundedValue']['calls']
        assert extra==original

        overview={'mData':{'ExtraInfo':extra},'mcRemainingBudget':sized_text(str(remaining)+'/'),
                  'mcTotalBudget':sized_text(total),'mcBudgetTitle':sized_text('Budget',300),
                  'mcBudgetBG':budget_frame(),'mcProgramPointsPie':{'mData':{'ExtraInfo':{'Currency':total}}},
                  'mcStaffAllocation':{'mData':{'ExtraInfo':{'SpentPercentage':25,'SpentTotal':55}}}}
        pie_before=copy.deepcopy(overview['mcProgramPointsPie'])
        allocation_before=copy.deepcopy(overview['mcStaffAllocation'])
        Machine(GLOBALS,[]).run(program(overview_budget_suffix,enabled),{1:overview})
        assert overview['mcRemainingBudget']['mData']['display']==(expected_remaining if enabled else str(remaining)+'/')
        assert overview['mcTotalBudget']['mData']['display']==(expected_total if enabled else native_label(total))
        frame=overview['mcBudgetBG']
        width=overview['mcRemainingBudget']['GetWidth']()+overview['mcTotalBudget']['GetWidth']()+24
        assert frame['width']==(width if enabled else 148)
        assert frame['_x']==(300-width/2 if enabled else 33) and frame['_y']==47
        assert extra==original and overview['mcProgramPointsPie']==pie_before and overview['mcStaffAllocation']==allocation_before
for builder in (school_budget_suffix,overview_budget_suffix):
    Machine(GLOBALS,[]).run(program(builder),{1:{}})

# Exact current Program Overview middle values, independent of allocation
# percentages. The SingleRow rendering is a different native percent variant.
for enabled in (True,False):
    for name,points,expected in [('Staff',445,'1.8M'),('Facilities',250,'1.0M'),
            ('Recruits',620,'2.5M'),('Roster',115,'460K'),('Unspent',200,'800K'),
            ('Zero',0,'0'),('String','1,475','5.9M')]:
        extra={'SpentTotal':points,'SingleRow':False,'Title':name,'SpentPercentage':31,
               'SuggestedPercentage':'20%','SpentTotalColor':0xabcdef,'IconId':999,'IconLibrary':123}
        before=copy.deepcopy(extra)
        receiver={'mData':{'ExtraInfo':extra},'mcSpentTotal':text(points),'mcSpentPercentage':text('31%'),
                  'mcSuggestedPercentage':text('20%'),'mcTitle':text(name),'mcIcon':{'Id':999}}
        for _ in range(2):
            Machine(GLOBALS,[]).run(program(allocation_suffix,enabled),{1:receiver})
            assert receiver['mcSpentTotal']['mData']['display']==(expected if enabled else native_label(points))
        assert not receiver['mcSpentPercentage']['calls'] and not receiver['mcSuggestedPercentage']['calls'] and not receiver['mcTitle']['calls']
        assert extra==before and receiver['mcIcon']=={'Id':999}
    receiver={'mData':{'ExtraInfo':{'SpentTotal':30,'SingleRow':True}},'mcSpentTotal':text('30%')}
    Machine(GLOBALS,[]).run(program(allocation_suffix,enabled),{1:receiver})
    assert receiver['mcSpentTotal']['mData']['display']=='30%' and not receiver['mcSpentTotal']['calls']

    extra={'UpperData':{'Title':'Total budget','Currency':1475},'LowerData':{'Title':'Remaining','Currency':200},
           'ItemArray':[{'CurrencyValue':445,'Y':31},{'CurrencyValue':250,'Y':17}],
           'BudgetVisible':True,'FocusIndex':0,'GraphSize':460,'RendererInfo':{'MaxY':100}}
    before=copy.deepcopy(extra)
    receiver={'mData':{'ExtraInfo':extra},'mcBudgetCurrency':text('1,475'),'mcRemainingCurrency':text('200/'),
              'mcBudgetTitle':text('Blueprint Budget'),'mBudgetCurrency':1475,'mGraphSize':460,
              'mPointsProvider':{'items':[31,17]},'mGraphRenderer':{'max':100},
              'mcTextContainer':{'_x':99,'_y':79}}
    for _ in range(2):
        Machine(GLOBALS,[]).run(program(pie_currency_suffix,enabled),{1:receiver})
        assert receiver['mcBudgetCurrency']['mData']['display']==('5.9M' if enabled else '1,475')
        assert receiver['mcRemainingCurrency']['mData']['display']==('800K/' if enabled else '200/')
    assert extra==before and receiver['mBudgetCurrency']==1475 and receiver['mGraphSize']==460
    assert receiver['mPointsProvider']=={'items':[31,17]} and receiver['mGraphRenderer']=={'max':100}
    assert receiver['mcTextContainer']=={'_x':99,'_y':79} and not receiver['mcBudgetTitle']['calls']
for builder in (allocation_suffix,pie_currency_suffix):
    Machine(GLOBALS,[]).run(program(builder),{1:{}})
for bad in (None,UNDEFINED,'Hidden','NaN','Infinity','$40K','40K','1.0M','25%'):
    receiver={'mData':{'ExtraInfo':{'SpentTotal':bad,'SingleRow':False,
               'UpperData':{'Currency':bad},'LowerData':{'Currency':bad}}},
              'mcSpentTotal':text('native'),'mcBudgetCurrency':text('native'),'mcRemainingCurrency':text('native')}
    for builder in (allocation_suffix,pie_currency_suffix):
        Machine(GLOBALS,[]).run(program(builder),{1:receiver})
    assert all(not receiver[k]['calls'] for k in ['mcSpentTotal','mcBudgetCurrency','mcRemainingCurrency'])

sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load
assets={'corePrograms':load(CFM),'animationPrograms':load(CONTROL),'artPrograms':load(ART)}
for group,offset,argc,registers,flags,size,hash_,prefix,builder in SPECS:
    apt=assets[group];h=apt.data[offset:offset+48];body=apt.data[offset+48:offset+48+size]
    assert struct.unpack_from('<IHH',h,8)==(argc,registers,flags)
    assert struct.unpack_from('<I',h,24)[0]==size and fnv(body)==hash_
    class Bounded(Assembler):
        def reg(self,n):assert n<registers;super().reg(n)
        def store(self,n):assert n<registers;super().store(n)
    a=Bounded()
    if prefix:prefix(a);a.pad_code()
    a.code.extend(bytes(size))
    if builder:builder(a)
    else:a.ret()
    assert len(a.finish().code)<32768

cfm=assets['corePrograms']
budget=cfm.data[0x39078:0x39078+3377]
assert bytes.fromhex('b901ac0385398d') in budget # mData.ExtraInfo.ProgramPtsValue
assert bytes.fromhex('b901ac0385399b') in budget # mData.ExtraInfo.MaxProgramPtsValue
assert bytes.fromhex('b901af62b2aa') in budget # mcProgramPtsValue.SetLabel
assert bytes.fromhex('b901af66b2aa') in budget # mcProgramPtsMax.SetLabel
update=cfm.data[0x38A58:0x38A58+61]
assert bytes.fromhex('b901ac0385398d') in update and bytes.fromhex('b901ac0385398e') in update
assert bytes.fromhex('b901af62b50aad028f90b291') in update # target + steps10 + TextUtil.Increment
setup=cfm.data[0x7C4A0:0x7C4A0+3922]
assert bytes.fromhex('b901ac033839d2') in setup # popup.CustomData.NILValuation
changed=cfm.data[0x7E700:0x7E700+554]
assert bytes.fromhex('b907b9040b') in changed # native available-minus-current-offer
assert bytes.fromhex('b901af15a353015d') in changed # mcProgramPoints.SetLabel
control=assets['animationPrograms'];body=control.data[0x66DE0:0x66DE0+227]
assert bytes.fromhex('b902') in body and bytes.fromhex('b903b228') in body # current numeric value; target.SetLabel
school=cfm.data[0x70258:0x70258+1024]
assert bytes.fromhex('b901ac03b744b3') in school # mData.ExtraInfo.SchoolInfo
assert bytes.fromhex('b903afc5') in school and bytes.fromhex('b901af83b2c2') in school # DynastyPointsBudget -> mcDynastyPointsValue.SetLabel
assert bytes.fromhex('b901ac03b744b5') in school # mData.ExtraInfo.Budget
assert bytes.fromhex('b907afed') in school and bytes.fromhex('b907afb5') in school # Budget.Remaining, Budget.Budget
assert bytes.fromhex('b901af3db2c2') in school and bytes.fromhex('b901af3bb2c2') in school # split remaining/total labels
overview=cfm.data[0x71120:0x71120+526]
assert bytes.fromhex('b901ac037b2a77') in overview # mData.ExtraInfo.BudgetData
assert bytes.fromhex('b904af91') in overview and bytes.fromhex('b904af8f') in overview # Remaining, Budget
assert bytes.fromhex('b901af27b285') in overview and bytes.fromhex('b901af25b285') in overview # split labels
art=assets['artPrograms'];allocation=art.data[0x43F38:0x43F38+942]
assert bytes.fromhex('b901ac03511842') in allocation # mData.ExtraInfo.SpentTotal
assert bytes.fromhex('b901af2ab25e') in allocation # mcSpentTotal.SetLabel
assert bytes.fromhex('b901ac0351184f') in allocation # separate SingleRow percent variant
assert bytes.fromhex('b901ac03511841') in allocation # distinct SpentPercentage remains native
assert art.data[0x43D60:0x43D62]==bytes.fromhex('743e') # native SingleRow default callback returns false
pie=art.data[0x45780:0x45780+310]
assert bytes.fromhex('b901ac033d3134') in pie and bytes.fromhex('b901ac033d3135') in pie # UpperData/LowerData
assert bytes.fromhex('b906af96') in pie and bytes.fromhex('b904af96') in pie # each Currency source
assert bytes.fromhex('b901af71b247') in pie and bytes.fromhex('b901af72b247') in pie # budget/remaining labels
with tempfile.TemporaryDirectory() as folder:
    output=Path(folder)/'budget.h';generate(output)
    assert output.read_bytes()==(ROOT/'Source/CurrencyBudgetUiPrograms.h').read_bytes()
print('Passed: native school/overview budget headers, inner allocation totals and pie center amounts, monetary ratios and slash-decorated rows, wallet/grade layout, marker-only animation and offer popup; numeric sources, contracts, grades, records, graph data, percentage variants and counters preserved; symbol-free, invalid/preformatted rejection, original register frames and exact source fingerprints.')
