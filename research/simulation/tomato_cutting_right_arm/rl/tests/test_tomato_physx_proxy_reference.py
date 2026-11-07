import unittest
from tomato_physx_proxy_reference import check_pulse,check_coast
from tomato_isaac_startup_guard import worker_passed


class PhysxProxyReferenceTests(unittest.TestCase):
    def test_known_linear_and_angular_impulses(self):
        r=check_pulse([0.]*6,[.125,0.,0.,0.,0.,-.001],[3.,0.,0.],[0.,0.,-.0012],.02,.001,1/1200)
        self.assertLess(r['linear_velocity_error_m_s'],1e-15)
        self.assertLess(r['angular_velocity_error_rad_s'],1e-15)

    def test_wrong_frame_or_double_moment_rejected(self):
        for after in ([0.,.125,0.,0.,0.,-.001],[.125,0.,0.,0.,0.,-.002]):
            with self.assertRaises(ValueError):check_pulse([0.]*6,after,[3.,0.,0.],[0.,0.,-.0012],.02,.001,1/1200)

    def test_stale_force_would_fail_coast_check(self):
        v=[.125,0.,0.,0.,0.,-.001]
        self.assertEqual(check_coast(v,v)['linear_velocity_change_m_s'],0.)
        with self.assertRaises(ValueError):check_coast(v,[.25,0.,0.,0.,0.,-.002])

    def test_nonfinite_or_bad_mass_refused(self):
        with self.assertRaises(ValueError):check_pulse([0.]*6,[0.]*6,[0.]*3,[0.]*3,0.,.001,1/1200)
        with self.assertRaises(ValueError):check_coast([0.]*6,[float('nan')]*6)

    def test_guard_requires_both_echoes_and_exact_controlled_steps(self):
        r={'diagnostic_passed':True,'shutdown_requested':True,'physx_proxy_cases_completed':2,
           'controlled_steps':2,'cuda_state_echoes_completed':2,'physx_proxy_checks_passed':True}
        self.assertTrue(worker_passed(r,'physx_proxy'))
        for key,value in [('controlled_steps',3),('cuda_state_echoes_completed',1),('physx_proxy_checks_passed',False)]:
            self.assertFalse(worker_passed(dict(r,**{key:value}),'physx_proxy'))
        self.assertFalse(worker_passed(r,'dynamic_proxy'))


if __name__=='__main__':unittest.main()
