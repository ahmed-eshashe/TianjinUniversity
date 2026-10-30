"""Analytic energy and contact-handoff regressions for damaged unloading."""
import json,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_unloading import ledger,damage_changes,withdrawal_guess
from tomato_blade_damage import EvolvingCohesion,wedge_geometry,edge_history,contact_eligibility
from tomato_coupled_contact import cut_pairs
from tomato_bonds import DamageState
from tomato_surface_cohesion import patch_response


class EnergyLedgerTests(unittest.TestCase):
    def test_unloading_returns_only_elastic_energy(self):
        s=ledger(0.,.3,-2.,initial_energy=2.,initial_dissipation=.3)
        self.assertTrue(s['passed']);self.assertEqual(s['new_fracture_dissipation_j'],0.)
        self.assertEqual(s['residual_j'],0.)
        # Refunding the old fracture loss must fail even though the faces close.
        self.assertFalse(ledger(0.,.3,-2.3,initial_energy=2.,initial_dissipation=.3)['passed'])

    def test_small_reclosure_is_not_normalized_by_old_fracture_loss(self):
        good=ledger(1e-6,.3,1e-6,initial_energy=0.,initial_dissipation=.3)
        bad=ledger(1e-6,.3,1.1e-6,initial_energy=0.,initial_dissipation=.3)
        self.assertTrue(good['passed']);self.assertFalse(bad['passed'])

    def test_new_damage_loss_must_be_paid_by_work(self):
        s=ledger(1.,.4,-.9,initial_energy=2.,initial_dissipation=.3)
        self.assertTrue(s['passed']);self.assertAlmostEqual(s['residual_j'],0.)
        self.assertFalse(ledger(1.,.4,-1.,initial_energy=2.,initial_dissipation=.3)['passed'])

    def test_roundtrip_keeps_peak_energy_scale_and_rejects_healing(self):
        s=ledger(0.,.3,1e-10,initial_energy=0.,initial_dissipation=.3,peak_energy=1e-6)
        self.assertTrue(s['passed'])
        with self.assertRaises(ValueError):ledger(0.,.2,0.,initial_energy=0.,initial_dissipation=.3)
        a=[DamageState(.002,.4)];b=[DamageState(.001,.2)]
        self.assertEqual(damage_changes(a,b)['healed_patches'],1)
        self.assertEqual(damage_changes(a,b)['decreased_histories'],1)


class ContactHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2]
        cls.design=json.loads((root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text())
        cls.points=np.asarray([n['position_m'] for n in cls.design['nodes']]);cls.pairs=cut_pairs(cls.design)

    def test_predictor_changes_only_a_copy_of_loaded_normal_positions(self):
        initial=np.array([[-.002,1.,2.],[.002,1.,2.],[-.002,3.,4.],[.002,3.,4.]])
        original=initial.copy();pairs=np.array([[0,1],[2,3]])
        # Two cut rows followed by left/right blade multipliers for each pair.
        old=np.array([0.,0.,1.,1.,0.,0.])
        guess=withdrawal_guess(initial,pairs,old,np.array([.003,.003]),0.)
        np.testing.assert_array_equal(initial,original)
        np.testing.assert_array_equal(guess[:,1:],initial[:,1:])
        np.testing.assert_allclose(guess[:2,0],[-.0015,.0015])
        np.testing.assert_array_equal(guess[2:],initial[2:])

    def test_withdrawing_wedge_restores_contact_without_damage_gate(self):
        top=self.points[self.pairs[:,0],2].max()
        _,inserted,_,_,w=wedge_geometry(self.design,self.points,self.pairs,top-.004)
        _,withdrawn,labels,_,zero=wedge_geometry(self.design,self.points,self.pairs,top)
        n=len(self.pairs);self.assertTrue((inserted[:n]<0).any())
        np.testing.assert_array_equal(withdrawn[:n],0.)
        np.testing.assert_array_equal(zero,0.)
        self.assertEqual(sum(l[0]=='cut' for l in labels),257)
        self.assertTrue(np.all(withdrawn[n:]==-1.))

    def test_edge_history_does_not_clear_and_no_load_cannot_advance_damage(self):
        c=EvolvingCohesion(self.design,self.pairs);n=len(self.pairs)
        old=np.ones(n,dtype=bool);top=self.points[self.pairs[:,0],2].max()
        hits=edge_history(self.points,self.pairs,top-.004,top,old)
        np.testing.assert_array_equal(hits,old)
        eligible=contact_eligibility(c,hits,np.zeros(3*n),np.zeros(n))
        oldstates=[DamageState(.002,.5)]*47
        self.assertEqual(c.trial_states(self.points,oldstates,eligible),oldstates)

    def test_closed_faces_reopen_with_degraded_tensile_stiffness(self):
        c=EvolvingCohesion(self.design,self.pairs);p=c.patches[19];n=len(p['indices']);D=.18786211220311036
        closed=patch_response(np.zeros((n,3)),p['weights'],p['stiffness'],D)
        self.assertEqual(closed['energy_j'],0.)
        g=np.tile([.0001,0.,0.],(n,1))
        a=patch_response(g,p['weights'],p['stiffness'],D)
        intact=patch_response(g,p['weights'],p['stiffness'],0.)
        self.assertAlmostEqual(a['gradient_n'][:,0].sum()/intact['gradient_n'][:,0].sum(),1-D,places=12)


if __name__=='__main__':unittest.main()
