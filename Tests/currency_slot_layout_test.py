"""Native Class & NIL text fitting; source values and adjacent slots stay intact."""
from pathlib import Path
from dataclasses import replace
import copy, math, sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
from build_currency_ui import info_slot_suffix
from build_recruit_notes_ui import Assembler
from recruit_notes_vm import Machine, UNDEFINED


def program(on=True):
    a = Assembler(); info_slot_suffix(a); p = a.finish(); code = bytearray(p.code)
    for at in p.dollar_offsets: code[at] = int(on)
    return replace(p, code=bytes(code))


globals_ = {
    'Math': {'round': lambda n: math.floor(n + .5), 'floor': math.floor},
    'shared_enum': {'fblibraries': {'global': {'Icons': {
        'LIBRARY_ID': 7, 'ASSETID_ICON_CURRENCY_PROGRAMPOINTS': 19}}}},
    'art_styleguide': {'Font': {'RESIZE_SCALEDOWN': 4}},
}


def fixture(year='SR (RS)', points=295, slot_width=210, currency_x=122):
    # Native InfoSlotsItemWidget owns the class text and the separate money
    # child. Its Draw already resolved x from class.GetWidth() +17 padding.
    native_style = {'fontColor': 0xE0DCD2, 'size': 26, 'vAlign': 'center',
                    'forceCaps': True, 'font': 'SPEC_NUMBER_8',
                    'resize': 0, 'resizeWidth': 500, 'maxNumLines': 1}
    calls = {'label': [], 'extra': [], 'width': [], 'clone': []}
    style = native_font_style(native_style, calls['clone'])
    source = {'Width': slot_width, 'Height': 48, 'display': 'Class & NIL',
              'ExtraInfo': {'UseCurrencyValue': True, 'CurrencyValue': points,
                            'CurrencyIconId': 19, 'CurrencyIconLibrary': 7}}
    child_data = {'value': '7/19', 'display': points, 'Width': 164,
                  'ExtraInfo': {'IconSize': 32, 'TextPadding': 0,
                                'LabelTextStyle': style, 'IconColor': 0xE0DCD2,
                                'FixedWidth': False}}
    currency = {'_x': currency_x, '_y': 6, 'mData': child_data,
                'mcImage': {'asset': '7/19', '_width': 32, 'color': 0xE0DCD2}}
    def extra(value):
        calls['extra'].append(value)
        child_data['ExtraInfo'].update(value)
    def width(value):
        calls['width'].append(value); child_data['Width'] = value
    def label(value):
        calls['label'].append(value); child_data['display'] = value
    currency.update(SetLabel=label, SetExtraInfo=extra, SetWidth=width)
    receiver = {'mData': source, 'mcInfoSlotValue': {'label': year + ' |'},
                'mcCurrencyValue': currency,
                'heightWeight': {'label': '6\' 3" | 300 lbs', 'x': slot_width + 10}}
    return receiver, calls, native_style


def native_font_style(data, clone_calls=None):
    # A native TextStyle.CloneAndModify clones its actual receiver, including
    # changes to that style since the previous clone (not a closed-over base).
    style = {k: v for k, v in data.items() if k != 'CloneAndModify'}
    def clone(extra):
        if clone_calls is not None: clone_calls.append(dict(extra))
        return native_font_style({**style, **extra}, clone_calls)
    style['CloneAndModify'] = clone
    return style


def style_values(style):
    return {k: v for k, v in style.items() if k != 'CloneAndModify'}


for year, currency_x in [('FR', 53), ('SO', 58), ('JR', 52), ('SR', 52),
                         ('FR (RS)', 122), ('SO (RS)', 124),
                         ('JR (RS)', 120), ('SR (RS)', 122)]:
    for points, expected in [(10, '40K'), (150, '600K'), (250, '1.0M'),
                             (295, '1.2M'), (9999, '40.0M')]:
        receiver, calls, native_style = fixture(year, points, 210, currency_x)
        source = copy.deepcopy(receiver['mData'])
        year_label = copy.deepcopy(receiver['mcInfoSlotValue'])
        neighbor = copy.deepcopy(receiver['heightWeight'])
        icon = copy.deepcopy(receiver['mcCurrencyValue']['mcImage'])
        for _ in range(3):
            # Repeated parent Draw plus the child's deferred native Draw must
            # reuse the same available space and the cloned original styling.
            Machine(globals_, []).run(program(), {1: receiver})
            child = receiver['mcCurrencyValue']; extra = child['mData']['ExtraInfo']
            label_style = extra['LabelTextStyle']
            assert calls['label'][-1] == expected
            assert label_style['resize'] == 4 and label_style['maxNumLines'] == 1
            assert label_style['resizeWidth'] == 210 - currency_x - 10 - 32
            assert child['mData']['Width'] == 210 - currency_x - 10
            assert extra['FixedWidth'] is True
            for key, value in native_style.items():
                if key not in ['resize', 'resizeWidth', 'maxNumLines']: assert label_style[key] == value
            # The native child's Draw reapplies LabelTextStyle to mcLabel;
            # retaining the cloned style also retains this bound afterward.
            rendered_text_right = currency_x + extra['IconSize'] + extra['TextPadding'] + label_style['resizeWidth']
            assert rendered_text_right == 200 < neighbor['x']
            assert receiver['mData'] == source
            assert receiver['mcInfoSlotValue'] == year_label
            assert receiver['heightWeight'] == neighbor and child['mcImage'] == icon
        assert calls['width'] == [210 - currency_x - 10], 'Unchanged Draw set width again'
        assert calls['label'] == [expected], 'Unchanged Draw formatted the label again'
        assert len(calls['extra']) == 1 and len(calls['clone']) == 1, 'Unchanged Draw cloned/invalidated the style again'

# The fast path is setter/clone free on an unchanged cached widget. Source,
# parent/child geometry and native layout changes must all leave that path.
receiver, calls, _ = fixture()
Machine(globals_, []).run(program(True), {1: receiver})
initial = {name: len(values) for name, values in calls.items()}
for _ in range(50): Machine(globals_, []).run(program(True), {1: receiver})
assert {name: len(values) for name, values in calls.items()} == initial

for path, value, expected_width, expected_text in [
    (('mData', 'ExtraInfo', 'CurrencyValue'), 500, 78, '2.0M'),
    (('mData', 'Width'), 230, 98, '1.2M'),
    (('mcCurrencyValue', '_x'), 112, 88, '1.2M'),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'IconSize'), 24, 78, '1.2M'),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'TextPadding'), 6, 78, '1.2M'),
    (('mcCurrencyValue', 'mData', 'Width'), 180, 78, '1.2M'),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'FixedWidth'), False, 78, '1.2M'),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'LabelTextStyle', 'resize'), 2, 78, '1.2M'),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'LabelTextStyle', 'resizeWidth'), 120, 78, '1.2M'),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'LabelTextStyle', 'maxNumLines'), 2, 78, '1.2M'),
    (('mcCurrencyValue', 'mData', 'display'), 295, 78, '1.2M'),
]:
    receiver, calls, _ = fixture()
    Machine(globals_, []).run(program(True), {1: receiver})
    target = receiver
    for part in path[:-1]: target = target[part]
    target[path[-1]] = value
    before = {name: len(values) for name, values in calls.items()}
    Machine(globals_, []).run(program(True), {1: receiver})
    data = receiver['mcCurrencyValue']['mData']
    assert data['Width'] == expected_width and data['display'] == expected_text, path
    assert len(calls['label']) > before['label'] and len(calls['clone']) > before['clone'], ('Stale fast path', path)
    after = {name: len(values) for name, values in calls.items()}
    Machine(globals_, []).run(program(True), {1: receiver})
    assert {name: len(values) for name, values in calls.items()} == after, ('Refresh did not settle', path)
    if path == ('mData', 'ExtraInfo', 'CurrencyValue'):
        Machine(globals_, []).run(program(False), {1: receiver})
        assert data['display'] == 500, 'Off restored an obsolete point amount'

# Toggle the option on this SAME widget, without recreating it or asking the
# native parent to invalidate the currency field. Width, fit mode, style and
# the numeric point label must all return, then fit again correctly when On.
receiver, calls, native_style = fixture()
child = receiver['mcCurrencyValue']; data = child['mData']
for _ in range(3):
    Machine(globals_, []).run(program(True), {1: receiver})
    assert data['Width'] == 78 and data['display'] == '1.2M'
    Machine(globals_, []).run(program(False), {1: receiver})
    assert data['Width'] == 164 and data['display'] == 295
    assert data['ExtraInfo']['FixedWidth'] is False
    assert style_values(data['ExtraInfo']['LabelTextStyle']) == native_style
    assert child['mDEDollarSlotState'] is UNDEFINED

# Reusing the native slot for a different currency restores only our layout;
# it must no longer apply the dollars transform to the new currency.
Machine(globals_, []).run(program(True), {1: receiver})
receiver['mData']['ExtraInfo']['CurrencyIconId'] = 18
Machine(globals_, []).run(program(True), {1: receiver})
assert data['display'] == 295 and data['Width'] == 164
assert data['ExtraInfo']['FixedWidth'] is False
assert style_values(data['ExtraInfo']['LabelTextStyle']) == native_style

# A native style replacement while On is a new baseline, rather than a reason
# to restore the cached old font/color afterward. Test both style-only refresh
# and a simultaneous native width/fixed-width change.
for replace_width in [False, True]:
    receiver, calls, _ = fixture()
    child = receiver['mcCurrencyValue']; data = child['mData']
    Machine(globals_, []).run(program(True), {1: receiver})
    new_style = {**native_style, 'fontColor': 0x4455AA, 'size': 24,
                 'resize': 2, 'resizeWidth': 700, 'maxNumLines': 2}
    data['ExtraInfo']['LabelTextStyle'] = native_font_style(new_style)
    if replace_width:
        data['Width'] = 180; data['ExtraInfo']['FixedWidth'] = True
    # Native currency refresh already supplied a new numeric value. Cleanup
    # must not write the previous recruit/player's numeric label over it.
    data['display'] = 500; receiver['mData']['ExtraInfo']['CurrencyValue'] = 500
    Machine(globals_, []).run(program(True), {1: receiver})
    assert data['display'] == '2.0M'
    Machine(globals_, []).run(program(False), {1: receiver})
    assert data['Width'] == (180 if replace_width else 164)
    assert data['ExtraInfo']['FixedWidth'] is replace_width
    assert data['display'] == 500
    assert style_values(data['ExtraInfo']['LabelTextStyle']) == new_style

# Native in-place color/font edits must survive too; only the three resize
# fields owned by this suffix are restored on Off.
receiver, calls, _ = fixture()
child = receiver['mcCurrencyValue']; data = child['mData']
Machine(globals_, []).run(program(True), {1: receiver})
data['ExtraInfo']['LabelTextStyle']['fontColor'] = 0xAA7755
data['ExtraInfo']['LabelTextStyle']['size'] = 23
Machine(globals_, []).run(program(False), {1: receiver})
assert style_values(data['ExtraInfo']['LabelTextStyle']) == {**native_style, 'fontColor': 0xAA7755, 'size': 23}

# Native replacement of one of the same resize fields is authoritative too;
# restoration must not blindly put a saved original over that newer value.
receiver, calls, _ = fixture()
data = receiver['mcCurrencyValue']['mData']
Machine(globals_, []).run(program(True), {1: receiver})
data['ExtraInfo']['LabelTextStyle'].update(resize=2, resizeWidth=333, maxNumLines=2)
Machine(globals_, []).run(program(False), {1: receiver})
assert style_values(data['ExtraInfo']['LabelTextStyle']) == {**native_style, 'resize': 2, 'resizeWidth': 333, 'maxNumLines': 2}

# Guard unknown/non-numeric geometry: formatting can still work, but it must
# never alter layout from an unproven width, origin or style. No NaN reaches
# the native text renderer.
for path, value in [
    (('mData', 'Width'), None), (('mData', 'Width'), UNDEFINED),
    (('mData', 'Width'), '210'), (('mData', 'Width'), float('nan')),
    (('mData', 'Width'), float('inf')), (('mData', 'Width'), -1),
    (('mData', 'Width'), 4096), (('mData', 'Width'), 150),
    (('mcCurrencyValue', '_x'), -1), (('mcCurrencyValue', '_x'), None),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'IconSize'), float('nan')),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'TextPadding'), -1),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'LabelTextStyle'), None),
    (('mcCurrencyValue', 'mData', 'ExtraInfo', 'LabelTextStyle'), {'fontColor': 0xFFFFFF}),
]:
    receiver, calls, _ = fixture()
    target = receiver
    for part in path[:-1]: target = target[part]
    target[path[-1]] = value
    Machine(globals_, []).run(program(), {1: receiver})
    assert calls['label'] == ['1.2M']
    assert calls['extra'] == [] and calls['width'] == [], (path, value)

for on, currency in [(False, 19), (True, 18)]:
    receiver, calls, _ = fixture()
    receiver['mData']['ExtraInfo']['CurrencyIconId'] = currency
    Machine(globals_, []).run(program(on), {1: receiver})
    assert not any(calls.values()), 'Disabled/nonmoney widget changed'

print('Passed: native Class & NIL currency bounds, redshirt/nonredshirt and K/M labels, deferred/redraw persistence, original font/color/icon/year/data/neighbor preservation, invalid geometry and default-Off gates.')
