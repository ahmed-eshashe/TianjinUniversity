"""Offline geometry and constitutive checks; no simulated blade or physical success."""
import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_bonds import (CohesiveLaw, DamageState, update_damage, scalar_response,
                          bundle_response, local_separation, update_bundle_damage)
from tomato_layout import build_layout, audit_layout, components


def synthetic_law(scale=1.):
    return CohesiveLaw(1000*scale,25e-6*scale,40000.,80.,.2*scale)


class ScalarBondTests(unittest.TestCase):
    def test_onset_and_failure_from_independent_triangle_area(self):
        law=synthetic_law()
        self.assertAlmostEqual(law.onset_m,.001)
        self.assertAlmostEqual(law.failure_m,.004)
        for x,expected in [(0.,0.),(.0005,.5),(.001,1.),(.002,2/3),(.004,0.)]:
            state=update_damage(law,DamageState(),x,eligible=True)
            self.assertAlmostEqual(scalar_response(law,state,x)['force_n'],expected)

    def test_fracture_work_and_damage_energy(self):
        law=synthetic_law(); state=DamageState(); work=0.; dissipated=0.; previous_f=0.; n=8000
        for i in range(1,n+1):
            x=law.failure_m*i/n
            new=update_damage(law,state,x,eligible=True)
            dissipated+=.5*law.stiffness_n_m*x*x*(new.damage-state.damage)
            force=scalar_response(law,new,x)['force_n']
            work+=(force+previous_f)/2*law.failure_m/n
            previous_f=force; state=new
        expected=.5*1.*.004  # Independent area under prescribed force-opening triangle.
        self.assertAlmostEqual(work,expected,places=10)
        self.assertLess(abs(dissipated/expected-1),.001)
        self.assertEqual(state.damage,1.)

    def test_no_contact_no_clock_or_depth_damage(self):
        law=synthetic_law(); state=DamageState()
        for _ in range(200):
            state=update_damage(law,state,1.,eligible=False)
        self.assertEqual(state,DamageState())

    def test_compression_alone_does_not_damage(self):
        law=synthetic_law()
        self.assertEqual(update_damage(law,DamageState(),-.02,eligible=True),DamageState())
        self.assertLess(scalar_response(law,DamageState(),-.001)['force_n'],0.)

    def test_unloading_and_contact_loss_cannot_heal(self):
        law=synthetic_law(); state=update_damage(law,DamageState(),.002,eligible=True)
        self.assertEqual(update_damage(law,state,0.,eligible=True),state)
        self.assertEqual(update_damage(law,state,1.,eligible=False),state)
        force=scalar_response(law,state,.001)['force_n']
        self.assertAlmostEqual(force,1/3)

    def test_broken_stiffness_and_damping_exact_zero(self):
        law=synthetic_law(); state=update_damage(law,DamageState(),.005,eligible=True)
        response=scalar_response(law,state,.01,10.)
        self.assertTrue(all(v==0 for v in response.values()))

    def test_patch_subdivision_preserves_budget(self):
        full=synthetic_law(); split=synthetic_law(.25)
        for x in [.0005,.001,.002,.003,.004]:
            f=scalar_response(full,update_damage(full,DamageState(),x,eligible=True),x)['force_n']
            q=scalar_response(split,update_damage(split,DamageState(),x,eligible=True),x)['force_n']
            self.assertAlmostEqual(f,4*q)
        self.assertAlmostEqual(full.fracture_energy_j_m2*full.area_m2,4*split.fracture_energy_j_m2*split.area_m2)

    def test_invalid_material_and_nonfinite_inputs_refused(self):
        for args in [(0.,1.,1.,1.,0.),(1000.,25e-6,40000.,1.,0.),(1000.,25e-6,40000.,80.,-1.)]:
            with self.assertRaises(ValueError):CohesiveLaw(*args)
        with self.assertRaises(ValueError):update_damage(synthetic_law(),DamageState(),float('nan'),eligible=True)
        with self.assertRaises(ValueError):update_damage(synthetic_law(),DamageState(damage=2),0.)


class BundleTests(unittest.TestCase):
    rest=[(.005,0.,0.),(.005,.005,0.),(.005,-.005,0.),(.005,0.,.005),(.005,0.,-.005)]
    def response(self,delta,state=DamageState()):
        current=[tuple(a+b for a,b in zip(v,delta)) for v in self.rest]
        return bundle_response(self.rest,current,[1000/3]*5,[.1]*5,state)

    def test_geometric_tangent_normal_and_shear(self):
        eps=1e-8
        self.assertAlmostEqual(self.response((eps,0,0))['force_n'][0]/eps,1000.,delta=.01)
        self.assertAlmostEqual(self.response((0,eps,0))['force_n'][1]/eps,1000/3,delta=.01)
        self.assertAlmostEqual(self.response((0,0,eps))['force_n'][2]/eps,1000/3,delta=.01)

    def test_zero_force_under_common_rigid_rotation(self):
        # A 90-degree rotation maps (x,y,z) to (-y,x,z), preserving all lengths.
        rotated=[(-v[1],v[0],v[2]) for v in self.rest]
        q=bundle_response(self.rest,rotated,[1000/3]*5,[.1]*5,DamageState())
        self.assertLess(math.sqrt(sum(x*x for x in q['force_n'])),1e-12)
        self.assertLess(q['stored_energy_j'],1e-20)

    def test_local_measure_removes_rigid_motion(self):
        identity=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
        rotated=((0.,1.,0.),(-1.,0.,0.),(0.,0.,1.))
        self.assertEqual(local_separation((.005,0.,0.),(0.,.005,0.),identity,rotated),(0.,0.))
        opening,shear=local_separation((.005,0.,0.),(0.,.006,.002),identity,rotated)
        self.assertAlmostEqual(opening,.001); self.assertAlmostEqual(shear,.002)
        with self.assertRaises(ValueError):local_separation((0,0,0),(0,0,0),identity,((2,0,0),(0,1,0),(0,0,1)))

    def test_complete_damage_removes_bundle_force_and_damping(self):
        q=bundle_response(self.rest,[(.01,0,0)]*5,[1.]*5,[100.]*5,DamageState(.01,1.),velocities=[(10.,0.,0.)]*5)
        self.assertEqual(q,{'force_n':[0.,0.,0.],'stored_energy_j':0.})

    def test_no_zero_length_spring_even_if_broken(self):
        with self.assertRaises(ValueError):bundle_response([(0.,0.,0.)],[(1.,0.,0.)],[1.],[0.],DamageState())
        with self.assertRaises(ValueError):bundle_response([(1.,0.,0.)],[(0.,0.,0.)],[1.],[0.],DamageState(damage=1.))

    def test_mixed_mode_history_no_healing(self):
        law=synthetic_law(); state=update_damage(law,DamageState(),0.,.002,eligible=True)
        self.assertGreater(state.damage,0)
        self.assertEqual(update_damage(law,state,-.001,0.,eligible=True),state)


class PatchEnergyTests(unittest.TestCase):
    rest = BundleTests.rest

    def integrate(self, direction, *, scale=1., n=4000, path=None):
        law=synthetic_law(scale); state=DamageState(); work=0.; loss=0.
        previous_delta=(0.,0.,0.); previous_force=[0.,0.,0.]
        for i in range(1,n+1):
            delta=path(i/n) if path else tuple(.012*i/n*x for x in direction)
            current=[tuple(a+b for a,b in zip(v,delta)) for v in self.rest]
            new=update_bundle_damage(law,state,self.rest,current,[1000/3*scale]*5,
                                     opening_m=delta[0],shear_m=math.hypot(delta[1],delta[2]),eligible=True)
            before=bundle_response(self.rest,current,[1000/3*scale]*5,[0.]*5,state)
            response=bundle_response(self.rest,current,[1000/3*scale]*5,[0.]*5,new)
            loss+=before['stored_energy_j']-response['stored_energy_j']
            work+=sum(.5*(a+b)*(x-y) for a,b,x,y in zip(previous_force,response['force_n'],delta,previous_delta))
            previous_delta=delta; previous_force=response['force_n']; state=new
        return state,work,loss

    def test_opening_energy(self):
        state,work,loss=self.integrate((1.,0.,0.))
        self.assertEqual(state.damage,1.)
        self.assertLess(abs(work/.002-1),.001)
        self.assertLess(abs(loss/.002-1),.005)

    def test_both_shear_axes_and_signs(self):
        for direction in [(0.,1.,0.),(0.,-1.,0.),(0.,0.,1.),(0.,0.,-1.)]:
            state,work,loss=self.integrate(direction)
            self.assertEqual(state.damage,1.)
            self.assertLess(abs(work/.002-1),.001)
            self.assertLess(abs(loss/.002-1),.005)

    def test_mixed_mode_and_nonproportional_loading(self):
        paths=[lambda t:(.0072*t,.0096*t,0.),
               lambda t:(min(.002,.008*t),max(0.,(t-.25))*.012,0.)]
        for path in paths:
            state,work,loss=self.integrate(None,path=path)
            self.assertEqual(state.damage,1.)
            self.assertLess(abs(work/.002-1),.001)
            self.assertLess(abs(loss/.002-1),.005)

    def test_unload_reload_path_work(self):
        def path(t):
            if t<.25:return (.008*t,0.,0.)
            if t<.5:return (.004-.008*t,0.,0.)
            return (.024*(t-.5),0.,0.)
        state,work,loss=self.integrate(None,path=path,n=8000)
        self.assertEqual(state.damage,1.)
        self.assertLess(abs(work/.002-1),.001)
        self.assertLess(abs(loss/.002-1),.005)

    def test_subdivision_shares_patch_budget(self):
        _,work,loss=self.integrate((.6,.8,0.))
        _,part_work,part_loss=self.integrate((.6,.8,0.),scale=.25)
        self.assertAlmostEqual(work,part_work*4)
        self.assertAlmostEqual(loss,part_loss*4)

    def test_gate_compression_and_unsupported_combination(self):
        law=synthetic_law(); current=[(v[0]+.005,v[1],v[2]) for v in self.rest]
        self.assertEqual(update_bundle_damage(law,DamageState(),self.rest,current,[1000/3]*5,
                                             opening_m=.005,shear_m=0.,eligible=False),DamageState())
        compressed=[(v[0]-.001,v[1],v[2]) for v in self.rest]
        self.assertEqual(update_bundle_damage(law,DamageState(),self.rest,compressed,[1000/3]*5,
                                             opening_m=-.001,shear_m=0.,eligible=True),DamageState())
        with self.assertRaises(ValueError):
            update_bundle_damage(law,DamageState(),self.rest,compressed,[1000/3]*5,
                                 opening_m=-.001,shear_m=.001,eligible=True)

    def test_rigid_rotation_and_post_failure_no_residual(self):
        law=synthetic_law(); rotated=[(-v[1],v[0],v[2]) for v in self.rest]
        self.assertEqual(update_bundle_damage(law,DamageState(),self.rest,rotated,[1000/3]*5,
                                             opening_m=0.,shear_m=0.,eligible=True),DamageState())
        broken,_,_=self.integrate((1.,0.,0.))
        response=bundle_response(self.rest,[(v[0]+.001,v[1],v[2]) for v in self.rest],
                                 [1000/3]*5,[100.]*5,broken,velocities=[(10.,0.,0.)]*5)
        self.assertEqual(response['force_n'],[0.,0.,0.])
        self.assertEqual(response['stored_energy_j'],0.)


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout=build_layout()

    def test_layout_audit(self):
        report=audit_layout(self.layout)
        self.assertTrue(report['passed'],report)

    def test_partial_cut_retains_single_connection(self):
        cross=[b['id'] for b in self.layout['bonds'] if b['kind']=='interface']
        self.assertEqual(len(components(self.layout,cross[:-1])),1)
        self.assertEqual(len(components(self.layout,cross)),2)

    def test_unregistered_diagonal_is_detected(self):
        bad=copy.deepcopy(self.layout)
        patch=next(p for p in bad['interface_patches'] if p['bond_ids'])
        patch['bond_ids'].pop()
        self.assertFalse(audit_layout(bad)['checks']['registered_once'])

    def test_fixture_cannot_constrain_slice(self):
        bad=copy.deepcopy(self.layout)
        bad['fixture']['node_ids'].append(next(n['id'] for n in bad['nodes'] if n['side']=='slice'))
        self.assertFalse(audit_layout(bad)['checks']['fixture_remainder_only'])

    def test_mass_and_area_match_independent_formulas(self):
        a=.0325; b=.0325; c=.0275; cut=-a+.010
        self.assertAlmostEqual(sum(n['mass_kg'] for n in self.layout['nodes']),4*math.pi*a*b*c/3*1000)
        self.assertAlmostEqual(sum(p['area_m2'] for p in self.layout['interface_patches']),math.pi*b*c*(1-(cut/a)**2))

    def test_resource_bounds_refuse_fine_grid(self):
        with self.assertRaises(ValueError):build_layout(spacing_m=.001)


if __name__=='__main__':
    unittest.main()
