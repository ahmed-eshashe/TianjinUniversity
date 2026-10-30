"""Regression checks for boundary repair and explicit isolated-piece diagnostics."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from offline_tomato_sensitivity_path import validate_preparation


class PreparationGateTests(unittest.TestCase):
    def setUp(self):
        self.prep={'preparation_pass':False,'spacing_mm':4.,'geometry':{'passed':True},
                   'small_strain_checks':[{'side':'slice','passed':True},
                                          {'side':'remainder','passed':False}]}

    def test_default_refuses_failed_whole_mesh(self):
        with self.assertRaises(ValueError):validate_preparation(self.prep,'slice')

    def test_explicit_isolation_requires_passing_piece(self):
        self.assertIn('whole_mesh_still_rejected',validate_preparation(self.prep,'slice',True))
        with self.assertRaises(ValueError):validate_preparation(self.prep,'remainder',True)

    def test_geometry_failure_cannot_be_bypassed(self):
        self.prep['geometry']['passed']=False
        with self.assertRaises(ValueError):validate_preparation(self.prep,'slice',True)


class BoundaryConformityTests(unittest.TestCase):
    def test_repairs_4mm_without_moving_nodes_or_changing_original_registry(self):
        from tomato_layout import build_layout
        from tomato_surfaces import build_surfaces
        from tomato_surface_conformity import conform_to_bulk
        from offline_tomato_surfaces import inspect_design
        layout=build_layout(spacing_m=.004)
        original=build_surfaces(layout);snapshot=copy.deepcopy(original)
        fixed=conform_to_bulk(original,layout)
        self.assertEqual(original,snapshot)
        self.assertEqual([n['position_m'] for n in fixed['nodes']],
                         [n['position_m'] for n in original['nodes']])
        self.assertEqual(fixed['bonds'][:len(layout['bonds'])],layout['bonds'])
        self.assertEqual(fixed['interface_patches'],layout['interface_patches'])
        for before,after in zip(original['pieces'],fixed['pieces']):
            self.assertEqual([t for t,tag in zip(before['triangles'],before['face_tags']) if tag=='cut'],
                             [t for t,tag in zip(after['triangles'],after['face_tags']) if tag=='cut'])
        self.assertTrue(inspect_design(layout,fixed)['passed'])
        self.assertGreater(sum(len(r['bulk_nodes_promoted_to_boundary'])
                               for r in fixed['boundary_conformity_records']),0)

    def test_5mm_geometry_is_unchanged(self):
        from tomato_layout import build_layout
        from tomato_surfaces import build_surfaces
        from tomato_surface_conformity import conform_to_bulk
        layout=build_layout(spacing_m=.005);original=build_surfaces(layout)
        fixed=conform_to_bulk(original,layout)
        self.assertEqual(fixed['nodes'],original['nodes'])
        self.assertEqual(fixed['bonds'],original['bonds'])
        for before,after in zip(original['pieces'],fixed['pieces']):
            for key in before:self.assertEqual(before[key],after[key])
        self.assertTrue(all(not r['bulk_nodes_promoted_to_boundary']
                            for r in fixed['boundary_conformity_records']))


if __name__=='__main__':unittest.main()
