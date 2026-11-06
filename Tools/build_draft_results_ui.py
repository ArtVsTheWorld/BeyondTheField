"""Build scoped Draft Results browsing from a worker-published native capture.

Only custom APT instructions and original-method fingerprints are distributed.
The native provider remains unchanged unless its own Draft Results strategy has
received a complete DEDraftBoard string from the synchronous native response.
"""
from pathlib import Path
import argparse
import json
import struct
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade,palette

ASSETS={'hub':'common/ui/node_cfm/hub/corenode.ast','cfm':'common/ui/node_cfm/corenode.ast','com':'common/ui/node_com/scriptpod.ast'}
COLUMNS=[('Name',260),('POS',80),('Year',110),('School',240),('OVR',110),('Result',160)]
# Loader relocation of this exact zero-body cancellation callback changes the
# enclosing HandleInput bytes. Normalize only its verified metadata, retaining
# the full source-body hash and all callback semantics/instructions.
NESTED_DEFINITIONS={'input':((0x240,0x7eb20,0x7eb28),)}
NAVIGATION_CODES=tuple('CODE_SPREADSHEET_'+name for name in (
    'PREVIOUS_ROW','PREVIOUS_ROW_ALT','NEXT_ROW','NEXT_ROW_ALT',
    'PREVIOUS_COL','PREVIOUS_COL_ALT','NEXT_COL','NEXT_COL_ALT',
    'PREVIOUS_ROW_U','NEXT_ROW_ALT_U','PREVIOUS_ROW_ALT_U','NEXT_ROW_U',
    'PREVIOUS_COL_ALT_U','NEXT_COL_ALT_U','PREVIOUS_COL_U','NEXT_COL_U'))

class FixedFrameAssembler(Assembler):
    """Keep preallocated native callback frames unchanged.

    Some spreadsheet provider methods bypass invocation setup. Their body
    accessor runs after register allocation, so extra scratch registers cannot
    be added safely. Ordinary AS2 function-local variables hold those temporary
    values instead. DefineLocal is present in the verified native scriptpod.
    """
    def __init__(self,registers):super().__init__();self.native_registers=registers
    def reg(self,n):
        if n<self.native_registers:super().reg(n)
        else:self.string('_DEDraftLocal'+str(n));self.raw(0x1C)
    def store(self,n):
        if n<self.native_registers:super().store(n)
        else:
            self.string('_DEDraftLocal'+str(n));self.raw(0x4D,0x3C)

def field(a,reg,name,value_reg):
    a.reg(reg);a.string(name);a.reg(value_reg);a.raw(0x4F)

def index(a,reg,n):a.reg(reg);a.number(n);a.raw(0x4E)

def push(a,array,item):a.reg(item);a.number(1);a.reg(array);a.call('push')

def array(a,reg):a.number(0);a.raw(0x42);a.store(reg)

def call(a,reg,name,args=()):
    for arg in reversed(args):a.reg(arg)
    a.number(len(args));a.reg(reg);a.string(name);a.raw(0x52)

def active(a,normal,provider=False):
    path(a,1,'mDEDraftRows' if provider else 'mDEDraftActive')
    if provider:a.raw(0x76,0x49);a.branch(normal)
    else:a.raw(0x73,0x66);a.branch(normal,0xB8)

def clear_retry(a):
    a.string('DynastyEnhancerDraftRefresh');a.number(1);a.reg(1);a.number(1)
    a.global_object('cafe','manager','IntervalManagerService');a.string('Get');a.raw(0x52);a.call('ClearDelay')

def schedule_retry(a):
    path(a,1,'mDEDraftRetries');a.store(6);a.reg(6);a.raw(0x76,0x49);a.branch('retry_count',0xB8);a.number(0);a.store(6)
    a.label('retry_count');a.reg(6);a.number(40);a.raw(0x48);a.branch('normal',0xB8)
    a.reg(1);a.string('mDEDraftRetries');a.reg(6);a.raw(0x50,0x4F)
    clear_retry(a)
    a.raw(0x76);a.number(500)
    path(a,1,'_GetTeamModule');a.reg(1);a.number(2);a.global_object('cafe','utility','Delegate');a.string('Create');a.raw(0x52)
    a.string('DynastyEnhancerDraftRefresh');a.number(4);a.reg(1);a.number(1)
    a.global_object('cafe','manager','IntervalManagerService');a.string('Get');a.raw(0x52);a.call('SetDelay')

def build_columns(a,provider=4):
    array(a,10)
    for i,(label,width) in enumerate(COLUMNS):
        a.empty_object(11)
        for name,value in [('key',i),('display',label),('hintText',label),('pixelWidth',width),('isStatic',i==0),('isHidden',False),('formatType',0)]:a.set_field(11,name,value)
        push(a,10,11)
    field(a,provider,'mDEDraftColumns',10);field(a,provider,'mColumnDefinitions',10);field(a,provider,'mColumnData',10)

def hide_sidebar(a,label):
    path(a,1,'mcSpreadsheetPlayerModule');a.store(11);a.missing(11,label);a.set_field(11,'_visible',False);a.label(label)

def defer_scope(a):
    # ItemChanged fires before the native toggle finishes closing. A nonlocked
    # next-tick callback rebuilds only after that native selection unwinds.
    clear_retry(a)
    a.raw(0x76);a.number(0)
    path(a,1,'_GetTeamModule');a.reg(1);a.number(2);a.global_object('cafe','utility','Delegate');a.string('Create');a.raw(0x52)
    a.string('DynastyEnhancerDraftRefresh');a.number(4);a.reg(1);a.number(1)
    a.global_object('cafe','manager','IntervalManagerService');a.string('Get');a.raw(0x52);a.call('SetDelay')

def rebuild(a,scope=5,provider=4):
    # Wire rows use actual round/school/name/key order; filtering preserves it.
    array(a,10);path(a,provider,'mDEDraftAllRows');a.store(7);a.number(0);a.store(8)
    a.label('filter_loop');a.reg(8);path(a,7,'length');a.raw(0x48);a.branch('filter_done',0xB8)
    a.reg(7);a.reg(8);a.raw(0x4E);a.store(9)
    a.reg(scope);a.string('national');a.raw(0x66);a.branch('filter_keep')
    a.string('team:');index(a,9,6);a.raw(0x47);a.reg(scope);a.raw(0x66);a.branch('filter_keep')
    a.string('conference:');index(a,9,8);a.raw(0x47);a.reg(scope);a.raw(0x66);a.branch('filter_next',0xB8)
    a.label('filter_keep');push(a,10,9)
    a.label('filter_next');a.reg(8);a.raw(0x50);a.store(8);a.branch('filter_loop',0x99)
    a.label('filter_done');field(a,provider,'mDEDraftRows',10)
    field(a,1,'mDEDraftScope',scope);a.set_field(1,'mCurrentRowIndex',0);a.set_field(1,'mRestartIndex',False);a.set_field(1,'mFilterItemChanged',False);a.set_field(1,'mChangedTeamFilter',False)
    # ResetData selects a row and dispatches its event synchronously. Publish
    # the new empty state first, especially empty user team -> National.
    a.reg(1);a.string('mIsSpreadsheetEmpty');path(a,10,'length');a.number(0);a.raw(0x66,0x4F)
    path(a,1,'mcSpreadsheet');a.store(11)
    a.number(0);a.number(0);a.number(2);a.reg(11);a.call('ResetData')
    # A native team header describes its engine's current team, which is not
    # necessarily our aggregate scope. Hide it rather than display wrong data.
    path(a,1,'mcSpreadsheetTeamModuleHorizontal');a.store(11);a.missing(11,'no_header');a.set_field(11,'_visible',False);a.label('no_header')
    hide_sidebar(a,'no_sidebar')

def team_module(a):
    path(a,1,'mIsDraftClass');a.raw(0x73,0x66);a.branch('normal',0xB8)
    path(a,1,'mSpreadsheetDataProvider');a.store(4);a.missing(4,'normal')
    # Mark only this native Draft Results provider even before a full board is
    # ready. Its stock row callback must never briefly expose numerical OVR.
    a.set_field(4,'mDEDraftNative',True)
    # Do not intercept native filters until both actual provider classes have
    # executed their frame-safe adapters. A hub-only attachment must leave the
    # stock screen and Back lifecycle intact.
    a.number(0);a.reg(4);a.string('GetNumMaxRows');a.raw(0x52,0x17)
    a.number(0);a.reg(4);a.string('_GetColumnData');a.raw(0x52,0x17)
    path(a,4,'mDEDraftComReady');a.raw(0x73,0x66);a.branch('pending',0xB8)
    path(a,4,'mDEDraftCfmReady');a.raw(0x73,0x66);a.branch('pending',0xB8)
    a.number(0);path(a,1,'mPlayersLeavingAdapter');a.string('GetTeamInfo');a.raw(0x52);a.store(2)
    a.missing(2,'normal');path(a,2,'DEDraftBoard');a.store(3)
    a.reg(3);a.raw(0x44);a.string('string');a.raw(0x66);a.branch('pending',0xB8)
    path(a,1,'mDEDraftWire');a.reg(3);a.raw(0x66);a.branch('ready_existing')
    a.string('\n');a.number(1);a.reg(3);a.string('split');a.raw(0x52);a.store(7)
    index(a,7,0);a.store(8);a.string('\t');a.number(1);a.reg(8);a.string('split');a.raw(0x52);a.store(8)
    index(a,8,0);a.string('DE_DRAFT_2');a.raw(0x66);a.branch('normal',0xB8)
    path(a,7,'length');a.number(3);a.raw(0x48);a.branch('normal')
    path(a,7,'length');a.number(1326);a.raw(0x67);a.branch('normal')
    a.string('team:');index(a,8,3);a.raw(0x47);a.store(5)
    index(a,8,3);a.string('-1');a.raw(0x66);a.branch('default_scope',0xB8);a.string('national');a.store(5);a.label('default_scope')
    array(a,12);array(a,13);a.number(1);a.store(9)
    a.label('parse_loop');a.reg(9);path(a,7,'length');a.raw(0x48);a.branch('parsed',0xB8)
    a.reg(7);a.reg(9);a.raw(0x4E);a.store(10);a.string('\t');a.number(1);a.reg(10);a.string('split');a.raw(0x52);a.store(10)
    index(a,10,0);a.string('S');a.raw(0x66);a.branch('parse_scope')
    index(a,10,0);a.string('P');a.raw(0x66);a.branch('parse_next',0xB8)
    path(a,10,'length');a.number(10);a.raw(0x66);a.branch('normal',0xB8)
    push(a,12,10);a.branch('parse_next',0x99)
    a.label('parse_scope');path(a,10,'length');a.number(4);a.raw(0x66);a.branch('normal',0xB8)
    a.empty_object(11);a.reg(11);a.string('key');index(a,10,1);a.raw(0x4F)
    a.reg(11);a.string('display');index(a,10,2);a.raw(0x4F)
    a.reg(11);a.string('isDefault');index(a,10,1);a.reg(5);a.raw(0x66,0x4F);push(a,13,11)
    a.label('parse_next');a.reg(9);a.raw(0x50);a.store(9);a.branch('parse_loop',0x99)
    a.label('parsed');path(a,12,'length');a.number(1024);a.raw(0x67);a.branch('normal')
    path(a,13,'length');a.number(1);a.raw(0x48);a.branch('normal')
    path(a,13,'length');a.number(300);a.raw(0x67);a.branch('normal')
    field(a,4,'mDEDraftAllRows',12);field(a,1,'mDEDraftWire',3);a.set_field(1,'mDEDraftActive',True);a.set_field(1,'mSortDisabled',True)
    build_columns(a)
    a.set_field(1,'mDEDraftBuilding',True)
    path(a,1,'mcFilter');a.store(6);a.number(1);a.number(1);a.reg(6);a.call('ChangeNumToggles')
    a.reg(13);a.number(0);a.number(2);a.reg(6);a.call('SetByItemArray')
    a.set_field(1,'mDEDraftBuilding',False)
    rebuild(a)
    clear_retry(a);a.set_field(1,'mDEDraftRetries',0);a.ret()
    a.label('ready_existing');path(a,1,'mDEDraftPendingScope');a.store(5)
    a.reg(5);a.raw(0x44);a.string('string');a.raw(0x66);a.branch('existing_done',0xB8)
    a.reg(1);a.string('mDEDraftPendingScope');a.raw(0x76,0x4F)
    # Shared loop labels cannot be reused in one function. Reenter the public
    # filter callback in its applying mode rather than duplicate its builder.
    a.set_field(1,'mDEDraftApplying',True)
    a.raw(0x76);a.number(1);a.reg(1);a.call('_OnFilterItemChanged')
    a.set_field(1,'mDEDraftApplying',False)
    a.label('existing_done');a.ret()
    a.label('pending');schedule_retry(a)

def filter_changed(a):
    active(a,'normal');path(a,1,'mSpreadsheetDataProvider');a.store(4);path(a,1,'mcFilter');a.store(6)
    path(a,1,'mDEDraftBuilding');a.raw(0x73,0x66);a.branch('handled')
    a.number(0);a.number(1);a.reg(6);a.string('GetToggleValue');a.raw(0x52);a.store(5)
    a.reg(5);a.raw(0x44);a.string('string');a.raw(0x66);a.branch('handled',0xB8)
    path(a,1,'mDEDraftApplying');a.raw(0x73,0x66);a.branch('apply_scope')
    field(a,1,'mDEDraftPendingScope',5);a.set_field(1,'mFilterItemChanged',False);a.set_field(1,'mRestartIndex',False);a.set_field(1,'mChangedTeamFilter',False)
    defer_scope(a);a.ret()
    a.label('apply_scope')
    rebuild(a)
    a.label('handled');a.ret()

def row_changed(a):
    active(a,'normal');a.missing(25,'row_no_index');path(a,25,'NewRowIndex');a.store(3)
    a.reg(3);a.raw(0x44);a.string('number');a.raw(0x66);a.branch('row_no_index',0xB8)
    field(a,1,'mCurrentRowIndex',3)
    a.label('row_no_index');a.set_field(1,'mChangedTeamFilter',False)
    hide_sidebar(a,'row_no_sidebar');a.ret()

def handle_input(a):
    active(a,'normal')
    # Forward native component navigation, never the Players Leaving command
    # helper/persuasion path. The custom rows are persistent Player IDs, while
    # that path requires transient Blaze PlayerLeaving DTO IDs.
    path(a,1,'mcFilter');a.store(3);a.missing(3,'input_back')
    a.reg(7);a.number(1);a.reg(3);a.string('HandleInput');a.raw(0x52);a.raw(0x73,0x66);a.branch('input_handled')
    a.label('input_back');path(a,7,'KeyCode');a.global_object('ion','enum','Input','CODE_BACK');a.raw(0x66);a.branch('input_leave')
    # Only the verified spreadsheet movement press/release codes may reach the
    # grid. Y/card, primary action, sort and other commands are consumed here.
    for code in NAVIGATION_CODES:
        path(a,7,'KeyCode');a.global_object('ion','enum','Input',code);a.raw(0x66);a.branch('input_grid')
    a.branch('input_handled',0x99)
    a.label('input_grid')
    path(a,1,'mcSpreadsheet');a.store(3);a.missing(3,'input_unhandled')
    a.reg(7);a.number(1);a.reg(3);a.string('HandleInput');a.raw(0x52,0x3E)
    a.label('input_leave');path(a,1,'mContext');a.store(3)
    a.reg(3);a.number(1);a.global_object('cafe','node','NavigatorService');a.string('Get');a.raw(0x52);a.store(4)
    a.reg(3);a.number(1);a.reg(4);a.call('NavigateBackward')
    a.label('input_handled');a.raw(0x73,0x3E)
    a.label('input_unhandled');a.raw(0x74,0x3E)

def provider_rows(a):
    active(a,'normal',True)
    # Verified native argument registers: row index5, requested columns4.
    path(a,1,'mDEDraftRows');a.reg(5);a.raw(0x4E);a.store(6)
    array(a,7);a.missing(6,'return');a.number(0);a.store(8)
    a.label('row_loop');a.reg(8);path(a,4,'length');a.raw(0x48);a.branch('return',0xB8)
    a.reg(4);a.reg(8);a.raw(0x4E);a.store(9);a.empty_object(10)
    for col,field_index in [(0,2),(1,3),(2,4),(3,7),(4,5),(5,9)]:
        a.reg(9);a.number(col);a.raw(0x66);a.branch('column'+str(col))
    a.string('');a.store(11);a.branch('cell',0x99)
    for col,field_index in [(0,2),(1,3),(2,4),(3,7),(4,5),(5,9)]:
        a.label('column'+str(col));index(a,6,field_index)
        if col==5:a.store(11);a.string('Round ');a.reg(11);a.raw(0x47)
        a.store(11)
        if col==4:
            a.reg(11);a.raw(0x4A);a.store(12);numeric_grade(a,12,11,'cell','draft_row_grade')
        a.branch('cell',0x99)
    a.label('cell');field(a,10,'display',11);field(a,10,'value',11);push(a,7,10)
    a.reg(8);a.raw(0x50);a.store(8);a.branch('row_loop',0x99)
    a.label('return');a.reg(7);a.raw(0x3E)

def native_rows_suffix(a):
    # The verified native GetRowData ends with `r2; return`; we copy everything
    # before that return, then convert only its explicitly requested OVR cells.
    # Original WidgetData.value, keys and every other column remain untouched.
    path(a,1,'mDEDraftNative');a.raw(0x73,0x66);a.branch('native_return',0xB8)
    a.missing(2,'native_return');a.missing(4,'native_return');a.number(0);a.store(8)
    a.label('native_row_loop');a.reg(8);path(a,4,'length');a.raw(0x48);a.branch('native_return',0xB8)
    a.reg(4);a.reg(8);a.raw(0x4E);a.number(4);a.raw(0x66);a.branch('native_row_next',0xB8)
    a.reg(2);a.reg(8);a.raw(0x4E);a.store(10);a.missing(10,'native_row_next')
    path(a,10,'display');a.store(11)
    a.reg(11);a.raw(0x44);a.string('number');a.raw(0x66);a.branch('native_number')
    a.reg(11);a.raw(0x44);a.string('string');a.raw(0x66);a.branch('native_row_next',0xB8)
    a.reg(11);a.raw(0x4A);a.store(12);a.reg(12);a.raw(0x4B);a.reg(11);a.raw(0x66);a.branch('native_row_next',0xB8);a.branch('native_grade',0x99)
    a.label('native_number');a.reg(11);a.store(12)
    a.label('native_grade');numeric_grade(a,12,11,'native_row_next','draft_native_grade')
    field(a,10,'display',11)
    a.label('native_row_next');a.reg(8);a.raw(0x50);a.store(8);a.branch('native_row_loop',0x99)
    a.label('native_return');a.reg(2);a.raw(0x3E)

def row_key(a):
    active(a,'normal',True);path(a,1,'mDEDraftRows');a.reg(3);a.raw(0x4E);a.store(4);a.missing(4,'empty');index(a,4,1);a.raw(0x3E);a.label('empty');a.ret()

def key_index(a,arg=2):
    active(a,'normal',True);path(a,1,'mDEDraftRows');a.store(4);a.number(0);a.store(5)
    a.label('key_loop');a.reg(5);path(a,4,'length');a.raw(0x48);a.branch('not_found',0xB8)
    a.reg(4);a.reg(5);a.raw(0x4E);a.store(6);index(a,6,1);a.reg(arg);a.raw(0x66);a.branch('key_found')
    a.reg(5);a.raw(0x50);a.store(5);a.branch('key_loop',0x99)
    a.label('key_found');a.reg(5);a.raw(0x3E);a.label('not_found');a.number(-1);a.raw(0x3E)

def cell_color(a):
    active(a,'normal');a.reg(6);a.number(4);a.raw(0x66);a.branch('color_undefined',0xB8)
    a.reg(5);a.number(1);a.reg(1);a.string('_IsRowSelected');a.raw(0x52);a.raw(0x73,0x66);a.branch('color_selected')
    path(a,1,'mSpreadsheetDataProvider','mDEDraftRows');a.reg(5);a.raw(0x4E);a.store(7);a.missing(7,'color_undefined')
    index(a,7,5);a.raw(0x4A);a.store(8);a.reg(8);a.store(9)
    palette(a,8,9,'color_undefined','draft_cell_color')
    a.reg(9);a.raw(0x3E)
    a.label('color_selected');a.number(0x252525);a.raw(0x3E)
    a.label('color_undefined');a.ret()

# Method descriptors are independently fingerprinted in each private asset.
# Native bodies are copied at invocation setup only, after every hash matches.
SPECS=[
 ('hub','_GetTeamModule',0x49ac8,0,3,41,207,'team'),
 ('hub','_OnFilterItemChanged',0x4a520,1,4,25,16,'filter'),
 ('hub','_OnFilterChanged',0x49a70,1,3,41,34,'filter_guard'),
 ('hub','_GetCellColor',0x49dc8,2,7,41,237,'color'),
 ('hub','Shutdown',0x49080,0,4,25,107,'shutdown'),
 ('hub','_RowChanged',0x494d0,1,26,25,833,'row_changed'),
 ('hub','_GetRowColor',0x49848,1,6,41,200,'row_color'),
 ('hub','_GetRowBackgroundColor',0x49948,1,6,41,112,'row_background'),
 ('hub','_IsRowSelected',0x499f0,1,5,41,70,'row_selected'),
 ('hub','HandleInput',0x491b8,1,17,25,736,'input'),
 ('hub','GetHints',0x49cc0,0,3,26,16,'hints'),
 ('cfm','_GetColumnData',0x8e660,0,3,41,58,'columns'),
 ('cfm','GetRowIndexFromKey',0x8e188,1,3,41,21,'key_index'),
 ('cfm','GetBackupState',0xa3790,0,5,41,168,'backup'),
 ('com','GetRowData',0x108a40,2,6,41,72,'rows'),
 ('com','GetRowKey',0x108738,1,4,41,88,'key'),
 ('com','GetNumMaxRows',0x108b00,0,4,41,88,'count'),
 ('com','GetCellKey',0x108810,2,4,41,18,'cell_key'),
 ('com','Sort',0x108908,2,4,41,48,'sort'),
 ('com','GetSortInfo',0x108970,0,6,41,151,'sort_info'),
 ('com','FilterData',0x108858,1,4,41,120,'filter_data'),
 ('com','RefreshDataSource',0x109578,0,2,41,11,'refresh'),
]

def emit(mode):
    a=FixedFrameAssembler(next(spec[4] for spec in SPECS if spec[-1]==mode))
    if mode=='team':team_module(a)
    elif mode=='filter':filter_changed(a)
    elif mode=='filter_guard':active(a,'normal');a.ret()
    elif mode=='color':cell_color(a)
    elif mode=='row_changed':row_changed(a)
    elif mode=='row_color':active(a,'normal');a.global_object('art_styleguide','Color','FLOATING_TEXT_COLOR');a.raw(0x3E)
    elif mode=='row_background':active(a,'normal');a.ret()
    elif mode=='row_selected':active(a,'normal');a.raw(0x74,0x3E)
    elif mode=='input':handle_input(a)
    elif mode=='hints':
        # Native flags0x1a preload super into r1 and suppress preloaded this.
        # Read the ordinary function-local this binding; preserve r1 so the
        # copied native super.GetHints fallback retains its original ABI.
        a.string('this');a.raw(0x1C);a.store(2)
        path(a,2,'mDEDraftActive');a.raw(0x73,0x66);a.branch('normal',0xB8)
        array(a,0);a.reg(0);a.raw(0x3E)
    elif mode=='shutdown':
        # A pending draft owns a retry timer before mDEDraftActive is set.
        # Cancel that timer on exit too; do not call back into a dead screen.
        path(a,1,'mIsDraftClass');a.raw(0x73,0x66);a.branch('shutdown_draft')
        path(a,1,'mDEDraftActive');a.raw(0x73,0x66);a.branch('shutdown_draft')
        path(a,1,'mDEDraftRetries');a.raw(0x76,0x49);a.branch('normal')
        a.label('shutdown_draft');clear_retry(a)
        a.reg(1);a.string('mDEDraftActive');a.raw(0x76,0x4F)
        a.reg(1);a.string('mDEDraftRetries');a.raw(0x76,0x4F)
        a.reg(1);a.string('mDEDraftWire');a.raw(0x76,0x4F)
        a.reg(1);a.string('mDEDraftPendingScope');a.raw(0x76,0x4F)
        a.reg(1);a.string('mDEDraftBuilding');a.raw(0x76,0x4F)
        a.reg(1);a.string('mDEDraftApplying');a.raw(0x76,0x4F)
        path(a,1,'mSpreadsheetDataProvider');a.store(4);a.missing(4,'normal');a.reg(4);a.string('mDEDraftRows');a.raw(0x76,0x4F)
        a.reg(4);a.string('mDEDraftNative');a.raw(0x76,0x4F)
    elif mode=='columns':a.set_field(1,'mDEDraftCfmReady',True);active(a,'normal',True);path(a,1,'mDEDraftColumns');a.raw(0x3E)
    elif mode=='key_index':key_index(a)
    elif mode=='backup':
        # Navigation requests backup before Shutdown. Stock backup converts
        # selected row keys to transient native DTO IDs and persists a team-
        # only filter. Neither operation accepts our custom rows/scopes.
        active(a,'normal');a.empty_object(2);a.reg(2);a.raw(0x3E)
    elif mode=='rows':provider_rows(a)
    elif mode=='key':row_key(a)
    elif mode=='count':a.set_field(1,'mDEDraftComReady',True);active(a,'normal',True);path(a,1,'mDEDraftRows','length');a.raw(0x3E)
    elif mode=='cell_key':
        active(a,'normal',True);path(a,1,'mDEDraftRows');a.reg(2);a.raw(0x4E);a.store(4);a.missing(4,'cell_key_empty');index(a,4,1);a.string('|');a.raw(0x47);a.reg(3);a.raw(0x4B,0x47,0x3E);a.label('cell_key_empty');a.ret()
    elif mode in ('sort','filter_data'):active(a,'normal',True);a.raw(0x73,0x3E)
    elif mode=='sort_info':
        active(a,'normal',True);array(a,4);a.empty_object(5);a.set_field(5,'key',5)
        a.reg(5);a.string('order');a.global_object('adapterenum_com','DataSource','SORTORDER_ASCENDING');a.raw(0x4F);push(a,4,5);a.reg(4);a.raw(0x3E)
    elif mode=='refresh':active(a,'normal',True);a.ret()
    else:raise ValueError(mode)
    a.label('normal');a.pad_code();return a

def generate(root,header,evidence):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools');from inspect_tb_ast import load
    assets={key:load(root/value) for key,value in ASSETS.items()};programs=[];report=[]
    for asset,name,body,argc,registers,flags,size,mode in SPECS:
        original=assets[asset].data[body:body+size];descriptor=assets[asset].data[body-48:body]
        assert struct.unpack_from('<IHH',descriptor,8)==(argc,registers,flags),(asset,name,'header')
        assert struct.unpack_from('<I',descriptor,24)[0]==size,(asset,name,'size')
        nested=NESTED_DEFINITIONS.get(mode,())
        # Every source loader-sentinel header must be explicitly described.
        # This guards against silently missing another relocated callback.
        observed=[]
        for at in range(0,size-47,8):
            if struct.unpack_from('<I',original,at+32)[0]==0x98765432 and struct.unpack_from('<Q',original,at+40)[0]==0x12345678:
                observed.append((at,struct.unpack_from('<Q',original,at)[0],struct.unpack_from('<Q',original,at+16)[0]))
        assert tuple(observed)==nested,(asset,name,'unlisted nested header')
        for at,name_rva,param_rva in nested:
            assert original[at-6]==0x9b,(asset,name,'nested opcode')
            assert struct.unpack_from('<Q',original,at)[0]==name_rva
            assert struct.unpack_from('<Q',original,at+16)[0]==param_rva
            assert struct.unpack_from('<IHH',original,at+8)==(0,0,0)
            assert struct.unpack_from('<I',original,at+24)[0]==0
            assert struct.unpack_from('<I',original,at+32)[0]==0x98765432
            assert struct.unpack_from('<Q',original,at+40)[0]==0x12345678
        a=emit(mode);copy_at=len(a.code);copy_bytes=size
        if mode=='rows':assert original[-3:]==bytes.fromhex('b9023e');copy_bytes-=3
        a.code.extend(bytes(copy_bytes))
        if mode=='rows':native_rows_suffix(a)
        p=a.finish();programs.append((asset,name,body-48,argc,registers,flags,size,fnv(original),copy_at,copy_bytes,p))
        report.append(dict(asset=ASSETS[asset],name=name,definition=body-48,argc=argc,registers=registers,flags=flags,size=size,hash=fnv(original),customBytes=len(p.code)-copy_bytes,copyAt=copy_at,copyBytes=copy_bytes,nestedDefinitions=[dict(offset=at,name=name_rva,params=param_rva) for at,name_rva,param_rva in nested]))
    lines=['// Generated by Tools/build_draft_results_ui.py; custom bytecode only.','#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::draftui {']
    for group in ASSETS:
        lines.append(f'inline std::vector<notesui::Program> {group}Programs(){{std::vector<notesui::Program> result;')
        for asset,name,offset,argc,regs,flags,size,hash_,copy_at,copy_bytes,p in programs:
            if asset!=group:continue
            code='{'+','.join(hex(b) for b in p.code)+'}'
            lines.append(f'// {name}\nresult.push_back({{{offset},{argc},{regs},{flags},{size},{hash_}ull,{regs},{copy_at},{copy_bytes},{code}}});')
            for at,name_rva,param_rva in NESTED_DEFINITIONS.get(next(spec[-1] for spec in SPECS if spec[0]==asset and spec[1]==name),()):
                lines.append(f'result.back().nestedDefinitions.push_back({{{at},{name_rva},{param_rva}}});')
            for field_name,offsets in [('scaleOffsets',p.scale_offsets),('teamScaleOffsets',p.team_scale_offsets),('colorOffsets',p.color_offsets),('fogOffsets',p.fog_offsets),('teamOffsets',p.team_offsets)]:
                for at in offsets:lines.append(f'result.back().{field_name}.push_back({at});')
            for at,value in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(value)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}')
    header.parent.mkdir(parents=True,exist_ok=True);header.write_text('\n'.join(lines)+'\n',encoding='utf8');evidence.mkdir(parents=True,exist_ok=True);(evidence/'programs.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'programs':len(programs),'customBytes':sum(len(p[-1].code)-p[-2] for p in programs),'header':str(header)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assets',type=Path,default=Path('../PlayerAnalytics/Research/assets'));parser.add_argument('--header',type=Path,default=Path('Source/DraftResultsUiPrograms.h'));parser.add_argument('--evidence',type=Path,default=Path('Evidence/PlayerFog/Draft'));args=parser.parse_args();generate(args.assets,args.header,args.evidence)
