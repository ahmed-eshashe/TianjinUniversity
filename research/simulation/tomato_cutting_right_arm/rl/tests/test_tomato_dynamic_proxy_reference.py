import unittest
from tomato_dynamic_proxy_reference import reference_step,assess_step


class DynamicProxyReferenceTests(unittest.TestCase):
    initial={'particle_z':.001,'body_z':0.,'particle_vz':0.,'body_vz':0.}
    parameters=(.01,.02,1750.,.002,1/1200)

    def test_free_pair_momentum_and_opposite_mass_weighted_motion(self):
        final=reference_step(self.initial,*self.parameters)
        self.assertAlmostEqual(.01*final['particle_vz']+.02*final['body_vz'],0.)
        self.assertAlmostEqual(final['particle_vz'],-2*final['body_vz'])
        self.assertGreater(final['particle_z'],.001);self.assertLess(final['body_z'],0.)

    def test_numerical_energy_loss_has_expected_positive_terms(self):
        final=reference_step(self.initial,*self.parameters);result=assess_step(self.initial,final,*self.parameters)
        self.assertLess(result['energy_change_j'],0.)
        self.assertGreater(result['velocity_numerical_dissipation_j'],0.)
        self.assertGreater(result['position_numerical_dissipation_j'],0.)
        self.assertLess(result['energy_identity_residual_j'],1e-15)

    def test_backward_euler_work_includes_velocity_defect(self):
        result=assess_step(self.initial,reference_step(self.initial,*self.parameters),*self.parameters)
        self.assertAlmostEqual(result['contact_work_backward_euler_j'],2*result['kinetic_final_j'])
        self.assertLess(result['work_identity_residual_j'],1e-15)

    def test_clear_control_stays_at_rest(self):
        initial=dict(self.initial,particle_z=.003);final=reference_step(initial,*self.parameters)
        self.assertEqual(final['contact_force_n'],0.)
        result=assess_step(initial,final,*self.parameters);self.assertEqual(result['energy_change_j'],0.)

    def test_held_body_or_wrong_reaction_sign_rejected(self):
        final=reference_step(self.initial,*self.parameters)
        with self.assertRaises(ValueError):assess_step(self.initial,dict(final,body_z=0.,body_vz=0.),*self.parameters)
        with self.assertRaises(ValueError):assess_step(self.initial,dict(final,body_vz=-final['body_vz']),*self.parameters)

    def test_invalid_mass_refused(self):
        with self.assertRaises(ValueError):reference_step(self.initial,0.,.02,1750.,.002,1/1200)


if __name__=='__main__':unittest.main()
