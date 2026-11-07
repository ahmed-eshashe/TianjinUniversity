import math,unittest
from tomato_offset_contact_reference import expected_contact,validate_wrench,world_point,rotation_vector
from tomato_isaac_startup_guard import worker_passed

class OffsetContactTests(unittest.TestCase):
    def test_identity_off_centre_torque(self):
        e=expected_contact([0,0,0,0,0,0,1],[0,0,0],[.004,.003,.001],.01,1750.,.002,1/1200)
        f=e['soft_force'][2]
        self.assertAlmostEqual(e['torque'][0],-.003*f);self.assertAlmostEqual(e['torque'][1],.004*f)
        validate_wrench(e,e['soft_force'],e['rigid_point'],e['reaction_force']+e['torque'])
    def test_rotated_offset_com(self):
        s=math.sqrt(.5);p=[0,.05,0,0,s,0,s];local=[.002,-.001,.0005]
        e=expected_contact(p,local,world_point(p,[.004,.003,.001]),.01,1750.,.002,1/1200)
        self.assertGreater(e['soft_force'][0],1.)
        self.assertAlmostEqual(e['torque'][1],.002*e['soft_force'][0])
        self.assertAlmostEqual(e['torque'][2],.004*e['soft_force'][0])
        wrong=expected_contact(p,[0,0,0],world_point(p,[.004,.003,.001]),.01,1750.,.002,1/1200)
        with self.assertRaises(ValueError):validate_wrench(e,e['soft_force'],e['rigid_point'],e['reaction_force']+wrong['torque'])
    def test_rotation_world_increment(self):
        a=.01;s=math.sqrt(.5)
        self.assertAlmostEqual(rotation_vector([0,0,0,1],[math.sin(a/2),0,0,math.cos(a/2)])[0],a)
        self.assertLess(math.dist(rotation_vector([0,s,0,s],[0,s,0,s]),[0,0,0]),1e-15)
    def test_bad_contact_refused(self):
        with self.assertRaises(ValueError):expected_contact([0,0,0,0,0,0,1],[0,0,0],[0,0,.003],.01,1750.,.002,1/1200)
    def test_guard_counts(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,offset_contact_checks_passed=True,
            offset_contact_cases_completed=2,newton_steps=2,physx_steps=1)
        self.assertTrue(worker_passed(r,'offset_contact'))
        for k in ('newton_steps','physx_steps','offset_contact_cases_completed'):
            self.assertFalse(worker_passed(dict(r,**{k:9}),'offset_contact'))
