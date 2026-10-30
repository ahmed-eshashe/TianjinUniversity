"""Adversarial local contact/coupon tests, not full-tomato cutting tests."""
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_contact_reference import (edge_hits_site,outlines_overlap,wedge_patch_coupon,
                                       normal_contact_coupon,containing_cut_triangles)


class ContactGeometryTests(unittest.TestCase):
    square=np.array([[0.,0.],[1.,0.],[1.,1.],[0.,1.]])
    blade={'length_m':.1,'height_m':.05,'max_thickness_m':.0076,'single_bevel_length_m':.008}

    def test_continuous_edge_sweep_and_finite_width(self):
        self.assertTrue(edge_hits_site((0.,.02),.04,0.,self.blade))
        self.assertFalse(edge_hits_site((.2,.02),.04,0.,self.blade))
        self.assertFalse(edge_hits_site((0.,.02),.04,0.,self.blade,x_offset=.01))
        self.assertFalse(edge_hits_site((0.,.02),.04,.03,self.blade))

    def test_finite_faces_and_rim(self):
        self.assertTrue(outlines_overlap(self.square,self.square+[1.,0.]))
        self.assertFalse(outlines_overlap(self.square,self.square+[1.01,0.]))
        self.assertTrue(outlines_overlap(self.square,self.square+[.5,.5]))

    def test_triangle_interior_edge_vertex_and_outside(self):
        d={'nodes':[{'position_m':[0.,0.,0.]},{'position_m':[0.,1.,0.]},{'position_m':[0.,0.,1.]}]}
        p={'triangles':[[0,1,2]],'face_tags':['cut']}
        for site in [(1/3,1/3),(.5,.5),(0.,0.)]:self.assertEqual(containing_cut_triangles(d,p,site),[0])
        self.assertEqual(containing_cut_triangles(d,p,(1.,1.)),[])

    def test_no_tunnelling_energy_balance_and_reopening(self):
        for dt in [.001,.0005]:
            r=normal_contact_coupon(self.square,self.square,.01,dt)
            self.assertGreater(r['contact_steps'],0);self.assertEqual(r['minimum_gap_m'],0.)
            self.assertGreater(r['final_gap_m'],0.);self.assertEqual(r['crossings'],0)
            self.assertLess(abs(r['energy_residual_j']),1e-12)

    def test_contact_remains_after_any_damage_and_no_preload(self):
        values=[normal_contact_coupon(self.square,self.square,.01,.001,damage=d) for d in [0.,.5,1.]]
        self.assertEqual([r['impact_time_s'] for r in values],[values[0]['impact_time_s']]*3)
        r=normal_contact_coupon(self.square,self.square,.01,.001,gap=0.,initial_velocity=0.,force_scale=0.)
        self.assertEqual(r['impact_impulse_ns'],0.);self.assertEqual(r['max_sustained_reaction_n'],0.)

    def test_disjoint_finite_faces_do_not_create_infinite_wall(self):
        r=normal_contact_coupon(self.square,self.square,.01,.001,offset_yz=(10.,0.))
        self.assertFalse(r['finite_outlines_overlap']);self.assertEqual(r['contact_steps'],0)


class PatchCouponTests(unittest.TestCase):
    def setUp(self):
        self.design={'nodes':[{'side':'slice','position_m':[-.0025,0.,.02]},
                              {'side':'remainder','position_m':[.0025,0.,.02]}],
                     'bonds':[{'kind':'interface','nodes':[0,1]}]}
        self.patch={'id':0,'bond_ids':[0],'area_m2':25e-6,'anchor_yz_m':[0.,.02]}
        self.blade=ContactGeometryTests.blade

    def test_contact_driven_complete_failure_energy_and_zero_residue(self):
        r=wedge_patch_coupon(self.design,self.patch,self.blade,2400)
        self.assertEqual(r['damage'],1.);self.assertTrue(r['zero_broken_force_and_damping'])
        self.assertLess(abs(r['work_relative_error']),.01);self.assertLess(abs(r['damage_energy_relative_error']),.01)
        self.assertAlmostEqual(r['blade_virtual_work_j'],r['work_j'],places=12)
        self.assertTrue(r['stopped_state_unchanged'])

    def test_no_contact_and_face_rubbing_do_not_break_bond(self):
        for mode in ['miss','off_plane','face_rub']:
            self.assertEqual(wedge_patch_coupon(self.design,self.patch,self.blade,2400,mode=mode)['damage'],0.)

    def test_partial_and_thin_bevel_are_not_complete_cuts(self):
        self.assertLess(wedge_patch_coupon(self.design,self.patch,self.blade,2400,mode='partial')['damage'],1.)
        blade=dict(self.blade,max_thickness_m=.002)
        self.assertLess(wedge_patch_coupon(self.design,self.patch,blade,2400)['damage'],1.)


if __name__=='__main__':unittest.main()
