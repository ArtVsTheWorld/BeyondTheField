"""Build scoped player-card label adapters, preserving numeric progression data.

Only custom instructions, native fingerprints and zeroed copy regions are emitted.
Private extracted game assets are read at development time and never distributed.
"""
from pathlib import Path
import json
import sys
from build_recruit_notes_ui import Assembler, fnv, GRADE_COLORS


def path(a, register, *members):
    a.reg(register)
    for member in members:
        a.member(member)


def numeric_grade(a, value, label, done, prefix, team=False, force=False):
    # A strict numeric guard leaves unknown strings/sentinels untouched. Neither
    # the underlying WidgetData.value nor any progression input is replaced.
    a.grade_scale(team);a.number(4);a.raw(0x66);a.branch(prefix+'notBlind',0xB8)
    if not force:
        a.fog_enabled(team);a.number(1);a.raw(0x66);a.branch(prefix+'notBlind',0xB8)
    a.string('–');a.store(label);a.branch(prefix+'ready',0x99)
    a.label(prefix+'notBlind')
    a.reg(value); a.raw(0x44); a.string('number'); a.raw(0x66); a.branch(done, 0xB8)
    a.reg(value); a.reg(value); a.raw(0x66); a.branch(done, 0xB8)
    a.reg(value); a.number(0); a.raw(0x48); a.branch(done)
    a.reg(value); a.number(100); a.raw(0x67); a.branch(done)
    if not force:
        a.fog_enabled(team);a.number(1);a.raw(0x66);a.branch(prefix+'fog')
        a.grade_colors_enabled();a.number(1);a.raw(0x66);a.branch(done,0xB8)
        a.reg(value);a.raw(0x4B);a.store(label);a.branch(prefix+'ready',0x99)
        a.label(prefix+'fog')
    from grade_scales import BANDS
    a.grade_scale(team);a.number(4);a.raw(0x66);a.branch(prefix+'blind')
    for scale in range(1,4):
        a.grade_scale(team);a.number(scale);a.raw(0x66);a.branch(prefix+'scale'+str(scale))
    for scale,bands in enumerate(BANDS):
        if scale:a.label(prefix+'scale'+str(scale))
        for index,(upper,grade) in enumerate(bands[:-1]):
            a.reg(value);a.number(upper);a.raw(0x48);a.branch(prefix+str(scale)+'band'+str(index))
        a.string(bands[-1][1]);a.store(label);a.branch(prefix+'ready',0x99)
        for index,(_,grade) in enumerate(bands[:-1]):
            a.label(prefix+str(scale)+'band'+str(index));a.string(grade);a.store(label);a.branch(prefix+'ready',0x99)
    a.label(prefix+'blind');a.string('–');a.store(label)
    a.label(prefix+'ready')


def numeric_display_grade(a, source, output, done, prefix):
    # Call only for an explicitly scoped player-rating display. Native sources
    # may supply numbers or canonical integer text. Reject formatted statistics,
    # blanks and sentinels instead of coercing arbitrary strings with Number().
    a.reg(source);a.raw(0x44);a.string('string');a.raw(0x66);a.branch(prefix+'Strings')
    numeric_grade(a,source,output,done,prefix+'Numeric');a.branch(prefix+'Ready',0x99)
    a.label(prefix+'Strings')
    for value in range(101):
        a.reg(source);a.string(str(value));a.raw(0x66);a.branch(prefix+'Convert')
    a.branch(done,0x99)
    a.label(prefix+'Convert');a.reg(source);a.raw(0x4A);a.store(output)
    numeric_grade(a,output,output,done,prefix+'TextNumeric')
    a.label(prefix+'Ready')


def palette(a, label, color, done, prefix, numeric_guard=None,team=False):
    from grade_scales import COLORS,BANDS
    a.grade_scale(team);a.number(4);a.raw(0x66);a.branch(prefix+'native')
    for scale in range(1,4):
        a.grade_scale(team);a.number(scale);a.raw(0x66);a.branch(prefix+'scale'+str(scale))
    for scale,bands in enumerate(BANDS):
        if scale:a.label(prefix+'scale'+str(scale))
        for index,(_,grade) in enumerate(bands):
            a.reg(label);a.string(grade);a.raw(0x66);a.branch(prefix+str(scale)+'grade'+str(index))
        a.branch(prefix+str(scale)+'numericEntry',0x99)
        for index,(_,grade) in enumerate(bands):
            a.label(prefix+str(scale)+'grade'+str(index));a.number(COLORS[grade]);a.store(color);a.branch(prefix+'chosen',0x99)
        a.label(prefix+str(scale)+'numericEntry')
        if numeric_guard:
            path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
            path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
            for guard in numeric_guard:
                path(a,1,*guard);a.raw(0x73,0x66);a.branch(prefix+str(scale)+'numericAllowed')
            a.branch(done,0x99)
            a.label(prefix+str(scale)+'numericAllowed')
        a.reg(label);a.raw(0x44);a.string('number');a.raw(0x66);a.branch(prefix+str(scale)+'number')
        # Retain the original on its register until canonical text is checked.
        # Some native focus callbacks intentionally alias label/color register0.
        a.reg(label);a.raw(0x4A,0x4C,0x4B);a.reg(label);a.raw(0x66);a.branch(prefix+str(scale)+'string')
        a.raw(0x17);a.branch(done,0x99)
        a.label(prefix+str(scale)+'string');a.store(color);a.branch(prefix+str(scale)+'numeric',0x99)
        a.label(prefix+str(scale)+'number');a.reg(label);a.store(color)
        a.label(prefix+str(scale)+'numeric')
        a.reg(color);a.reg(color);a.raw(0x66);a.branch(done,0xB8)
        a.reg(color);a.number(0);a.raw(0x48);a.branch(done)
        a.reg(color);a.number(100);a.raw(0x67);a.branch(done)
        for index,(upper,_) in enumerate(bands[:-1]):
            a.reg(color);a.number(upper);a.raw(0x48);a.branch(prefix+str(scale)+'grade'+str(index))
        a.branch(prefix+str(scale)+'grade'+str(len(bands)-1),0x99)
    a.label(prefix+'chosen');a.grade_colors_enabled();a.number(1);a.raw(0x66);a.branch(prefix+'ready')
    a.number(0xF3F0E7);a.store(color)
    a.branch(prefix+'ready',0x99)
    a.label(prefix+'native');a.number(-1);a.store(color)
    a.label(prefix+'ready')


def text_label(a, target, label, color, style, done, prefix,team=False):
    a.missing(target, done)
    # Preserve native colors across scale changes on a reused text child.
    # Native focus/disabled repaints are authoritative whenever they differ
    # from the last color this adapter applied.
    path(a,target,'mData','ExtraInfo','fontColor');a.raw(0x44);a.string('number');a.raw(0x66);a.branch(prefix+'nativeColorReady',0xB8)
    path(a,target,'mData','ExtraInfo','fontColor');path(a,target,'mDEAppliedRatingColor');a.raw(0x66);a.branch(prefix+'nativeColorReady')
    a.reg(target);a.string('mDENativeRatingColor');path(a,target,'mData','ExtraInfo','fontColor');a.raw(0x4F)
    a.label(prefix+'nativeColorReady')
    # Preserve the native text slot width before assigning a longer label.
    path(a,target,'mDERatingWidth');a.raw(0x76,0x49);a.branch(prefix+'widthReady',0xB8)
    path(a,target,'_width');a.raw(0x44);a.string('number');a.raw(0x66);a.branch(prefix+'widthReady',0xB8)
    path(a,target,'_width');a.number(0);a.raw(0x67);a.branch(prefix+'widthReady',0xB8)
    a.reg(target);a.string('mDERatingWidth');path(a,target,'_width');a.raw(0x4F)
    a.label(prefix+'widthReady')
    path(a, target, 'mData'); a.raw(0x76, 0x49); a.branch(prefix+'setlabel')
    path(a, target, 'mData', 'display'); a.reg(label); a.raw(0x66); a.branch(prefix+'color')
    a.label(prefix+'setlabel'); a.reg(label); a.number(1); a.reg(target); a.call('SetLabel')
    a.label(prefix+'color')
    a.reg(color);a.number(0);a.raw(0x48);a.branch(prefix+'blindColor')
    a.grade_scale(team);a.number(0);a.raw(0x66);a.branch(prefix+'nativeFit')
    path(a,target,'mDERatingFitScale');a.grade_scale(team);a.raw(0x66);a.branch(prefix+'setcolor',0xB8)
    a.branch(prefix+'checkColor',0x99)
    a.label(prefix+'nativeFit')
    path(a,target,'mDERatingFitScale');a.raw(0x76,0x49);a.branch(prefix+'checkColor')
    path(a,target,'mDERatingFitScale');a.number(0);a.raw(0x66);a.branch(prefix+'setcolor',0xB8)
    a.label(prefix+'checkColor')
    path(a, target, 'mData'); a.raw(0x76, 0x49); a.branch(prefix+'setcolor')
    path(a, target, 'mData', 'ExtraInfo'); a.raw(0x76, 0x49); a.branch(prefix+'setcolor')
    path(a, target, 'mData', 'ExtraInfo', 'fontColor'); a.reg(color); a.raw(0x66); a.branch(done)
    a.label(prefix+'setcolor')
    a.empty_object(style); a.reg(style); a.string('fontColor'); a.reg(color); a.raw(0x4F)
    for scale in [1,3]:
        a.grade_scale(team);a.number(scale);a.raw(0x66);a.branch(prefix+'fit')
    a.branch(prefix+'applyStyle',0x99)
    a.label(prefix+'fit')
    a.reg(style);a.string('resize');a.global_object('art_styleguide','Font','RESIZE_SCALEDOWN');a.raw(0x4F)
    a.set_field(style,'maxNumLines',1)
    path(a,target,'mDERatingWidth');a.raw(0x76,0x49);a.branch(prefix+'applyStyle')
    a.reg(style);a.string('resizeWidth');path(a,target,'mDERatingWidth');a.raw(0x4F)
    a.label(prefix+'applyStyle')
    a.reg(style); a.number(1); a.reg(target); a.call('SetExtraInfo')
    a.reg(target);a.string('mDERatingFitScale');a.grade_scale(team);a.raw(0x4F)
    a.reg(target);a.string('mDEAppliedRatingColor');a.reg(color);a.raw(0x4F)
    a.branch(done,0x99)
    a.label(prefix+'blindColor')
    path(a,target,'mData','ExtraInfo','fontColor');path(a,target,'mDEAppliedRatingColor');a.raw(0x66);a.branch(prefix+'blindDone',0xB8)
    path(a,target,'mDENativeRatingColor');a.raw(0x44);a.string('number');a.raw(0x66);a.branch(prefix+'blindDone',0xB8)
    a.empty_object(style);a.reg(style);a.string('fontColor');path(a,target,'mDENativeRatingColor');a.raw(0x4F)
    a.reg(style);a.number(1);a.reg(target);a.call('SetExtraInfo')
    a.label(prefix+'blindDone');a.reg(target);a.string('mDEAppliedRatingColor');a.raw(0x76,0x4F)


def value_item_suffix(a, container, scratch, prefix, numeric=True, mark=False, numeric_text=False,team=False):
    # container is a RatingValueItem, whose mcValue is its real text child.
    value, label, color, target, style = range(scratch, scratch+5)
    done = prefix+'done'
    a.missing(container, done)
    path(a, container, 'mData'); a.raw(0x76, 0x49); a.branch(done)
    if numeric_text:
        # Opt in only the two known KickerRange player badges. Mark before
        # checking the value/child so a deferred native SetValue+Draw can apply
        # the same strict conversion when the widget finishes initialization.
        path(a,container,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(prefix+'textExtra',0xB8)
        path(a,container,'mData');a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
        a.label(prefix+'textExtra')
        for field in ['DEPlayerRating','DEPlayerRatingNumericText']:
            path(a,container,'mData','ExtraInfo');a.string(field);a.raw(0x73,0x4F)
    path(a, container, 'mData', 'value'); a.store(value)
    if numeric:
        converter=numeric_display_grade if numeric_text else numeric_grade
        if team:numeric_grade(a,value,label,done,prefix+'grade',team=True)
        else:converter(a, value, label, done, prefix+'grade')
    else:
        a.reg(value); a.store(label)
        a.reg(value);a.raw(0x44);a.string('number');a.raw(0x66);a.branch(prefix+'numericReady',0xB8)
        path(a,1,'mData');a.raw(0x76,0x49);a.branch(prefix+'numericReady')
        path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(prefix+'numericReady')
        for key in ['roster','DEFormationPlayerRatings','DEInjuryPlayerRatings']:
            path(a,1,'mData','ExtraInfo',key);a.raw(0x73,0x66);a.branch(prefix+'numericPlayer')
        a.branch(prefix+'numericReady',0x99)
        a.label(prefix+'numericPlayer');numeric_grade(a,value,label,done,prefix+'nativePlayerGrade')
        a.label(prefix+'numericReady')
    guard=None if numeric else [('mData','ExtraInfo','roster'),('mData','ExtraInfo','DEFormationPlayerRatings'),('mData','ExtraInfo','DEInjuryPlayerRatings')]
    palette(a, label, color, done, prefix+'palette',numeric_guard=guard,team=team)
    if mark:
        path(a,container,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(prefix+'extra',0xB8)
        path(a,container,'mData');a.string('ExtraInfo');a.number(0);a.raw(0x43,0x4F)
        a.label(prefix+'extra');path(a,container,'mData','ExtraInfo');a.string('DEPlayerRating');a.raw(0x73,0x4F)
    path(a, container, 'mcValue'); a.store(target)
    text_label(a, target, label, color, style, done, prefix+'text',team=team)
    a.label(done)


def header_suffix(a):
    path(a, 1, 'mcRatingValueItem'); a.store(24)
    value_item_suffix(a, 24, 25, 'header',mark=True)


def team_module_suffix(a):
    # TeamModuleHorizontal owns exactly three rating badges. Do not alter its
    # stars, rank, records, conference, NIL values or original numeric model.
    for index,widget in enumerate(('mcOVRRating','mcOFFRating','mcDEFRating')):
        done='teamBadgeDone'+str(index)
        path(a,1,widget);a.store(0);a.missing(0,done)
        path(a,0,'mData');a.raw(0x76,0x49);a.branch(done)
        path(a,0,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
        path(a,0,'mData','ExtraInfo');a.string('DETeamRating');a.raw(0x73,0x4F)
        path(a,0,'mData','value');a.store(2)
        numeric_grade(a,2,3,done,'teamBadgeGrade'+str(index),team=True)
        palette(a,3,4,done,'teamBadgePalette'+str(index),team=True)
        path(a,0,'mcValue');a.store(2)
        text_label(a,2,3,4,0,done,'teamBadgeText'+str(index),team=True)
        a.label(done)
    # Same native Draw owns the NIL budget labels. Merge this optional suffix
    # rather than competing with a second adapter for its method definition.
    from build_currency_ui import team_budget_suffix
    team_budget_suffix(a)


def ovr_item_suffix(a):
    # The older OVRItem is used by Select Your Team's Top Players. OFF/DEF
    # captions identify team ratings; an unmarked OVR item is a player rating.
    done='ovrItemDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('ovrItemCaption')
    path(a,1,'mData','ExtraInfo','DEPlayerRating');a.raw(0x73,0x66);a.branch('ovrItemPlayer')
    path(a,1,'mData','ExtraInfo','DETeamRating');a.raw(0x73,0x66);a.branch('ovrItemTeam')
    a.label('ovrItemCaption')
    path(a,1,'mData','display');a.store(2)
    for caption in ['OFF','DEF']:
        a.reg(2);a.string(caption);a.raw(0x66);a.branch('ovrItemTeam')
    a.reg(2);a.string('OVR');a.raw(0x66);a.branch(done,0xB8)
    a.label('ovrItemPlayer');a.set_field(1,'mDEActiveRatingTeam',False)
    path(a,1,'mData','value');a.store(0);numeric_grade(a,0,2,done,'ovrItemPlayerGrade')
    a.branch('ovrItemStyle',0x99)
    a.label('ovrItemTeam');a.set_field(1,'mDEActiveRatingTeam',True);path(a,1,'mData','value');a.store(0);numeric_grade(a,0,2,done,'ovrItemTeamGrade',team=True)
    a.label('ovrItemStyle');palette(a,2,3,done,'ovrItemPalette',team='auto')
    path(a,1,'mcValue');a.store(0);text_label(a,0,2,3,2,done,'ovrItemText',team='auto')
    a.label(done)


def header_event_suffix(a):
    path(a, 1, 'mcRatingValueItem'); a.store(12)
    value_item_suffix(a, 12, 13, 'headerEvent',mark=True)


def rating_value_draw_suffix(a):
    done='ratingDrawDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DETeamRating');a.raw(0x73,0x66);a.branch('ratingDrawTeam')
    path(a,1,'mData','ExtraInfo','DEPlayerRating');a.raw(0x73,0x66);a.branch(done,0xB8)
    a.set_field(1,'mDEActiveRatingTeam',False)
    path(a,1,'mData','value');a.store(0)
    a.grade_scale();a.number(4);a.raw(0x66);a.branch('ratingDrawNormal',0xB8)
    a.fog_enabled();a.number(1);a.raw(0x66);a.branch('ratingDrawNormal',0xB8)
    a.string('–');a.store(2);a.branch('ratingDrawLabel',0x99)
    a.label('ratingDrawNormal')
    path(a,1,'mData','ExtraInfo','DEPlayerRatingNumericText');a.raw(0x73,0x66);a.branch('ratingDrawNumericText')
    a.reg(0);a.raw(0x44);a.string('number');a.raw(0x66);a.branch('ratingDrawNumeric')
    a.reg(0);a.store(2);a.branch('ratingDrawLabel',0x99)
    a.label('ratingDrawNumeric');numeric_grade(a,0,2,done,'ratingDrawGrade')
    a.branch('ratingDrawLabel',0x99)
    a.label('ratingDrawNumericText');numeric_display_grade(a,0,2,done,'ratingDrawTextGrade')
    a.branch('ratingDrawLabel',0x99)
    a.label('ratingDrawTeam');a.set_field(1,'mDEActiveRatingTeam',True);path(a,1,'mData','value');a.store(0)
    numeric_grade(a,0,2,done,'ratingDrawTeamGrade',team=True)
    a.label('ratingDrawLabel');palette(a,2,3,done,'ratingDrawPalette',team='auto')
    path(a,1,'mcValue');a.store(4);text_label(a,4,2,3,5,done,'ratingDrawText',team='auto')
    a.label(done)


def kicker_value_set_suffix(a):
    # Native SetValue directly rewrites mcValue even before the next Draw.
    # Only the two KickerRange badges opt into this four-register suffix.
    done='kickerSetDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DEPlayerRatingNumericText');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mData','value');a.store(0)
    numeric_display_grade(a,0,2,done,'kickerSetGrade');palette(a,2,3,done,'kickerSetPalette')
    path(a,1,'mcValue');a.store(0)
    text_label(a,0,2,3,2,done,'kickerSetText')
    a.label(done);a.ret()


def generic_slider_draw_suffix(a):
    # GenericSlider is shared with progression/settings. Recolor only a
    # private-marked, already-converted player display override; never infer
    # a rating from the shared numeric slider value or skill-group level.
    done='sliderDrawDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DEPlayerRating');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mData','ExtraInfo','RightLabelDisplayOverride');a.store(2)
    palette(a,2,3,done,'sliderDrawPalette')
    path(a,1,'mcRightValue');a.store(4)
    text_label(a,4,2,3,5,done,'sliderDrawText')
    a.label(done)


def formation_parent_suffix(a):
    # Formation Subs supplies a numeric PlayerModule model. Native Draw resets
    # the badge after its parent's Draw; convert only this explicitly marked
    # player's presentation, after that reset, never a shared NIL/stat module.
    done='formationModuleDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DEFormationPlayerRatings');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mData','ExtraInfo','roster');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mData','ExtraInfo','overall');a.store(17)
    numeric_grade(a,17,18,done,'formationModuleGrade')
    path(a,1,'mcInfoSlotAttributes');a.store(17);a.missing(17,'formationModuleBadge')
    path(a,17,'mData');a.raw(0x76,0x49);a.branch('formationModuleBadge')
    path(a,17,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('formationModuleBadge')
    path(a,17,'mData','ExtraInfo');a.string('DEFormationPlayerRatings');a.raw(0x73,0x4F)
    a.label('formationModuleBadge')
    path(a,1,'mcStat');a.store(17);a.missing(17,done)
    path(a,17,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,17,'mData','value');path(a,1,'mData','ExtraInfo','overall');a.raw(0x66);a.branch(done,0xB8)
    value_item_suffix(a,17,18,'formationModuleValue',mark=True)
    a.label(done)


def badge_suffix(a):
    formation_parent_suffix(a)
    # Formation's verified source/value guard owns this badge. Do not let the
    # generic numeric-color path repaint a stale or mismatched formation value.
    path(a,1,'mData');a.raw(0x76,0x49);a.branch('badgeContinue')
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('badgeContinue')
    path(a,1,'mData','ExtraInfo','DEFormationPlayerRatings');a.raw(0x73,0x66);a.branch('badgeDone')
    a.label('badgeContinue')
    # Pause Injury Report uses legacy skillValue data. It owns this private
    # marker; forward it only to that screen's attribute-label renderer. The
    # native module defaults roster=false even for these active players.
    done='injuryAttributesDone'
    path(a,1,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,1,'mData','ExtraInfo','DEInjuryPlayerRatings');a.raw(0x73,0x66);a.branch(done,0xB8)
    path(a,1,'mcInfoSlotAttributes');a.store(17);a.missing(17,done)
    path(a,17,'mData');a.raw(0x76,0x49);a.branch(done)
    path(a,17,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch(done)
    path(a,17,'mData','ExtraInfo');a.string('DEInjuryPlayerRatings');a.raw(0x73,0x4F)
    a.label(done)
    path(a, 1, 'mcStat'); a.store(17)
    # Shared PlayerModule may show NIL/stat values. Only an already-converted
    # exact grade is recolored; this adapter never converts its numeric values.
    value_item_suffix(a, 17, 18, 'badge', numeric=False)
    a.label('badgeDone')


def attributes_suffix(a):
    done='attributesDone'
    path(a, 1, 'mData'); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, 'mData', 'ExtraInfo'); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, 'mData', 'ExtraInfo', 'DEPlayerRating'); a.raw(0x73, 0x66); a.branch(done, 0xB8)
    for index, (source, widget) in enumerate([(('mData', 'value'), 'mcValue'), (('mData', 'ExtraInfo', 'MaxValue'), 'mcMaxValue')]):
        prefix='attribute'+str(index)
        path(a, 1, *source); a.store(0)
        numeric_grade(a, 0, 2, prefix+'done', prefix+'grade')
        palette(a, 2, 3, prefix+'done', prefix+'palette')
        path(a, 1, widget); a.store(4)
        text_label(a, 4, 2, 3, 0, prefix+'done', prefix+'text')
        a.label(prefix+'done')
    a.label(done)


def template_suffix(a):
    # The original function returns WidgetData in r1. Mark only the Skills
    # attributes/info template, not its containers, headers or unrelated UI.
    a.reg(2); a.global_object('fb_shared_enum', 'BindingType', 'ATTRIBUTES'); a.raw(0x66); a.branch('return', 0xB8)
    a.reg(3); a.global_object('fb_shared_enum', 'BindingType', 'INFO'); a.raw(0x66); a.branch('return', 0xB8)
    a.missing(1, 'return')
    path(a, 1, 'ExtraInfo'); a.raw(0x76, 0x49); a.branch('extra', 0xB8)
    a.reg(1); a.string('ExtraInfo'); a.number(0); a.raw(0x43, 0x4F)
    a.label('extra'); path(a, 1, 'ExtraInfo'); a.string('DEPlayerRating'); a.raw(0x73, 0x4F)
    a.label('return'); a.reg(1); a.raw(0x3E)


def group_suffix(a):
    done='groupDone'
    a.missing(1, done); a.missing(2, done)
    path(a, 1, 'ExtraInfo'); a.raw(0x76, 0x49); a.branch(done)
    path(a, 1, 'ExtraInfo', 'Rating'); a.store(3)
    numeric_grade(a, 3, 4, done, 'groupGrade')
    palette(a, 4, 6, done, 'groupPalette')
    a.empty_object(5); a.reg(5); a.string('RightLabelDisplayOverride'); a.reg(4); a.raw(0x4F)
    a.set_field(5,'DEPlayerRating',True)
    # Native slider applies these style objects again on focus changes. Clone
    # each available style and alter only its color, retaining fonts/layout.
    path(a, 2, 'mData'); a.raw(0x76, 0x49); a.branch('groupApply')
    path(a, 2, 'mData', 'ExtraInfo'); a.raw(0x76, 0x49); a.branch('groupApply')
    for index, name in enumerate(('FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle')):
        path(a, 2, 'mData', 'ExtraInfo', name); a.store(7); a.missing(7, 'groupStyle'+str(index))
        a.empty_object(8); a.reg(8); a.string('fontColor'); a.reg(6); a.raw(0x4F)
        a.reg(5); a.string(name); a.reg(8); a.number(1); a.reg(7); a.string('CloneAndModify'); a.raw(0x52, 0x4F)
        a.label('groupStyle'+str(index))
    a.label('groupApply')
    a.reg(5); a.number(1); a.reg(2); a.call('SetExtraInfo')
    a.label(done)


def level_suffix(a):
    numeric_grade(a, 4, 6, 'levelDone', 'levelGrade')
    a.reg(6); a.string('display'); a.number(0); a.number(3)
    path(a, 1, 'mSkillLevelDataProvider'); a.call('UpdateProperty')
    palette(a,6,7,'levelDone','levelPalette')
    a.number(0);a.number(1);path(a,1,'mSkillLevelDataProvider');a.string('GetItemData');a.raw(0x52);a.store(8);a.missing(8,'levelDone')
    path(a,8,'ExtraInfo');a.store(9);a.missing(9,'levelDone')
    a.empty_object(10);a.reg(10);a.string('fontColor');a.reg(7);a.raw(0x4F)
    a.reg(10);a.number(1);a.reg(9);a.string('CloneAndModify');a.raw(0x52);a.store(10)
    a.reg(10);a.string('fontColor');a.reg(7);a.raw(0x4F)
    a.set_field(10,'DEPlayerRating',True)
    a.reg(10);a.string('ExtraInfo');a.number(0);a.number(3)
    path(a,1,'mSkillLevelDataProvider');a.call('UpdateProperty')
    a.label('levelDone')


def subskills_suffix(a):
    # Verified active Ratings renderer: GenericSlider. Leave numeric values,
    # min/max/boost/costs and progression records untouched. Set only its
    # existing right-label display override and cloned value font styles.
    path(a,1,'mSubskillsDataProvider');a.raw(0x76,0x49);a.branch('subskillsDone')
    a.number(0);a.store(2)
    a.label('subskillsLoop')
    a.reg(2);a.number(128);a.raw(0x48);a.branch('subskillsDone',0xB8)
    a.reg(2);a.number(0);path(a,1,'mSubskillsDataProvider');a.string('GetNumItems');a.raw(0x52,0x48);a.branch('subskillsDone',0xB8)
    a.reg(2);a.number(1);path(a,1,'mSubskillsDataProvider');a.string('GetItemData');a.raw(0x52);a.store(3);a.missing(3,'subskillsNext')
    path(a,3,'value');a.store(4);numeric_grade(a,4,5,'subskillsNext','subskillsGrade');palette(a,5,6,'subskillsNext','subskillsPalette')
    path(a,3,'ExtraInfo');a.store(8);a.missing(8,'subskillsNext');a.empty_object(7)
    a.reg(8);a.reg(7);a.number(2);a.global_object('cafe','utility','ObjectUtil');a.call('MergeInto')
    a.reg(7);a.string('RightLabelDisplayOverride');a.reg(5);a.raw(0x4F)
    a.set_field(7,'DEPlayerRating',True)
    for index,name in enumerate(('FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle')):
        path(a,7,name);a.store(8);a.missing(8,'subskillsStyle'+str(index))
        a.empty_object(9);a.reg(9);a.string('fontColor');a.reg(6);a.raw(0x4F)
        a.reg(7);a.string(name);a.reg(9);a.number(1);a.reg(8);a.string('CloneAndModify');a.raw(0x52,0x4F)
        a.label('subskillsStyle'+str(index))
    a.reg(7);a.string('ExtraInfo');a.reg(2);a.number(3);path(a,1,'mSubskillsDataProvider');a.call('UpdateProperty')
    a.label('subskillsNext');a.reg(2);a.raw(0x50);a.store(2);a.branch('subskillsLoop',0x99)
    a.label('subskillsDone')


def attribute_slots_suffix(a):
    a.number(0);a.store(3)
    a.label('slotsLoop');a.reg(3);a.number(6);a.raw(0x48);a.branch('slotsDone',0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch('slotsDone')
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('slotsDone')
    path(a,1,'mData','ExtraInfo');a.string('AttributesData');a.reg(3);a.raw(0x47,0x4E);a.store(4);a.missing(4,'slotsNext')
    path(a,4,'isFullyScouted');a.raw(0x73,0x66);a.branch('slotsNext',0xB8)
    path(a,4,'ratingValue');a.store(5)
    path(a,1,'mData','ExtraInfo','DEInjuryPlayerRatings');a.raw(0x73,0x66);a.branch('slotsInjuryRating')
    a.reg(5);a.raw(0x44);a.string('number');a.raw(0x66);a.branch('slotsExistingGrade',0xB8)
    path(a,1,'mData','ExtraInfo','DEFormationPlayerRatings');a.raw(0x73,0x66);a.branch('slotsNext',0xB8)
    numeric_grade(a,5,5,'slotsNext','slotsFormationGrade')
    a.branch('slotsExistingGrade',0x99)
    a.label('slotsInjuryRating')
    from grade_scales import COLORS
    for grade in COLORS:
        a.reg(5);a.string(grade);a.raw(0x66);a.branch('slotsExistingGrade')
    numeric_display_grade(a,5,5,'slotsNext','slotsInjuryGrade')
    a.label('slotsExistingGrade')
    palette(a,5,6,'slotsNext','slotsPalette')
    a.reg(1);a.string('mcValueSlotText');a.reg(3);a.raw(0x47,0x4E);a.store(7)
    text_label(a,7,5,6,8,'slotsNext','slotsText')
    a.label('slotsNext');a.reg(3);a.raw(0x50);a.store(3);a.branch('slotsLoop',0x99)
    a.label('slotsDone')


def skill_slots_suffix(a):
    a.number(0);a.store(12)
    a.label('skillSlotsLoop');a.reg(12);a.number(6);a.raw(0x48);a.branch('skillSlotsDone',0xB8)
    path(a,1,'mData');a.raw(0x76,0x49);a.branch('skillSlotsDone')
    path(a,1,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('skillSlotsDone')
    path(a,1,'mData','ExtraInfo');a.string('SkillData');a.reg(12);a.raw(0x47,0x4E);a.store(13);a.missing(13,'skillSlotsNext')
    path(a,13,'Rating');a.store(14)
    numeric_grade(a,14,15,'skillSlotsNext','skillSlotsGrade')
    palette(a,15,16,'skillSlotsNext','skillSlotsPalette')
    a.reg(1);a.string('mcSkill');a.reg(12);a.raw(0x47,0x4E);a.store(17);a.missing(17,'skillSlotsNext')
    a.empty_object(18);a.reg(18);a.string('RightLabelDisplayOverride');a.reg(15);a.raw(0x4F)
    a.set_field(18,'DEPlayerRating',True)
    path(a,17,'mData');a.raw(0x76,0x49);a.branch('skillSlotsApply')
    path(a,17,'mData','ExtraInfo');a.raw(0x76,0x49);a.branch('skillSlotsApply')
    for index,name in enumerate(('FocusValueTextStyle','UnfocusValueTextStyle','UnfocusableValueTextStyle')):
        path(a,17,'mData','ExtraInfo',name);a.store(19);a.missing(19,'skillSlotsStyle'+str(index))
        a.empty_object(20);a.reg(20);a.string('fontColor');a.reg(16);a.raw(0x4F)
        a.reg(18);a.string(name);a.reg(20);a.number(1);a.reg(19);a.string('CloneAndModify');a.raw(0x52,0x4F)
        a.label('skillSlotsStyle'+str(index))
    a.label('skillSlotsApply');a.reg(18);a.number(1);a.reg(17);a.call('SetExtraInfo')
    a.label('skillSlotsNext');a.reg(12);a.raw(0x50);a.store(12);a.branch('skillSlotsLoop',0x99)
    a.label('skillSlotsDone')


def append_program(size, suffix, copy_bytes=None):
    a=Assembler(); a.code.extend(bytes(size if copy_bytes is None else copy_bytes))
    suffix(a); a.ret()
    return a.finish()


SPECS={
    'controlPrograms': ('C:/Apps/CFB 27/MMC/AbilityColors/Research/assets/common/ui/art_control/scriptpod.ast', [
        (0x36EB0,0,23,25,6675,0x27B53CDB6D8B7673,23,badge_suffix,None),
        (0x18CC0,0,5,25,1233,0x9DCA6F0E09D88CDA,5,attributes_suffix,None),
        (0x327E8,0,9,25,388,0x45B4DB9AE855957E,9,attribute_slots_suffix,None),
        (0x44BF8,0,12,25,204,0xC3220200E8D796CA,21,skill_slots_suffix,None),
        (0x22150,0,9,25,1730,0x444360923A963AB5,9,rating_value_draw_suffix,None),
        (0x21AF8,1,4,25,20,0x6D730F72E674695B,4,kicker_value_set_suffix,None),
        (0x1CDA8,1,4,25,57,0x78F056F002C47EF3,4,ovr_item_suffix,None)]),
    'sliderPrograms': ('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_com/scriptpod.ast', [
        (0x3EEB0,0,10,25,2587,0xF364EAE7B6CB59CA,10,generic_slider_draw_suffix,None)]),
    'cardPrograms': ('Evidence/PlayerFog/manageplayerart.ast', [
        (0x3038,1,30,41,2224,0xA6909B15969FC597,30,header_suffix,None),
        (0x3EF0,6,18,41,876,0x944C06B02B868F03,18,header_event_suffix,None)]),
    'templatePrograms': ('Evidence/PlayerFog/manageplayer-skills.ast', [
        (0x860,3,4,42,414,0x351678A392FC9086,4,template_suffix,411)]),
    'skillPrograms': ('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_cfm/corenode.ast', [
        (0x54C20,4,3,42,240,0x1A7E5A93BC79FFE4,9,group_suffix,None),
        (0x54E20,2,6,41,100,0x3C700A570F7C0AA9,11,level_suffix,None),
        (0x54EC0,1,8,41,164,0xC40A11F67BBBC449,10,subskills_suffix,None),
        (0x728D0,0,5,25,2002,0xD6E51594B47DB8CD,5,team_module_suffix,None)])}


def generate(destination):
    sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
    from inspect_tb_ast import load
    lines=['// Generated custom label adapters. Native bodies are verified/copied at attachment.',
           '#pragma once','#include "RecruitNotesUiPrograms.h"','namespace recruitingfog::playercardui {']
    methods=0
    for name,(asset,specs) in SPECS.items():
        apt=load(Path(asset)); lines.append(f'inline std::vector<notesui::Program> {name}(){{std::vector<notesui::Program> result;')
        for off,argc,regs,flags,size,expected,newregs,suffix,copy_bytes in specs:
            original=apt.data[off+48:off+48+size]
            if fnv(original)!=expected:raise ValueError(f'Unsupported native player method {asset}:{off:x}')
            count=size if copy_bytes is None else copy_bytes
            program=append_program(size,suffix,copy_bytes)
            code='{'+','.join(hex(b) for b in program.code)+'}'
            lines.append(f'result.push_back({{{off},{argc},{regs},{flags},{size},{expected}ull,{newregs},0,{count},{code}}});')
            if name=='cardPrograms' and off==0x3EF0:
                # Only loader metadata is normalized for the parent-body hash.
                # Every callback instruction/header semantic remains checked.
                for at,name_rva,param_rva in [(0x90,0x61D0,0x61D8),(0x108,0x61F8,0x6200),(0x180,0x6220,0x6228)]:
                    lines.append(f'result.back().nestedDefinitions.push_back({{{at},{name_rva},{param_rva}}});')
            for at in program.color_offsets:lines.append(f"result.back().colorOffsets.push_back({at});")
            for at in program.scale_offsets:lines.append(f"result.back().scaleOffsets.push_back({at});")
            for at in program.team_scale_offsets:lines.append(f"result.back().teamScaleOffsets.push_back({at});")
            for at in program.fog_offsets:lines.append(f"result.back().fogOffsets.push_back({at});")
            for at in program.team_offsets:lines.append(f"result.back().teamOffsets.push_back({at});")
            for at in program.dollar_offsets:lines.append(f"result.back().dollarOffsets.push_back({at});")
            for at,text in program.literals:
                lines.append('{const auto pointer=reinterpret_cast<uintptr_t>('+json.dumps(text)+f');memcpy(result.back().code.data()+{at},&pointer,8);}}')
            methods+=1
        lines.append('return result;}')
    lines.append('}')
    destination.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'playerCardMethods':methods,'numericProgressionPreserved':True}))


if __name__=='__main__':generate(Path('Source/PlayerCardUiPrograms.h'))
