"""Fresh display cells in the named legacy in-game depth chart only."""
from build_player_card_ui import path,numeric_grade,palette

SHEET='Player - DepthChart Slotted'
ATTRIBUTES=('SPD','ACC','AGI','COD','STR','AWR','CAR','BCV','BTK','TRK','SFA',
            'SPM','JKM','CTH','CIT','SPC','SRR','MRR','DRR','RLS','JMP','THP',
            'SAC','MAC','DAC','RUN','TUP','BSK','PAC','PBK','PBP','PBF','RBK',
            'RBP','RBF','LBK','IBL','PRC','TAK','POW','BSH','FMV','PMV','PUR',
            'MCV','ZCV','PRS','RET','KPW','KAC','STA','TGH','INJ','LSP')


def named_sheet(a,done):
    path(a,1,'mSpreadsheetId');a.string(SHEET);a.raw(0x66);a.branch(done,0xB8)


def columns_suffix(a):
    # r13 is the native fresh result. Cache a private presentation-only mask,
    # never change its columns, widths, order, native sort or row identity.
    done='depthColumnsReturn'
    named_sheet(a,done)
    a.reg(1);a.string('DEPauseRatingColumns');a.raw(0x76,0x4F)
    a.missing(13,done)
    path(a,13,'length');a.number(6);a.raw(0x48);a.branch(done)
    path(a,13,'length');a.number(90);a.raw(0x67);a.branch(done)
    for i,names in enumerate([('Slot','SLOT'),('Player','PLAYER'),('POS','Pos'),('OVR','Ovr'),('Year','YEAR')]):
        a.reg(13);a.number(i);a.raw(0x4E);a.store(3);a.missing(3,done)
        path(a,3,'mHeaderText');a.store(3)
        for name in names:a.reg(3);a.string(name);a.raw(0x66);a.branch('depthPrefix'+str(i))
        a.branch(done,0x99);a.label('depthPrefix'+str(i))
    a.number(0);a.raw(0x42);a.store(5);a.number(0);a.store(2)
    a.label('depthColumnLoop')
    a.reg(2);path(a,13,'length');a.raw(0x48);a.branch('depthColumnsReady',0xB8)
    a.reg(13);a.reg(2);a.raw(0x4E);a.store(3);a.missing(3,'depthColumnFalse')
    a.reg(2);a.number(3);a.raw(0x66);a.branch('depthColumnTrue')
    a.reg(2);a.number(5);a.raw(0x48);a.branch('depthColumnFalse')
    path(a,3,'mHeaderText');a.store(3)
    for name in ATTRIBUTES:a.reg(3);a.string(name);a.raw(0x66);a.branch('depthColumnTrue')
    a.label('depthColumnFalse');a.raw(0x74);a.branch('depthColumnStore',0x99)
    a.label('depthColumnTrue');a.raw(0x73)
    a.label('depthColumnStore');a.number(1);a.reg(5);a.call('push')
    a.reg(2);a.raw(0x50);a.store(2);a.branch('depthColumnLoop',0x99)
    a.label('depthColumnsReady');a.reg(1);a.string('DEPauseRatingColumns');a.reg(5);a.raw(0x4F)
    a.label(done);a.reg(13);a.raw(0x3E)


def canonical_rating(a,value,scratch,done,prefix):
    a.reg(value);a.raw(0x44);a.string('string');a.raw(0x66);a.branch(prefix+'numeric',0xB8)
    path(a,value,'length');a.number(1);a.raw(0x48);a.branch(done)
    path(a,value,'length');a.number(3);a.raw(0x67);a.branch(done)
    path(a,value,'length');a.number(1);a.raw(0x67);a.branch(prefix+'leading')
    a.branch(prefix+'digits',0x99)
    a.label(prefix+'leading');a.number(0);a.number(1);a.reg(value);a.string('charAt');a.raw(0x52)
    a.string('0');a.raw(0x66);a.branch(done)
    a.label(prefix+'digits');a.number(0);a.store(scratch)
    a.label(prefix+'digitLoop');a.reg(scratch);path(a,value,'length');a.raw(0x48);a.branch(prefix+'convert',0xB8)
    for edge,op in [('0',0x48),('9',0x67)]:
        a.reg(scratch);a.number(1);a.reg(value);a.string('charAt');a.raw(0x52);a.string(edge);a.raw(op);a.branch(done)
    a.reg(scratch);a.raw(0x50);a.store(scratch);a.branch(prefix+'digitLoop',0x99)
    a.label(prefix+'convert');a.reg(value);a.raw(0x4A);a.store(value)
    a.label(prefix+'numeric');numeric_grade(a,value,value,done,prefix+'grade')


def rows_suffix(a):
    # GetRowData has already made fresh display/trend/rating cells in r3.
    # r5 contains the requested semantic column IDs; retain every numeric
    # rating/trend/source value and modify only each returned display string.
    done='depthRowsReturn'
    named_sheet(a,done)
    path(a,1,'DEPauseRatingColumns');a.store(0);a.missing(0,done)
    a.missing(3,done);a.missing(5,done);a.number(0);a.store(2)
    a.label('depthRowLoop');a.reg(2);path(a,3,'length');a.raw(0x48);a.branch(done,0xB8)
    a.reg(2);path(a,5,'length');a.raw(0x48);a.branch(done,0xB8)
    a.reg(2);a.number(90);a.raw(0x48);a.branch(done,0xB8)
    a.reg(0);a.reg(5);a.reg(2);a.raw(0x4E,0x4E,0x73,0x66);a.branch('depthRowNext',0xB8)
    a.reg(3);a.reg(2);a.raw(0x4E);a.store(4);a.missing(4,'depthRowNext')
    path(a,4,'display');a.store(6)
    # r0 is scratch while parsing; restore the cached mask before next cell.
    canonical_rating(a,6,0,'depthRowNext','depthRowRating')
    a.reg(4);a.string('display');a.reg(6);a.raw(0x4F)
    a.set_field(4,'DEPausePlayerRating',True)
    palette(a,6,0,'depthRowNext','depthRowPalette')
    a.reg(0);a.number(0);a.raw(0x48);a.branch('depthRowNext')
    a.reg(4);a.string('DEPauseGradeColor');a.reg(0);a.raw(0x4F)
    a.label('depthRowNext');path(a,1,'DEPauseRatingColumns');a.store(0)
    a.reg(2);a.raw(0x50);a.store(2);a.branch('depthRowLoop',0x99)
    a.label(done);a.reg(3);a.raw(0x3E)


def color_prefix(a):
    # Native special-color GetCellColor is the unfocused callback. Its
    # highlight colors remain native. Non-rating tables fall straight through
    # to an exact copied original body with its original branch structure.
    fallback='depthColorNative'
    a.grade_scale();a.number(4);a.raw(0x66);a.branch(fallback)
    named_sheet(a,fallback)
    path(a,1,'DEPauseRatingColumns');a.store(0);a.missing(0,fallback)
    a.reg(0);a.reg(8);a.raw(0x4E,0x73,0x66);a.branch(fallback,0xB8)
    a.reg(8);a.number(1);a.raw(0x42);a.reg(7);a.number(2);a.reg(1);a.string('GetRowData');a.raw(0x52);a.store(0)
    a.missing(0,fallback);a.reg(0);a.number(0);a.raw(0x4E);a.store(0);a.missing(0,fallback)
    path(a,0,'DEPausePlayerRating');a.raw(0x73,0x66);a.branch(fallback,0xB8)
    path(a,0,'DEPauseGradeColor');a.raw(0x3E)
    a.label(fallback);a.pad_code()


# offset,argc,regs,flags,size,FNV,suffix/prefix,copy length
SPECS=[(0x107490,0,14,41,279,0x2A37DE785A696AE5,columns_suffix,276),
       (0x107278,2,7,41,223,0xA23A1FA01042BB68,rows_suffix,220),
       (0x107C88,2,9,25,376,0xFD18CCE92BCB6E64,color_prefix,376)]
