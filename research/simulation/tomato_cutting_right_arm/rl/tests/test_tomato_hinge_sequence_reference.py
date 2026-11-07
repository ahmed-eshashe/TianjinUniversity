import unittest,math
from tomato_hinge_sequence_reference import step,pose_from_joint
from tomato_wrench_contract import cross
from tomato_isaac_startup_guard import worker_passed

class HingeSequenceTests(unittest.TestCase):
    def test_natural_separation_and_axis_balance(self):
        b=dict(q=0.,qd=0.,p=[.014,.004,0.],vp=[0.]*3);clear=0
        for _ in range(32):
            r=step(b,0.,.01,.000102,.005,1750.,1/2400);b=r['after'];clear+=r['signed_depth_m']<=0
            l=cross(b['p'],[.01*v for v in b['vp']])[2]+.000102*b['qd']
            self.assertLess(abs(l),1e-17)
        self.assertGreater(clear,3);self.assertLess(b['qd'],0.)
    def test_quarter_turn_equivalence(self):
        a=dict(q=0.,qd=0.,p=[.014,.004,0.],vp=[0.]*3)
        b=dict(q=0.,qd=0.,p=[-.004,.014,0.],vp=[0.]*3)
        for _ in range(32):
            a=step(a,0.,.01,.000102,.005,1750.,1/2400)['after']
            b=step(b,math.pi/2,.01,.000102,.005,1750.,1/2400)['after']
        self.assertAlmostEqual(a['q'],b['q']);self.assertAlmostEqual(a['qd'],b['qd'])
    def test_stale_force_not_expected_on_clear_step(self):
        b=dict(q=0.,qd=-.1,p=[.014,.008,0.],vp=[0.,.2,0.])
        r=step(b,0.,.01,.000102,.005,1750.,1/2400)
        self.assertEqual(r['force'],[0.]*3);self.assertEqual(r['after']['qd'],b['qd'])
    def test_guard_counts_and_coast(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,hinge_sequence_checks_passed=True,hinge_sequence_cases_completed=2,
            controlled_steps=32,newton_steps=64,cuda_state_echoes=66,min_coast_steps=20,natural_separation=True)
        self.assertTrue(worker_passed(r,'hinge_sequence'))
        for k,v in [('controlled_steps',33),('newton_steps',63),('cuda_state_echoes',64),('min_coast_steps',0),('natural_separation',False)]:
            self.assertFalse(worker_passed(dict(r,**{k:v}),'hinge_sequence'))
