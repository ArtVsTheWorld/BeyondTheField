"""Execute the minimal adapter around the actual unchanged native UI bodies."""
from dataclasses import replace
import copy
import inspect
import math
from pathlib import Path
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from build_draft_ovr_ui import emit,FixedFrameAssembler,rows_suffix,SPECS
from grade_scales import BANDS
from recruit_notes_vm import Machine,UNDEFINED,ScriptFunction
sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load

class DraftMachine(Machine):
    @staticmethod
    def member(receiver,key):
        if isinstance(receiver,str) and key=='toUpperCase':return lambda:receiver.upper()
        return Machine.member(receiver,key)
namespace=dict(math=math,struct=struct,UNDEFINED=UNDEFINED,ScriptFunction=ScriptFunction)
source=inspect.getsource(Machine.run).replace('    def run(','def run(',1).replace('\n    ','\n')
source=source.replace('pc, stack = begin, []','pc, stack = begin, []; locals_ = {}')
source=source.replace('stack.append(self.globals[stack.pop()])','stack.append((lambda key: locals_.get(key,self.globals.get(key,UNDEFINED)))(stack.pop()))')
source=source.replace('elif op == 0xAF:',"elif op == 0xA3:\n                stack.append(self.pool[struct.unpack_from('<H',code,pc)[0]]);pc+=2\n            elif op == 0xAF:")
source=source.replace('elif op == 0x4F:',"elif op == 0x4D:\n                stack[-1],stack[-2]=stack[-2],stack[-1]\n            elif op == 0x3C:\n                value,key=stack.pop(),stack.pop();locals_[key]=value\n            elif op == 0x4F:")
exec(source,namespace);DraftMachine.run=namespace['run']

hub=load(ROOT.parent/'PlayerAnalytics/Research/assets/common/ui/node_cfm/hub/corenode.ast')
com=load(ROOT.parent/'PlayerAnalytics/Research/assets/common/ui/node_com/scriptpod.ast')
hub_items=hub.decode(298176);hub_pool=hub_items[0][2];row_pool=com.decode(1081200)[0][2]
assert hub_pool[6]=='PlayersLeavingStrategy'
methods=[(i,item) for i,item in enumerate(hub_items) if len(item)>3 and item[2][3]=='0x49ac8']
assert len(methods)==1 and hub_items[methods[0][0]-1][2][1]=='_GetTeamModule'
assert len(SPECS)==2 and {spec[0] for spec in SPECS}=={'strategy','rows'}

def program(mode):
    if mode=='strategy':
        a=emit(mode);begin=len(a.code);native=hub.data[0x49ac8:0x49ac8+207];a.code.extend(native)
    else:
        a=FixedFrameAssembler(6);begin=0;native=com.data[0x108a40:0x108a40+69];a.code.extend(native);rows_suffix(a)
    p=a.finish();assert p.code[begin:begin+len(native)]==native
    return p

native_header_calls=[];provider={};team_header={'_visible':True,'SetExtraInfo':lambda info:native_header_calls.append(('team',info))}
player_header={'SetExtraInfo':lambda info:native_header_calls.append(('player',info))}
team={'isEmpty':False,'teamLogoId':'native-logo','teamNickName':'Native','teamRank':4,'teamLongName':'Native School','teamRecords':'4-0','schoolPrestige':3,'teamOVR':86,'teamOFF':85,'teamDEF':84,'teamPrimaryColor':1,'teamSecondaryColor':2,'conferenceLogoId':'native-conf','isUserTeam':True}
strategy={'mIsDraftClass':True,'mSpreadsheetDataProvider':provider,'mPlayersLeavingAdapter':{'GetTeamInfo':lambda:team},'mcSpreadsheet':{'IsEmpty':lambda:False},'mcSpreadsheetTeamModuleHorizontal':team_header,'mcSpreadsheetPlayerModule':player_header}
assert DraftMachine({},hub_pool).run(program('strategy'),{1:strategy}) is UNDEFINED
assert provider=={'mDEDraftOvr':True}
assert len(native_header_calls)==2 and native_header_calls[0][1]['TeamOVR']==86 and team['teamOVR']==86
assert team_header['_visible'] is True
for value in [False,None,UNDEFINED,'true',1]:
    strategy['mIsDraftClass']=value
    DraftMachine({},hub_pool).run(program('strategy'),{1:strategy})
    assert provider['mDEDraftOvr'] is False,'Ordinary Players Leaving retained the Draft marker'
strategy['mIsDraftClass']=True;DraftMachine({},hub_pool).run(program('strategy'),{1:strategy})

def show(cells,columns,marker=True,scale=0,fog=True,colors=True):
    original=copy.deepcopy(cells);calls=[]
    p=program('rows');code=bytearray(p.code)
    for offsets,value in [(p.scale_offsets,scale),(p.fog_offsets,int(fog)),(p.color_offsets,int(colors))]:
        for at in offsets:code[at]=value
    p=replace(p,code=bytes(code))
    def native_rows(sheet,row,requested):
        calls.append((sheet,row,requested));assert requested is columns
        return cells
    receiver={'mDEDraftOvr':marker,'mSpreadsheetId':88,'_GetDatasourceRowIndexFromSpreadSheetRowIndex':lambda row:row+20,'mSpreadsheetAdapter':{'GetListRowData':native_rows}}
    result=DraftMachine({},row_pool).run(p,{1:receiver,5:7,4:columns})
    assert result is cells and calls==[(88,27,columns)]
    for before,after in zip(original,cells):
        assert {k:v for k,v in before.items() if k!='display'}=={k:v for k,v in after.items() if k!='display'}
    return result

for scale,bands in enumerate(BANDS):
    for value in range(101):
        for colors in [False,True]:
            for selected,gray in [(False,False),(True,False),(False,True)]:
                cell={'display':str(value),'value':value,'style':{'color':0x777777 if gray else 0 if selected else 0xffffff},'ExtraInfo':{'native':'retained'},'key':'native-opaque-dto-key','isSelected':selected,'isGray':gray}
                cells=show([cell,{'display':'Round 3','value':3}],[4,5],scale=scale,colors=colors)
                assert cells[0]['display']==next(label for upper,label in bands if value<upper)
                assert cells[1]=={'display':'Round 3','value':3}
for marker in [False,None,UNDEFINED,'true',1]:
    cell={'display':'91','value':91};show([cell],[4],marker=marker);assert cell['display']=='91'
for value in [None,UNDEFINED,'?','--','','-1','101','85,TrendUp',' 85','085',-1,101,float('nan'),float('inf')]:
    cell={'display':value,'value':123,'style':{'color':0x777777}};show([cell],[4]);assert cell['display'] is value or cell['display']==value
for fog in [False,True]:
    cell={'display':'85','value':85};show([cell],[4],fog=fog);assert cell['display']==('B' if fog else '85')
for columns in [[1,5],[5,1,4],[4,4,5]]:
    cells=[{'display':'85','value':85} for _ in columns];show(cells,columns)
    assert [c['display'] for c in cells]==['B' if col==4 else '85' for col in columns]
show([],[])

for mode,_,_,_,registers,_,_,_ in SPECS:
    a=emit(mode);assert a.native_registers==registers
    p=a.finish();pc=0
    while pc<len(p.code):
        op=p.code[pc];pc+=1
        if op==0xb9:assert p.code[pc]<registers;pc+=1
        elif op==0xb5:pc+=1
        elif op==0xb6:pc+=2
        elif op==0xa1:pc=((pc+7)&~7)+8
        elif op in (0x87,0x9d,0xb8,0x99):pc=((pc+7)&~7)+4
forbidden={'GetTeamInfo','SetByItemArray','ResetData','HandleInput','GetHints','GetEntryInfo','FindLeavingPlayer','NavigateBackward','GetRowKey','SetDelay','mDEDraftRows','DEDraftBoard'}
assert not forbidden.intersection(value for _,value in program('rows').literals)
assert not forbidden.intersection(value for _,value in emit('strategy').finish().literals)
print('Minimal Draft OVR: exact two native callbacks, full stock bodies, all101 grades ×4 scales, unmodified styles/values/keys and native frames pass')
