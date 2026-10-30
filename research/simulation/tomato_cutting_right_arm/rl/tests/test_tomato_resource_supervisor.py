import unittest,tempfile,json
from pathlib import Path
from tomato_resource_supervisor import supervise_fixture
from tomato_preupgrade_guard import group_members
HIGH=(11e9,5*1024**3)
WARNING=(2_500_000*1024,2*1024**3)
HARD=(1_000_000*1024,2*1024**3)

class ResourceSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.out=Path(self.t.name)/'run'
    def monitor(self,values):
        it=iter(values);last=values[-1]
        def read():
            v=next(it,last)
            if isinstance(v,BaseException):raise v
            return v
        return read
    def run_case(self,values,**kw):
        r=supervise_fixture(self.out,monitor=self.monitor(values),**kw)
        if r['launched']:self.assertEqual(r['running_group_members_after_cleanup'],[])
        return r
    def test_warning_checkpoint_ack_and_exit(self):
        r=self.run_case([HIGH,WARNING]);self.assertEqual(r['reason'],'checkpoint_and_exit');self.assertEqual(r['warning_requests'],1);self.assertTrue(r['checkpoint_verified'])
    def test_hard_stop_no_wait(self):
        r=self.run_case([HIGH,HARD]);self.assertEqual(r['reason'],'hard_memory_stop');self.assertFalse(r['checkpoint_requested'])
    def test_three_errors_stop(self):
        r=self.run_case([HIGH,OSError('fixture')]);self.assertEqual(r['reason'],'monitor_error');self.assertEqual(r['monitor_errors'],3)
    def test_warning_then_hard_stop(self):
        r=self.run_case([HIGH,WARNING,HARD]);self.assertEqual(r['reason'],'hard_memory_stop')
    def test_checkpoint_timeout_cleanup(self):self.assertEqual(self.run_case([HIGH,WARNING],mode='ignore',checkpoint_grace_s=.06)['reason'],'checkpoint_timeout')
    def test_bad_ack_refused(self):self.assertEqual(self.run_case([HIGH,WARNING],mode='bad_hash')['reason'],'invalid_ack')
    def test_wall_timeout_cleanup(self):self.assertEqual(self.run_case([HIGH],wall_s=.06)['reason'],'wall_timeout')
    def test_startup_unreadable_no_output(self):
        r=self.run_case([OSError('fixture')]);self.assertFalse(r['launched']);self.assertFalse(self.out.exists())
    def test_startup_insufficient_no_child(self):self.assertFalse(self.run_case([HARD])['launched'])
    def test_interrupt_cleans_child(self):
        with self.assertRaises(KeyboardInterrupt):self.run_case([HIGH,KeyboardInterrupt()])
        pid=json.loads((self.out/'owned_pid.json').read_text())['pid'];self.assertEqual([p for p,s in group_members(pid) if s!='Z'],[])
