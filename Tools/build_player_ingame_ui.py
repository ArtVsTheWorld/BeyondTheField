"""Scoped in-game player-rating labels; no gameplay or model changes."""
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


def direct_player_suffix(a,field,widget,*,ovr_suffix=False,color=False):
    # These exact native Draw methods own a player-only text label. Never
    # replace ExtraInfo: other playcall consumers use its numeric ratings.
    done='directDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo',field);a.store(0)
    numeric_grade(a,0,0,done,'directGrade')
    path(a,1,widget);a.store(2);a.missing(2,done)
    path(a,2,'_visible');a.raw(0x73,0x66);a.branch(done,0xB8)
    if color:palette(a,0,3,done,'directPalette')
    if ovr_suffix:a.reg(0);a.string(' OVR');a.raw(0x47);a.store(0)
    if color:
        text_label(a,2,0,3,0,done,'directText')
    else:
        # Focus callbacks own the foreground on selectable playcall rows.
        # Keep their native black/white contrast rather than override it.
        path(a,2,'mData');a.raw(0x76,0x49);a.branch('directSetLabel')
        path(a,2,'mData','display');a.reg(0);a.raw(0x66);a.branch(done)
        a.label('directSetLabel');a.reg(0);a.number(1);a.reg(2);a.call('SetLabel')
    a.label(done);a.ret()


def key_player_suffix(a):direct_player_suffix(a,'overall','mcOVR',ovr_suffix=True,color=True)
def playcall_player_suffix(a):direct_player_suffix(a,'PrimaryTargetOVR','mcOvrStat')
def substitution_player_suffix(a):direct_player_suffix(a,'overallRating','mcOvrStat')
def depth_panel_player_suffix(a):direct_player_suffix(a,'PlayerOvr','mcOvr')


SPECS=[(0x37FE8,0,7,25,674,0xA570B1AFB77C6507,13,player_ratings_suffix),
       (0x2EB18,0,4,25,384,0xA4ED8C8AB9298E2B,4,key_player_suffix),
       (0x32720,0,13,41,3669,0xBDCD7B378AF81866,13,playcall_player_suffix),
       (0x37450,0,4,25,244,0xD63997CEC6812D50,4,substitution_player_suffix),
       (0x2C0E8,0,4,25,93,0x0FFA0C82BC667F1C,4,depth_panel_player_suffix)]


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    apt=load(Path('Evidence/PlayerFog/node-ig-scriptpod.ast'))
    lines=['// Custom presentation bytecode only; native body verified/copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::playeringameui {',
           'inline std::vector<notesui::Program> programs(){std::vector<notesui::Program> result;']
    for offset,argc,regs,flags,size,expected,newregs,suffix in SPECS:
        if fnv(apt.data[offset+48:offset+48+size])!=expected:
            raise ValueError(f'Unsupported native in-game player renderer {offset:x}')
        a=Assembler();a.code.extend(bytes(size));suffix(a);p=a.finish()
        code='{'+','.join(hex(b) for b in p.code)+'}'
        lines.append(f'result.push_back({{{offset},{argc},{regs},{flags},{size},{expected}ull,{newregs},0,{size},{code}}});')
        for at,text in p.literals:
            lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
    lines+=['return result;}','}'];destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'inGameRatingMethods':len(SPECS),'nativeModelChanges':False}))


if __name__=='__main__':generate(Path('Source/PlayerInGameUiPrograms.h'))
