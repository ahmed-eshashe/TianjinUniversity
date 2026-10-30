import math
import os
import signal
import subprocess
import time
import unittest
from unittest.mock import patch
from tomato_preupgrade_guard import startup_decision,runtime_decision,native_preview,run_dummy,group_members

G=1024**3


class PreparationGuardTests(unittest.TestCase):
    def monitor(self):return (12_000_000_000,5*G)

    def test_startup_exact_floors(self):
        self.assertTrue(startup_decision(10_000_000_000,4*G))
        self.assertFalse(startup_decision(9_999_999_999,4*G))
        self.assertFalse(startup_decision(12_000_000_000,4*G-1))

    def test_production_warning_and_hard_thresholds(self):
        self.assertEqual(runtime_decision(2_999_999*1024,5*G),'checkpoint_and_stop')
        self.assertEqual(runtime_decision(1_999_999*1024,5*G),'stop')
        self.assertEqual(runtime_decision(12_000_000_000,G-1),'stop')
        self.assertEqual(runtime_decision(12_000_000_000,int(1.5*G)-1),'checkpoint_and_stop')
        self.assertEqual(runtime_decision(12_000_000_000,5*G,3),'stop')

    def test_unknown_or_nonfinite_resources_fail_closed(self):
        for x in [math.nan,math.inf,-1,None]:
            self.assertFalse(startup_decision(x,5*G));self.assertEqual(runtime_decision(x,5*G),'stop')

    def test_preview_has_no_process_side_effect(self):
        with patch('subprocess.Popen',side_effect=AssertionError('Unexpected process')):
            r=native_preview('/tmp','coupon.json')
        self.assertFalse(r['execution_enabled']);self.assertFalse(r['imports_or_subprocesses_started'])

    def test_low_memory_refuses_before_launch(self):
        with patch('subprocess.Popen',side_effect=AssertionError('Unexpected process')):
            self.assertFalse(run_dummy('exit',monitor=lambda:(1,1))['launched'])

    def test_dummy_exit(self):
        self.assertEqual(run_dummy('exit',monitor=self.monitor)['reason'],'exited')

    def test_timeout_kills_term_ignoring_dummy(self):
        r=run_dummy('ignore_term',monitor=self.monitor,wall_s=.05)
        self.assertEqual(r['reason'],'wall_timeout')
        with self.assertRaises(ProcessLookupError):os.kill(r['pid'],0)

    def test_monitor_failure_stops_without_infinite_retry(self):
        count=[0]
        def monitor():
            count[0]+=1
            if count[0]>1:raise OSError('GPU unavailable')
            return self.monitor()
        r=run_dummy('sleep',monitor=monitor)
        self.assertEqual(r['reason'],'monitor_error');self.assertEqual(count[0],4)

    def test_runtime_warning_stops_dummy(self):
        count=[0]
        def monitor():
            count[0]+=1
            return self.monitor() if count[0]==1 else (2_999_999*1024,5*G)
        self.assertEqual(run_dummy('sleep',monitor=monitor)['reason'],'checkpoint_and_stop')

    def test_arbitrary_commands_not_accepted(self):
        with self.assertRaises(ValueError):run_dummy('launch_native',monitor=self.monitor)

    def test_spawned_child_has_no_running_group_members_after_cleanup(self):
        r=run_dummy('spawn_sleep',monitor=self.monitor,wall_s=.2)
        self.assertGreaterEqual(len(r['group_before_cleanup']),2)
        until=time.monotonic()+.5
        while any(state!='Z' for _,state in group_members(r['pid'])) and time.monotonic()<until:
            time.sleep(.005)
        self.assertFalse(any(state!='Z' for _,state in group_members(r['pid'])))

    def test_interrupt_runs_cleanup(self):
        launched=[];original=subprocess.Popen;calls=[0]
        def launch(*a,**kw):
            p=original(*a,**kw);launched.append(p.pid);return p
        def monitor():
            calls[0]+=1
            if calls[0]>1:raise KeyboardInterrupt()
            return self.monitor()
        with patch('subprocess.Popen',side_effect=launch):
            with self.assertRaises(KeyboardInterrupt):run_dummy('sleep',monitor=monitor)
        with self.assertRaises(ProcessLookupError):os.kill(launched[0],0)
