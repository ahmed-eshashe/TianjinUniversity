import unittest
from tomato_hinge_reference import expected_pulse,check
from tomato_isaac_startup_guard import worker_passed

class HingeTests(unittest.TestCase):
    def test_effective_inertia_and_positive_joint_impulse(self):
        r=expected_pulse(.02,.0001,[.01,0,0],[0,3,0],[0,0,.0012],[0,0,1],1/2400)
        self.assertAlmostEqual(r['effective_inertia_kg_m2'],.000102)
        self.assertAlmostEqual(r['generalized_effort_nm'],.0312)
        check(r,.000102,r['joint_position_rad'],r['joint_velocity_rad_s'])
    def test_rotated_world_force_is_equivalent(self):
        a=expected_pulse(.02,.0001,[.01,0,0],[0,3,0],[0,0,.0012],[0,0,1],1/2400)
        b=expected_pulse(.02,.0001,[0,.01,0],[-3,0,0],[0,0,.0012],[0,0,1],1/2400)
        self.assertEqual(a,b)
    def test_missing_lever_moment_rejected(self):
        r=expected_pulse(.02,.0001,[.01,0,0],[0,3,0],[0,0,.0012],[0,0,1],1/2400)
        with self.assertRaises(ValueError):check(r,.000102,0.,(1/2400)*.0012/.000102)
    def test_guard_contract(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,hinge_checks_passed=True,hinge_cases_completed=2,
            controlled_steps=2,cuda_state_echoes=4,newton_steps=0)
        self.assertTrue(worker_passed(r,'hinge_interface'))
        for k,v in [('controlled_steps',3),('cuda_state_echoes',3),('hinge_checks_passed',False)]:
            self.assertFalse(worker_passed(dict(r,**{k:v}),'hinge_interface'))
