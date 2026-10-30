import unittest
from tomato_learning_contract import *

class LearningContractTests(unittest.TestCase):
    def sample(self):return {'joint_position_rad':{'source':'encoder','verified':True,'time_s':1.,'values':[.1,.2]}}
    def test_hidden_state_invariance(self):
        s=self.sample();base=actor_observation(s,{'joint_position_rad':2},now_s=1,max_age_s=.1)
        s.update(damage=[1],connectivity='detached',wrist_force=[999])
        self.assertEqual(base,actor_observation(s,{'joint_position_rad':2},now_s=1,max_age_s=.1))
    def test_hidden_or_wrist_layout_refused(self):
        for name in ['damage','connectivity','wrist_force','wrist_torque']:
            with self.assertRaises(ValueError):actor_observation({}, {name:3},now_s=1,max_age_s=.1)
    def test_stale_future_missing_unverified_masked(self):
        for t in [0.,2.]:
            s=self.sample();s['joint_position_rad']['time_s']=t
            self.assertEqual(actor_observation(s,{'joint_position_rad':2},now_s=1,max_age_s=.1)['mask'],[0,0])
        self.assertEqual(actor_observation({}, {'joint_position_rad':2},now_s=1,max_age_s=.1)['values'],[0.,0.])
    def test_exact_state_not_vision(self):
        s={'tomato_pose_estimate':{'source':'simulator_truth','verified':True,'time_s':1,'values':[1,2,3]}}
        self.assertEqual(actor_observation(s,{'tomato_pose_estimate':3},now_s=1,max_age_s=.1)['mask'],[0,0,0])
    def test_invalid_verified_sample_refused(self):
        s=self.sample();s['joint_position_rad']['values']=[float('nan'),0]
        with self.assertRaises(ValueError):actor_observation(s,{'joint_position_rad':2},now_s=1,max_age_s=.1)
    def test_privileged_separate(self):self.assertEqual(privileged_observation({'damage':[1],'joint_position_rad':[0]}),{'damage':[1]})
    def action(self,residual,**kw):
        return bounded_residual([0,0,0],residual,[0,0,0],dt_s=.1,lower=[-1]*3,upper=[1]*3,max_acceleration=[2]*3,**kw)
    def test_acceleration_and_speed_bounds(self):self.assertEqual(self.action([100,-100,0])['reference_action'],[.2,-.2,0])
    def test_zero_residual_baseline(self):self.assertEqual(self.action([0]*3)['reference_action'],[0]*3)
    def test_nonfinite_action(self):
        with self.assertRaises(ValueError):self.action([float('inf'),0,0])
    def test_prior_outside_bounds_refused(self):
        with self.assertRaises(ValueError):bounded_residual([0]*3,[0]*3,[2]*3,dt_s=.1,lower=[-1]*3,upper=[1]*3,max_acceleration=[1]*3)
    def test_safety_is_independent_termination(self):
        r=episode_outcome([],safety_failure=True);self.assertTrue(r['terminate']);self.assertFalse(r['success_bonus_enabled'])
    def test_no_reward_for_incomplete(self):
        r=episode_outcome([]);self.assertFalse(r['success_bonus_enabled']);self.assertFalse(r['training_enabled'])
