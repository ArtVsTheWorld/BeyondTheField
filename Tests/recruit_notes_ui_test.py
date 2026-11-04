"""Execute custom Notes bytecode offline against native-view stand-ins."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Assembler,append_tab,category_changed,draw_notes,restore_layout,ALL
from recruit_notes_vm import Machine,UNDEFINED


def globals_for_test():
    search=lambda rows,value,key:next((i for i,row in enumerate(rows) if row.get(key)==value),-1)
    return {'cafe':{'utility':{'ArrayUtil':{'Search':search,'SEARCH_FAIL':-1}}},'shared_enum_career':{'recruitinghub':{'StateMachine':{'STATE_SCOUTING_TAB':'scout'},'ScreenKey':{'SUBSCREEN_RECRUITINGHUB_BOARD_SCOUTING':'scoutScreen'}}},'art_styleguide':{'Color':{'PRIMARY_LIGHT_COLOR':123,'UNFOCUS_FONT_COLOR':456}},'loc':{'career':{'Recruiting':{'SCOUT':'Scout','SCOUT_DESCRIPTION':'Original scout description'}}}}


def program(builder):
    a=Assembler();builder(a);return a.finish()


def main():
    g=globals_for_test();machine=Machine(g,[])
    original=[{'display':'Overview'},{'display':'Recruiting'},{'display':'Scouting'}];rows=original.copy()
    result=machine.run(program(append_tab),{1:rows})
    assert result is rows and len(rows)==4 and all(rows[i] is original[i] for i in range(3))
    assert rows[2]['display']=='Scouting (100%)', 'Reserve the longest percentage label before native tab layout'
    assert rows[3]=={'display':'Notes','DENotes':True,'isDefault':False,'StateMachineKey':'scout','ScreenKey':'scoutScreen'}
    locks=[];transitions=[];state={'current':'scout'}
    g['logic_cfm']={'service':{'RecruitingBoardServiceImpl':{'INPUT_LOCK_TAB':'TAB'}}}
    g['cafe']['manager']={'InputLockManagerService':{'Get':lambda parent:{'LockInput':lambda token:locks.append(token)}}}
    service={'mStateMachine':{'GetCurrentStateKey':lambda:state['current']},'TransitionToState':lambda target:transitions.append(target)}
    model={'mParentNode':{},'mRecruitingBoardService':service}
    event={'Data':{'Index':3,'WidgetData':{'ExtraInfo':rows[3]}}}
    machine.run(program(category_changed),{1:model,2:event})
    assert g['cafe']['DynastyEnhancerRecruitNotesSelected'] is True and model['mCurrentTabIndex']==3
    assert not locks and not transitions, 'Same-state page changes must not leave an input lock waiting for an event'
    state['current']='overview';machine.run(program(category_changed),{1:model,2:event})
    assert locks==['TAB'] and transitions==['scout']
    event['Data']['Index']=2;event['Data']['WidgetData']['ExtraInfo']={'StateMachineKey':'scout'}
    machine.run(program(category_changed),{1:model,2:event});assert g['cafe']['DynastyEnhancerRecruitNotesSelected'] is False
    view={};saved={}
    for i,name in enumerate(ALL):
        widget={'_visible':i%2==0,'_x':i*7,'_y':i*9}
        widget['SetLabel']=lambda label,w=widget:w.update(label=label)
        widget['SetExtraInfo']=lambda style,w=widget:w.update(style=style)
        widget['Unfocus']=lambda w=widget:w.update(focused=False)
        view[name]=widget;saved[name]=dict(widget)
    recruit={'RecordId':561120980,'DENotesBody':'Early profile\nA stable, qualitative observation.'}
    recruits=[{'RecordId':777,'DENotesBody':'Different recruit'},recruit];active={'id':recruit['RecordId']}
    model={'mView':view,'mRecruitingBoardService':{'GetActiveRecruit':lambda:active['id']},'mRecruitingBoardAdapter':{'GetTeamRecruitList':lambda:recruits}}
    machine.run(program(draw_notes),{1:model})
    assert view['mcDescription']['label']==recruit['DENotesBody'] and view['mcTitle']['label']=='Recruit Notes'
    assert view['mcDescription']['style']['resizeWidth']==1180
    for name,lift in [('mcTitle',140),('mcDescription',154)]:
        assert view[name]['_x']==saved[name]['_x'] and view[name]['_y']==saved[name]['_y']-lift, 'Notes escaped the native panel anchors'
    assert all(not view[name]['_visible'] for name in ALL if name not in ('mcTitle','mcDescription'))
    saved_snapshot=dict(view['mDENotesSaved'])
    recruit['DENotesBody']='A different prospect';machine.run(program(draw_notes),{1:model})
    assert view['mcDescription']['label']=='A different prospect' and view['mDENotesSaved']==saved_snapshot
    active['id']=777;machine.run(program(draw_notes),{1:model});assert view['mcDescription']['label']=='Different recruit'
    active['id']=999;machine.run(program(draw_notes),{1:model});assert view['mcDescription']['label'].startswith('The staff is gathering'), 'Missing selection retained another recruit’s notes'
    a=Assembler();restore_layout(a);a.label('native');a.ret();machine.run(a.finish(),{1:model})
    for name in ALL:
        assert view[name]['_visible']==saved[name]['_visible']
        if name in ('mcTitle','mcDescription'):assert view[name]['_x']==saved[name]['_x'] and view[name]['_y']==saved[name]['_y']
    assert view['mcDescription']['style']['resizeWidth']==256 and view['mcDescription']['label']=='Original scout description'
    assert view['mDENotesSaved'] is UNDEFINED
    machine.run(program(draw_notes),{1:{'mView':{}}})
    for count in range(8):
        a=Assembler()
        if count%2:a.raw(0x59,0x50,0x17)
        for _ in range(count//2):a.raw(0x76,0x17)
        a.pad_code();assert len(a.code)%8==0
        a.ret();machine.run(a.finish(),{})
    print('Passed: fourth-tab metadata, same-state input-lock handling, Notes rendering, recruit changes, absent widgets, and native Scouting layout restoration.')


if __name__=='__main__':main()
