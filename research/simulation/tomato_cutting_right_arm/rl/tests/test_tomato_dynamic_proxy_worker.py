import unittest
from tomato_isaac_startup_guard import worker_passed
from tomato_dynamic_proxy_worker import DT,ITERATIONS


class DynamicProxyScopeTests(unittest.TestCase):
    def test_two_one_step_fixtures_cannot_cross_qualify_other_modes(self):
        self.assertEqual(DT,1/1200);self.assertEqual(ITERATIONS,16)
        result={'shutdown_requested':True,'diagnostic_passed':True,'dynamic_proxy_cases_completed':2,
                'committed_steps':2,'dynamic_proxy_checks_passed':True}
        self.assertTrue(worker_passed(result,'dynamic_proxy'))
        for key,value in [('committed_steps',3),('dynamic_proxy_cases_completed',3),('dynamic_proxy_checks_passed',False)]:
            self.assertFalse(worker_passed(dict(result,**{key:value}),'dynamic_proxy'))
        self.assertFalse(worker_passed(result,'particle_scatter'))


if __name__=='__main__':unittest.main()
