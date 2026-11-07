import unittest
from tomato_blade_contact_candidates import segment_face_witness, generate_seeds


class BladeCandidateTests(unittest.TestCase):
    face=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]]

    def test_non_coplanar_crossing(self):
        self.assertEqual(segment_face_witness([.2,.2,-1.],[.2,.2,1.],self.face),(.2,.2,0.))

    def test_plane_crossing_outside_finite_face_is_clear(self):
        self.assertIsNone(segment_face_witness([2.,2.,-1.],[2.,2.,1.],self.face))

    def test_coplanar_seed_is_explicitly_unsupported(self):
        self.assertIsNone(segment_face_witness([.1,.1,0.],[.2,.2,0.],self.face))

    def test_capacity_saturation_rejected(self):
        soft=[[.2,.2,-1.],[.2,.2,1.],[.3,.3,1.]]
        with self.assertRaisesRegex(ValueError,'capacity'):
            generate_seeds(self.face,[[0,1,2]],soft,witness_capacity=1)


if __name__=='__main__':unittest.main()
