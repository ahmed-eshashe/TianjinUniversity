import unittest,tempfile
from pathlib import Path
from tomato_checkpoint_supervisor import run_checkpoint_fixture
from tomato_native_launch_preview import preview
from test_tomato_native_launch_contract import LaunchContractTests

class CheckpointSupervisorTests(unittest.TestCase):
    def test_fixture_cases_and_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode,reason in [('ack','checkpoint_and_exit'),('ignore','checkpoint_timeout'),
                                ('exit_without_ack','exit_without_valid_ack'),('bad_hash','invalid_ack')]:
                with self.subTest(mode=mode):
                    r=run_checkpoint_fixture(Path(tmp)/mode,mode=mode,ack_timeout_s=.3)
                    self.assertEqual(r['reason'],reason)
                    self.assertEqual(r['process_group_running_after_cleanup'],[])
                    self.assertFalse(r['native_runtime_validated'])
    def test_unknown_command_refused(self):
        with self.assertRaises(ValueError):run_checkpoint_fixture('/unused',mode='anything')
    def test_output_reuse_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):run_checkpoint_fixture(tmp)
    def test_preview_disabled(self):
        fixture=LaunchContractTests();fixture.setUp()
        try:
            r=preview(fixture.root,fixture.req,'2026-10-28T09:00:00Z')
            self.assertFalse(r['execution_enabled']);self.assertFalse(r['imports_or_processes_started'])
        finally:fixture.doCleanups()
