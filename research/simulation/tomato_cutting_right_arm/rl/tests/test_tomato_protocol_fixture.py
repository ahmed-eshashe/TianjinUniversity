import tempfile
import unittest
from pathlib import Path
from tomato_protocol_fixture import run_fixture

SAFE=(12_000_000_000,5*1024**3);WARN=(2_999_999*1024,2*1024**3)
class FixtureTests(unittest.TestCase):
    def run_case(self,mode):
        n=0
        def monitor():
            nonlocal n
            n+=1;return SAFE if n==1 else WARN
        with tempfile.TemporaryDirectory() as d:
            a=run_fixture(Path(d)/'case',monitor=monitor,mode=mode,wall_s=.8,grace_s=.4)
        self.assertEqual(a['running_after_cleanup'],[]);self.assertFalse(a['native_runtime_validated'])
        self.assertEqual(a['actions'].count('request_checkpoint_once'),1)
        return a
    def test_ack(self):self.assertEqual(self.run_case('ack')['reason'],'checkpoint_and_exit')
    def test_ignore(self):self.assertEqual(self.run_case('ignore')['reason'],'stop_timeout')
    def test_bad_hash(self):self.assertEqual(self.run_case('bad_hash')['reason'],'invalid_ack')
    def test_exit_no_ack(self):self.assertEqual(self.run_case('exit_without_ack')['reason'],'exit_without_valid_ack')
    def test_startup_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'never';a=run_fixture(p,monitor=lambda:(0,0))
            self.assertFalse(a['launched']);self.assertFalse(p.exists())
