"""Adversarial geometry checks; no native collision solver is imported."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_surfaces import (audit_piece,segment_triangle_hit,sub,dot,cross,vertex_face_eligible,
                             SurfaceNodeRegistry,build_surfaces)


def cube():
    points=[(-1.,-1.,-1.),(-1.,-1.,1.),(-1.,1.,-1.),(-1.,1.,1.),
            (0.,-1.,-1.),(0.,-1.,1.),(0.,1.,-1.),(0.,1.,1.)]
    triangles=[];tags=[];ref=(-.5,0.,0.)
    for a,b,c,d in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        for tri in [[a,b,c],[a,c,d]]:
            p,q,r=[points[i] for i in tri]
            if dot(cross(sub(q,p),sub(r,p)),sub(p,ref))<0:tri=tri[::-1]
            triangles.append(tri);tags.append('cut' if all(points[i][0]==0. for i in tri) else 'exterior')
    design={'cut_x_m':0.,'nodes':[{'position_m':p,'side':'slice'} for p in points]}
    piece={'side':'slice','surface_node_ids':list(range(8)),'triangles':triangles,'face_tags':tags,'reference_interior_m':ref}
    return design,piece


class ClosedGeometryTests(unittest.TestCase):
    def test_closed_convex_cube_known_volume_area(self):
        design,piece=cube();result=audit_piece(design,piece)
        self.assertTrue(result['passed'],result)
        self.assertAlmostEqual(result['signed_volume_m3'],4.)
        self.assertAlmostEqual(result['cut_area_m2'],4.)

    def test_missing_face_rejected(self):
        design,piece=cube();piece['triangles'].pop();piece['face_tags'].pop()
        self.assertFalse(audit_piece(design,piece)['checks']['two_opposite_uses_per_edge'])

    def test_flipped_cut_face_rejected(self):
        design,piece=cube();i=piece['face_tags'].index('cut');piece['triangles'][i].reverse()
        result=audit_piece(design,piece)
        self.assertFalse(result['checks']['outward_cut_normals'])
        self.assertFalse(result['checks']['two_opposite_uses_per_edge'])

    def test_duplicate_face_rejected(self):
        design,piece=cube();piece['triangles'].append(piece['triangles'][0]);piece['face_tags'].append('exterior')
        self.assertFalse(audit_piece(design,piece)['checks']['two_opposite_uses_per_edge'])

    def test_degenerate_triangle_rejected(self):
        design,piece=cube();piece['triangles'][0]=[0,0,1]
        self.assertFalse(audit_piece(design,piece)['checks']['positive_triangle_areas'])

    def test_wrong_material_side_rejected(self):
        design,piece=cube();design['nodes'][0]['side']='remainder'
        self.assertFalse(audit_piece(design,piece)['checks']['side_identity'])

    def test_out_of_plane_cut_rejected(self):
        design,piece=cube();design['nodes'][4]['position_m']=(.01,-1.,-1.)
        self.assertFalse(audit_piece(design,piece)['checks']['exact_cut_plane'])


class AnalyticCrossingTests(unittest.TestCase):
    triangle=[(0.,0.,0.),(0.,1.,0.),(0.,0.,1.)]
    def test_triangle_interior_edge_and_vertex(self):
        for y,z in [(1/3,1/3),(.5,.5),(0.,0.)]:
            hit=segment_triangle_hit((-1.,y,z),(1.,y,z),self.triangle)
            self.assertIsNotNone(hit);self.assertAlmostEqual(hit['fraction'],.5)

    def test_finite_triangle_not_infinite_plane(self):
        self.assertIsNone(segment_triangle_hit((-1.,1.,1.),(1.,1.,1.),self.triangle))

    def test_parallel_and_non_crossing_segments(self):
        self.assertIsNone(segment_triangle_hit((.1,.1,.1),(.1,.2,.1),self.triangle))
        self.assertIsNone(segment_triangle_hit((.1,.1,.1),(.2,.1,.1),self.triangle))

    def test_gap_and_crossing_order(self):
        # Prescribed geometry only: detects crossing, does not prevent it dynamically.
        tri=[(.002,y,z) for _,y,z in self.triangle]
        self.assertIsNone(segment_triangle_hit((0.,.2,.2),(.001,.2,.2),tri))
        hit=segment_triangle_hit((0.,.2,.2),(.004,.2,.2),tri)
        self.assertAlmostEqual(hit['fraction'],.5)
        self.assertIsNone(segment_triangle_hit((.003,.2,.2),(.004,.2,.2),tri))


class PairPolicyTests(unittest.TestCase):
    def test_touching_opposite_face_stays_eligible(self):
        nodes=[{'side':'slice'},{'side':'remainder'},{'side':'remainder'},{'side':'remainder'}]
        self.assertTrue(vertex_face_eligible(nodes,0,[1,2,3]))
        self.assertFalse(vertex_face_eligible(nodes,1,[1,2,3]))

    def test_cross_material_triangle_rejected(self):
        nodes=[{'side':'slice'},{'side':'remainder'},{'side':'remainder'}]
        with self.assertRaises(ValueError):vertex_face_eligible(nodes,0,[0,1,2])


class NodeReuseTests(unittest.TestCase):
    def test_same_piece_reuses_id_without_moving_original(self):
        nodes=[{'id':0,'side':'slice','position_m':[0.,0.,0.],'mass_kg':1.}]
        registry=SurfaceNodeRegistry(nodes,[0],'slice')
        self.assertEqual(registry.get_or_add((0.,0.,1e-15)),0)
        self.assertEqual(len(nodes),1)
        self.assertEqual(nodes[0]['position_m'],[0.,0.,0.])

    def test_opposite_cut_sides_never_weld(self):
        nodes=[{'id':0,'side':'slice','position_m':[0.,0.,0.],'mass_kg':1.}]
        registry=SurfaceNodeRegistry(nodes,[0],'remainder')
        self.assertEqual(registry.get_or_add((0.,0.,0.)),1)
        self.assertEqual(nodes[1]['side'],'remainder')
        self.assertTrue(vertex_face_eligible(nodes+[{'side':'remainder'},{'side':'remainder'}],0,[1,2,3]))

    def test_roundoff_bucket_boundary_and_distinct_points(self):
        nodes=[{'id':0,'side':'slice','position_m':[.49e-12,0.,0.],'mass_kg':1.}]
        registry=SurfaceNodeRegistry(nodes,[0],'slice')
        self.assertEqual(registry.get_or_add((.51e-12,0.,0.)),0)
        self.assertEqual(registry.get_or_add((3e-12,0.,0.)),1)

    def test_ambiguous_original_duplicates_are_not_silently_welded(self):
        nodes=[{'id':i,'side':'slice','position_m':[0.,0.,0.],'mass_kg':1.} for i in range(2)]
        with self.assertRaises(ValueError):SurfaceNodeRegistry(nodes,[0,1],'slice').get_or_add((0.,0.,0.))

    def test_full_4mm_layout_reuses_nodes_preserves_mass_and_cut_registry(self):
        from tomato_layout import build_layout,components
        layout=build_layout(spacing_m=.004);design=build_surfaces(layout)
        reused=[i for p in design['pieces'] for i in p['reused_original_surface_node_ids']]
        self.assertGreater(len(reused),0)
        self.assertEqual(design['bonds'][:len(layout['bonds'])],layout['bonds'])
        self.assertEqual(design['interface_patches'],layout['interface_patches'])
        self.assertAlmostEqual(sum(n['mass_kg'] for n in design['nodes']),sum(n['mass_kg'] for n in layout['nodes']))
        self.assertTrue(all(b['rest_length_m']>1e-9 for b in design['bonds']))
        self.assertEqual(len({tuple(sorted(b['nodes'])) for b in design['bonds']}),len(design['bonds']))
        cut={b['id'] for b in design['bonds'] if b['kind']=='interface'}
        groups=components(design,cut)
        self.assertEqual(len(groups),2)
        self.assertTrue(all(len({design['nodes'][i]['side'] for i in g})==1 for g in groups))


if __name__=='__main__':unittest.main()
