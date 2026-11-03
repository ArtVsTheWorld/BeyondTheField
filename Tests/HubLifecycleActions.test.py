"""Execute the emitted APT subset to check child lifecycle isolation offline."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
from build_hub_lifecycle import Program, ORIGINAL_INIT, scoped_init, scoped_shutdown
from apt_subset_vm import Machine, UNDEFINED

POOL = {
    10: 'Init', 11: 'GetScreenInfo', 12: 'GetInitParams',
    13: 'MenuInstanceName', 14: 'logic_com', 15: 'enum',
    16: 'Navigation', 17: 'MENU_CAREER', 18: 'SetInitParams',
    19: 'mRestorePrevFocus', 20: 'mAddedFilter',
    22: 'fb_shared_enum', 28: 'BindingType', 29: 'NEWS_CATEGORY',
    34: 'Shutdown', 35: 'mFilterCollection', 36: 'DATAPROVIDER',
    37: 'ClearAllItems',
}


def execute(code, literals, params, initial=None, environment=None, references=None):
    """No native execution: reject every opcode outside this known subset."""
    calls = []
    instance = initial if initial is not None else {
        '_OnServiceTileFocusChanged': lambda *args: None, '_signals': [], '_timers': {},
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
            'utility': {'Delegate': {
                'Bind': lambda receiver, fn, *args: lambda: vm.invoke(fn, receiver, list(args)),
                'Create': lambda receiver, fn: lambda: vm.invoke(fn, receiver, []),
            }},
        },
    }
    switcher_class = instance.setdefault('_switcherClass', (environment or {}).get('switcher_class', object()))
    preview_service = (environment or {}).get('preview_service', {'mHidePanelHandler': {'mListeners': []}})
    globals_['logic_cfm'] = {'service': {'HubInfoPanelsService': {'Get': lambda context: preview_service}}}
    globals_['panelmenu'] = {'service': {'PanelMenuDataService': {'Get': lambda context: {
        'GetCurrentPanelFocus': lambda: (environment or {}).get('focus', 'CM_DYNASTY_SOCIAL')}}}}
    globals_['art_screen'] = {'panel': {'career': {'HubPanelSwitcher': switcher_class}}}
    if environment is not None:
        globals_['cafe'].update(environment)
    screen = {'GetInitParams': lambda: params}
    screen['SetInitParams'] = lambda value: screen.update(params=value)
    header_calls = instance.setdefault('_headerCalls', [])
    real_header = instance.setdefault('_realHeader', {
        'SetState': lambda *args: header_calls.append(('state', args)),
        'SetTitle': lambda *args: header_calls.append(('title', args)),
        'Show': lambda: header_calls.append(('show',)),
        'Hide': lambda: header_calls.append(('hide',)),
        'GetValidDisplayString': lambda: 'Original hub title',
    })
    view = instance.setdefault('_view', {'GetScreenInfo': lambda: screen, 'GetHeader': lambda: real_header,
        'Focus': lambda method: events.append(('focus', method)),
        'Unfocus': lambda method: events.append(('unfocus', method))})
    parent = {
        'Init': lambda *args: (instance.update(mView=view), calls.append((args, deepcopy(screen['params']))), events.append('base-init')),
        'Shutdown': lambda *args: (calls.append(args), events.append('base-shutdown')),
    }
    registers = {1: instance, 2: parent, 4: view, 5: 'arg5', 6: 'arg6'}
    vm = Machine(globals_, POOL)
    result = vm.run(Program(code, literals, references or []), registers)
    if result is not UNDEFINED:
        raise AssertionError('Lifecycle method must return undefined')
    instance['_machine'] = vm
    if environment is not None and 'DynastyEnhancerSocialTimerSerial' in globals_['cafe']:
        environment['DynastyEnhancerSocialTimerSerial'] = globals_['cafe']['DynastyEnhancerSocialTimerSerial']
    return instance, screen.get('params', params), calls, noop


class LifecycleActions(unittest.TestCase):
    def run_init(self, params):
        program = scoped_init()
        return execute(program.code, program.literals, params, references=program.references)

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

    def test_embedded_header_cannot_change_or_hide_the_hub_header(self):
        instance, _, _, _ = self.run_init({'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'})
        view, vm = instance['_view'], instance['_machine']
        facade = vm.invoke(view['GetHeader'], view, [])
        self.assertIsNot(facade, instance['_realHeader'])
        self.assertIs(view['mDynastySocialRealHeader'], instance['_realHeader'])
        self.assertFalse(view['mHideHeaderOnTransitionOut'])
        for name, args in (('SetState', ['title']), ('SetTitle', ['Social Media']),
                           ('Show', []), ('Hide', [])):
            vm.invoke(facade[name], facade, args)
        self.assertEqual(vm.invoke(facade['GetValidDisplayString'], facade, []), '')
        self.assertEqual(instance['_headerCalls'], [])

    def test_focus_hides_only_preview_holders_and_restores_exact_visibility(self):
        instance, _, _, _ = self.run_init({'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'})
        vm, view = instance['_machine'], instance['_view']
        service = vm.globals['logic_cfm']['service']['HubInfoPanelsService']['Get']('arg6')
        listeners = service['mHidePanelHandler']['mListeners']
        visible, hidden, unrelated = ({'_visible': value} for value in (True, False, True))
        def record(holder, class_):
            scope = {'_class': class_, '_HideAllScreens': lambda: None,
                     'GetScreenInfo': lambda: {'GetHolderMovie': lambda: holder}}
            return {'Callback': {'scope': scope, 'func': scope['_HideAllScreens']}}
        first = record(visible, instance['_switcherClass'])
        listeners.extend([None, {}, record(unrelated, object()), first,
                          record(hidden, instance['_switcherClass']), first])
        vm.invoke(view['Focus'], view, [42])
        self.assertFalse(visible['_visible'])
        self.assertFalse(hidden['_visible'])
        self.assertTrue(unrelated['_visible'])
        self.assertEqual(len(view['mDynastySocialSavedPreviews']), 2)
        vm.invoke(view['Focus'], view, [42])
        self.assertEqual(len(view['mDynastySocialSavedPreviews']), 2)
        vm.invoke(view['Unfocus'], view, [43])
        self.assertTrue(visible['_visible'])
        self.assertFalse(hidden['_visible'])
        self.assertEqual(view['mDynastySocialSavedPreviews'], [])
        self.assertEqual(instance['_events'][-1], ('unfocus', 43))

    def test_mount_uses_live_tab_bottom_and_parent_coordinate_conversion(self):
        moves = []
        def global_to_local(point):
            point.update(x=(point['x'] - 100) / 2, y=(point['y'] - 200) / 2)
        def local_to_global(point):
            point.update(x=100 + point['x'] * 2, y=200 + point['y'] * 2)
        outer = {'mcMount': {'_x': -40, '_parent': {'globalToLocal': global_to_local, 'localToGlobal': local_to_global}},
                 'SetScreenMountPosition': lambda x, y: moves.append((x, y))}
        instance, _, _, _ = self.run_init({'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL',
            'Panel': {'mId': 'CM_DYNASTY_SOCIAL', 'mMovie': outer}})
        tabs = {'GetHeight': lambda: 32, 'localToGlobal': lambda p: p.update(x=p['x'] + 44, y=p['y'] + 120)}
        instance['_realHeader']['mcTabs'] = tabs
        vm, view = instance['_machine'], instance['_view']
        vm.invoke(view['mDynastySocialAlignMount'], view, [])
        self.assertEqual(moves, [(-40, -138)])
        dropdown_stage_y = 200 + (moves[0][1] + 138) * 2
        self.assertEqual(dropdown_stage_y, max(120 + 32 + 16, 200))
        tabs['localToGlobal'] = lambda p: p.update(x=p['x'] + 44, y=p['y'] + 400)
        vm.invoke(view['mDynastySocialAlignMount'], view, [])
        self.assertEqual(moves[-1], (-40, -14))
        self.assertEqual(200 + (moves[-1][1] + 138) * 2, 400 + 32 + 16)
        tabs['GetHeight'] = lambda: 0
        vm.invoke(view['mDynastySocialAlignMount'], view, [])
        self.assertEqual(len(moves), 2)
        tabs['GetHeight'] = lambda: 32
        outer['mcMount']['_parent']['globalToLocal'] = lambda p: p.update(y=float('nan'))
        vm.invoke(view['mDynastySocialAlignMount'], view, [])
        self.assertEqual(len(moves), 2)

    def test_preview_listener_scan_is_bounded(self):
        instance, _, _, _ = self.run_init({'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'})
        vm, view = instance['_machine'], instance['_view']
        holder = {'_visible': True}
        scope = {'_class': instance['_switcherClass'], '_HideAllScreens': lambda: None,
                 'GetScreenInfo': lambda: {'GetHolderMovie': lambda: holder}}
        listeners = [None] * 16 + [{'Callback': {'scope': scope, 'func': scope['_HideAllScreens']}}]
        vm.globals['logic_cfm']['service']['HubInfoPanelsService']['Get']('arg6')['mHidePanelHandler']['mListeners'] = listeners
        vm.invoke(view['mDynastySocialHidePreview'], view, [])
        self.assertTrue(holder['_visible'])
        vm.globals['art_screen']['panel']['career'].pop('HubPanelSwitcher')
        vm.globals['logic_cfm']['service']['HubInfoPanelsService']['Get']('arg6')['mHidePanelHandler']['mListeners'] = listeners[-1:]
        vm.invoke(view['mDynastySocialHidePreview'], view, [])
        self.assertTrue(holder['_visible'])

    def test_shutdown_restores_preview_even_without_unfocus(self):
        instance, _, _, _ = self.run_init({'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'})
        holder = {'_visible': False, 'mDynastySocialHideCount': 1, 'mDynastySocialOriginalVisible': True}
        instance['_view']['mDynastySocialSavedPreviews'] = [{'holder': holder, 'visible': True}]
        program = scoped_shutdown()
        execute(program.code, program.literals, None, initial=instance)
        self.assertTrue(holder['_visible'])

    def test_overlapping_views_restore_only_after_the_last_owner_releases(self):
        for originally_visible in (True, False):
            holder = {'_visible': originally_visible}
            class_ = object()
            scope = {'_class': class_, '_HideAllScreens': lambda: None,
                     'GetScreenInfo': lambda: {'GetHolderMovie': lambda: holder}}
            env = {'switcher_class': class_, 'preview_service': {
                'mHidePanelHandler': {'mListeners': [{'Callback': {'scope': scope, 'func': scope['_HideAllScreens']}}]}}}
            program = scoped_init()
            views = []
            for _ in range(2):
                instance, _, _, _ = execute(program.code, program.literals,
                    {'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'},
                    environment=env, references=program.references)
                vm, view = instance['_machine'], instance['_view']
                vm.invoke(view['Focus'], view, [1])
                views.append((vm, view))
            self.assertEqual(holder['mDynastySocialHideCount'], 2)
            self.assertFalse(holder['_visible'])
            views[0][0].invoke(views[0][1]['Unfocus'], views[0][1], [2])
            self.assertFalse(holder['_visible'])
            self.assertEqual(holder['mDynastySocialHideCount'], 1)
            views[1][0].invoke(views[1][1]['Unfocus'], views[1][1], [2])
            self.assertIs(holder['_visible'], originally_visible)
            self.assertEqual(holder['mDynastySocialHideCount'], 0)

    def test_timer_is_context_owned_and_cleared_on_shutdown(self):
        init = scoped_init(timer=True)
        instance, _, _, _ = execute(init.code, init.literals,
            {'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'}, references=init.references)
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
        signal_count = len(instance['_signals'])
        callback()  # A previously queued callback must be harmless after teardown.
        self.assertEqual(len(instance['_signals']), signal_count)

    def test_overlapping_instances_have_distinct_timer_names(self):
        program = scoped_init(timer=True)
        environment = {}
        names = []
        for _ in range(3):
            instance, _, _, _ = execute(program.code, program.literals,
                {'IsSubscreen': True, 'PanelId': 'CM_DYNASTY_SOCIAL'}, environment=environment, references=program.references)
            names.append(instance['mDynastySocialTimerName'])
        self.assertEqual(len(set(names)), 3)

    def test_nonembedded_news_never_registers_a_timer(self):
        program = scoped_init(timer=True)
        instance, _, _, _ = execute(program.code, program.literals, {'PanelId': 'CM_NEWSSUB'}, references=program.references)
        self.assertFalse(instance['_timers'])
        self.assertFalse(instance['_signals'])

    def test_other_screens_keep_the_original_init_behavior(self):
        original = ORIGINAL_INIT
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
