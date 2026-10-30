import unittest,json
from pathlib import Path
from tomato_kinematic_interval import interval_target
from tomato_coupon_trajectory import pose_at

class KinematicIntervalTests(unittest.TestCase):
    def config(self):
        return json.loads((Path(__file__).resolve().parents[2]/'runs/offline/tomato_preupgrade_20261027T171031Z/coupon_trajectory.json').read_text())
    def test_stationary_first_rebaseline(self):
        c=self.config();r=interval_target(c,step=0,dt_s=c['dt_s']);self.assertEqual(r['pose']['linear_velocity_m_s'],[0.,0.,0.]);self.assertEqual(r['pose']['translation_m'],r['start_pose']['translation_m'])
    def test_pose_is_interval_endpoint(self):
        c=self.config();r=interval_target(c,step=61,dt_s=c['dt_s']);self.assertEqual(r['pose']['translation_m'],pose_at(c,62*c['dt_s'])['translation_m']);self.assertNotEqual(r['pose']['translation_m'],pose_at(c,61*c['dt_s'])['translation_m'])
    def test_velocity_matches_displacement_history(self):
        c=self.config();dt=c['dt_s'];r=interval_target(c,step=61,dt_s=dt)
        for v,a,b in zip(r['pose']['linear_velocity_m_s'],r['start_pose']['translation_m'],r['pose']['translation_m']):self.assertAlmostEqual(v*dt,b-a,places=15)
    def test_moving_first_interval_refused(self):
        c=self.config();c['stages'][0][0]='indent'
        # pose_at's stage profile is driven by stage names: this starts motion.
        with self.assertRaises(ValueError):interval_target(c,step=0,dt_s=c['dt_s'])
    def test_timestep_mismatch_refused(self):
        c=self.config()
        with self.assertRaises(ValueError):interval_target(c,step=0,dt_s=c['dt_s']/2)
    def test_native_validity_not_assumed(self):
        c=self.config();self.assertFalse(interval_target(c,step=0,dt_s=c['dt_s'])['native_kinematic_runtime_validated'])
