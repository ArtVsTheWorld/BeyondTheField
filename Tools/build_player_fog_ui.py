"""Generate a fingerprinted native spreadsheet color adapter; no game bytes shipped."""
from pathlib import Path
import argparse
import json
import sys
from build_recruit_notes_ui import Assembler, fnv


def spreadsheet_columns():
    a = Assembler()
    a.number(0); a.store(3)
    a.label('loop')
    a.reg(3); a.reg(7); a.raw(0x48); a.branch('done', 0xB8)
    a.reg(5); a.global_object('fb_shared_enum', 'BindingType', 'PRIMARY_DATA')
    a.number(2); a.reg(1); a.string('_GetTemplate'); a.raw(0x52); a.store(2)
    a.reg(5); a.string('column'); a.raw(0x49); a.branch('add', 0xB8)
    a.reg(2); a.member('ExtraInfo'); a.raw(0x76, 0x49); a.branch('extra_ready', 0xB8)
    a.reg(2); a.string('ExtraInfo'); a.number(0); a.string('Object'); a.raw(0x40, 0x4F)
    a.label('extra_ready')
    for output, source in [('Header', 'mHeaderText'), ('Hint', 'mHint'), ('IsStatic', 'mIsStatic')]:
        a.reg(2); a.member('ExtraInfo'); a.string(output)
        a.reg(1); a.member('mColumns'); a.reg(3); a.raw(0x4E); a.member(source); a.raw(0x4F)
    a.reg(2); a.member('ExtraInfo'); a.string('SortKey'); a.reg(3); a.raw(0x4F)
    a.reg(3); a.reg(1); a.member('mSortKey'); a.raw(0x49); a.branch('unsorted', 0xB8)
    a.reg(2); a.member('ExtraInfo'); a.string('SortDirection'); a.reg(1); a.member('mSortOrder'); a.raw(0x4F)
    a.branch('get_row', 0x99)
    a.label('unsorted'); a.reg(2); a.member('ExtraInfo'); a.string('SortDirection'); a.string(''); a.raw(0x4F)
    a.label('get_row')
    a.reg(3); a.number(1); a.raw(0x42); a.reg(8); a.number(2)
    a.reg(1); a.member('mLegacyDataProvider'); a.string('GetRowData'); a.raw(0x52); a.store(4)
    for output, source in [('display', 'display'), ('value', 'intValue')]:
        a.reg(2); a.string(output); a.reg(4); a.number(0); a.raw(0x4E); a.member(source); a.raw(0x4F)
    # Only native rows explicitly marked by the exact roster schema qualify.
    # No player, scene or process discovery is performed in the draw path.
    a.reg(4); a.number(0); a.raw(0x4E); a.member('DEPlayerRating'); a.raw(0x73, 0x66); a.branch('add', 0xB8)
    a.reg(2); a.member('ExtraInfo'); a.string('fontColor')
    a.reg(4); a.number(0); a.raw(0x4E); a.member('DEGradeColor'); a.raw(0x4F)
    a.label('add'); a.reg(2); a.number(1); a.reg(6); a.call('AddItem')
    a.reg(3); a.raw(0x50); a.store(3); a.branch('loop', 0x99)
    a.label('done'); a.ret()
    return a.finish()


def legacy_color():
    a=Assembler()
    # Ucm caches the raw column definitions including our exact-schema marker.
    a.reg(1); a.member('mColumnData'); a.raw(0x76,0x49); a.branch('fallback')
    a.reg(1); a.member('mColumnData'); a.reg(3); a.raw(0x4E); a.store(0)
    a.reg(0); a.raw(0x76,0x49); a.branch('fallback')
    a.reg(0); a.member('DEPlayerRating'); a.raw(0x73,0x66); a.branch('fallback',0xB8)
    a.reg(3); a.number(1); a.raw(0x42); a.reg(2); a.number(2); a.reg(1)
    a.string('GetRowData'); a.raw(0x52); a.store(0)
    a.reg(0); a.number(0); a.raw(0x4E); a.store(0)
    a.reg(0); a.raw(0x76,0x49); a.branch('fallback')
    a.reg(0); a.member('DEPlayerRating'); a.raw(0x73,0x66); a.branch('fallback',0xB8)
    a.reg(0); a.member('DEGradeColor'); a.raw(0x3E)
    a.label('fallback')
    a.reg(3); a.reg(2); a.number(2); a.reg(1); a.member('mCallbacks')
    a.string('CellColorCallback'); a.raw(0x52,0x3E)
    return a.finish()


def generate(asset, destination):
    sys.path.insert(0, 'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    apt = load(asset)
    offset, size, expected = 0xCAC90, 260, 0xF06BD459B1CE1E27
    original = apt.data[offset+48:offset+48+size]
    if fnv(original) != expected:
        raise ValueError('Unsupported native spreadsheet method; refusing to generate')
    lines = ['// Generated custom bytecode only; native method verified at attachment.', '#pragma once',
             '#include "RecruitNotesUiPrograms.h"', 'namespace recruitingfog::playerui {',
             ]
    legacy=load(asset.parent/'scriptpod.ast')
    legacy_offset,legacy_size,legacy_hash=0x108FE8,14,0xD913F7BA474B1A0F
    if fnv(legacy.data[legacy_offset+48:legacy_offset+48+legacy_size])!=legacy_hash:
        raise ValueError('Unsupported native legacy spreadsheet color method')
    # Keep native black selected-row foreground for readability on the light
    # selection scrim. Only the provider's unselected color callback is adapted.
    groups=[('programs',[
        (legacy_color(),legacy_offset,2,4,41,legacy_size,legacy_hash,0,0)]),
        ('modernPrograms',[(spreadsheet_columns(),offset,4,9,41,size,expected,0,0)])]
    for name,specs in groups:
        lines.append(f'inline std::vector<notesui::Program> {name}(){{std::vector<notesui::Program> result;')
        for p,off,argc,regs,flags,native_size,hash_,copy_at,copy_size in specs:
            array='{'+','.join(hex(b) for b in p.code)+'}'
            lines.append(f'result.push_back({{{off},{argc},{regs},{flags},{native_size},{hash_}ull,{regs},{copy_at},{copy_size},{array}}});')
            for at,text in p.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}')
    destination.write_text('\n'.join(lines)+'\n', encoding='utf8')
    print(json.dumps({'methods': 2, 'legacyRegistersPreserved': [4], 'modernRegistersPreserved': 9, 'selectedRow': 'native black foreground'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asset', type=Path, default=Path('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_com/frameworkscriptpod.ast'))
    parser.add_argument('--header', type=Path, default=Path('Source/PlayerFogUiPrograms.h'))
    args = parser.parse_args()
    generate(args.asset, args.header)
