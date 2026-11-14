import unittest
from tomato_thin_slab_reference import point_penalty, normalized_integral_reference, sample_slab


class ThinSlabTests(unittest.TestCase):
    h=.002
    length=.01
    stiffness=1750.

    def test_midplane_is_explicitly_ambiguous(self):
        result=point_penalty(0.,self.h,self.stiffness)
        self.assertIsNone(result['normal']);self.assertIsNone(result['force_n'])

    def test_one_sided_limits_have_opposite_force(self):
        positive=point_penalty(1e-12,self.h,self.stiffness)['force_n']
        negative=point_penalty(-1e-12,self.h,self.stiffness)['force_n']
        self.assertEqual(positive,-negative)
        self.assertAlmostEqual(positive,self.stiffness*self.h,places=8)

    def test_clear_and_touch_have_zero_force(self):
        for z in (self.h,2*self.h,-self.h,-2*self.h):
            self.assertEqual(point_penalty(z,self.h,self.stiffness)['force_n'],0.)

    def test_point_force_matches_negative_energy_gradient_off_medial_plane(self):
        z=.0007;eps=1e-8
        derivative=(point_penalty(z+eps,self.h,self.stiffness)['energy_j']-
                    point_penalty(z-eps,self.h,self.stiffness)['energy_j'])/(2*eps)
        self.assertAlmostEqual(-derivative,point_penalty(z,self.h,self.stiffness)['force_n'],places=8)

    def test_weighted_quadrature_matches_independent_integral_at_all_densities(self):
        reference=normalized_integral_reference(self.h,self.length,self.stiffness)
        for count in (1,2,4,8,16):
            result=sample_slab(self.h,self.length,self.stiffness,subdivisions_per_side=count)
            self.assertAlmostEqual(result['weighted_energy_j'],reference['energy_j'],places=15)
            for a,b in zip(result['weighted_endpoint_forces_n'],reference['endpoint_forces_n']):
                self.assertAlmostEqual(a,b,places=14)
            self.assertAlmostEqual(result['weight_sum'],self.h/self.length,places=14)

    def test_net_balance_does_not_hide_raw_sample_count_dependence(self):
        low=sample_slab(self.h,self.length,self.stiffness,subdivisions_per_side=1)
        high=sample_slab(self.h,self.length,self.stiffness,subdivisions_per_side=8)
        self.assertAlmostEqual(low['raw_net_force_n'],0.,places=12)
        self.assertAlmostEqual(high['raw_net_force_n'],0.,places=12)
        self.assertAlmostEqual(high['raw_endpoint_forces_n'][1]/low['raw_endpoint_forces_n'][1],8.)

    def test_integrated_endpoint_work_matches_energy_change(self):
        eps=1e-7;h=self.h;k=self.stiffness;L=self.length
        derivative=(normalized_integral_reference(h,L+eps,k)['energy_j']-
                    normalized_integral_reference(h,L-eps,k)['energy_j'])/(2*eps)
        forces=normalized_integral_reference(h,L,k)['endpoint_forces_n']
        self.assertAlmostEqual(-derivative,forces[1]-forces[0],places=9)

    def test_invalid_geometry_or_unbounded_sampling_refused(self):
        with self.assertRaises(ValueError):sample_slab(.02,.01,1750.)
        with self.assertRaises(ValueError):sample_slab(.002,.01,1750.,subdivisions_per_side=65)


if __name__=='__main__':unittest.main()
