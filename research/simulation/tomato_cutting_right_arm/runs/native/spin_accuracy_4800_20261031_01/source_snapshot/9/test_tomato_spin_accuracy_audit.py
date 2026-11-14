import unittest
from tomato_spin_accuracy_audit import violations,FIELDS,LIMITS
from tomato_isaac_startup_guard import worker_passed

class SpinAuditTests(unittest.TestCase):
    def test_failed_com_gate_stays_failed(self):
        s={f:0. for f in FIELDS.values()};s['com_position_error_m']=1.04146e-7
        self.assertEqual(violations(s,True),['com_position_m'])
        self.assertEqual(LIMITS['com_position_m'],1e-7)
    def test_disabled_control_still_checks_translation(self):
        s={f:0. for f in FIELDS.values()};s['angular_velocity_error_rad_s']=1.
        self.assertEqual(violations(s,False),[])
        self.assertIn('angular_velocity_rad_s',violations(s,True))
    def test_nonfinite_is_not_a_valid_audit(self):
        s={f:0. for f in FIELDS.values()};s['relative_energy_drift']=float('nan')
        with self.assertRaises(ValueError):violations(s,True)
    def test_guard_means_collection_completed_not_physics_pass(self):
        for factor in (1,2,4):
            r=dict(shutdown_requested=True,diagnostic_passed=True,audit_measurements_completed=True,
                audit_cases_completed=3,refinement=factor,physx_steps=16*factor,newton_steps=0,cuda_state_echoes=48*factor,
                physical_accuracy_passed=False)
            self.assertTrue(worker_passed(r,'spin_audit_'+str(factor)))
            self.assertFalse(worker_passed(dict(r,physx_steps=1),'spin_audit_'+str(factor)))
            self.assertFalse(worker_passed(dict(r,audit_measurements_completed=False),'spin_audit_'+str(factor)))
