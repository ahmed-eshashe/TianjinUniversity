import unittest,math
from tomato_bent_contact_reference import expected_response,coast_velocity
from tomato_two_joint_sequence_reference import geometry
from tomato_two_joint_reference import check,reference
from tomato_isaac_startup_guard import worker_passed
class BentTests(unittest.TestCase):
    def test_bent_matrix_and_rotated_response(self):
        q=[math.pi/6,-math.pi/3];a=expected_response(0,q,[0,-2,0,0,0,-.008],1/2400)
        b=expected_response(math.pi/2,q,[2,0,0,0,0,-.008],1/2400)
        self.assertAlmostEqual(a['matrix'][0][0],.000216)
        self.assertAlmostEqual(a['matrix'][0][1],.000104)
        for x,y in zip(a['velocity'],b['velocity']):self.assertAlmostEqual(x,y)
        check(a,a['matrix'],a['jacobian'],a['position'],a['velocity'])
    def test_straight_matrix_rejected(self):
        a=expected_response(0,[.5,-1.],[0,-2,0,0,0,-.008],1/2400)
        with self.assertRaises(ValueError):check(a,reference()['matrix'],a['jacobian'],a['position'],a['velocity'])
    def test_unforced_bent_velocity_evolves(self):
        v=[.2,-.1];self.assertNotEqual(coast_velocity([.5,-1.],v,1/2400),v)
    def test_guard(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,bent_contact_checks_passed=True,bent_contact_cases_completed=2,controlled_steps=2,newton_steps=4,cuda_state_echoes=6,clear_controls_passed=2)
        self.assertTrue(worker_passed(r,'bent_contact'))
        for k,v in [('controlled_steps',3),('newton_steps',3),('clear_controls_passed',1)]:self.assertFalse(worker_passed(dict(r,**{k:v}),'bent_contact'))
