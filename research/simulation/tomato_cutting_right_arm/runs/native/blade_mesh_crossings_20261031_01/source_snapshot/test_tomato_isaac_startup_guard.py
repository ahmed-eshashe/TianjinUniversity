"""Real subprocess protection tests without any simulator imports."""
from pathlib import Path
import sys
import tempfile
import unittest

from tomato_isaac_startup_guard import supervise, worker_passed


class IsaacStartupGuardTests(unittest.TestCase):
    def test_fixed_mode_result_contracts_cannot_cross_qualify(self):
        startup = {'startup_step_passed': True, 'shutdown_requested': True, 'steps': 1}
        coupon = {'diagnostic_passed': True, 'shutdown_requested': True, 'committed_steps': 1}
        self.assertTrue(worker_passed(coupon, 'coupon_initial'))
        self.assertFalse(worker_passed(startup, 'coupon_initial'))
        self.assertFalse(worker_passed(coupon, 'startup'))
        self.assertFalse(worker_passed(coupon, 'coupon_stationary_sdf'))
        stationary = dict(coupon, committed_steps=12, sdf_queries_completed=True)
        self.assertTrue(worker_passed(stationary, 'coupon_stationary_sdf'))
        self.assertFalse(worker_passed(stationary, 'coupon_initial'))
        self.assertFalse(worker_passed(dict(stationary, sdf_queries_completed=False), 'coupon_stationary_sdf'))
        self.assertTrue(worker_passed(dict(stationary, sdf_resolution=256), 'coupon_sdf256'))
        self.assertFalse(worker_passed(dict(stationary, sdf_resolution=128), 'coupon_sdf256'))
        self.assertTrue(worker_passed(dict(stationary, sdf_resolution=512), 'coupon_sdf512'))
        self.assertFalse(worker_passed(dict(stationary, sdf_resolution=256), 'coupon_sdf512'))
        self.assertFalse(worker_passed(dict(stationary, sdf_resolution=512), 'coupon_target512'))
        self.assertTrue(worker_passed(dict(stationary, sdf_resolution=512, targeted_sdf_completed=True), 'coupon_target512'))
        self.assertFalse(worker_passed(dict(stationary, sdf_resolution=512, targeted_sdf_completed=True), 'coupon_target256'))
        fine = dict(stationary, sdf_resolution=1024, targeted_sdf_completed=True, sdf_cooking_padding_m=.005)
        self.assertTrue(worker_passed(fine, 'coupon_tight1024'))
        self.assertFalse(worker_passed(fine, 'coupon_fine1024'))
        self.assertFalse(worker_passed(dict(fine, sdf_resolution=512), 'coupon_tight1024'))
        direct = dict(diagnostic_passed=True, shutdown_requested=True, direct_queries_completed=562, mechanical_steps=0)
        self.assertTrue(worker_passed(direct, 'direct_mesh'))
        self.assertFalse(worker_passed(dict(direct, mechanical_steps=1), 'direct_mesh'))
        self.assertFalse(worker_passed(dict(direct, direct_queries_completed=561), 'direct_mesh'))
        self.assertFalse(worker_passed(direct, 'direct_mesh_centered'))
        self.assertTrue(worker_passed(dict(direct, centered_coordinates=True), 'direct_mesh_centered'))
        self.assertFalse(worker_passed(direct, 'direct_mesh_double'))
        self.assertTrue(worker_passed(dict(direct, double_precision_all_facets=True), 'direct_mesh_double'))
        crossing = dict(diagnostic_passed=True, shutdown_requested=True, crossing_cases_completed=11, mechanical_steps=0)
        self.assertTrue(worker_passed(crossing, 'mesh_crossings'))
        self.assertFalse(worker_passed(dict(crossing, mechanical_steps=1), 'mesh_crossings'))
        with self.assertRaises(ValueError):
            supervise('/unused', mode='arbitrary_worker')
    def run_case(self, script, monitor=None, wall_s=.3):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'run'
            return supervise(output, monitor=monitor or (lambda: (12_000_000_000, 5*1024**3)),
                             wall_s=wall_s, _fixture_command=[sys.executable, '-c', script, str(output)])

    def test_low_memory_prevents_launch(self):
        result = self.run_case('raise AssertionError()', monitor=lambda: (1, 1))
        self.assertFalse(result['launched'])

    def test_three_minute_budget_keeps_memory_refusal_and_upper_bound(self):
        result = self.run_case('raise AssertionError()', monitor=lambda: (1, 1), wall_s=180)
        self.assertFalse(result['launched'])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                supervise(Path(directory)/'refused', wall_s=181)

    def test_actual_clean_exit_requires_worker_result(self):
        result = self.run_case('import json,pathlib,sys,os; pathlib.Path(sys.argv[1], "worker_result.json").write_text(json.dumps({"startup_step_passed": True, "shutdown_requested": True, "steps": 1})); os._exit(0)')
        self.assertTrue(result['passed'])
        self.assertFalse(self.run_case('pass')['passed'])

    def test_preclose_record_cannot_override_failed_process_exit(self):
        result = self.run_case('import json,pathlib,sys,os; pathlib.Path(sys.argv[1], "worker_result.json").write_text(json.dumps({"startup_step_passed": True, "shutdown_requested": True, "steps": 1})); os._exit(1)')
        self.assertFalse(result['passed'])

    def test_deadline_kills_term_ignoring_process_and_child(self):
        result = self.run_case('import signal,subprocess,sys,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); time.sleep(30)')
        self.assertEqual(result['reason'], 'wall_timeout')
        self.assertFalse(result['remaining_live_group_members'])
        self.assertLess(result['elapsed_wall_s'], 3)

    def test_three_hardware_reader_failures_stop_worker(self):
        calls = [0]
        def monitor():
            calls[0] += 1
            if calls[0] > 1:
                raise OSError('reader failed')
            return 12_000_000_000, 5*1024**3
        result = self.run_case('import time; time.sleep(30)', monitor=monitor, wall_s=1)
        self.assertEqual(result['reason'], 'monitor_errors')
        self.assertEqual(calls[0], 4)
        self.assertFalse(result['remaining_live_group_members'])

    def test_memory_warning_requests_stop_and_cleans_up(self):
        calls = [0]
        def monitor():
            calls[0] += 1
            return (12_000_000_000, 5*1024**3) if calls[0] == 1 else (3_000_000*1024-1, 5*1024**3)
        result = self.run_case('import time; time.sleep(30)', monitor=monitor)
        self.assertTrue(result['warning_requested'])
        self.assertFalse(result['passed'])
        self.assertFalse(result['remaining_live_group_members'])

    def test_hard_memory_stop_and_interrupt_both_cleanup(self):
        for interrupted in (False, True):
            calls = [0]
            def monitor():
                calls[0] += 1
                if calls[0] == 1:
                    return 12_000_000_000, 5*1024**3
                if interrupted:
                    raise InterruptedError('signal during hardware read')
                return 1, 5*1024**3
            result = self.run_case('import time; time.sleep(30)', monitor=monitor)
            self.assertEqual(result['reason'], 'interrupted' if interrupted else 'hard_memory_stop')
            self.assertFalse(result['remaining_live_group_members'])


if __name__ == '__main__':
    unittest.main()
