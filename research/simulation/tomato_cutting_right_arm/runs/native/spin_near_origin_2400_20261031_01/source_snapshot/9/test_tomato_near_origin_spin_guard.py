import unittest
from tomato_isaac_startup_guard import worker_passed

class NearOriginGuardTests(unittest.TestCase):
    def test_requires_physical_accuracy_and_exact_scope(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,audit_measurements_completed=True,
            physical_accuracy_passed=True,near_origin_fixture=True,audit_cases_completed=3,refinement=2,
            physx_steps=32,newton_steps=0,cuda_state_echoes=96,gyro_control_distinguished=True)
        self.assertTrue(worker_passed(r,'near_origin_spin'))
        for k,v in [('physical_accuracy_passed',False),('near_origin_fixture',False),('refinement',4),
                    ('physx_steps',64),('newton_steps',1),('cuda_state_echoes',95),('gyro_control_distinguished',False)]:
            self.assertFalse(worker_passed(dict(r,**{k:v}),'near_origin_spin'))
        self.assertFalse(worker_passed(dict(r,shutdown_requested=False),'near_origin_spin'))
