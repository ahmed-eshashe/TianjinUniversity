"""Blade eligibility, analytic dissipation and tentative-history checks."""
import json,sys,unittest
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix,eye
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_blade_damage import EvolvingCohesion,fracture_loss,edge_history,contact_eligibility,wedge_geometry
from tomato_bonds import CohesiveLaw,DamageState,update_damage
from tomato_coupled_contact import cut_pairs,solve_contact
from test_tomato_coupled_contact import Quadratic


class BladeDamageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=Path(__file__).resolve().parents[2]/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json'
        cls.design=json.loads(path.read_text());cls.points=np.asarray([n['position_m'] for n in cls.design['nodes']]);cls.pairs=cut_pairs(cls.design)
        cls.cohesion=EvolvingCohesion(cls.design,cls.pairs)

    def test_left_blade_unilateral_sign_and_no_adhesion(self):
        points=np.zeros((1,3));a=csr_matrix([[-1.,0.,0.]])
        x,lam,_,_,ok,*_=solve_contact(Quadratic(1.),points,points,{},a,np.zeros(1),[['blade_left',0]])
        self.assertTrue(ok);self.assertAlmostEqual(x[0,0],0.);self.assertAlmostEqual(lam[0],1.)
        x,lam,_,_,ok,*_=solve_contact(Quadratic(-1.),points,points,{},a,np.zeros(1),[['blade_left',0]])
        self.assertTrue(ok);self.assertAlmostEqual(x[0,0],-1.);self.assertEqual(lam[0],0.)

    def test_roundoff_cut_overlap_does_not_bind_incompatible_wedge(self):
        points=np.zeros((2,3));initial=points.copy();initial[0,0]=1e-14
        a=csr_matrix([[-1.,0.,0.,1.,0.,0.],[-1.,0.,0.,0.,0.,0.],[0.,0.,0.,1.,0.,0.]])
        labels=[['cut',0,1],['blade_left',0],['blade',1]]
        x,lam,_,_,ok,*_=solve_contact(Quadratic(0.),points,initial,{},a,np.array([0.,.1,.1]),labels)
        self.assertTrue(ok);np.testing.assert_allclose(x[:,0],[-.1,.1],atol=1e-12)
        np.testing.assert_allclose(lam,[0.,.1,.1],atol=1e-12)

    def test_wedge_faces_replace_only_redundant_closed_cut_constraints(self):
        top=self.points[self.pairs[:,0],2].max()
        A,b,_,_,width=wedge_geometry(self.design,self.points,self.pairs,top-.001)
        n=len(self.pairs);self.assertTrue((width>0).any());self.assertTrue((width==0).any())
        np.testing.assert_array_equal(b[:n],np.where(width>0,-1.,0.))
        # Feasible blade halfspaces imply the stronger positive cut gap.
        x=self.points.copy();x[self.pairs[:,0],0]-=width/2;x[self.pairs[:,1],0]+=width/2
        self.assertGreaterEqual(float((A@x.ravel()-b).min()),-1e-12)
        np.testing.assert_allclose(x[self.pairs[:,1],0]-x[self.pairs[:,0],0],width,atol=1e-12)

    def test_contact_load_and_edge_history_both_required(self):
        n=len(self.pairs);hits=np.ones(n,dtype=bool);width=np.ones(n)*.001;lam=np.ones(3*n)
        self.assertTrue(contact_eligibility(self.cohesion,hits,lam,width).all())
        for h,l,w in [(hits*False,lam,width),(hits,lam*0,width),(hits,-lam,width),(hits,lam,width*0)]:
            self.assertFalse(contact_eligibility(self.cohesion,h,l,w).any())

    def test_miss_and_face_rub_have_no_edge_activation(self):
        empty=np.zeros(len(self.pairs),dtype=bool)
        for mode in ['miss','face_rub']:
            self.assertFalse(edge_history(self.points,self.pairs,1.,-1.,empty,mode=mode).any())
        self.assertTrue(edge_history(self.points,self.pairs,1.,-1.,empty).all())
        _,_,_,_,width=wedge_geometry(self.design,self.points,self.pairs,0.,mode='miss')
        self.assertFalse(width.any())

    def test_depth_or_edge_event_without_opening_does_not_damage(self):
        states=self.cohesion.trial_states(self.points,[DamageState()]*47,np.ones(47,dtype=bool))
        self.assertTrue(all(s==DamageState() for s in states))

    def test_tentative_updates_do_not_mutate_committed_states(self):
        old=[DamageState() for _ in range(47)];x=self.points.copy();x[self.pairs[:,1],0]+=.002
        trial=self.cohesion.trial_states(x,old,np.ones(47,dtype=bool))
        self.assertTrue(all(s.damage>0 for s in trial));self.assertTrue(all(s==DamageState() for s in old))
        self.assertTrue(all(s==DamageState() for s in self.cohesion.states))
        rejected=self.cohesion.trial_states(self.points,old,np.ones(47,dtype=bool))
        self.assertEqual(rejected,old)

    def test_preloaded_face_rub_cannot_trigger_damage(self):
        x=self.points.copy();x[self.pairs[:,1],0]+=.003
        n=len(self.pairs)
        eligible=contact_eligibility(self.cohesion,np.zeros(n,dtype=bool),np.ones(3*n),np.ones(n)*.003)
        old=[DamageState()]*47
        self.assertEqual(self.cohesion.trial_states(x,old,eligible),old)

    def test_subthreshold_history_is_retained(self):
        x=self.points.copy();x[self.pairs[:,1],0]+=.0005
        trial=self.cohesion.trial_states(x,[DamageState()]*47,np.ones(47,dtype=bool))
        self.assertTrue(all(s.damage==0. and s.kappa_m>0. for s in trial))

    def test_exact_fracture_integral_and_unloading(self):
        for patch in self.cohesion.patches:
            law=patch['law'];state=DamageState()
            for q in np.linspace(0,law.failure_m,11):
                state=update_damage(law,state,float(q),eligible=True)
            self.assertAlmostEqual(fracture_loss(law,state),law.area_m2*law.fracture_energy_j_m2,places=14)
            unloaded=update_damage(law,state,0.,eligible=True)
            self.assertEqual(unloaded,state);self.assertEqual(fracture_loss(law,unloaded),fracture_loss(law,state))

    def test_held_geometry_does_not_accumulate_damage_or_dissipation(self):
        old=[DamageState() for _ in range(47)];x=self.points.copy();x[self.pairs[:,1],0]+=.002
        one=self.cohesion.trial_states(x,old,np.ones(47,dtype=bool));two=self.cohesion.trial_states(x,one,np.ones(47,dtype=bool))
        self.assertEqual(one,two);self.assertEqual(self.cohesion.dissipation(one),self.cohesion.dissipation(two))

    def test_delayed_activation_energy_jump_is_not_fracture_integral(self):
        law=self.cohesion.patches[0]['law'];q=.003
        state=update_damage(law,DamageState(),q,eligible=True)
        jump=.5*law.stiffness_n_m*q*q*state.damage
        self.assertGreater(jump,fracture_loss(law,state))

    def test_history_boundary_uses_loading_side_tangent(self):
        c=EvolvingCohesion(self.design,self.pairs);ok=np.ones(47,dtype=bool)
        x=self.points.copy();x[self.pairs[:,1],0]+=.002
        c.states=c.trial_states(x,[DamageState()]*47,ok);old=list(c.states)
        base=c.evaluate(x,tangent=True);H=c.algorithmic_tangent(x,base['tangent_n_m'],old,ok)
        v=np.zeros_like(x);v[self.pairs[:,1],0]=1.;eps=1e-8
        c.states=c.trial_states(x+eps*v,old,ok);a=c.evaluate(x+eps*v)['gradient_n']
        np.testing.assert_allclose((a-base['gradient_n']).ravel()/eps,H@v.ravel(),rtol=1e-7,atol=1e-6)
        unloaded=x-.0005*v;c.states=c.trial_states(unloaded,old,ok)
        elastic=c.evaluate(unloaded,tangent=True)['tangent_n_m']
        self.assertEqual((c.algorithmic_tangent(unloaded,elastic,old,ok)-elastic).nnz,0)

    def test_softening_tangent_matches_loading_finite_difference(self):
        c=EvolvingCohesion(self.design,self.pairs);old=[DamageState()]*47;ok=np.ones(47,dtype=bool)
        x=self.points.copy();x[self.pairs[:,1],0]+=.002
        c.states=c.trial_states(x,old,ok);base=c.evaluate(x,tangent=True)
        H=c.algorithmic_tangent(x,base['tangent_n_m'],old,ok)
        v=np.zeros_like(x);v[self.pairs[:,1],0]=1.;eps=1e-8
        c.states=c.trial_states(x+eps*v,old,ok);a=c.evaluate(x+eps*v)['gradient_n']
        c.states=c.trial_states(x-eps*v,old,ok);b=c.evaluate(x-eps*v)['gradient_n']
        np.testing.assert_allclose((a-b).ravel()/(2*eps),H@v.ravel(),rtol=1e-7,atol=1e-6)


if __name__=='__main__':unittest.main()
