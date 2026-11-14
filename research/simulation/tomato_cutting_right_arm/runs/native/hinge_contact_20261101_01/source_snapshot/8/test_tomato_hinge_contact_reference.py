import unittest,math
from tomato_hinge_contact_reference import expected_contact
from tomato_hinge_reference import expected_pulse
from tomato_isaac_startup_guard import worker_passed

class HingeContactTests(unittest.TestCase):
    def test_native_side_geometry_and_hinge_angular_balance(self):
        dt=1/2400;mp=.01
        c=expected_contact([.01,0,0,0,0,0,1],[.014,.004,0],mp,.005,1750.,dt)
        e=expected_pulse(.02,.0001,[.01,0,0],c['wrench'][:3],c['wrench'][3:],[0,0,1],dt)
        self.assertLess(e['joint_velocity_rad_s'],0.)
        self.assertAlmostEqual(e['generalized_effort_nm'],-.014*c['force'][1])
        self.assertAlmostEqual(e['effective_inertia_kg_m2']*e['joint_velocity_rad_s']+.014*mp*c['velocity'][1],0.)
    def test_rotated_contact_same_joint_effort(self):
        s=math.sqrt(.5);dt=1/2400
        a=expected_contact([.01,0,0,0,0,0,1],[.014,.004,0],.01,.005,1750.,dt)
        b=expected_contact([0,.01,0,0,0,s,s],[-.004,.014,0],.01,.005,1750.,dt)
        self.assertAlmostEqual(a['wrench'][5],b['wrench'][5])
        self.assertAlmostEqual(b['force'][0],-a['force'][1])
    def test_clear_geometry_not_a_contact(self):
        with self.assertRaises(ValueError):expected_contact([.01,0,0,0,0,0,1],[.014,.008,0],.01,.005,1750.,1/2400)
    def test_guard_scope(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,hinge_contact_checks_passed=True,
            hinge_contact_cases_completed=2,controlled_steps=2,newton_steps=4,cuda_state_echoes=6,clear_controls_passed=2)
        self.assertTrue(worker_passed(r,'hinge_contact'))
        for k,v in [('controlled_steps',3),('newton_steps',2),('cuda_state_echoes',4),('clear_controls_passed',0)]:
            self.assertFalse(worker_passed(dict(r,**{k:v}),'hinge_contact'))
