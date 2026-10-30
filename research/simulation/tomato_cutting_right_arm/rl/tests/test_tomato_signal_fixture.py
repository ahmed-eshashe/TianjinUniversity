import signal,tempfile,unittest
from pathlib import Path
from tomato_signal_fixture import run_signal_fixture
RESULTS=[]
class SignalTests(unittest.TestCase):
    def check(self,number):
        with tempfile.TemporaryDirectory() as d:a=run_signal_fixture(Path(d)/'case',int(number))
        RESULTS.append(a)
        self.assertEqual(a['received_signal'],int(number));self.assertEqual(a['supervisor_returncode'],0)
        self.assertEqual(a['remaining_child_group'],[]);self.assertEqual(a['remaining_supervisor_group'],[])
        self.assertFalse(a['native_runtime_validated'])
    def test_real_sigint(self):self.check(signal.SIGINT)
    def test_real_sigterm(self):self.check(signal.SIGTERM)
    def test_refuses_other_signals(self):
        with self.assertRaises(ValueError):run_signal_fixture('/unused',int(signal.SIGKILL))
