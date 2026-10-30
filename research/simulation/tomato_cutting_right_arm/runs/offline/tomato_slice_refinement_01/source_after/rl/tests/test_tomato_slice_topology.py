"""Regression checks for real slice resolution, without altered fixed DOFs."""
import itertools
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_slice_topology import add_slice_cell_edges,refine_slice_cloud
from tomato_surface_mechanics import volume_lumping,analyse_piece


class SimpleCellTests(unittest.TestCase):
    def test_tetrahedron_edges_unique_positive_and_idempotent(self):
        positions=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
        original={'nodes':[{'id':i,'side':'slice','position_m':p} for i,p in enumerate(positions)],'bonds':[]}
        refined=add_slice_cell_edges(original)
        self.assertEqual(len(refined['bonds']),6)
        self.assertEqual({tuple(b['nodes']) for b in refined['bonds']},set(itertools.combinations(range(4),2)))
        self.assertTrue(all(b['rest_length_m']>0 for b in refined['bonds']))
        self.assertEqual(original['bonds'],[])
        self.assertEqual(add_slice_cell_edges(refined)['bonds'],refined['bonds'])


class SliceResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tomato_layout import build_layout
        from tomato_surfaces import build_surfaces
        from tomato_surface_conformity import conform_to_bulk
        cls.layout=build_layout(spacing_m=.004)
        cls.original=conform_to_bulk(build_surfaces(cls.layout),cls.layout,refine_near_boundary=True)
        cls.refined=add_slice_cell_edges(refine_slice_cloud(cls.original,cls.layout))

    def test_preserves_existing_geometry_interface_fixture_and_fixed_nodes(self):
        a,b=self.original,self.refined
        self.assertEqual([n['position_m'] for n in a['nodes']],
                         [n['position_m'] for n in b['nodes'][:len(a['nodes'])]])
        self.assertEqual(b['bonds'][:len(a['bonds'])],a['bonds'])
        self.assertEqual(b['interface_patches'],a['interface_patches'])
        self.assertEqual(b['fixture'],a['fixture'])
        self.assertEqual(b['pieces'],a['pieces'])
        for side in ['slice','remainder']:
            self.assertAlmostEqual(sum(n['mass_kg'] for n in a['nodes'] if n['side']==side),
                                   sum(n['mass_kg'] for n in b['nodes'] if n['side']==side),places=14)

    def test_all_new_nodes_inside_and_all_cells_connected_without_extra_constraints(self):
        from offline_tomato_surfaces import inspect_design
        a,b=self.original,self.refined;piece=b['pieces'][0]
        points=np.asarray([n['position_m'] for n in b['nodes']])
        p=points[np.asarray(piece['triangles'])]
        normals=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
        new=points[len(a['nodes']):]
        for start in range(0,len(normals),128):
            ns=normals[start:start+128];anchors=p[start:start+128,0]
            self.assertLessEqual(float((new@ns.T-np.einsum('ni,ni->n',ns,anchors)).max()),-.02*self.layout['spacing_m']+1e-12)
        ids=[n['id'] for n in b['nodes'] if n['side']=='slice']
        cells,*_=volume_lumping(points[ids]);edges={tuple(sorted(v['nodes'])) for v in b['bonds']}
        self.assertTrue(all(tuple(sorted((ids[i],ids[j]))) in edges for cell in cells for i,j in itertools.combinations(cell,2)))
        check=inspect_design(self.layout,b);self.assertTrue(check['passed'],check)
        self.assertEqual(check['added_interior_nodes'],b['slice_cloud_refinement']['added_nodes'])
        self.assertFalse(b['slice_cloud_refinement']['new_constraints'])
        self.assertLessEqual(len(b['nodes']),7000);self.assertLessEqual(len(b['bonds']),50000)

    def test_small_strain_pass_and_remainder_assignment_unchanged(self):
        a,b=self.original,self.refined
        record,_=analyse_piece(b,b['pieces'][0]);self.assertTrue(record['passed'],record)
        _,old=analyse_piece(a,a['pieces'][1]);_,new=analyse_piece(b,b['pieces'][1])
        for key in old:np.testing.assert_equal(new[key],old[key])

    def test_second_refinement_does_not_create_extra_nodes_or_bonds(self):
        twice=add_slice_cell_edges(refine_slice_cloud(self.refined,self.layout))
        self.assertEqual([n['position_m'] for n in twice['nodes']],
                         [n['position_m'] for n in self.refined['nodes']])
        self.assertEqual(twice['bonds'],self.refined['bonds'])


if __name__=='__main__':unittest.main()
