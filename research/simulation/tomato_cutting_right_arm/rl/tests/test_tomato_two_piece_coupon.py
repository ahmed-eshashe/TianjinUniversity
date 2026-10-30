import unittest
from tomato_two_piece_coupon import description,native_solver_options
from tomato_coupon_trajectory import audit_closed_surface

class TwoPieceTests(unittest.TestCase):
    def test_counts(self):
        d=description()
        self.assertEqual([len(d[k]) for k in ('positions_m','triangles','springs')],[16,24,56])
    def test_no_bridge(self):
        for a,b in description()['springs']:
            self.assertEqual(a//8,b//8)
    def test_closed_positive_solids(self):
        d=description()
        for side in range(2):
            audit_closed_surface(d['positions_m'][8*side:8*side+8],
                [[i-8*side for i in t] for t in d['triangles'][12*side:12*side+12]])
    def test_gap_and_fixtures(self):
        d=description();p=d['positions_m']
        self.assertAlmostEqual(min(x[0] for x in p[8:])-max(x[0] for x in p[:8]),.001)
        self.assertEqual(d['fixed_particle_ids'],[0,1,2,3,12,13,14,15])
    def test_modern_explicit_margin_gap(self):
        o=description()['self_contact_solver_options']
        self.assertTrue(o['particle_enable_self_contact'])
        self.assertNotIn('particle_self_contact_radius',o)
        self.assertEqual(o['particle_self_contact_margin'],.0001)
        self.assertEqual(o['particle_self_contact_gap'],.0001)
        self.assertEqual(o['particle_rest_shape_contact_exclusion_radius'],0.)
    def test_disabled(self):
        with self.assertRaises(PermissionError):native_solver_options()
        self.assertFalse(description()['cut_or_release_pass'])
    def test_fresh_description(self):
        d=description();d['positions_m'][0][0]=9
        self.assertLess(description()['positions_m'][0][0],0)
    def test_builder_refuses_before_native_import(self):
        import sys
        from tomato_two_piece_coupon import build_native_candidate
        with self.assertRaises(PermissionError):build_native_candidate()
        self.assertNotIn('newton',sys.modules)
        self.assertNotIn('warp',sys.modules)
    def test_source_matches_installed_solver_keywords(self):
        import ast
        from pathlib import Path
        source=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/solver_vbd.py')
        tree=ast.parse(source.read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SolverVBD')
        ctor=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
        keywords={a.arg for a in ctor.args.kwonlyargs}
        self.assertLessEqual(set(description()['self_contact_solver_options']),keywords)
