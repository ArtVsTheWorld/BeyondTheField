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
