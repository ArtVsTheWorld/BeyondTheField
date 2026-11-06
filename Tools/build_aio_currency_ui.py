"""AIO 1.4.1 currency compatibility; exact callbacks, original models retained.
Private method-map/AST evidence is required to regenerate this custom-only header.
"""
from pathlib import Path
import json,struct,sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,team_module_suffix
import build_currency_ui as cu
import build_currency_budget_ui as cb
import build_currency_topbar_ui as ct
import build_currency_recruitdetail_ui as cd
import build_currency_recruiteditor_ui as ce

native_money=cu.money

def aio_money(a,done,prefix):
    a.reg(0);a.raw(0x44);a.string('string');a.raw(0x66);a.branch(prefix+'plain',0xB8)
    a.number(0);a.number(1);a.reg(0);a.string('charAt');a.raw(0x52);a.string('$');a.raw(0x66);a.branch(prefix+'plain',0xB8)
    a.string('$');a.number(1);a.reg(0);a.string('split');a.raw(0x52);a.store(3)
    path(a,3,'length');a.number(2);a.raw(0x66);a.branch(done,0xB8)
    a.reg(3);a.number(1);a.raw(0x4E);a.store(0)
    a.number(1);a.store(2)
    for suffix,multiplier in [('K',1000),('M',1000000)]:
        path(a,0,'length');a.number(1);a.raw(0x0B);a.number(1);a.reg(0);a.string('charAt');a.raw(0x52);a.string(suffix);a.raw(0x66);a.branch(prefix+'not'+suffix,0xB8)
        a.string(suffix);a.number(1);a.reg(0);a.string('split');a.raw(0x52);a.number(0);a.raw(0x4E);a.store(0)
        a.number(multiplier);a.store(2)
        a.label(prefix+'not'+suffix)
    a.string(',');a.number(1);a.reg(0);a.string('split');a.raw(0x52);a.store(3)
    a.string('');a.number(1);a.reg(3);a.string('join');a.raw(0x52);a.store(3)
    path(a,3,'length');a.number(0);a.raw(0x67);a.branch(done,0xB8)
    for invalid in ['NaN','Infinity','-Infinity']:
        a.reg(3);a.string(invalid);a.raw(0x66);a.branch(done)
    a.reg(3);a.raw(0x4A);a.store(0)
    a.reg(0);a.raw(0x4B);a.reg(3);a.raw(0x66);a.branch(prefix+'valid')
    a.reg(0);a.raw(0x4B);a.string('.0');a.raw(0x47);a.reg(3);a.raw(0x66);a.branch(done,0xB8)
    a.label(prefix+'valid');a.reg(0);a.reg(2);a.raw(0x0C);a.number(4000);a.raw(0x0D);a.store(0)
    a.label(prefix+'plain');native_money(a,done,prefix+'base')


def builders():
    result={}
    for group,(_,specs) in cu.SPECS.items():
        for off,*rest in specs:result[(group,off)]=(None,rest[-1])
    for group,off,argc,regs,flags,size,hash_,pre,post in cb.SPECS:result[(group,off)]=(pre,post)
    result[('topbar',ct.OFFSET)]=(None,ct.suffix)
    for off,argc,regs,flags,size,hash_,builder in ct.GROUPS['recruitingPrograms'][1]:result[('recruiting',off)]=(None,builder)
    result[('detail',cd.OFFSET)]=(None,cd.suffix)
    for _,off,*_ in ce.SPECS:result[('editor',off)]=(None,ce.suffix)
    result[('team',0x728d0)]=(None,team_module_suffix)
    return result


def generate():
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    rows=json.loads(Path('Evidence/Aio141/method-map.json').read_text());specs=builders()
    for mod in [cu,cb,ct,cd,ce]:mod.money=aio_money
    groups={}
    for r in rows:
        if r['group']=='detail' or r['old']==r['new']:continue # unchanged callback already has its ordinary adapter
        pre,post=specs[(r['group'],r['old'])];apt=load(r['asset']);off=r['new'];size=r['size'];h=apt.data[off:off+48]
        assert struct.unpack_from('<IHH',h,8)==(r['argc'],r['registers'],r['flags'])
        a=ce.FixedFrameAssembler(r['registers']) if r['group']=='editor' else Assembler()
        if pre:pre(a);a.pad_code()
        copy_at=len(a.code);a.code.extend(bytes(size))
        if post:post(a)
        a.ret()
        p=a.finish();assert len(p.code)<=32768
        groups.setdefault(Path(r['asset']).stem.replace('-','_'),[]).append((r,p,copy_at,fnv(apt.data[off+48:off+48+size])))
    lines=['// Custom AIO 1.4.1 suffixes only. Native code is verified and copied live.','#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::aiocurrencyui {']
    for idx,entries in enumerate(groups.values()):
        lines.append(f'inline std::vector<notesui::Program> group{idx}(){{std::vector<notesui::Program> result;')
        for r,p,at,hash_ in entries:
            code='{'+','.join(hex(v) for v in p.code)+'}'
            lines.append(f'result.push_back({{{r["new"]},{r["argc"]},{r["registers"]},{r["flags"]},{r["size"]},{hash_}ull,{r["registers"]},{at},{r["size"]},{code}}});')
            for attr,member in [('scale_offsets','scaleOffsets'),('team_scale_offsets','teamScaleOffsets'),('color_offsets','colorOffsets'),('fog_offsets','fogOffsets'),('team_offsets','teamOffsets'),('dollar_offsets','dollarOffsets')]:
                for pos in getattr(p,attr):lines.append(f'result.back().{member}.push_back({pos});')
            for pos,txt in p.literals:lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(txt)+f');memcpy(result.back().code.data()+{pos},&pointer,8);}}')
        lines.append('return result;}')
    lines.append('}')
    Path('Source/AioCurrencyUiPrograms.h').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'assetBanks':len(groups),'callbacks':sum(map(len,groups.values()))}))
if __name__=='__main__':generate()
