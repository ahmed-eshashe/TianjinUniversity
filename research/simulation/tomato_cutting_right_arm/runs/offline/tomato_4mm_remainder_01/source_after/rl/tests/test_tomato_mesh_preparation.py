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


class LocalRefinementRegressionTests(unittest.TestCase):
    def test_refined_remainder_passes_original_checks_without_clamping_interior_nodes(self):
        import numpy as np
        from tomato_layout import build_layout
        from tomato_surfaces import build_surfaces
        from tomato_surface_conformity import conform_to_bulk
        from tomato_surface_mechanics import analyse_piece,closed_volume_moments
        from offline_tomato_surfaces import inspect_design
        layout=build_layout(spacing_m=.004);original=build_surfaces(layout)
        fixed=conform_to_bulk(original,layout,refine_near_boundary=True)
        self.assertEqual([n['position_m'] for n in fixed['nodes'][:len(original['nodes'])]],
                         [n['position_m'] for n in original['nodes']])
        self.assertEqual(fixed['bonds'][:len(layout['bonds'])],layout['bonds'])
        self.assertEqual(fixed['interface_patches'],layout['interface_patches'])
        self.assertEqual(fixed['fixture'],original['fixture'])
        self.assertTrue(inspect_design(layout,fixed)['passed'])
        piece=fixed['pieces'][1]
        # Previously inverting free material nodes remain free, with the same coordinates.
        self.assertTrue({1766,1774,1820,1828}.isdisjoint(piece['surface_node_ids']))
        added={i for r in fixed['boundary_conformity_records'] for i in r['added_exterior_node_ids']}
        for bond in fixed['bonds']:
            if bond.get('role')=='surface tether; stiffness unset' and added.intersection(bond['nodes']):
                self.assertGreaterEqual(bond['rest_length_m'],.25*layout['spacing_m'])
        axes=np.asarray(layout['dimensions_m'])/2;centre=np.array([0.,0.,axes[2]])
        for record in fixed['boundary_conformity_records']:
            for idx in record['added_exterior_node_ids']:
                pos=np.asarray(fixed['nodes'][idx]['position_m'])
                self.assertAlmostEqual(float(np.sum(((pos-centre)/axes)**2)),1.,places=12)
        for before,after in zip(original['pieces'],fixed['pieces']):
            self.assertEqual([t for t,tag in zip(before['triangles'],before['face_tags']) if tag=='cut'],
                             [t for t,tag in zip(after['triangles'],after['face_tags']) if tag=='cut'])
        volume=closed_volume_moments(fixed,piece)[0]
        total_volume=sum(closed_volume_moments(fixed,p)[0] for p in fixed['pieces'])
        total_mass=sum(n['mass_kg'] for n in fixed['nodes'])
        record,assignment=analyse_piece(fixed,piece,density_mass=total_mass*volume/total_volume)
        self.assertTrue(record['passed'],record)
        self.assertTrue(all(m['min_cell_volume_ratio']>0 for m in record['modes']))
        self.assertLess(record['isotropic_direction_correction']['max_fourth_moment_residual'],1e-9)
        self.assertTrue(all(k>0 for k in assignment['bond_stiffness_n_m']))
        twice=conform_to_bulk(fixed,layout,refine_near_boundary=True)
        self.assertEqual(twice['nodes'],fixed['nodes'])
        self.assertEqual(twice['bonds'],fixed['bonds'])


if __name__=='__main__':unittest.main()
