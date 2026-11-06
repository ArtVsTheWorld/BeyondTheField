"""Currency-only labels, icon gates, source preservation and native frames."""
from pathlib import Path
import copy,math,sys,struct
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,fnv
from build_currency_ui import money,icon_label_suffix,info_slot_suffix,point_cell_suffix,team_budget_suffix,SPECS
from recruit_notes_vm import Machine,UNDEFINED

def program(suffix,on=True):
    a=Assembler();suffix(a);p=a.finish();code=bytearray(p.code)
    for at in p.dollar_offsets:code[at]=int(on)
    return replace(p,code=bytes(code))
globals_={'Math':{'round':lambda n:math.floor(n+.5),'floor':math.floor},
          'shared_enum':{'fblibraries':{'global':{'Icons':{'LIBRARY_ID':7,'ASSETID_ICON_CURRENCY_PROGRAMPOINTS':19}}}},
          'art_utility':{'ImageUtil':{'BuildFbImageString':lambda icon,lib:f'fbimage:{icon}:{lib}'}}}
cases={0:'0',1:'4K',10:'40K',249:'996K',250:'1.0M',275:'1.1M',860:'3.4M',1860:'7.4M',10630:'42.5M',-10:'-40K',-250:'-1.0M'}
for source,expected in [*cases.items(),('1,860','7.4M'),('915/10,630','3.7M / 42.5M'),('915 / 10,630','3.7M / 42.5M')]:
    for on in [False,True]:
        for icon in ['fbimage:19:7','19:7']:
            calls=[];data={'value':icon,'display':source,'ExtraInfo':{'font':'native'}};before=copy.deepcopy(data)
            child={'SetLabel':calls.append};receiver={'mData':data,'mcLabel':child}
            Machine(globals_,[]).run(program(icon_label_suffix,on),{1:receiver})
            assert calls==([expected] if on else []) and data==before,(icon,source,calls)
for icon in ['fbimage:18:7','fbimage:19:0','18:7','19:0','7:19','swap:19:7','unexpected:19:7','19:7:extra','19','',None,UNDEFINED]:
    calls=[];receiver={'mData':{'value':icon,'display':10},'mcLabel':{'SetLabel':calls.append}}
    Machine(globals_,[]).run(program(icon_label_suffix),{1:receiver});assert not calls
for hidden in [None,UNDEFINED,'','   ','?','--','Hidden','$0','$40K','$1.0M','40K','1.0M','NaN','Infinity','-Infinity','10%','1/2/3',float('nan'),float('inf')]:
    calls=[];receiver={'mData':{'value':'fbimage:19:7','display':hidden},'mcLabel':{'SetLabel':calls.append}}
    Machine(globals_,[]).run(program(icon_label_suffix),{1:receiver});assert not calls,hidden
    calls=[]
    Machine(globals_,[]).run(program(point_cell_suffix),{1:{'mTextField':{'SetText':calls.append}},3:{'display':hidden}})
    assert not calls,('grid text converted twice',hidden)
# The native APT engine must not need IEEE NaN equality/Math behavior to reject
# text a preceding display adapter already converted. Emulate a permissive
# numeric VM too, so the guard itself proves that these values never reach Math.
class PermissiveNaN(Machine):
    @staticmethod
    def equal(left,right,loose=False):
        if isinstance(left,float) and isinstance(right,float) and math.isnan(left) and math.isnan(right):return True
        return Machine.equal(left,right,loose)
def no_bad_math(value):
    assert math.isfinite(value),'Invalid currency reached native arithmetic'
    return math.floor(value+.5)
permissive={**globals_,'Math':{'round':no_bad_math,'floor':lambda value:math.floor(value)}}
for hidden in ['$0','$40K','$1.0M','NaN',float('nan')]:
    calls=[];PermissiveNaN(permissive,[]).run(program(point_cell_suffix),{1:{'mTextField':{'SetText':calls.append}},3:{'display':hidden}})
    assert not calls,('Noncanonical money reached a permissive native VM',hidden)
for source,expected in cases.items():
    for suffix,target,model,registers in [
        (info_slot_suffix,'mcCurrencyValue',{'mData':{'ExtraInfo':{'UseCurrencyValue':True,'CurrencyValue':source,'CurrencyIconId':19,'CurrencyIconLibrary':7}}},{}),
        (point_cell_suffix,'mTextField',{}, {3:{'display':str(source),'intValue':source,'isDisabled':True}})]:
        calls=[];before=copy.deepcopy(model);original=copy.deepcopy(registers);receiver={**model,target:{'SetLabel':calls.append,'SetText':calls.append}}
        Machine(globals_,[]).run(program(suffix),{1:receiver,**registers})
        assert calls==[expected] and registers==original,(source,suffix.__name__,calls,expected)
        for key,value in before.items():assert receiver[key]==value
for prop,value in [('CurrencyIconId',18),('CurrencyIconLibrary',0),('UseCurrencyValue',False)]:
    calls=[];info={'UseCurrencyValue':True,'CurrencyValue':10,'CurrencyIconId':19,'CurrencyIconLibrary':7};info[prop]=value
    Machine(globals_,[]).run(program(info_slot_suffix),{1:{'mData':{'ExtraInfo':info},'mcCurrencyValue':{'SetLabel':calls.append}}})
    assert not calls,(prop,value)
for enabled in [False,True]:
    for money_layout in [False,True]:
        fields=['RecruitNILValue','RosterNILValue','UnspentValue','RecruitNILSuggestedValue','RosterNILSuggestedValue','UnspentSuggestedValue']
        widgets=['mcRecruitNILValue','mcRosterNILValue','mcUnspentNILValue','mcRecruitNILSubvalue','mcRosterNILSubvalue','mcUnspentNILSubvalue']
        values=dict(zip(fields,[10,1500,250,25,2000,500]));data={'ExtraInfo':{'IsProgramPointsNILData':money_layout,'ProgramPointsNILData':values}};original=copy.deepcopy(data)
        calls={widget:[] for widget in widgets};receiver={'mData':data,**{widget:{'SetLabel':calls[widget].append} for widget in widgets}}
        Machine(globals_,[]).run(program(team_budget_suffix,enabled),{1:receiver})
        assert data==original
        assert [calls[w] for w in widgets]==([[s] for s in ['40K','6.0M','1.0M','100K','8.0M','2.0M']] if enabled and money_layout else [[]]*6)
class Bounded(Assembler):
    def reg(self,n):assert n<4;super().reg(n)
    def store(self,n):assert n<4;super().store(n)
for suffix in [icon_label_suffix,info_slot_suffix,point_cell_suffix]:
    a=Bounded();suffix(a);a.finish()
sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load
# Source contract: canonical ImageUtil prepends the native format token; the
# coach pending-offer widget instead constructs exactly assetId:libraryId.
# These are explicit forms, not substring/icon-name heuristics.
framework=load(Path('../AbilityColors/Research/assets/common/ui/node_com/frameworkscriptpod.ast'))
helper=framework.data[0x751a8:0x751a8+21]
assert helper.hex()=='59ad024546a24752a24347b90147a24347b902473e'
pending=load(Path('Evidence/PlayerFog/Gaps/current-cfm-currency.ast'))
assert fnv(pending.data[0xbd738:0xbd738+1076])==0xe151c595349a4bc3
assert pending.data[0xbda1b:0xbda2e].hex()=='ad054748494a4ba24c47ad054748494a4d474f'
for asset,specs in SPECS.values():
    apt=load(Path(asset))
    for off,argc,regs,flags,size,expected,suffix in specs:
        header=apt.data[off:off+48]
        assert (struct.unpack_from('<I',header,8)[0],struct.unpack_from('<H',header,12)[0],struct.unpack_from('<H',header,14)[0])==(argc,regs,flags)
        assert fnv(apt.data[off+48:off+48+size])==expected
        assert len(program(suffix).code)<32768
print('Passed: $4K per point, K/M rounding, signed values/ratios, default-Off no-op, exact program-point icon gate, untouched budgets/sorting/styles and four-register native frames.')
