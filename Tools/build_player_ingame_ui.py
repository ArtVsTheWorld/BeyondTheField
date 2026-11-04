"""Scoped coach-camera player-rating labels; no gameplay or model changes."""
from pathlib import Path
import json
import sys
from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path,numeric_grade,palette,text_label,value_item_suffix


FIELDS=[('awareness','mcAwarenessValue'),('speed','mcSpeedValue'),
        ('acceleration','mcAccelerationValue'),('agility','mcAgilityValue'),
        ('strength','mcStrengthValue')]


def player_ratings_suffix(a):
    path(a,1,'mData');a.raw(0x76,0x49);a.branch('overlayDone')
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('overlayDone')
    for index,(field,widget) in enumerate(FIELDS):
        done='overlayNext'+str(index)
        path(a,1,'mData','ExtraInfo',field);a.store(3)
        numeric_grade(a,3,4,done,'overlayGrade'+str(index))
        palette(a,4,5,done,'overlayPalette'+str(index))
        path(a,1,widget);a.store(6)
        text_label(a,6,4,5,7,done,'overlayText'+str(index))
        a.label(done)
    # Native constructor explicitly creates a medium RatingValueItem. Its
    # numeric value still drives native layout; only mcValue's label changes.
    path(a,1,'mData','ExtraInfo','overallrating');a.store(3)
    numeric_grade(a,3,4,'overlayDone','overlayOvrVisibility')
    path(a,1,'mcOvr');a.store(7)
    value_item_suffix(a,7,8,'overlayOvr',mark=True)
    a.label('overlayDone');a.ret()


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    apt=load(Path('Evidence/PlayerFog/node-ig-scriptpod.ast'))
    offset,size,expected=0x37FE8,674,0xA570B1AFB77C6507
    if fnv(apt.data[offset+48:offset+48+size])!=expected:
        raise ValueError('Unsupported native coach-camera rating renderer')
    a=Assembler();a.code.extend(bytes(size));player_ratings_suffix(a);p=a.finish()
    lines=['// Custom presentation bytecode only; native body verified/copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::playeringameui {',
           'inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;']
    code='{'+','.join(hex(b) for b in p.code)+'}'
    lines.append(f'result.push_back({{{offset},0,7,25,{size},{expected}ull,13,0,{size},{code}}});')
    for at,text in p.literals:
        lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}'];destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'coachCameraRatingMethods':1,'nativeModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerInGameUiPrograms.h'))
