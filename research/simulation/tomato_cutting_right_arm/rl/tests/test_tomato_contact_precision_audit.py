"""Rounding controls independent of any native simulator."""
import unittest
from fractions import Fraction
from tomato_contact_precision_audit import round32, fma32, interpolate32, separated_reference_checks


class PrecisionAuditTests(unittest.TestCase):
    def test_halfway_rounds_to_even(self):
        self.assertEqual(round32(1+Fraction(1, 2**24)), 1.)
        self.assertEqual(round32(1+Fraction(3, 2**24)), 1+2**-22)

    def test_fused_cancellation_keeps_product_residual(self):
        a=1+2**-23; b=1-2**-23
        self.assertEqual(fma32(a,b,-1.), -2**-46)
        self.assertEqual(round32(round32(Fraction(a)*Fraction(b))-1), 0.)

    def test_translation_amplifies_nonunit_weight_sum(self):
        points=[[0.,0.,0.],[1.,0.,0.]]; weights=[.5, .5+2**-23, 0.]
        base=interpolate32(points,[0,1,-1],weights,fused=True)
        moved=interpolate32([[1.,0.,0.],[2.,0.,0.]],[0,1,-1],weights,fused=True)
        self.assertNotEqual(moved[0]-base[0], 1.)

    def test_padding_is_ignored(self):
        self.assertEqual(interpolate32([[1.,2.,3.]],[0,-1,-1],[1.,0.,0.],fused=True),[1.,2.,3.])

    def fixture(self):
        point=[0.,0.,round32(.001)]
        payload={'soft_contact_count':[1], 'particle_q_world_m':[point], 'arrays':{
            'soft_contact_normal':[[0.,0.,1.]], 'soft_contact_body_vel':[[0.,0.,0.]],
            'soft_contact_indices':[[0,-1,-1]], 'soft_contact_barycentric':[[1.,0.,0.]]}}
        comparison={'expected_mu':0., 'expected_ke':1750., 'expected_force_n':[0.,0.,1.75],
            'force_error_n':0., 'independent_penetration_m':.001,
            'record':{'corners':[0,-1,-1], 'barycentric':[1.,0.,0.], 'normal_world':[0.,0.,1.],
                      'soft_point_world_m':point},
            'native_arrays':{'rigid_point':[[0.,0.,round32(.002)]], 'force':[[0.,0.,1.7500001192092896]]}}
        return payload,comparison

    def test_wrong_native_force_rejected_despite_good_geometry(self):
        p,c=self.fixture()
        c['native_arrays']['force'][0][2]+=.01
        result=separated_reference_checks(p,c,surface_error_m=0.,normal_error=0.)
        self.assertTrue(result['geometry_passed'])
        self.assertFalse(result['arithmetic_passed'])

    def test_owned_in_memory_tuples_match_json_lists(self):
        p,c=self.fixture()
        for key in ('corners','barycentric','normal_world','soft_point_world_m'):
            c['record'][key]=tuple(c['record'][key])
        result=separated_reference_checks(p,c,surface_error_m=0.,normal_error=0.)
        self.assertTrue(result['geometry_passed'])
        self.assertTrue(result['arithmetic_passed'])

    def test_bad_geometry_rejected_despite_exact_arithmetic(self):
        p,c=self.fixture()
        result=separated_reference_checks(p,c,surface_error_m=2e-7,normal_error=0.)
        self.assertFalse(result['geometry_passed'])
        self.assertTrue(result['arithmetic_passed'])

    def test_historical_failure_remains_visible_when_separate_gates_pass(self):
        p,c=self.fixture(); c['force_error_n']=1.2e-5
        result=separated_reference_checks(p,c,surface_error_m=0.,normal_error=0.)
        self.assertTrue(result['geometry_passed'])
        self.assertTrue(result['arithmetic_passed'])
        self.assertFalse(result['historical_geometry_force_gate_passed'])


if __name__ == '__main__': unittest.main()
