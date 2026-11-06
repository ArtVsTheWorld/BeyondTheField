"""Run the custom draft provider without native methods, hooks or a game."""
import copy
from dataclasses import replace
import inspect
import math
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler
from build_draft_results_ui import emit,COLUMNS,native_rows_suffix,SPECS,FixedFrameAssembler,NAVIGATION_CODES
from recruit_notes_vm import Machine,UNDEFINED,ScriptFunction
from grade_scales import BANDS

# A full224-row wire plus scope filtering is bounded but exceeds the tiny
# single-widget verifier's default budget. The emitted game code has no timer
# or recurring sort: this parse runs once when a fresh draft view is ready.
class DraftMachine(Machine):
    @staticmethod
    def member(receiver,key):
        if isinstance(receiver,str) and key=='split':return lambda separator:receiver.split(separator)
        return Machine.member(receiver,key)
namespace=dict(math=math,struct=struct,UNDEFINED=UNDEFINED,ScriptFunction=ScriptFunction)
machine_source=inspect.getsource(Machine.run).replace('    def run(','def run(',1).replace('\n    ','\n').replace('range(10000)','range(500000)')
machine_source=machine_source.replace('pc, stack = begin, []','pc, stack = begin, []; locals_ = {}')
machine_source=machine_source.replace('stack.append(self.globals[stack.pop()])','stack.append((lambda key: locals_.get(key,self.globals.get(key,UNDEFINED)))(stack.pop()))')
machine_source=machine_source.replace("elif op == 0x4F:","elif op == 0x4D:\n                stack[-1],stack[-2]=stack[-2],stack[-1]\n            elif op == 0x3C:\n                value,key=stack.pop(),stack.pop();locals_[key]=value\n            elif op == 0x4F:")
exec(machine_source,namespace)
DraftMachine.run=namespace['run']

def program(mode):
    a=emit(mode);a.string('native');a.raw(0x3E);return a.finish()

def run(mode,self,args=None,globals_=None):
    environment={**(globals_ or {}),'this':self}
    # GetHints has SuppressThis/PreloadSuper: r1 is super, not this.
    receiver={'GetHints':lambda:(_ for _ in ()).throw(AssertionError('native command hints'))} if mode=='hints' else self
    return DraftMachine(environment,[]).run(program(mode),{1:receiver,**(args or {})})

def provider_callbacks(provider):
    provider['GetNumMaxRows']=lambda:run('count',provider)
    provider['_GetColumnData']=lambda:run('columns',provider)
    return provider

def fixture():
    rows=[['P',f'8:{i}',f'Player {i}',['QB','HB'][i%2],'SR (RS)',str(60+i%41),str(i%2+1),['Custom U','State'][i%2],['2:0','2:1'][i%2],str(i//32+1)] for i in range(224)]
    scopes=[['S','national','National','1,2,3'],['S','conference:2:1','Another Conference','2'],['S','conference:2:0','Custom Conference','1,3'],['S','team:1','Custom U','1'],['S','team:2','State','2'],['S','team:3','Empty U','3']]
    wire='DE_DRAFT_2\t4294954951\t2028\t1\n'+'\n'.join('\t'.join(row) for row in scopes+rows)+'\n'
    return wire,rows,scopes

def connected_screen(wire):
    """Native-component stand-ins execute the actual emitted callback chain.

    Synchronous dropdown/ResetData events deliberately reenter the strategy.
    All DTO, player-card and Ucm command paths are poisoned, not mocked safe.
    """
    provider=provider_callbacks({});calls=[];reset_observations=[];timers={};forbidden=[]
    filters={'value':None,'open':False};strategy={};context=object()
    def poison(name):
        def fail(*args):forbidden.append(name);raise AssertionError('Unsafe native DTO route: '+name)
        return fail
    def set_items(index,items):
        calls.append(('scopes',index,items));filters['value']=next(v['key'] for v in items if v['isDefault'])
        # The game emits this before SetByItemArray returns.
        strategy['_OnFilterItemChanged']({'ToggleIndex':index})
    def filter_input(event):
        code=event['KeyCode'];calls.append(('filter_input',code))
        if code=='LT':filters['open']=True;return True
        if filters['open']:
            if code in ['BACK','PRIMARY']:filters['open']=False
            return True
        return False
    filters.update(ChangeNumToggles=lambda n:calls.append(('toggles',n)),SetByItemArray=set_items,
                   GetToggleValue=lambda index:filters['value'],HandleInput=filter_input)
    def clear_delay(name):calls.append(('clear',(name,)));timers.pop(name,None)
    def set_delay(name,callback,delay,unused):calls.append(('delay',(name,delay)));timers[name]=callback
    manager={'ClearDelay':clear_delay,'SetDelay':set_delay}
    def navigate_backward(ctx):
        # Native navigation backs the strategy up synchronously, before it
        # shuts down. No selected custom key may reach its DTO converter.
        assert run('backup',strategy,globals_=globals_)=={}
        calls.append(('back',ctx))
    navigator={'NavigateBackward':navigate_backward}
    globals_={'cafe':{'manager':{'IntervalManagerService':{'Get':lambda *args:manager}},
                      'utility':{'Delegate':{'Create':lambda receiver,fn:fn}},
                      'node':{'NavigatorService':{'Get':lambda ctx:navigator}}},
              'ion':{'enum':{'Input':{'CODE_BACK':'BACK',**{code:code for code in NAVIGATION_CODES}}}},
              'art_styleguide':{'Color':{'FLOATING_TEXT_COLOR':0xdddddd}},
              'adapterenum_com':{'DataSource':{'SORTORDER_ASCENDING':1}}}
    adapter={'GetTeamInfo':lambda:{'DEDraftBoard':wire},**{name:poison(name) for name in ['GetEntryInfo','GetPersuasionData','FindLeavingPlayer','CanPersuadePlayer']}}
    strategy.update(mIsDraftClass=True,mSpreadsheetDataProvider=provider,mPlayersLeavingAdapter=adapter,
                    mcFilter=filters,mcSpreadsheetTeamModuleHorizontal={'_visible':True},mContext=context,
                    mcSpreadsheetPlayerModule={'_visible':True,'HandleInput':poison('player-card HandleInput')},
                    mCommandHelper={'HandleInput':poison('command HandleInput'),'GetHints':poison('command GetHints')})
    strategy['_GetTeamModule']=lambda:run('team',strategy,globals_=globals_)
    strategy['_OnFilterItemChanged']=lambda event:run('filter',strategy,{3:event},globals_)
    strategy['_RowChanged']=lambda event:run('row_changed',strategy,{25:event},globals_)
    strategy['_IsRowSelected']=lambda row:run('row_selected',strategy,{4:row},globals_)
    def reset_data(*args):
        calls.append(('reset',args));length=len(provider.get('mDEDraftRows',[]))
        reset_observations.append((strategy.get('mIsSpreadsheetEmpty'),length))
        assert strategy['mIsSpreadsheetEmpty'] is (length==0)
        # ResetData dispatches SelectRow/RowChanged synchronously, even when
        # the previous table was empty and its native sidebar had no DTO.
        strategy['_RowChanged']({'NewRowIndex':0 if length else -1})
        assert run('row_color',strategy,{5:0},globals_)==0xdddddd
        assert run('row_background',strategy,{5:0},globals_) is UNDEFINED
        assert strategy['_IsRowSelected'](0) is False
        assert run('hints',strategy,globals_=globals_)==[]
        if length:run('color',strategy,{5:0,6:4},globals_)
    def grid_input(event):
        code=event['KeyCode'];assert code in NAVIGATION_CODES
        calls.append(('grid_input',code));strategy['_RowChanged']({'NewRowIndex':min(1,len(provider['mDEDraftRows'])-1)})
        return True
    strategy['mcSpreadsheet']={'ResetData':reset_data,'HandleInput':grid_input}
    def drain():
        assert not filters['open'],'Native toggle is still unwinding'
        count=0
        while timers:
            _,callback=timers.popitem();callback();count+=1;assert count<4
    def choose_scope(scope):
        before=len(reset_observations);filters['open']=True;filters['value']=scope
        strategy['_OnFilterItemChanged']({'ToggleIndex':0})
        assert len(reset_observations)==before,'Rebuilt inside native toggle ItemChanged'
        filters['open']=False;drain();assert len(reset_observations)==before+1
        assert strategy['mDEDraftPendingScope'] is UNDEFINED and strategy['mDEDraftApplying'] is False
    return dict(strategy=strategy,provider=provider,calls=calls,resets=reset_observations,filters=filters,
                globals_=globals_,timers=timers,forbidden=forbidden,choose=choose_scope,drain=drain)

wire,rows,scopes=fixture();screen=connected_screen(wire)
provider=screen['provider'];calls=screen['calls'];reset_observations=screen['resets'];filters=screen['filters'];globals_=screen['globals_'];strategy=screen['strategy']
assert run('team',strategy,globals_=globals_) is UNDEFINED
assert strategy['mDEDraftActive'] is True and strategy['mSortDisabled'] is True
assert len(provider['mDEDraftAllRows'])==224 and len(provider['mDEDraftRows'])==112
assert [r[1] for r in provider['mDEDraftRows']]==[r[1] for r in rows if r[6]=='1']
scope_call=next(c for c in calls if c[0]=='scopes');assert [s['display'] for s in scope_call[2]]==[s[2] for s in scopes]
assert [s['key'] for s in scope_call[2] if s['isDefault']]==['team:1']
assert [s['display'] for s in provider['mDEDraftColumns']]==[c[0] for c in COLUMNS]
assert strategy['mcSpreadsheetTeamModuleHorizontal']['_visible'] is False
assert strategy['mcSpreadsheetPlayerModule']['_visible'] is False
assert len(reset_observations)==1 and not screen['timers'],'Synchronous initial dropdown event caused a reentrant rebuild'
assert run('count',provider)==112
assert run('key',provider,{3:0})=='8:0'
assert run('key_index',provider,{2:'8:2'})==1
assert run('key_index',provider,{2:'8:1'})==-1
assert run('key',provider,{3:999}) is UNDEFINED

no_user_screen=connected_screen(wire.replace('\t2028\t1\n','\t2028\t-1\n',1));no_user=no_user_screen['strategy']
run('team',no_user,globals_=no_user_screen['globals_']);assert no_user['mDEDraftScope']=='national' and len(no_user['mSpreadsheetDataProvider']['mDEDraftRows'])==224

# No second parse or spreadsheet reset on unchanged native header callbacks.
calls.clear();assert run('team',strategy,globals_=globals_) is UNDEFINED;assert calls==[],calls
screen['choose']('national');assert len(provider['mDEDraftRows'])==224
screen['choose']('conference:2:1');assert len(provider['mDEDraftRows'])==112 and all(r[8]=='2:1' for r in provider['mDEDraftRows'])
screen['choose']('team:2');assert all(r[6]=='2' for r in provider['mDEDraftRows'])
screen['choose']('team:3');assert provider['mDEDraftRows']==[] and strategy['mIsSpreadsheetEmpty'] is True
screen['choose']('team:2');assert strategy['mIsSpreadsheetEmpty'] is False
assert all(empty is (length==0) for empty,length in reset_observations),'ResetData observed stale emptiness before its synchronous row callback'

# Live regression shape: ULM has no picks. SetByItemArray and ResetData fire
# synchronous native events before the table switches safely to National.
empty_screen=connected_screen(wire.replace('\t2028\t1\n','\t2028\t3\n',1))
es=empty_screen['strategy'];eg=empty_screen['globals_'];ep=empty_screen['provider']
run('team',es,globals_=eg);assert ep['mDEDraftRows']==[] and es['mIsSpreadsheetEmpty'] is True
empty_screen['choose']('national');assert len(ep['mDEDraftRows'])==224 and es['mIsSpreadsheetEmpty'] is False
empty_screen['choose']('conference:2:1');assert len(ep['mDEDraftRows'])==112
assert run('input',es,{7:{'KeyCode':NAVIGATION_CODES[2]}},eg) is True and es['mCurrentRowIndex']==1
for code in ['PRIMARY','VIEW_PLAYER_CARD','SECONDARY_ACTION','MOUSE_CLICK']:
    before=len(empty_screen['calls']);assert run('input',es,{7:{'KeyCode':code}},eg) is True
    assert not any(c[0] in ['grid_input','back'] for c in empty_screen['calls'][before:])
run('input',es,{7:{'KeyCode':'LT'}},eg);assert empty_screen['filters']['open']
run('input',es,{7:{'KeyCode':'BACK'}},eg);assert not empty_screen['filters']['open']
assert not any(c[0]=='back' for c in empty_screen['calls'])
run('input',es,{7:{'KeyCode':'BACK'}},eg);assert len([c for c in empty_screen['calls'] if c[0]=='back'])==1
assert empty_screen['forbidden']==[] and screen['forbidden']==[]

# Actual-only format accepts empty/small/large draft classes without imposing
# a modeled NFL32-club or224-player requirement. Assignment columns are absent.
assert [label for label,_ in COLUMNS]==['Name','POS','Year','School','OVR','Result']
for row_count in [0,1,1024]:
    actual_rows=[]
    for i in range(row_count):
        row=list(rows[i%len(rows)]);row[1]='8:'+str(i);row[9]=str(i%7+1);actual_rows.append(row)
    actual_wire='DE_DRAFT_2\t4294954951\t2028\t1\n'+'\n'.join('\t'.join(row) for row in scopes+actual_rows)+'\n'
    bounded=connected_screen(actual_wire);run('team',bounded['strategy'],globals_=bounded['globals_'])
    bounded['choose']('national');assert run('count',bounded['provider'])==row_count
    assert not bounded['forbidden']

# Pending, ready and already-partially-torn-down draft strategies must cancel
# retry callbacks. Ordinary Players Leaving has no owned draft timer.
for state in [
    {'mIsDraftClass':True,'mDEDraftRetries':3,'mSpreadsheetDataProvider':{'mDEDraftNative':True}},
    {'mIsDraftClass':True,'mDEDraftActive':True,'mDEDraftRetries':0,'mDEDraftWire':wire,'mSpreadsheetDataProvider':{'mDEDraftRows':rows,'mDEDraftNative':True}},
    {'mIsDraftClass':True,'mDEDraftRetries':1},
]:
    calls.clear();assert run('shutdown',state,globals_=globals_)=='native'
    assert len([c for c in calls if c[0]=='clear'])==1
    assert all(state[field] is UNDEFINED for field in ['mDEDraftActive','mDEDraftRetries','mDEDraftWire','mDEDraftPendingScope','mDEDraftBuilding','mDEDraftApplying'])
    if 'mSpreadsheetDataProvider' in state:assert state['mSpreadsheetDataProvider']['mDEDraftRows'] is UNDEFINED and state['mSpreadsheetDataProvider']['mDEDraftNative'] is UNDEFINED
calls.clear();assert run('shutdown',{'mIsDraftClass':False},globals_=globals_)=='native' and calls==[]

# Column requests can be reordered and subsetted; result/pick/NFL fields are
# independent of the native OVR value and use the same shared grade policy.
shown=run('rows',provider,{5:0,4:[5,4,3,2,1,0]})
assert [c['display'] for c in shown]==['Round 1','D','State','SR (RS)','HB','Player 1']
assert provider['mDEDraftRows'][0][5]=='61','Underlying overall was changed'
assert run('rows',provider,{5:999,4:[4]})==[]

for scale,bands in enumerate(BANDS):
    for fog in [0,1]:
        for colors in [0,1]:
            p=program('rows');code=bytearray(p.code)
            for at in p.scale_offsets:code[at]=scale
            for at in p.fog_offsets:code[at]=fog
            for at in p.color_offsets:code[at]=colors
            p=replace(p,code=bytes(code))
            for value in [0,59,60,69,70,79,80,89,90,94,95,97,100]:
                row=list(rows[0]);row[5]=str(value);local={'mDEDraftRows':[row]}
                shown=DraftMachine({},[]).run(p,{1:local,5:0,4:[4,5]})
                expected=next(label for upper,label in bands if value<upper) if fog else str(value)
                assert shown[0]['display']==expected,(scale,fog,colors,value,shown)
                assert shown[1]['display']=='Round 1' and row[5]==str(value)

# Pending data never captures an unrelated screen or disables its stock table.
for value in [None,'not a board','DE_DRAFT_2\t1\t2028\t1\n',wire.replace('DE_DRAFT_2','DE_DRAFT_1',1)]:
    s=copy.copy(strategy);s.pop('mDEDraftWire',None);s.pop('mDEDraftActive',None);s['mPlayersLeavingAdapter']={'GetTeamInfo':lambda value=value:{'DEDraftBoard':value}}
    assert run('team',s,globals_=globals_)=='native' and 'mDEDraftActive' not in s
for mode in ['rows','count','columns','key','key_index','refresh','sort','filter_data','sort_info','row_changed','row_color','row_background','row_selected','input','hints','backup']:
    assert run(mode,{},args={2:0,3:0,4:[],5:0})=='native',mode
assert run('team',{'mIsDraftClass':False})=='native'

# Provider callbacks can arrive with their native frame already allocated.
# Every custom method must execute using exactly that register count. Any
# scratch beyond it is a function-local variable, not an extra frame slot.
for _,_,_,_,registers,_,_,mode in SPECS:
    a=emit(mode);assert isinstance(a,FixedFrameAssembler) and a.native_registers==registers
    p=a.finish();pc=0;used=[]
    while pc<len(p.code):
        op=p.code[pc];pc+=1
        if op==0xB9:used.append(p.code[pc]);pc+=1
        elif op==0xB5:pc+=1
        elif op==0xB6:pc+=2
        elif op==0xA1:pc=((pc+7)&~7)+8
        elif op in (0x87,0x9D,0xB8,0x99):pc=((pc+7)&~7)+4
    assert all(n<registers for n in used),(mode,registers,used)

# A hub method attaching before either provider bank must leave stock filter
# and Back handling intact, rather than committing a partially custom screen.
for missing in ['both','cfm','com']:
    callbacks=provider_callbacks({})
    if missing in ['both','com']:callbacks['GetNumMaxRows']=lambda:0
    if missing in ['both','cfm']:callbacks['_GetColumnData']=lambda:[]
    s=copy.copy(strategy);s.pop('mDEDraftActive',None);s.pop('mDEDraftWire',None);s['mSpreadsheetDataProvider']=callbacks
    calls.clear();assert run('team',s,globals_=globals_)=='native'
    assert 'mDEDraftActive' not in s and 'mDEDraftRows' not in callbacks
    assert run('filter',s)=='native' and len([c for c in calls if c[0]=='delay'])==1

# Stock data remains fogged while the independent worker is preparing. The
# copied native body supplies its original array in r2; this test starts at the
# custom suffix, preserving native scalar/model values and arbitrary requests.
a=Assembler();native_rows_suffix(a);native=a.finish()
for value in [0,59,60,79,90,100,'85','?','--','',None,'85,TrendUp',' 85','085']:
    for scoped in [False,True]:
        cells=[{'display':value,'value':1234,'ExtraInfo':{'keep':'native'}},{'display':'Round 1','value':1}]
        before=copy.deepcopy(cells);receiver={'mDEDraftNative':scoped}
        result=DraftMachine({},[]).run(native,{1:receiver,2:cells,4:[4,5]})
        assert result is cells and cells[0]['value']==1234 and cells[0]['ExtraInfo']==before[0]['ExtraInfo']
        assert cells[1]==before[1]
        if scoped and (isinstance(value,int) or value=='85'):
            n=int(value);expected='A' if n>=90 else 'B' if n>=80 else 'C' if n>=70 else 'D' if n>=60 else 'F'
            assert cells[0]['display']==expected
        else:assert cells==before,(value,scoped,cells)
cells=[{'display':'88','value':88}];DraftMachine({},[]).run(native,{1:{'mDEDraftNative':True},2:cells,4:[6]});assert cells[0]['display']=='88','Non-OVR numeric column was converted'
print('Draft UI wire parse, actual scopes, key/column data, fog and fallback checks pass')
