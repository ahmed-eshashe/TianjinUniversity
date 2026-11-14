import copy
import unittest
from tomato_contact_selection_preview import selection_preview


def fixture():
    identity={'rotation':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],'translation_m':[0.,0.,0.]}
    context={'step':0,'dt_s':.001,'body_id':0,'shape_id':0,
        'particles_world_m':[[0.,0.,-.001],[1.,0.,-.001],[0.,1.,-.001]],
        'particle_radius_m':[0.,0.,0.],'shape_margin_m':0.,
        'rigid_vertices_shape_m':[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],
        'rigid_triangles':[[0,1,2]],'shape_to_body':identity,'body_to_world':identity}
    record={'id':'a','source_kind':'signed_surface_reference','normal_source':'outward_rigid_face_reference',
        'step':0,'shape_id':0,'body_id':0,'feature':'face','corners':[0,1,2],
        'barycentric':[.5,.25,.25],'rigid_triangle_id':0,'rigid_barycentric':[.5,.25,.25],
        'rigid_surface_body_m':[.25,.25,0.],'normal_world':[0.,0.,1.],
        'projected_signed_gap_m':-.001,'rigid_surface_velocity_body_m_s':[0.,0.,0.]}
    return context,record


class SelectionPreviewTests(unittest.TestCase):
    def test_duplicates_and_reordering_do_not_multiply_representative(self):
        context,a=fixture();b=dict(a,id='duplicate')
        x=selection_preview([a,b],context);y=selection_preview([b,a],context)
        self.assertEqual(x['selected_records'],y['selected_records'])
        self.assertEqual(x['unique_count'],1)
        self.assertEqual(len(x['selected_records']),1)
        self.assertFalse(x['native_write_allowed'])

    def test_raw_overflow_rejected_before_duplicate_reduction(self):
        context,a=fixture()
        with self.assertRaisesRegex(ValueError,'capacity'):
            selection_preview([a,dict(a,id='b')],context,raw_capacity=2)

    def test_conflicting_normals_refused(self):
        context,a=fixture()
        context['rigid_vertices_shape_m'] += [[0.,0.,-.002],[0.,1.,-.002],[1.,0.,-.002]]
        context['rigid_triangles'].append([3,4,5])
        b=dict(a,id='opposite',rigid_triangle_id=1,normal_world=[0.,0.,-1.],rigid_surface_body_m=[.25,.25,-.002])
        result=selection_preview([a,b],context)
        self.assertEqual(result['status'],'blocked')
        self.assertEqual(result['selected_records'],[])

    def test_changed_support_not_silently_merged(self):
        context,a=fixture();b=dict(a,id='edge',feature='edge',corners=[0,1,-1],
            barycentric=[.5,.5,0.],rigid_barycentric=[.5,.5,0.],rigid_surface_body_m=[.5,0.,0.])
        self.assertEqual(selection_preview([a,b],context)['status'],'blocked')

    def test_intersection_only_record_refused(self):
        context,a=fixture();a['source_kind']='intersection_only'
        with self.assertRaises(ValueError):selection_preview([a],context)

    def test_cached_review_cannot_hide_bad_normal(self):
        context,a=fixture();a['normal_world']=[0.,0.,-1.]
        with self.assertRaises(ValueError):selection_preview([a],context)

    def test_inputs_not_modified(self):
        context,a=fixture();before=copy.deepcopy((context,a));selection_preview([a],context)
        self.assertEqual((context,a),before)


if __name__=='__main__':unittest.main()
