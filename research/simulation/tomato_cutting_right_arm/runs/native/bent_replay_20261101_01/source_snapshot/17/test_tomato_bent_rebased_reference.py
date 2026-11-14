import unittest,math
from tomato_bent_rebased_reference import REST,step,dynamics,physical_angles
from tomato_bent_origin_reference import step as original,origin_for
from tomato_two_joint_sequence_reference import dynamics as original_dynamics
from tomato_isaac_startup_guard import worker_passed
class RebasedTests(unittest.TestCase):
    def test_rest_geometry_and_dynamics_preserved(self):
        self.assertEqual(physical_angles([0.,0.]),REST)
        self.assertEqual(dynamics([0.,0.],[.1,-.2],[.01,.02]),original_dynamics(REST,[.1,-.2],[.01,.02]))
    def test_trajectory_equivalent(self):
        for yaw in (0.,math.pi/2):
            o=origin_for(yaw,REST);a=dict(q=REST.copy(),qd=[0.,0.],p=[0.,0.,0.],vp=[0.,0.,0.]);b=dict(a,q=[0.,0.])
            for _ in range(32):
                x=original(a,yaw,.01,.005,1750.,1/2400,o);y=step(b,yaw,.01,.005,1750.,1/2400,o)
                for key in ('force','effort_nm'):
                    for u,v in zip(x[key],y[key]):self.assertAlmostEqual(u,v,places=12)
                for u,v in zip(x['after']['q'],physical_angles(y['after']['q'])):self.assertAlmostEqual(u,v,places=12)
                a=x['after'];b=y['after']
    def test_guard(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,bent_rebased_checks_passed=True,bent_rebased_cases_completed=2,controlled_steps=32,newton_steps=64,cuda_state_echoes=66,min_coast_steps=3,natural_separation=True)
        self.assertTrue(worker_passed(r,'bent_rebased'))
        for k,v in [('newton_steps',63),('min_coast_steps',2),('natural_separation',False)]:self.assertFalse(worker_passed(dict(r,**{k:v}),'bent_rebased'))
