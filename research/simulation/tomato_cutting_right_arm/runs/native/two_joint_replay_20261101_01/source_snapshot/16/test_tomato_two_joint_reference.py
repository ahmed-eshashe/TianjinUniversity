import math,unittest
from tomato_two_joint_reference import reference,check
from tomato_isaac_startup_guard import worker_passed
class TwoJointTests(unittest.TestCase):
    def test_coupled_response(self):
        r=reference();self.assertAlmostEqual(r['matrix'][0][0],.000220)
        self.assertAlmostEqual(r['effort'][0],.0912);self.assertAlmostEqual(r['effort'][1],.0312)
        self.assertGreater(r['velocity'][0],0);self.assertLess(r['velocity'][1],0)
        check(r,r['matrix'],r['jacobian'],r['position'],r['velocity'])
    def test_rotation(self):
        a=reference();b=reference(math.pi/2)
        for k in ('matrix','effort','velocity','position'):self.assertEqual(a[k],b[k])
    def test_independent_joint_approximation_rejected(self):
        r=reference();wrong=[r['effort'][i]/r['matrix'][i][i]/2400 for i in range(2)]
        with self.assertRaises(ValueError):check(r,r['matrix'],r['jacobian'],r['position'],wrong)
    def test_guard_contract(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,two_joint_checks_passed=True,two_joint_cases_completed=2,controlled_steps=2,cuda_state_echoes=4,newton_steps=0)
        self.assertTrue(worker_passed(r,'two_joint_interface'))
        for k,v in [('controlled_steps',3),('cuda_state_echoes',3),('two_joint_checks_passed',False),('newton_steps',1)]:self.assertFalse(worker_passed(dict(r,**{k:v}),'two_joint_interface'))
