import unittest,copy
from tomato_optimizer_cycle import restart_fingerprint
class RestartCycle(unittest.TestCase):
    def setUp(self):
        self.base={'passed':False,'optimization_only':True,'depth_mm':8.8,'previous_summary_sha256':'previous','guess_sha256':'positions','trial_damage_states':[{'damage':.5,'kappa_m':.002}],'optimizer_active_rows':[1,2],'source_hashes':{'solver':'source'}}
    def test_repeated_restart_ignores_diagnostic_trace_and_runtime(self):
        other=copy.deepcopy(self.base);other.update(runtime_s=99.,outer_iterations=[{'force_residual':1.}]);self.assertEqual(restart_fingerprint(self.base),restart_fingerprint(other))
    def test_new_positions_are_not_cycle(self):
        other=copy.deepcopy(self.base);other['guess_sha256']='different';self.assertNotEqual(restart_fingerprint(self.base),restart_fingerprint(other))
    def test_bookkeeping_progress_without_movement_is_not_cycle(self):
        other=copy.deepcopy(self.base);other['optimizer_active_rows']=[1,2,3];self.assertNotEqual(restart_fingerprint(self.base),restart_fingerprint(other))
    def test_ordered_contact_state_is_retained(self):
        other=copy.deepcopy(self.base);other['optimizer_active_rows']=[2,1];self.assertNotEqual(restart_fingerprint(self.base),restart_fingerprint(other))
    def test_damage_and_history_changes_are_not_cycle(self):
        for key,value in [('damage',.6),('kappa_m',.003)]:
            other=copy.deepcopy(self.base);other['trial_damage_states'][0][key]=value;self.assertNotEqual(restart_fingerprint(self.base),restart_fingerprint(other))
    def test_different_physical_problem_is_not_same_restart(self):
        for key,value in [('depth_mm',8.9),('previous_summary_sha256','new'),('source_hashes',{'solver':'new'})]:
            other=copy.deepcopy(self.base);other[key]=value;self.assertNotEqual(restart_fingerprint(self.base),restart_fingerprint(other))
    def test_physical_checkpoint_and_missing_state_are_rejected(self):
        other=copy.deepcopy(self.base);other['passed']=True
        with self.assertRaises(ValueError):restart_fingerprint(other)
        other=copy.deepcopy(self.base);del other['trial_damage_states']
        with self.assertRaises(KeyError):restart_fingerprint(other)
    def test_nonfinite_state_cannot_be_fingerprinted(self):
        other=copy.deepcopy(self.base);other['trial_damage_states'][0]['damage']=float('nan')
        with self.assertRaises(ValueError):restart_fingerprint(other)
if __name__=='__main__':unittest.main()
