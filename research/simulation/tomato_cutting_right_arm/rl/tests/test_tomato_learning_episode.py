import unittest
from tomato_learning_episode import *

class EpisodeLearningTests(unittest.TestCase):
    def history(self):
        h=ObservationHistory({'joint_position_rad':1},3);h.reset('one',3);return h
    def add(self,h,step=0,time_s=0.,episode='one'):
        return h.append({'joint_position_rad':{'source':'encoder','verified':True,'time_s':time_s,'values':[.2]}},episode_id=episode,step=step,time_s=time_s,max_age_s=.1)
    def test_padding_and_mask(self):
        r=self.add(self.history());self.assertEqual(r['values'],[[0.],[0.],[.2]]);self.assertEqual(r['mask'],[[0],[0],[1]])
    def test_reset_erases_history(self):
        h=self.history();self.add(h);h.reset('two',3)
        self.assertEqual(h.snapshot()['mask'],[[0],[0],[0]]);self.assertIsNone(h.snapshot()['last_step'])
        self.assertFalse(h.snapshot()['native_reset_verified'])
    def test_episode_splice_refused(self):
        h=self.history()
        with self.assertRaises(ValueError):self.add(h,episode='withdrawal')
    def test_skips_duplicates_refused(self):
        h=self.history();self.add(h)
        for step in [0,2]:
            with self.assertRaises(ValueError):self.add(h,step=step,time_s=1)
    def test_snapshot_cannot_mutate_state(self):
        h=self.history();s=self.add(h);s['values'][-1][0]=99;self.assertEqual(h.snapshot()['values'][-1],[.2])
    def test_time_must_advance(self):
        h=self.history();self.add(h)
        with self.assertRaises(ValueError):self.add(h,step=1)
    def test_residual_amplitude(self):
        r=residual_reference([0]*3,[99,-99,99],[0]*3,max_residual=[.1,.2,0.],dt_s=.1,lower=[-1]*3,upper=[1]*3,max_acceleration=[100]*3)
        self.assertEqual(r['reference_action'],[.1,-.2,0.]);self.assertFalse(r['robot_command_authorized'])
    def cases(self):return [{'case_id':'a','split':'baseline','seed':1,'physical_config_sha256':'a'*64},{'case_id':'b','split':'heldout','seed':2,'physical_config_sha256':'b'*64}]
    def test_holdout_integrity(self):self.assertFalse(validate_case_registry(self.cases())['training_authorized'])
    def test_configuration_leak(self):
        c=self.cases();c[1]['physical_config_sha256']='a'*64
        with self.assertRaises(ValueError):validate_case_registry(c)
    def test_seed_leak(self):
        c=self.cases();c[1]['seed']=1
        with self.assertRaises(ValueError):validate_case_registry(c)
    def test_empty_holdout_refused(self):
        with self.assertRaises(ValueError):validate_case_registry(self.cases()[:1])
    def test_hidden_history_schema_refused(self):
        with self.assertRaises(ValueError):ObservationHistory({'damage':1},3)
