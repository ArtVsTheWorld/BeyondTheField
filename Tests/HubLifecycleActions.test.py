"""Execute the emitted APT subset to check child lifecycle isolation offline."""
from copy import deepcopy
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
from build_hub_lifecycle import scoped_init, scoped_shutdown

UNDEFINED = object()
POOL = {
    10: 'Init', 11: 'GetScreenInfo', 12: 'GetInitParams',
    13: 'MenuInstanceName', 14: 'logic_com', 15: 'enum',
    16: 'Navigation', 17: 'MENU_CAREER', 18: 'SetInitParams',
    19: 'mRestorePrevFocus', 20: 'mAddedFilter',
    22: 'fb_shared_enum', 28: 'BindingType', 29: 'NEWS_CATEGORY',
    34: 'Shutdown', 35: 'mFilterCollection', 36: 'DATAPROVIDER',
    37: 'ClearAllItems',
}


def execute(code, literals, params, initial=None, environment=None):
    """No native execution: reject every opcode outside this known subset."""
    literal_map = dict(literals)
    calls = []
    instance = initial if initial is not None else {
        '_OnServiceTileFocusChanged': object(), '_signals': [], '_timers': {},
        '_events': [], 'mParentNode': 'context-node'}
    noop = instance['_OnServiceTileFocusChanged']
    signals, timers, events = (instance[k] for k in ('_signals', '_timers', '_events'))
    adapter = {'SetFilterChanged': lambda *args: (signals.append(args), events.append(args[1]))}
    def timer_get(context):
        if context != 'context-node':
            raise AssertionError('Timer escaped its native parent context')
        return {
            'ClearInterval': lambda name: (timers.pop(name, None), events.append('clear')),
            'SetInterval': lambda name, callback, delay: (
                timers.update({name: (callback, delay)}), events.append('start')),
        }
    globals_ = {
        'madden': {'Adapters': {'GetPanelMenuAdapter': lambda: adapter}},
        'cafe': {
            'manager': {'IntervalManagerService': {'Get': timer_get}},
            'utility': {'Delegate': {'Bind': lambda receiver, fn, *args: lambda: fn(*args)}},
        },
    }
    if environment is not None:
        globals_['cafe'].update(environment)
    screen = {'GetInitParams': lambda: params}
    screen['SetInitParams'] = lambda value: screen.update(params=value)
    view = {'GetScreenInfo': lambda: screen}
    parent = {
        'Init': lambda *args: (calls.append((args, deepcopy(screen['params']))), events.append('base-init')),
        'Shutdown': lambda *args: (calls.append(args), events.append('base-shutdown')),
    }
    registers = {1: instance, 2: parent, 4: view, 5: 'arg5', 6: 'arg6'}
    stack = []
    pc = 0

    def word():
        nonlocal pc
        pc = (pc + 7) & ~7
        value = struct.unpack_from('<i', code, pc)[0]
        pc += 4
        return value

    while pc < len(code):
        op = code[pc]
        pc += 1
        if op == 0:
            continue
        if op in (0x59, 0x5A, 0x73, 0x74, 0x76):
            stack.append({0x59: 0, 0x5A: 1, 0x73: True,
                          0x74: False, 0x76: UNDEFINED}[op])
        elif op == 0xB5:
            stack.append(code[pc])
            pc += 1
        elif op == 0xB6:
            stack.append(struct.unpack_from('<H', code, pc)[0])
            pc += 2
        elif op == 0xB9:
            stack.append(registers.get(code[pc], UNDEFINED))
            pc += 1
        elif op == 0xA2:
            stack.append(POOL[code[pc]])
            pc += 1
        elif op == 0xA1:
            pc = (pc + 7) & ~7
            stack.append(literal_map[pc])
            pc += 8
        elif op == 0xAD:
            count = code[pc]
            pc += 1
            names = [POOL[n] for n in code[pc:pc + count]]
            pc += count
            if names == ['logic_com', 'enum', 'Navigation', 'MENU_CAREER']:
                stack.append('career-menu-enum')
            elif names == ['fb_shared_enum', 'BindingType', 'NEWS_CATEGORY']:
                stack.append('news-category-enum')
            else:
                raise AssertionError(f'Unexpected global lookup: {names}')
        elif op == 0x87:
            registers[word()] = stack[-1]
        elif op == 0x17:
            stack.pop()
        elif op == 0x1C:
            stack.append(globals_[stack.pop()])
        elif op == 0x43:
            count = stack.pop()
            if count != 0:
                raise AssertionError('Only the native empty-object fallback is expected')
            stack.append({})
        elif op == 0x4E:
            name, receiver = stack.pop(), stack.pop()
            stack.append(receiver.get(name, UNDEFINED))
        elif op == 0xAF:
            receiver = stack.pop()
            stack.append(receiver.get(POOL[code[pc]], UNDEFINED))
            pc += 1
        elif op == 0x4F:
            value, name, receiver = stack.pop(), stack.pop(), stack.pop()
            receiver[name] = value
        elif op == 0x47:
            right, left = stack.pop(), stack.pop()
            stack.append(str(left) + str(right) if isinstance(left, str) or isinstance(right, str) else left + right)
        elif op in (0x49, 0x66):
            right, left = stack.pop(), stack.pop()
            nullish = lambda x: x is UNDEFINED or x is None
            if op == 0x49 and nullish(left) and nullish(right):
                equal = True
            elif isinstance(left, dict) or isinstance(right, dict):
                equal = left is right
            else:
                equal = type(left) is type(right) and left == right
            stack.append(equal)
        elif op in (0xB8, 0x9D, 0x99):
            distance = word()
            take = op == 0x99
            if op != 0x99:
                condition = bool(stack.pop())
                take = condition if op == 0x9D else not condition
            if take:
                pc += distance
        elif op in (0x52, 0xB2):
            if op == 0xB2:
                name = POOL[code[pc]]
                pc += 1
            else:
                name = stack.pop()
            receiver, count = stack.pop(), stack.pop()
            args = [stack.pop() for _ in range(count)]
            result = receiver[name](*args)
            if op == 0x52:
                stack.append(result)
        elif op == 0x3E:
            if stack.pop() is not UNDEFINED:
                raise AssertionError('Init must return undefined')
            break
        else:
            raise AssertionError(f'Unexpected opcode {op:#x} at {pc - 1:#x}')
        if not 0 <= pc <= len(code):
            raise AssertionError('Branch escaped the function body')
    if stack:
        raise AssertionError(f'Unbalanced operand stack: {stack}')
    if environment is not None and 'DynastyEnhancerSocialTimerSerial' in globals_['cafe']:
        environment['DynastyEnhancerSocialTimerSerial'] = globals_['cafe']['DynastyEnhancerSocialTimerSerial']
    return instance, screen.get('params', params), calls, noop


class LifecycleActions(unittest.TestCase):
    def run_init(self, params):
        program = scoped_init()
        return execute(program.code, program.literals, params)

    def test_custom_subscreen_isolated_before_base_init(self):
        params = {'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL',
                  'Keep': 'value', 'BackupState': {'PanelId': 'CM_DYNASTY_SOCIAL',
                  'AllowFocus': True, 'AllowBack': True, 'Scroll': 27}}
        instance, result, calls, noop = self.run_init(params)
        for target in (result, result['BackupState'], calls[0][1]):
            self.assertEqual(target['PanelId'], 'CM_DYNASTY_SOCIAL_FEED')
            self.assertIs(target['AllowFocus'], False)
            self.assertIs(target['AllowBack'], False)
        self.assertIs(instance['_SetMenuVisible'], noop)
        self.assertTrue(instance['mDynastySocialEmbedded'])
        self.assertEqual(instance['_signals'], [('CM_DYNASTY_SOCIAL_FEED', 'SOCIAL_CHILD_ATTACH', 0)])
        self.assertEqual(result['Keep'], 'value')
        self.assertEqual(result['BackupState']['Scroll'], 27)
        self.assertEqual(calls[0][0][0], 'arg6')
        self.assertEqual(calls[0][0][2], 'arg5')
        self.assertFalse(instance['mRestorePrevFocus'])
        self.assertFalse(instance['mAddedFilter'])

    def test_missing_or_null_backup_does_not_create_shared_state(self):
        for backup in (UNDEFINED, None):
            params = {'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'}
            if backup is not UNDEFINED:
                params['BackupState'] = backup
            _, result, _, _ = self.run_init(params)
            self.assertEqual(result['PanelId'], 'CM_DYNASTY_SOCIAL_FEED')
            self.assertIs(result.get('BackupState', UNDEFINED), backup)

    def test_timer_is_context_owned_and_cleared_on_shutdown(self):
        init = scoped_init(timer=True)
        instance, _, _, _ = execute(init.code, init.literals,
            {'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'})
        callback, delay = instance['_timers'][instance['mDynastySocialTimerName']]
        self.assertEqual(delay, 250)
        self.assertEqual(instance['_events'], ['SOCIAL_CHILD_ATTACH', 'base-init', 'clear', 'start'])
        callback()
        self.assertEqual(instance['_signals'][-1], ('CM_DYNASTY_SOCIAL_FEED', 'SOCIAL_SYNC', 0))
        shutdown = scoped_shutdown(timer=True)
        execute(shutdown.code, shutdown.literals, None, initial=instance)
        self.assertFalse(instance['_timers'])
        self.assertFalse(instance['mDynastySocialEmbedded'])
        self.assertEqual(instance['_events'][-3:], ['clear', 'base-shutdown', 'SOCIAL_CHILD_DETACH'])

    def test_overlapping_instances_have_distinct_timer_names(self):
        program = scoped_init(timer=True)
        environment = {}
        names = []
        for _ in range(3):
            instance, _, _, _ = execute(program.code, program.literals,
                {'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'}, environment=environment)
            names.append(instance['mDynastySocialTimerName'])
        self.assertEqual(len(set(names)), 3)

    def test_nonembedded_news_never_registers_a_timer(self):
        program = scoped_init(timer=True)
        instance, _, _, _ = execute(program.code, program.literals, {'PanelId': 'CM_NEWSSUB'})
        self.assertFalse(instance['_timers'])
        self.assertFalse(instance['_signals'])

    def test_other_screens_keep_the_original_init_behavior(self):
        asset = Path(__file__).resolve().parents[2] / 'SocialMedia/Research/assets/common/ui/node_cfm/corenode.ast'
        # AST files are BGFA containers; offsets refer to the decoded Apt Data
        # stream rather than the container/compressed file bytes.
        sys.path.insert(0, 'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
        from inspect_tb_ast import load
        original = load(asset).data[0x24970:0x24970 + 91]
        for params in (None, UNDEFINED, {},
                       {'PanelId': 'CM_DYNASTY_SOCIAL'},
                       {'IsSubscreen': False, 'PanelId': 'CM_DYNASTY_SOCIAL'},
                       {'IsSubscreen': True, 'PanelId': 'STOCK_PANEL'}):
            new = self.run_init(deepcopy(params) if params is not UNDEFINED else params)
            old = execute(original, [], deepcopy(params) if params is not UNDEFINED else params)
            self.assertEqual(new[1], old[1])
            self.assertEqual(len(new[2]), len(old[2]))
            self.assertNotIn('_SetMenuVisible', new[0])
            self.assertNotIn('mDynastySocialEmbedded', new[0])


if __name__ == '__main__':
    unittest.main()
