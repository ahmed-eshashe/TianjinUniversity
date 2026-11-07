import copy,unittest
from tomato_two_joint_replay_reference import compare
from tomato_isaac_startup_guard import worker_passed

class HingeReplayTests(unittest.TestCase):
    def trace(self):
        state=dict(q=[0.,0.],qd=[0.,0.],p=[.014,.004,0.],vp=[0.]*3)
        return [dict(interval=0,contact_count=1,before=state,after=copy.deepcopy(state),force_n=[0.,1.,0.],wrench=[0.,-1.,0.,0.,0.,-.004],
            after_link_packet=dict(link_pose=[.01,0.,0.,0.,0.,0.,1.],link_com_velocity=[0.]*6))]
    def test_exact_replay(self):
        t=self.trace();self.assertEqual(compare(t,t)['intervals_compared'],1)
        self.assertTrue(all(v==0 for v in compare(t,t)['max_errors'].values()))
    def test_old_joint_state_or_force_rejected(self):
        a=self.trace();b=copy.deepcopy(a);b[0]['before']['qd']=[0.,.2]
        with self.assertRaises(ValueError):compare(a,b)
        b=copy.deepcopy(a);b[0]['force_n'][0]=99.
        with self.assertRaises(ValueError):compare(a,b)
    def test_contact_and_link_state_rejected(self):
        a=self.trace();b=copy.deepcopy(a);b[0]['contact_count']=0
        with self.assertRaises(ValueError):compare(a,b)
        b=copy.deepcopy(a);b[0]['after_link_packet']['link_com_velocity'][3]=.01
        with self.assertRaises(ValueError):compare(a,b)
    def test_guard_both_reset_conditions(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,two_joint_replay_checks_passed=True,two_joint_replay_cases_completed=2,
            controlled_steps=66,newton_steps=132,cuda_state_echoes=138,reset_cycles_completed=2,dirty_wrench_resets=4,replay_comparisons=4)
        self.assertTrue(worker_passed(r,'two_joint_replay'))
        for k in ('controlled_steps','newton_steps','cuda_state_echoes','reset_cycles_completed','dirty_wrench_resets','replay_comparisons'):
            self.assertFalse(worker_passed(dict(r,**{k:999}),'two_joint_replay'))
