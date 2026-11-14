import math,unittest
from tomato_two_joint_contact_reference import expected_response
from tomato_two_joint_reference import check
from tomato_hinge_contact_reference import expected_contact
from tomato_isaac_startup_guard import worker_passed
class ContactTests(unittest.TestCase):
    def test_contact_and_total_angular_impulse(self):
        dt=1/2400;c=expected_contact([.03,0,0,0,0,0,1],[.034,.004,0],.01,.005,1750.,dt)
        r=expected_response(0,c['wrench'],dt)
        chain=sum(m*v for m,v in zip(r['matrix'][0],r['velocity']))
        particle=.034*.01*c['velocity'][1]
        self.assertAlmostEqual(chain+particle,0)
        check(r,r['matrix'],r['jacobian'],r['position'],r['velocity'])
    def test_rotated_wrench(self):
        a=expected_response(0,[0,-2,0,0,0,-.008],1/2400)
        b=expected_response(math.pi/2,[2,0,0,0,0,-.008],1/2400)
        for x,y in zip(a['velocity'],b['velocity']):self.assertAlmostEqual(x,y)
    def test_wrong_reaction_sign_rejected(self):
        r=expected_response(0,[0,-2,0,0,0,-.008],1/2400)
        with self.assertRaises(ValueError):check(r,r['matrix'],r['jacobian'],r['position'],[-x for x in r['velocity']])
    def test_guard(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,two_joint_contact_checks_passed=True,two_joint_contact_cases_completed=2,controlled_steps=2,newton_steps=4,cuda_state_echoes=6,clear_controls_passed=2)
        self.assertTrue(worker_passed(r,'two_joint_contact'))
        for k,v in [('controlled_steps',3),('newton_steps',3),('cuda_state_echoes',5),('clear_controls_passed',1)]:self.assertFalse(worker_passed(dict(r,**{k:v}),'two_joint_contact'))
