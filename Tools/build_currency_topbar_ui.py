"""Format the native Dynasty topbar's own program-points text widget.

CareerInfoModule is a separate asset from generic SwappableAndTextItem. This
bank changes its rendered mcProgramPoints label, never its numeric budget or
the adjacent coach/staff skill-point values.
"""
from pathlib import Path
import json
import struct
import sys

from build_recruit_notes_ui import Assembler,fnv
from build_player_card_ui import path
from build_currency_ui import money

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'Evidence/PlayerFog/Gaps/current-infocenterart.ast'
OFFSET=0xBB90
SIZE=5040
HASH=0x5F96F78C7A24561E
ARGC,REGISTERS,FLAGS=1,20,41
RECRUITING_ASSET=ROOT/'Evidence/PlayerFog/Gaps/current-recruitinghub.ast'


def suffix(a):
    done='topbarDollarDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    # This shared career bar also displays RTG/owner modes. Native Dynasty
    # coaching data explicitly marks isCoach and supplies its remaining budget.
    path(a,1,'mData','ExtraInfo','isCoach');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mcProgramPoints');a.store(4);a.missing(4,done)
    path(a,1,'mData','ExtraInfo','remainingProgramPoints');a.store(0)
    money(a,done,'topbarDollar')
    # Keep native font, colors, right alignment, icon placement and point data.
    a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    a.label(done);a.ret()


def recruiting_wallet_suffix(a):
    done='recruitWalletDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mWalletProgramPoints');a.store(4);a.missing(4,done)
    # Native _RefreshStats has just stored GetRecruitInfoData.programPoints in
    # this animation/cache field. The other three wallets are count/hour ratios.
    path(a,1,'mPreviousProgramPoints');a.store(0);money(a,done,'recruitWallet')
    a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    a.label(done);a.ret()


def recruit_list_offer_suffix(a):
    done='recruitListOfferDone';restore='recruitListOfferRestore';format_='recruitListOfferFormat'
    # PlayerListItem owns a right-aligned points label and its left-hand icon.
    # Bound them to the existing right column rather than extending into names.
    # This callback remains dispatched while Off to restore an owned prior fit.
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcPoints');a.store(4);a.missing(4,done)
    path(a,1,'mcPointsIcon');a.store(6)
    path(a,1,'mDERecruitOfferFit');a.store(5)
    path(a,1,'mData','ExtraInfo','CurrentNILOffer');a.store(9)
    a.dollars_enabled();a.number(1);a.raw(0x66);a.store(17)
    a.raw(0x76);a.store(7) # no fit until native geometry is proven
    a.reg(17);a.branch(restore,0xB8)
    a.missing(6,restore)
    path(a,1,'mcPointsContainer');a.store(10);a.missing(10,restore)
    path(a,1,'mcName');a.store(11);a.missing(11,restore)
    for reg,parts in [(4,('mData',)),(4,('mData','ExtraInfo')),
                      (6,('GetWidth',)),(11,('GetWidth',))]:
        path(a,reg,*parts);a.store(3);a.missing(3,restore)
    for reg,prop,target in [(4,'_x',13),(10,'_x',14),(11,'_x',15),(1,'mCoordFarLeftIcon',8)]:
        path(a,reg,prop);a.store(target)
        a.reg(target);a.raw(0x44);a.string('number');a.raw(0x66);a.branch(restore,0xB8)
        a.reg(target);a.number(-4096);a.raw(0x67);a.branch(restore,0xB8)
        a.reg(target);a.number(4096);a.raw(0x48);a.branch(restore,0xB8)
    for reg,target in [(6,12),(11,16)]:
        a.number(0);a.reg(reg);a.string('GetWidth');a.raw(0x52);a.store(target)
        a.reg(target);a.raw(0x44);a.string('number');a.raw(0x66);a.branch(restore,0xB8)
        a.reg(target);a.number(0);a.raw(0x67);a.branch(restore,0xB8)
        a.reg(target);a.number(4096);a.raw(0x48);a.branch(restore,0xB8)
    # Name and points container are siblings. x332 is the native first right
    # flag's column; a longer rendered name can increase that left boundary.
    a.reg(15);a.reg(16);a.raw(0x47);a.number(8);a.raw(0x47);a.store(3)
    a.reg(3);a.reg(8);a.raw(0x67);a.branch('recruitListOfferNameBound',0xB8)
    a.reg(3);a.store(8)
    a.label('recruitListOfferNameBound')
    a.reg(13);a.reg(14);a.raw(0x47);a.reg(8);a.raw(0x0B);a.reg(12);a.raw(0x0B);a.number(4);a.raw(0x0B);a.store(3)
    a.reg(3);a.number(0);a.raw(0x67);a.branch(restore,0xB8)
    a.reg(3);a.number(1024);a.raw(0x48);a.branch(restore,0xB8)
    a.reg(3);a.store(7)
    # An unchanged native row gets no extra setters, clones or invalidations.
    a.missing(5,restore)
    for reg,prop in [(4,'label'),(6,'icon'),(9,'source'),(7,'width'),
                     (13,'x'),(14,'containerX'),(15,'nameX'),(16,'nameWidth'),(8,'left'),(12,'iconWidth')]:
        a.reg(reg);path(a,5,prop);a.raw(0x66);a.branch(restore,0xB8)
    path(a,4,'mData','display');path(a,5,'display');a.raw(0x66);a.branch(restore,0xB8)
    path(a,6,'_x');path(a,5,'iconX');a.raw(0x66);a.branch(restore,0xB8)
    path(a,4,'mData','ExtraInfo','resize');a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN');a.raw(0x66);a.branch(restore,0xB8)
    path(a,4,'mData','ExtraInfo','resizeWidth');a.reg(7);a.raw(0x66);a.branch(restore,0xB8)
    path(a,4,'mData','ExtraInfo','maxNumLines');a.number(1);a.raw(0x66);a.branch(restore,0xB8)
    a.branch(done,0x99)
    a.label(restore)
    a.missing(5,format_)
    a.reg(4);path(a,5,'label');a.raw(0x66);a.branch('recruitListOfferClear',0xB8)
    path(a,4,'mData');a.store(3);a.missing(3,'recruitListOfferClear')
    path(a,4,'mData','display');path(a,5,'display');a.raw(0x66);a.branch('recruitListOfferRestoreStyle',0xB8)
    a.reg(9);a.number(1);a.reg(4);a.call('SetLabel')
    a.label('recruitListOfferRestoreStyle')
    path(a,4,'mData','ExtraInfo');a.store(3);a.missing(3,'recruitListOfferRestoreIcon')
    # Restore only resize fields still owned by us, preserving native focus
    # colors and any later native edits to the same text widget.
    for prop in ['resize','resizeWidth','maxNumLines']:
        keep='recruitOfferKeep'+prop;ready='recruitOfferReady'+prop
        a.string(prop);path(a,4,'mData','ExtraInfo',prop)
        if prop=='resize':a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN')
        elif prop=='resizeWidth':path(a,5,'width')
        else:a.number(1)
        a.raw(0x66);a.branch(keep,0xB8)
        path(a,5,prop);a.branch(ready,0x99)
        a.label(keep);path(a,4,'mData','ExtraInfo',prop);a.label(ready)
    a.number(3);a.raw(0x43);a.number(1);a.reg(4);a.call('SetExtraInfo')
    a.label('recruitListOfferRestoreIcon')
    a.missing(6,'recruitListOfferClear')
    a.reg(6);path(a,5,'icon');a.raw(0x66);a.branch('recruitListOfferClear',0xB8)
    path(a,6,'_x');path(a,5,'iconX');a.raw(0x66);a.branch('recruitListOfferClear',0xB8)
    path(a,6,'GetWidth');a.store(3);a.missing(3,'recruitListOfferClear')
    a.reg(9);path(a,5,'source');a.raw(0x66);a.branch('recruitListOfferFreshNativeIcon',0xB8)
    # Restore the proven native raw-offer baseline without asking a deferred
    # text renderer for metrics immediately after changing text/style. Anchor
    # or image-size changes can be applied as exact coordinate deltas.
    a.reg(6);a.string('_x');path(a,5,'nativeIconX')
    path(a,4,'_x');path(a,5,'x');a.raw(0x0B,0x47)
    a.number(0);a.reg(6);a.string('GetWidth');a.raw(0x52);path(a,5,'iconWidth');a.raw(0x0B,0x0B,0x4F)
    a.branch('recruitListOfferClear',0x99)
    a.label('recruitListOfferFreshNativeIcon')
    # A new source normally arrives with native INVALIDATE_OFFERED geometry,
    # which the ownership check above leaves untouched. Keep the exact stock
    # formula as fallback for a changed source without native dirty rendering.
    path(a,4,'GetWidth');a.store(3);a.missing(3,'recruitListOfferClear')
    a.reg(6);a.string('_x');path(a,4,'_x')
    a.number(0);a.reg(4);a.string('GetWidth');a.raw(0x52,0x0B)
    a.number(0);a.reg(6);a.string('GetWidth');a.raw(0x52,0x0B);a.number(4);a.raw(0x0B,0x4F)
    a.label('recruitListOfferClear');a.reg(1);a.string('mDERecruitOfferFit');a.raw(0x76,0x4F)
    a.label(format_);a.reg(17);a.branch(done,0xB8)
    a.reg(9);a.store(0);money(a,done,'recruitListOffer')
    a.missing(7,'recruitListOfferSetLabel')
    # Capture only the three native style fields changed below, never colors.
    for prop in ['resize','resizeWidth','maxNumLines']:
        a.string(prop);path(a,4,'mData','ExtraInfo',prop)
    for reg,prop in [(4,'label'),(6,'icon'),(9,'source'),(2,'display'),(7,'width'),
                     (13,'x'),(14,'containerX'),(15,'nameX'),(16,'nameWidth'),(8,'left'),(12,'iconWidth')]:
        a.string(prop);a.reg(reg)
    a.string('nativeIconX');path(a,6,'_x')
    a.number(15);a.raw(0x43);a.store(5)
    a.reg(1);a.string('mDERecruitOfferFit');a.reg(5);a.raw(0x4F)
    a.string('resize');a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN')
    a.string('resizeWidth');a.reg(7);a.string('maxNumLines');a.number(1);a.number(3);a.raw(0x43)
    a.number(1);a.reg(4);a.call('SetExtraInfo')
    a.label('recruitListOfferSetLabel')
    path(a,4,'mData');a.store(3);a.missing(3,'recruitListOfferWriteLabel')
    path(a,4,'mData','display');a.reg(2);a.raw(0x66);a.branch('recruitListOfferPositionIcon')
    a.label('recruitListOfferWriteLabel');a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    a.label('recruitListOfferPositionIcon');a.missing(7,done)
    # Pin the icon at the reserved column's left edge, independently of a
    # deferred text-width recalculation. Right-aligned text can never cross it.
    a.reg(13);a.reg(7);a.raw(0x0B);a.reg(12);a.raw(0x0B);a.number(4);a.raw(0x0B);a.store(3)
    a.reg(6);a.string('_x');a.reg(3);a.raw(0x4F)
    a.reg(5);a.string('iconX');a.reg(3);a.raw(0x4F)
    a.label(done);a.ret()


def total_hours_offer_suffix(a):
    done='totalHoursOfferDone'
    a.dollars_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mcOfferPoints');a.store(4);a.missing(4,done)
    path(a,1,'mData','ExtraInfo','OfferPoints');a.store(0);money(a,done,'totalHoursOffer')
    a.reg(2);a.number(1);a.reg(4);a.call('SetLabel')
    # Native Draw lays out the offer wallet before this suffix changes its
    # label. Repeat only its verified offer-side geometry, with the new width;
    # the scouting-hours/background/bonus-hours values remain untouched.
    for name in ('mcOfferBackground','mcHoursBackground','mcOfferIcon'):
        path(a,1,name);a.store(0);a.missing(0,done)
    a.number(0);path(a,1,'mcOfferIcon');a.string('GetWidth');a.raw(0x52)
    a.number(0);path(a,1,'mcOfferPoints');a.string('GetWidth');a.raw(0x52,0x47)
    path(a,1,'PADDING_OFFER');a.number(2);a.raw(0x0C,0x47)
    path(a,1,'PADDING_TEXT');a.raw(0x47);a.number(1);path(a,1,'mcOfferBackground');a.call('SetWidth')
    path(a,1,'mcOfferBackground');a.string('_x');path(a,1,'mcHoursBackground','_x')
    a.number(0);path(a,1,'mcOfferBackground');a.string('GetWidth');a.raw(0x52,0x0B)
    a.number(12);a.raw(0x0B,0x4F)
    path(a,1,'mcOfferIcon');a.string('_x');path(a,1,'mcOfferBackground','_x')
    path(a,1,'PADDING_OFFER');a.raw(0x47,0x4F)
    path(a,1,'mcOfferPoints');a.string('_x');path(a,1,'mcOfferIcon','_x')
    a.number(0);path(a,1,'mcOfferIcon');a.string('GetWidth');a.raw(0x52,0x47)
    path(a,1,'PADDING_TEXT');a.raw(0x47,0x4F)
    a.label(done);a.ret()


GROUPS={
    'programs':(ASSET,[(OFFSET,ARGC,REGISTERS,FLAGS,SIZE,HASH,suffix)]),
    'recruitingPrograms':(RECRUITING_ASSET,[
        (0x4D58,0,7,41,314,0x34D3F102CB6B4D73,recruiting_wallet_suffix),
        (0x2C518,0,18,25,4524,0x0405A0D30750AD1F,recruit_list_offer_suffix),
        (0x37668,0,5,25,419,0x73484EDB978C539D,total_hours_offer_suffix),
    ])
}


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Native Dynasty topbar currency label only; numeric source remains unchanged.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"',
           'namespace recruitingfog::currencytopbarui {']
    count=0
    for group,(asset,specs) in GROUPS.items():
        apt=load(asset)
        lines.append(f'inline std::vector<notesui::Program> {group}(){{std::vector<notesui::Program> result;')
        for offset,argc,registers,flags,size,hash_,builder in specs:
            native_header=apt.data[offset:offset+48]
            if struct.unpack_from('<IHH',native_header,8)!=(argc,registers,flags) or struct.unpack_from('<I',native_header,24)[0]!=size:
                raise ValueError('Unsupported native currency frame '+builder.__name__)
            if fnv(apt.data[offset+48:offset+48+size])!=hash_:raise ValueError('Unsupported native currency body '+builder.__name__)
            a=Assembler();a.code.extend(bytes(size));builder(a);p=a.finish()
            if len(p.code)>32768:raise ValueError('Currency adapter exceeds bytecode bound')
            code='{'+','.join(hex(v) for v in p.code)+'}'
            lines.append(f'result.push_back({{{offset},{argc},{registers},{flags},{size},{hash_}ull,{registers},0,{size},{code}}});')
            for at in p.dollar_offsets:lines.append(f'result.back().dollarOffsets.push_back({at});')
            for at,literal in p.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(literal)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
            count+=1
        lines.append('return result;}')
    lines.append('}')
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'currencyMethods':count,'nativeRegisterFramesPreserved':True}))


if __name__=='__main__':generate(ROOT/'Source/CurrencyTopbarUiPrograms.h')
