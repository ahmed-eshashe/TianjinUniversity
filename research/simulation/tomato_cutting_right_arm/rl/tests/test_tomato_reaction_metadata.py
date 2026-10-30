import unittest
from tomato_reaction_metadata import *
class ReactionMetadataTests(unittest.TestCase):
    def row(self):return {'step':0,'start_s':0.,'dt_s':.1,'force_convention':'force_then_moment','spatial_wrench_world_about_com':[[0.,2.,0.,0.,0.,0.]]}
    def sample(self,target=(0.,0.,0.)):
        return endpoint_metadata(self.row(),body_pose_xyzw=[0.,0.,0.,0.,0.,0.,1.],body_com_local_m=[1.,0.,0.],body_spatial_velocity=[0.,0.,0.,0.,0.,1.],target_origin_world_m=target)
    def test_com_and_moment_shift(self):
        s=self.sample();self.assertEqual(s['com_world_m'],(1.,0.,0.));self.assertEqual(s['moment_world_nm'],(0.,0.,2.));self.assertEqual(s['velocity_at_origin_world_m_s'],(0.,-1.,0.))
    def test_power_origin_invariance(self):self.assertAlmostEqual(endpoint_work_estimate(self.sample())['estimated_contact_work_on_blade_j'],endpoint_work_estimate(self.sample((1.,0.,0.)))['estimated_contact_work_on_blade_j'])
    def test_endpoint_never_step_average(self):
        s=self.sample();self.assertFalse(s['work_ledger_admissible']);self.assertEqual(s['sample_time_s'],.1);self.assertFalse(endpoint_work_estimate(s)['exact_step_work'])
    def test_actual_fixed_rotation(self):
        r=quaternion_rotation([.5,.5,.5,.5]);self.assertEqual(r,((0.,0.,1.),(1.,0.,0.),(0.,1.,0.)))
    def test_zero_quaternion_refused(self):
        with self.assertRaises(ValueError):quaternion_rotation([0.]*4)
    def test_ambiguous_spatial_order(self):
        r=self.row();r['force_convention']='unknown'
        with self.assertRaises(ValueError):endpoint_metadata(r,body_pose_xyzw=[0.]*7,body_com_local_m=[0.]*3,body_spatial_velocity=[0.]*6,target_origin_world_m=[0.]*3)
    def test_default_state_access_refused(self):
        with self.assertRaises(PermissionError):capture_metadata(None,None,target_origin_world_m=[0.]*3)
