"""Energy, derivative and unilateral split checks for the revised interface."""
import json
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_surface_cohesion import SurfaceCohesion,patch_response,update_surface_damage
from tomato_coupled_contact import cut_pairs
from tomato_bonds import DamageState


class SurfaceCohesionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2]
        d=json.loads((root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text())
        cls.design=d;cls.points=np.asarray([n['position_m'] for n in d['nodes']])
        cls.model=SurfaceCohesion(d,cut_pairs(d),0.)

    def test_all_patch_budgets_and_small_strain_tangents(self):
        self.assertEqual(len(self.model.patches),47)
        all_ids=np.concatenate([p['indices'] for p in self.model.patches])
        self.assertTrue(np.all((all_ids>=0)&(all_ids<257)))
        self.assertEqual(len(all_ids),47*8)
        for p in self.model.patches:
            self.assertAlmostEqual(p['weights'].sum(),1.)
            self.assertAlmostEqual(p['stiffness'][0,0],4e7*p['law'].area_m2)
            self.assertGreater(np.linalg.eigvalsh(p['stiffness']).min(),0.)

    def test_compression_has_zero_normal_energy_force_and_stiffness(self):
        for p in self.model.patches:
            g=np.zeros((len(p['indices']),3));g[:,0]=-.001
            r=patch_response(g,p['weights'],p['stiffness'],0.,tangent=True)
            self.assertEqual(r['energy_j'],0.)
            np.testing.assert_array_equal(r['gradient_n'],0.)
            np.testing.assert_array_equal(r['tangent_n_m'][:,0,:],0.)
            self.assertEqual(update_surface_damage(p['law'],DamageState(),g,p['weights'],p['stiffness'],eligible=True),DamageState())

    def test_bulk_compression_with_closed_faces_does_not_load_cohesion(self):
        x=self.points.copy();x[:,0]*=.95
        r=self.model.evaluate(x,tangent=True)
        self.assertEqual(r['energy_j'],0.)
        np.testing.assert_array_equal(r['gradient_n'],0.)

    def test_tensile_reference_stiffness_and_partial_damage(self):
        opening=1e-5
        for p in self.model.patches:
            gaps=np.tile([opening,0.,0.],(len(p['indices']),1))
            for damage in [0.,.5,1.]:
                r=patch_response(gaps,p['weights'],p['stiffness'],damage)
                expected=(1-damage)*p['law'].stiffness_n_m
                self.assertAlmostEqual(r['gradient_n'][:,0].sum(),expected*opening,places=12)
                self.assertAlmostEqual(r['energy_j'],.5*expected*opening**2,places=15)

    def test_compression_preserves_shear_and_has_no_normal_force(self):
        p=self.model.patches[0];g=np.zeros((len(p['indices']),3));g[:,1]=.0001
        a=patch_response(g,p['weights'],p['stiffness'],.5)
        g[:,0]=-.001;b=patch_response(g,p['weights'],p['stiffness'],.5)
        self.assertEqual(a['energy_j'],b['energy_j'])
        np.testing.assert_array_equal(a['gradient_n'],b['gradient_n'])
        self.assertGreater(b['energy_j'],0.)
        with self.assertRaises(ValueError):update_surface_damage(p['law'],DamageState(),g,p['weights'],p['stiffness'],eligible=True)

    def test_energy_gradient_and_hessian_finite_difference(self):
        rng=np.random.default_rng(8)
        for normal in [-.0001,.0001]:
            p=self.model.patches[5];n=len(p['indices']);g=rng.normal(0,.00003,(n,3));g[:,0]=normal
            v=rng.normal(size=g.shape);v/=np.linalg.norm(v);eps=1e-8
            r=patch_response(g,p['weights'],p['stiffness'],.5,tangent=True)
            a=patch_response(g+eps*v,p['weights'],p['stiffness'],.5)
            b=patch_response(g-eps*v,p['weights'],p['stiffness'],.5)
            self.assertAlmostEqual((a['energy_j']-b['energy_j'])/(2*eps),float(np.sum(r['gradient_n']*v)),places=10)
            np.testing.assert_allclose((a['gradient_n']-b['gradient_n'])/(2*eps),np.einsum('nij,nj->ni',r['tangent_n_m'],v),rtol=1e-8,atol=1e-8)

    def test_zero_opening_energy_and_force_continuity(self):
        p=self.model.patches[0];g=np.zeros((len(p['indices']),3));g[:,1]=.0001
        center=patch_response(g,p['weights'],p['stiffness'],0.)
        for sign in [-1,1]:
            g[:,0]=sign*1e-12;r=patch_response(g,p['weights'],p['stiffness'],0.)
            self.assertLess(abs(r['energy_j']-center['energy_j']),1e-18)
            self.assertLess(np.linalg.norm(r['gradient_n']-center['gradient_n']),1e-8)

    def test_assembled_surface_gradient_tangent_and_translation(self):
        x=self.points.copy();pairs=self.model.pairs
        x[pairs[:,1]]+=[.0001,.00002,-.00003]
        r=self.model.evaluate(x,tangent=True)
        rng=np.random.default_rng(13);v=np.zeros_like(x);v[pairs.reshape(-1)]=rng.normal(size=(pairs.size,3));v/=np.linalg.norm(v)
        eps=1e-8;a=self.model.evaluate(x+eps*v);b=self.model.evaluate(x-eps*v)
        self.assertAlmostEqual((a['energy_j']-b['energy_j'])/(2*eps),float(np.sum(r['gradient_n']*v)),places=9)
        np.testing.assert_allclose((a['gradient_n']-b['gradient_n']).ravel()/(2*eps),r['tangent_n_m']@v.ravel(),rtol=1e-7,atol=1e-7)
        np.testing.assert_allclose(r['gradient_n'].sum(axis=0),0.,atol=1e-12)
        self.assertLess(self.model.evaluate(self.points+[.1,.2,.3])['energy_j'],1e-25)

    def test_damage_eligibility_no_healing_and_broken_no_adhesion(self):
        p=self.model.patches[0];g=np.tile([.002,0.,0.],(len(p['indices']),1))
        zero=DamageState();self.assertEqual(update_surface_damage(p['law'],zero,g,p['weights'],p['stiffness']),zero)
        damaged=update_surface_damage(p['law'],zero,g,p['weights'],p['stiffness'],eligible=True)
        self.assertGreater(damaged.damage,0.)
        self.assertEqual(update_surface_damage(p['law'],damaged,g*0,p['weights'],p['stiffness'],eligible=True),damaged)
        r=patch_response(g,p['weights'],p['stiffness'],1.,tangent=True)
        self.assertEqual(r['energy_j'],0.);np.testing.assert_array_equal(r['gradient_n'],0.);np.testing.assert_array_equal(r['tangent_n_m'],0.)


if __name__=='__main__':unittest.main()
