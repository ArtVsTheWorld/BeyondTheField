"""Execute native/custom spreadsheet programs against identical fake UI providers."""
from pathlib import Path
import copy
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'Tools'))
from build_recruit_notes_ui import Program
from build_player_fog_ui import spreadsheet_columns, legacy_color
from recruit_notes_vm import Machine
sys.path.insert(0, 'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load

apt=load(Path('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_com/frameworkscriptpod.ast'))
original=Program(apt.data[0xCACC0:0xCADC4],[],[])
pool=apt.decode(0xCA9F8)[0][2]
custom=spreadsheet_columns()

def execute(program, kind, marked, extra):
    calls=[];items=[]
    def get_row(row, columns):
        calls.append((row,columns))
        result={'display':['B','A','2,347'][columns[0]],'intValue':[83,90,2347][columns[0]]}
        if marked and columns[0]<2:
            result.update(DEPlayerRating=True, DEGradeColor=[0xA8D943,0x1FE840][columns[0]])
        return [result]
    def template(binding, type_):
        assert binding=='primary' and type_==kind
        return {'ExtraInfo':copy.deepcopy(extra)} if extra is not None else {}
    receiver={'_GetTemplate':template, 'mLegacyDataProvider':{'GetRowData':get_row},
              'mColumns':[{'mHeaderText':name,'mHint':'hint-'+name,'mIsStatic':i==0} for i,name in enumerate(['OVR','SPD','Yards'])],
              'mSortKey':1,'mSortOrder':'descending'}
    Machine({'fb_shared_enum':{'BindingType':{'PRIMARY_DATA':'primary'}}},pool).run(program,{1:receiver,5:kind,6:{'AddItem':items.append},7:3,8:12})
    return items,calls

for kind in ['column','row']:
    for extra in [None,{}, {'fontColor':0x123456,'unrelated':'preserved'}]:
        native,calls=execute(original,kind,True,extra)
        neutral,neutral_calls=execute(custom,kind,False,extra)
        assert neutral==native and neutral_calls==calls, 'Unmarked output differs from native behavior'
        colored,colored_calls=execute(custom,kind,True,extra)
        assert colored_calls==calls, 'Color adapter repeated a native data request'
        if kind=='column':
            for i,color in enumerate([0xA8D943,0x1FE840]):
                assert colored[i]['ExtraInfo'].pop('fontColor')==color
                expected=copy.deepcopy(native[i]);expected['ExtraInfo'].pop('fontColor',None)
                assert colored[i]==expected
            assert colored[2]==native[2], 'Non-rating column recolored'
        else:
            assert colored==native, 'Non-column provider changed'
print('Passed: native-equivalent spreadsheet semantics, exact marker colors, existing styles, sort metadata and one data call per cell.')

legacy=load(Path('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_com/scriptpod.ast'))
legacy_pool=legacy.decode(0x107F70)[0][2]
native_color=Program(legacy.data[0x109018:0x109026],[],[])
for column_marked in [True,False]:
    for row_marked in [True,False]:
        for color in [0x1FE840,0xA8D943,0xFFD34D,0xF68C2E,0xF04444]:
            calls=[]
            def row_data(row,cols):
                calls.append(('row',row,cols));return [{'display':'D','DEPlayerRating':row_marked,'DEGradeColor':color}]
            def fallback(row,col):
                calls.append(('fallback',row,col));return 0x123456
            receiver={'mColumnData':[{'DEPlayerRating':column_marked}], 'GetRowData':row_data, 'mCallbacks':{'CellColorCallback':fallback}}
            result=Machine({},legacy_pool).run(legacy_color(),{1:receiver,2:7,3:0})
            if column_marked and row_marked:
                assert result==color and calls==[('row',7,[0])]
            elif column_marked:
                assert result==0x123456 and calls==[('row',7,[0]),('fallback',7,0)]
            else:
                assert result==0x123456 and calls==[('fallback',7,0)]
            calls.clear();assert Machine({},legacy_pool).run(native_color,{1:receiver,2:7,3:0})==0x123456 and calls==[('fallback',7,0)]
print('Passed: legacy column+row marker gating, all five colors, native callback fallback, one-column reads and no color recursion.')

# Selected foreground remains entirely native; no selected-color method ships.
header=Path("Source/PlayerFogUiPrograms.h").read_text()
assert "controlPrograms" not in header and "462D3820" not in header
assert "inline std::vector<notesui::Program> programs()" in header
print("Passed: selected-row override absent; native highlight foreground preserved.")

# The older in-game depth chart uses Cafe2SpreadsheetProvider, not Ucm's
# native column collector. Its returned cells are fresh presentation objects.
from build_recruit_notes_ui import Assembler,GRADE_COLORS,fnv
from build_player_legacy_depth_ui import SHEET,ATTRIBUTES,columns_suffix,rows_suffix,color_prefix,SPECS as DEPTH_SPECS
from recruit_notes_vm import UNDEFINED

def suffix_program(suffix):
    a=Assembler();suffix(a);return a.finish()

headers=['Slot','Player','POS','OVR','Year',*ATTRIBUTES,'Other statistic']
definitions=[{'mHeaderText':h,'mHint':h+' hint','mIsStatic':i<2,'width':80} for i,h in enumerate(headers)]
original_defs=copy.deepcopy(definitions)
receiver={'mSpreadsheetId':SHEET}
assert Machine({},[]).run(suffix_program(columns_suffix),{1:receiver,13:definitions}) is definitions
assert definitions==original_defs
mask=receiver['DEPauseRatingColumns']
assert mask==[False,False,False,True,False]+[True]*len(ATTRIBUTES)+[False]

for rating in range(101):
    grade='A' if rating>=90 else 'B' if rating>=80 else 'C' if rating>=70 else 'D' if rating>=60 else 'F'
    for raw in [rating,str(rating)]:
        # Deliberately request out-of-order/noncontiguous columns. Conversion
        # must use semantic IDs, never the visible position in the row.
        columns=[4,3,6,0,len(headers)-1]
        cells=[{'display':v,'trend':'TrendDown','rating':rating,'intValue':rating,'rowKey':42} for v in ['SR',raw,raw,'2.',raw]]
        before=copy.deepcopy(cells);provider_before=copy.deepcopy(receiver)
        assert Machine({},[]).run(suffix_program(rows_suffix),{1:receiver,3:cells,5:columns}) is cells
        assert receiver==provider_before
        for i in [0,3,4]:assert cells[i]==before[i], 'Non-rating display was changed'
        for i in [1,2]:
            assert cells[i]['display']==grade and cells[i]['DEPauseGradeColor']==GRADE_COLORS[grade]
            assert cells[i]['DEPausePlayerRating'] is True
            for key in ['trend','rating','intValue','rowKey']:assert cells[i][key]==before[i][key]

for invalid in [UNDEFINED,None,'?','--','',-1,101,'01','090','1000','85.0','9.5','-1','+90',' 90','90 ','9%','A','85,TrendUp',float('nan'),float('inf')]:
    cell={'display':invalid,'trend':'TrendNone','rating':99}
    Machine({},[]).run(suffix_program(rows_suffix),{1:receiver,3:[cell],5:[3]})
    assert cell['display'] is invalid and 'DEPausePlayerRating' not in cell

for sheet in ['Roster','Edit Player','Player - DepthChart',None,UNDEFINED]:
    other={'mSpreadsheetId':sheet,'DEPauseRatingColumns':[True]*90};before=copy.deepcopy(other)
    result=Machine({},[]).run(suffix_program(columns_suffix),{1:other,13:definitions})
    assert result is definitions and other['DEPauseRatingColumns']==before['DEPauseRatingColumns']
    cell={'display':'92','rating':92,'trend':'TrendUp'}
    Machine({},[]).run(suffix_program(rows_suffix),{1:other,3:[cell],5:[3]})
    assert cell=={'display':'92','rating':92,'trend':'TrendUp'}

for bad_defs in [None,[],definitions[:5],definitions*2,[{'mHeaderText':'Jersey'},*definitions[1:]], [{'mHeaderText':'Slot'},{'mHeaderText':'Stats'},*definitions[2:]]]:
    other={'mSpreadsheetId':SHEET,'DEPauseRatingColumns':[True]*90}
    assert Machine({},[]).run(suffix_program(columns_suffix),{1:other,13:bad_defs}) is bad_defs
    assert other['DEPauseRatingColumns'] is UNDEFINED, 'Stale mask survived unsupported headers'

for column in [0,3,4,5,len(headers)-1]:
    calls=[]
    def get_row(row,cols):
        calls.append((row,cols));assert row==17 and cols==[column]
        return [{'display':'A','DEPausePlayerRating':True,'DEPauseGradeColor':GRADE_COLORS['A']}]
    provider={**receiver,'GetRowData':get_row}
    a=Assembler();color_prefix(a);a.number(12);a.raw(0x3E)
    super_object={'native':'preserved'}
    result=Machine({},[]).run(a.finish(),{1:provider,2:super_object,7:17,8:column})
    assert result==(GRADE_COLORS['A'] if mask[column] else 12)
    assert calls==([(17,[column])] if mask[column] else [])
    assert super_object=={'native':'preserved'}

class DepthBoundedAssembler(Assembler):
    def __init__(self,limit):super().__init__();self.limit=limit
    def reg(self,n):assert 0<=n<self.limit;super().reg(n)
    def store(self,n):assert 0<=n<self.limit;super().store(n)
for off,argc,regs,flags,size,hash_,suffix,copy_size in DEPTH_SPECS:
    a=DepthBoundedAssembler(regs);suffix(a);a.finish()
    assert fnv(legacy.data[off+48:off+48+size])==hash_
print('Passed: legacy pause depth101 numeric/string boundaries, exact named-sheet/header gates, reordered column subsets, hidden values, untouched source/trends/sort/slot/year fields, cached masks and fixed register frames.')
