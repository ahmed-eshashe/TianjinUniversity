import unittest
from tomato_bonds import CohesiveLaw,DamageState
from tomato_surface_cohesion import update_surface_damage
from tomato_blade_damage import fracture_loss
from tomato_cohesive_evolution_reference import evolve_patch,fracture_dissipation

# At most twelve top-level constitutive evaluations: five paired evolution
# comparisons/refusals and one paired fracture-loss comparison.
class EvolutionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.law=CohesiveLaw(100.,.01,10.,.02,0.)
        self.k=[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]]
    def compare(self,gap,state,eligible):
        new=evolve_patch(self.law,state,[gap],[1.],self.k,eligible=eligible)
        old=update_surface_damage(self.law,state,[gap],[1.],self.k,eligible=eligible)
        self.assertAlmostEqual(new['trial_state'].kappa_m,old.kappa_m,places=14)
        self.assertAlmostEqual(new['trial_state'].damage,old.damage,places=14)
        self.assertGreaterEqual(new['fracture_increment_j'],0.)
        self.assertFalse(new['native_runtime_validated']);return new
    def test_no_contact_freezes_history(self):
        s=DamageState();r=self.compare([.01,0.,0.],s,False);self.assertIs(r['trial_state'],s)
    def test_loading(self):self.compare([.002,.001,0.],DamageState(),True)
    def test_unloading_no_healing(self):
        s=DamageState(.003,.9);r=self.compare([.0001,0.,0.],s,True);self.assertEqual(r['trial_state'],s);self.assertEqual(r['fracture_increment_j'],0.)
    def test_full_failure(self):
        r=self.compare([.01,0.,0.],DamageState(),True);self.assertEqual(r['trial_state'].damage,1.)
    def test_unsupported_compression_shear_both_refuse(self):
        with self.assertRaises(ValueError):evolve_patch(self.law,DamageState(),[[-.001,.001,0.]],[1.],self.k,eligible=True)
        with self.assertRaises(ValueError):update_surface_damage(self.law,DamageState(),[[-.001,.001,0.]],[1.],self.k,eligible=True)
    def test_exact_fracture_energy_cap(self):
        s=DamageState(.1,1.);a=fracture_dissipation(self.law,s);b=fracture_loss(self.law,s)
        self.assertAlmostEqual(a,b,places=14);self.assertAlmostEqual(a,self.law.area_m2*self.law.fracture_energy_j_m2,places=14)
