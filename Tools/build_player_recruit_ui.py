"""Player-only recruiting preview labels; no scouting or risk model changes."""
from pathlib import Path
import json
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade,palette,text_label


ASSET=Path('C:/Apps/CFB 27/MMC/DynastyEnhancer-RecruitingFog/Evidence/RecruitingFog/Assets/common__ui__node_cfm__recruitinghub__corenode.ast')
OFFSET,SIZE,HASH=0x2A380,596,0x26C26CC3E3BFAC83


def risk_player_suffix(a):
    done='riskPlayerDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','IsHeader');a.raw(0x73,0x66);a.branch(done)
    path(a,1,'mData','ExtraInfo','OVR');a.store(0)
    numeric_grade(a,0,0,done,'riskGrade')
    palette(a,0,2,done,'riskPalette')
    path(a,1,'mcOVR');a.store(3)
    # Native frame has four registers. The label register can become the style
    # object only after SetLabel and its equality check have finished.
    text_label(a,3,0,2,0,done,'riskText')
    a.label(done);a.ret()


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    apt=load(ASSET)
    if fnv(apt.data[OFFSET+48:OFFSET+48+SIZE])!=HASH:
        raise ValueError('Unsupported My School player-risk renderer')
    a=Assembler();a.code.extend(bytes(SIZE));risk_player_suffix(a);p=a.finish()
    lines=['// Custom presentation suffix; native body verified/copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::playerrecruitui {',
           'inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;']
    code='{'+','.join(hex(b) for b in p.code)+'}'
    lines.append(f'result.push_back({{{OFFSET},0,4,25,{SIZE},{HASH}ull,4,0,{SIZE},{code}}});')
    for at in p.color_offsets:lines.append(f"result.back().colorOffsets.push_back({at});")
    for at in p.scale_offsets:lines.append(f"result.back().scaleOffsets.push_back({at});")
    for at in p.team_scale_offsets:lines.append(f"result.back().teamScaleOffsets.push_back({at});")
    for at in p.fog_offsets:lines.append(f"result.back().fogOffsets.push_back({at});")
    for at in p.team_offsets:lines.append(f"result.back().teamOffsets.push_back({at});")
    for at in p.dollar_offsets:lines.append(f"result.back().dollarOffsets.push_back({at});")
    for at,text in p.literals:
        lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}']
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'playerRecruitingMethods':1,'scoutingOrRiskModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerRecruitUiPrograms.h'))
