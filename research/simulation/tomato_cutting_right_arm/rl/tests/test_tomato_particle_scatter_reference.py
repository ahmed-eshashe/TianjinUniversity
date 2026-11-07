import unittest
from tomato_particle_scatter_reference import scatter_reference


class ParticleScatterTests(unittest.TestCase):
    h=[[0.,0.,0.],[0.,0.,0.],[0.,0.,100.]]
    def test_force_partition_and_squared_stiffness(self):
        f,h=scatter_reference([0.,0.,10.],self.h,[0,1,2],[.2,.3,.5],4)
        self.assertEqual([r[2] for r in f],[2.,3.,5.,0.])
        self.assertAlmostEqual(h[0][2][2],4.)
        self.assertAlmostEqual(h[1][2][2],9.)
        self.assertEqual(h[2][2][2],25.)

    def test_color_filter_and_spectator(self):
        f,h=scatter_reference([0.,0.,10.],self.h,[0,1,2],[.2,.3,.5],4,colors=[0,1,2,1],active_color=1)
        self.assertEqual([r[2] for r in f],[0.,3.,0.,0.])

    def test_padding_is_not_a_negative_index(self):
        f,h=scatter_reference([0.,0.,10.],self.h,[0,-1,-1],[1.,0.,0.],2)
        self.assertEqual(f,[[0.,0.,10.],[0.,0.,0.]])

    def test_weights_are_not_renormalized(self):
        f,h=scatter_reference([0.,0.,10.],self.h,[0,1,2],[.2,.3,.4],3)
        self.assertEqual(sum(r[2] for r in f),9.)

    def test_invalid_support_or_padding_refused(self):
        for corners,weights in [([0,0,-1],[.5,.5,0.]),([0,-1,-1],[1.,.1,0.])]:
            with self.assertRaises(ValueError):scatter_reference([0.,0.,10.],self.h,corners,weights,2)


if __name__=='__main__':unittest.main()
