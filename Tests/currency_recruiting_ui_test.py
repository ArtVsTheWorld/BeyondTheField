"""Recruiting money surfaces must preserve targets, hours, offers and sources."""
from dataclasses import replace
from pathlib import Path
import copy
import math
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from build_recruit_notes_ui import Assembler,fnv
from build_currency_topbar_ui import (GROUPS,RECRUITING_ASSET,generate,
    recruiting_wallet_suffix,recruit_list_offer_suffix,total_hours_offer_suffix)
from recruit_notes_vm import Machine,UNDEFINED

GLOBALS={'Math':{'round':lambda value:math.floor(value+.5),'floor':math.floor},
         'art_styleguide':{'Font':{'RESIZE_SCALEDOWN':4}}}


def program(builder,enabled):
    a=Assembler();builder(a);p=a.finish();code=bytearray(p.code)
    for at in p.dollar_offsets:code[at]=int(enabled)
    return replace(p,code=bytes(code))


def text(value):
    result={'mData':{'display':str(value),'ExtraInfo':{'font':'native','fontColor':123}},'calls':[],'extraCalls':[],'_x':0}
    def set_label(v):result['mData']['display']=str(v);result['calls'].append(v)
    def extra(v):result['mData']['ExtraInfo'].update(v);result['extraCalls'].append(dict(v))
    def width():
        natural=len(str(result['mData']['display']))*result.get('charWidth',8)
        style=result['mData']['ExtraInfo']
        return min(natural,style['resizeWidth']) if style.get('resize')==4 else natural
    result.update(SetLabel=set_label,GetWidth=width,SetExtraInfo=extra)
    return result


def background(width,x=0):
    result={'width':width,'_x':x}
    result.update(GetWidth=lambda:result['width'],SetWidth=lambda v:result.update(width=v))
    return result


CASES=[(0,'0'),(0.0,'0'),('0','0'),(15,'60K'),(75,'300K'),(220,'880K'),
       (250,'1.0M'),(1000,'4.0M'),('10,630','42.5M'),(-10,'-40K')]
for value,expected in CASES:
    for enabled in (True,False):
        data={'programPoints':value,'currentTargets':1,'maxTargets':35,'currentHours':480,'maxHours':480,'currentScholarships':0,'maxScholarships':35}
        model={'mPreviousProgramPoints':value,'mWalletProgramPoints':text(value),
               'mWalletTargets':text('1/35'),'mWalletHours':text('480/480'),'mWalletScholarships':text('0/35'),
               'mPreviousScholarships':0,'nativeResponse':data}
        before=copy.deepcopy(data)
        Machine(GLOBALS,[]).run(program(recruiting_wallet_suffix,enabled),{1:model})
        assert model['mWalletProgramPoints']['mData']['display']==(expected if enabled else str(value))
        assert model['mPreviousProgramPoints']==value and data==before
        for name,original in [('mWalletTargets','1/35'),('mWalletHours','480/480'),('mWalletScholarships','0/35')]:
            assert model[name]['mData']['display']==original and model[name]['calls']==[]

        for builder,field,target in [(recruit_list_offer_suffix,'CurrentNILOffer','mcPoints'),(total_hours_offer_suffix,'OfferPoints','mcOfferPoints')]:
            data={'ExtraInfo':{field:value,'HoursTotal':40,'MaxHours':50,'BonusHours':5,'PercentageScouted':40}}
            model={'mData':data,target:text(value),'mcHours':text('40/50'),'mcBonusHours':text('+5'),
                   'mcOfferIcon':background(18),'mcOfferBackground':background(40),'mcHoursBackground':background(100,-80),
                   'PADDING_OFFER':8,'PADDING_TEXT':6}
            before=copy.deepcopy(data)
            Machine(GLOBALS,[]).run(program(builder,enabled),{1:model})
            assert model[target]['mData']['display']==(expected if enabled else str(value))
            assert model['mcHours']['mData']['display']=='40/50' and model['mcHours']['calls']==[]
            assert model['mcBonusHours']['mData']['display']=='+5' and model['mcBonusHours']['calls']==[]
            assert data==before and model[target]['mData']['ExtraInfo']=={'font':'native','fontColor':123}
            assert model['mcHoursBackground']['width']==100 and model['mcHoursBackground']['_x']==-80
            if builder==total_hours_offer_suffix and enabled:
                width=18+len(expected)*8+8*2+6
                assert model['mcOfferBackground']['width']==width
                assert model['mcOfferBackground']['_x']==-80-width-12
                assert model['mcOfferIcon']['_x']==model['mcOfferBackground']['_x']+8
                assert model[target]['_x']==model['mcOfferIcon']['_x']+18+6

for value in (None,UNDEFINED,'',' ','?','Hidden','$0','$40K','$1.0M','40K','1.0M','NaN','Infinity',float('nan'),float('inf')):
    for builder,receiver,target in (
        (recruiting_wallet_suffix,{'mPreviousProgramPoints':value,'mWalletProgramPoints':text('native')},'mWalletProgramPoints'),
        (recruit_list_offer_suffix,{'mData':{'ExtraInfo':{'CurrentNILOffer':value}},'mcPoints':text('native')},'mcPoints'),
        (total_hours_offer_suffix,{'mData':{'ExtraInfo':{'OfferPoints':value}},'mcOfferPoints':text('native')},'mcOfferPoints'),
    ):
        Machine(GLOBALS,[]).run(program(builder,True),{1:receiver})
        assert receiver[target]['calls']==[],(builder.__name__,value,receiver)
for builder in (recruiting_wallet_suffix,recruit_list_offer_suffix,total_hours_offer_suffix):
    for receiver in ({},{'mData':{}},{'mData':{'ExtraInfo':{}}}):
        Machine(GLOBALS,[]).run(program(builder,True),{1:receiver})


def board_row(value=40,color=123,name_width=190):
    points=text(value);points['charWidth']=16
    points['mData']['ExtraInfo'].update(resize=0,resizeWidth=500,maxNumLines=1,fontColor=color)
    icon=background(26,-len(str(value))*16-26-4);icon.update(color='native-green',asset='program-points')
    name=background(name_width,71);name.update(display='L. Callen',fontColor=color)
    return {'mData':{'ExtraInfo':{'CurrentNILOffer':value,'HoursTotal':40,'UserRanking':1,'Stars':3}},
            'mcPoints':points,'mcPointsIcon':icon,'mcPointsContainer':{'_x':414,'_visible':True},
            'mCoordFarLeftIcon':332,'mcName':name,
            'mcHours':text('40'),'mcHoursIcon':background(18,360),
            'mcPosition':{'display':'QB','_x':20},'mcUserRanking':{'display':'1','_x':20},
            'mcFlags':{'_x':332,'offered':True,'visited':False,'scouted':40}}


for color in [0,123]: # native selected black and unselected light text
    for value,expected in [(5,'20K'),(40,'160K'),(250,'1.0M'),(10630,'42.5M')]:
        row=board_row(value,color);points=row['mcPoints'];icon=row['mcPointsIcon']
        original_data=copy.deepcopy(row['mData']);original_icon_x=icon['_x']
        original_style=dict(points['mData']['ExtraInfo'])
        others={key:copy.deepcopy(row[key]) for key in ['mcHours','mcHoursIcon','mcName','mcPosition','mcUserRanking','mcFlags','mcPointsContainer']}
        Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
        assert points['mData']['display']==expected
        assert points['mData']['ExtraInfo']['fontColor']==color
        assert points['mData']['ExtraInfo']['font']=='native'
        assert points['mData']['ExtraInfo']['resizeWidth']==52
        assert row['mcPointsContainer']['_x']+icon['_x']==332
        text_left=row['mcPointsContainer']['_x']+points['_x']-points['GetWidth']()
        icon_right=row['mcPointsContainer']['_x']+icon['_x']+icon['width']
        assert icon_right+4<=text_left and row['mcPointsContainer']['_x']+points['_x']==414
        assert icon['color']=='native-green' and icon['asset']=='program-points'
        calls=(len(points['calls']),len(points['extraCalls']))
        for _ in range(50):Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
        assert (len(points['calls']),len(points['extraCalls']))==calls,'Unchanged board row repainted'
        for key,old in others.items():assert row[key]==old,(key,row[key],old)
        assert row['mData']==original_data
        # Native focus/unfocus may update color independently while fit stays
        # active; the money suffix must never overwrite those colors.
        points['mData']['ExtraInfo']['fontColor']=987
        Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
        assert (len(points['calls']),len(points['extraCalls']))==calls
        Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,False),{1:row})
        assert points['mData']['display']==str(value) and icon['_x']==original_icon_x
        assert points['mData']['ExtraInfo']=={**original_style,'fontColor':987}
        assert row['mDERecruitOfferFit'] is UNDEFINED
        Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
        assert points['mData']['display']==expected

# A long name gets its measured native width protected; even the currency icon
# stays to its right. The label keeps its original right edge and scales down.
row=board_row(name_width=260)
Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
assert row['mcPoints']['mData']['ExtraInfo']['resizeWidth']==45
assert row['mcPointsContainer']['_x']+row['mcPointsIcon']['_x']==71+260+8

# The native prefix has already positioned its raw-point icon. A deferred text
# renderer need not expose fresh formatted-text metrics to the suffix: neither
# first fit nor the unchanged fast path calls the points label's GetWidth.
row=board_row();native_measure=row['mcPoints']['GetWidth']
def unavailable_formatted_metrics():raise AssertionError('Formatted text width requested before deferred Draw')
row['mcPoints']['GetWidth']=unavailable_formatted_metrics
Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
for _ in range(50):Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
# Same-instance Off also uses the captured native icon baseline; it must not
# request a just-restored raw text width while a text Draw is still deferred.
original_icon_x=-len('40')*16-26-4
Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,False),{1:row})
assert row['mcPoints']['mData']['display']=='40' and row['mcPointsIcon']['_x']==original_icon_x
row['mcPoints']['GetWidth']=native_measure
Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
assert row['mcPointsIcon']['_x']+26+4<=row['mcPoints']['_x']-native_measure()

# A stale getter returning the old fitted-dollar width must likewise have no
# effect on Off, including exact icon-anchor and image-width deltas.
row=board_row(10630);native_icon_x=row['mcPointsIcon']['_x']
Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
stale_width=row['mcPoints']['GetWidth']();row['mcPoints']['GetWidth']=lambda:stale_width
row['mcPoints']['_x']=-4;row['mcPointsIcon']['width']=24
Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,False),{1:row})
assert row['mcPoints']['mData']['display']=='10630'
assert row['mcPointsIcon']['_x']==native_icon_x-4-(24-26)

# Amount/geometry/native overrides refresh and then settle, rather than using
# stale fit state. A native text color update alone requires no style setter.
for route,value in [
    (('mData','ExtraInfo','CurrentNILOffer'),75),
    (('mcPointsContainer','_x'),424),
    (('mcPoints','_x'),-4),
    (('mcPointsIcon','width'),24),
    (('mcName','width'),260),
    (('mcPoints','mData','ExtraInfo','resizeWidth'),80),
    (('mcPointsIcon','_x'),-70),
    (('mcPoints','mData','display'),'40'),
]:
    row=board_row();Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
    target=row
    for key in route[:-1]:target=target[key]
    target[route[-1]]=value
    points=row['mcPoints'];before=(len(points['calls']),len(points['extraCalls']))
    Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
    assert (len(points['calls']),len(points['extraCalls']))!=before,route
    settled=(len(points['calls']),len(points['extraCalls']))
    Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,True),{1:row})
    assert (len(points['calls']),len(points['extraCalls']))==settled,route
    left=row['mcPointsContainer']['_x']+row['mcPointsIcon']['_x']
    assert left>=max(row['mCoordFarLeftIcon'],row['mcName']['_x']+row['mcName']['width']+8)
    assert row['mcPointsIcon']['_x']+row['mcPointsIcon']['width']+4<=points['_x']-points['GetWidth']()

# A newly default-Off row retains the complete native appearance and geometry.
row=board_row();style=copy.deepcopy(row['mcPoints']['mData']);icon_x=row['mcPointsIcon']['_x']
Machine(GLOBALS,[]).run(program(recruit_list_offer_suffix,False),{1:row})
assert row['mcPoints']['mData']==style and row['mcPointsIcon']['_x']==icon_x
assert not row['mcPoints']['calls'] and not row['mcPoints']['extraCalls']

sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load
apt=load(RECRUITING_ASSET)
for offset,argc,regs,flags,size,hash_,builder in GROUPS['recruitingPrograms'][1]:
    header=apt.data[offset:offset+48];body=apt.data[offset+48:offset+48+size]
    assert struct.unpack_from('<IHH',header,8)==(argc,regs,flags)
    assert struct.unpack_from('<I',header,24)[0]==size and fnv(body)==hash_
    class Bounded(Assembler):
        def reg(self,n):assert n<regs;super().reg(n)
        def store(self,n):assert n<regs;super().store(n)
    a=Bounded();builder(a);assert len(a.finish().code)+size<32768
    if builder==recruiting_wallet_suffix:
        pool=apt.decode(0x40E8)[0][2]
        assert pool.index('programPoints')==156 and pool.index('mWalletProgramPoints')==71 and pool.index('mPreviousProgramPoints')==170
        assert bytes.fromhex('b902af9c') in body # native response.programPoints
        assert bytes.fromhex('b901af47b2a1') in body # wallet.SetLabel
        assert bytes.fromhex('b901a2aab9034f') in body # cache programPoints unchanged
    elif builder==recruit_list_offer_suffix:
        assert bytes.fromhex('b901ac03e082cc') in body # mData.ExtraInfo.CurrentNILOffer
        assert bytes.fromhex('b901af6eb2ea') in body # mcPoints.SetLabel
    else:
        assert bytes.fromhex('b901ac03451443') in body # mData.ExtraInfo.OfferPoints
        assert bytes.fromhex('b901af22b250') in body # mcOfferPoints.SetLabel
        assert bytes.fromhex('b901af3e') in body # native offer background
with tempfile.TemporaryDirectory() as folder:
    out=Path(folder)/'header.h';generate(out)
    assert out.read_bytes()==(ROOT/'Source/CurrencyTopbarUiPrograms.h').read_bytes()
print('Passed: Recruiting remaining budget, board offers and scouting offer wallet; current native sources/frames; no currency symbol; unchanged hours/targets/scholarships/source amounts; native offer-wallet geometry; preformatted and invalid-value rejection.')
