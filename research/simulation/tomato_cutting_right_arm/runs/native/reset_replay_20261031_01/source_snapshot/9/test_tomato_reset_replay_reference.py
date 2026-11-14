import copy,unittest
from tomato_reset_replay_reference import compare_traces
from tomato_isaac_startup_guard import worker_passed

class ResetReplayTests(unittest.TestCase):
    def trace(self):
        state=dict(p=[0.,0.,.001],vp=[0.]*3,pose=[0.,0.,0.,0.,0.,0.,1.],velocity=[0.]*6)
        return [dict(interval=0,contact_count=1,before=state,after=copy.deepcopy(state),force_n=[0.,0.,1.],wrench=[0.,0.,-1.,.01,0.,0.])]
    def test_identical_and_prefix_replay(self):
        t=self.trace();self.assertEqual(compare_traces(t,t)['intervals_compared'],1)
    def test_old_state_refused(self):
        t=self.trace();r=copy.deepcopy(t);r[0]['before']['velocity'][3]=.1
        with self.assertRaises(ValueError):compare_traces(t,r)
    def test_stale_contact_or_force_refused(self):
        for field,value in [('contact_count',0),('force_n',[0.,0.,99.])]:
            t=self.trace();r=copy.deepcopy(t);r[0][field]=value
            with self.assertRaises(ValueError):compare_traces(t,r)
    def test_guard_requires_both_reset_situations(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,reset_checks_passed=True,
            reset_cases_completed=2,newton_steps=68,physx_steps=34,reset_cycles_completed=2,replay_comparisons=4,dirty_wrench_resets=4)
        self.assertTrue(worker_passed(r,'reset_replay'))
        for k in ('newton_steps','physx_steps','reset_cycles_completed','replay_comparisons','dirty_wrench_resets'):
            self.assertFalse(worker_passed(dict(r,**{k:99}),'reset_replay'))
