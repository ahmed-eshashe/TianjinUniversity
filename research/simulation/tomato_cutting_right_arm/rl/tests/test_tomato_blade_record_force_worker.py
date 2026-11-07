import copy
import unittest
from tomato_blade_record_force_worker import stationary_checks
from tomato_isaac_startup_guard import worker_passed


def fixture():
    payload={'soft_contact_count':[1],'particle_q_world_m':[[0.,-.001,0.]],'arrays':{
        'soft_contact_normal':[[0.,1.,0.]],'soft_contact_indices':[[0,-1,-1]],
        'soft_contact_barycentric':[[1.,0.,0.]],'soft_contact_body_pos':[[0.,0.,0.]],
        'soft_contact_body_vel':[[0.,0.,0.]]}}
    raw={'ke':[1750.],'material_ke':[1750.],'kd':[55.],'mu':[0.],
         'force':[[0.,1.75,0.]],'wrench':[[0.,-1.75,0.,0.,0.,0.]],
         'hessian':[[[0.,0.,0.],[0.,1750.,0.],[0.,0.,0.]]],'rigid_point':[[0.,0.,0.]]}
    return payload,raw


class BladeForceReferenceTests(unittest.TestCase):
    def test_known_force_and_unchanged_inputs(self):
        p,r=fixture();before=copy.deepcopy((p,r));result=stationary_checks(p,r)
        self.assertLess(result['force_error_n'],1e-6);self.assertEqual((p,r),before)

    def test_wrong_force_sign_rejected(self):
        p,r=fixture();r['force'][0][1]*=-1
        with self.assertRaises(ValueError):stationary_checks(p,r)

    def test_wrong_material_cache_rejected(self):
        p,r=fixture();r['ke']=[100.]
        with self.assertRaises(ValueError):stationary_checks(p,r)

    def test_wrong_moment_and_nonfinite_hessian_rejected(self):
        p,r=fixture();r['wrench'][0][3]=.01
        with self.assertRaises(ValueError):stationary_checks(p,r)
        p,r=fixture();r['hessian'][0][0][0]=float('nan')
        with self.assertRaises(ValueError):stationary_checks(p,r)

    def test_clear_or_moving_records_cannot_use_stationary_reference(self):
        p,r=fixture();p['particle_q_world_m'][0][1]=.001
        with self.assertRaises(ValueError):stationary_checks(p,r)
        p,r=fixture();p['arrays']['soft_contact_body_vel'][0][0]=1.
        with self.assertRaises(ValueError):stationary_checks(p,r)

    def test_guard_does_not_cross_qualify_force_free_modes(self):
        r={'diagnostic_passed':True,'shutdown_requested':True,'blade_force_cases_completed':3,
           'stationary_force_checks_passed':True,'mechanical_steps':0,'force_evaluations':2}
        self.assertTrue(worker_passed(r,'blade_record_forces'))
        for key,value in [('force_evaluations',3),('mechanical_steps',1),('stationary_force_checks_passed',False)]:
            self.assertFalse(worker_passed(dict(r,**{key:value}),'blade_record_forces'))
        self.assertFalse(worker_passed(r,'blade_record_roundtrip'))


if __name__=='__main__':unittest.main()
