"""Independent volume/moment and spring-matrix references; no simulator backend."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_surface_mechanics import (volume_lumping,closed_volume_moments,
                                      stiffness_matrix,finite_spring_energy,isotropic_orientation_weights)


class VolumeTests(unittest.TestCase):
    points=np.array([(0.,0.,0.),(1.,0.,0.),(0.,1.,0.),(0.,0.,1.)])
    def test_simplex_volume_lumps_and_exact_moments(self):
        cells,volumes,lumps,first,second=volume_lumping(self.points)
        self.assertAlmostEqual(volumes.sum(),1/6)
        np.testing.assert_allclose(lumps,np.full(4,1/24))
        np.testing.assert_allclose(first,np.full(3,1/24))
        expected=np.full((3,3),1/120);np.fill_diagonal(expected,1/60)
        np.testing.assert_allclose(second,expected)

    def test_mass_geometry_rigid_transform(self):
        _,v,l,f,_=volume_lumping(self.points)
        rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]])
        moved=self.points@rotation.T+[2,3,4]
        _,mv,ml,mf,_=volume_lumping(moved)
        np.testing.assert_allclose(mv.sum(),v.sum())
        np.testing.assert_allclose(ml,l)
        np.testing.assert_allclose(mf/mv.sum(),rotation@(f/v.sum())+[2,3,4])

    def test_independent_boundary_integral(self):
        centre=self.points.mean(axis=0);faces=[]
        for triangle in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]:
            a,b,c=self.points[triangle]
            if np.dot(np.cross(b-a,c-a),a-centre)<0:triangle=triangle[::-1]
            faces.append(triangle)
        design={'nodes':[{'position_m':p.tolist()} for p in self.points]}
        piece={'triangles':faces,'reference_interior_m':centre.tolist()}
        volume,first=closed_volume_moments(design,piece)
        self.assertAlmostEqual(volume,1/6)
        np.testing.assert_allclose(first,np.full(3,1/24))


class SpringMatrixTests(unittest.TestCase):
    points=VolumeTests.points
    pairs=np.array([(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)])
    def test_single_spring_known_matrix(self):
        matrix=stiffness_matrix([[0,0,0],[2,0,0]],[[0,1]],[7.]).toarray()
        expected=np.zeros((6,6));expected[0,0]=expected[3,3]=7.;expected[0,3]=expected[3,0]=-7.
        np.testing.assert_allclose(matrix,expected)

    def test_psd_and_six_rigid_modes(self):
        matrix=stiffness_matrix(self.points,self.pairs,np.ones(6)).toarray()
        eigen=np.linalg.eigvalsh(matrix)
        self.assertGreaterEqual(eigen.min(),-1e-12)
        self.assertEqual(np.sum(eigen<1e-10),6)
        np.testing.assert_allclose(matrix,matrix.T)

    def test_translation_and_infinitesimal_rotation(self):
        matrix=stiffness_matrix(self.points,self.pairs,np.ones(6))
        for u in [np.tile([1.,2.,3.],(4,1)),np.cross([.1,.2,.3],self.points)]:
            np.testing.assert_allclose(matrix@u.reshape(-1),0.,atol=1e-12)

    def test_finite_energy_matches_small_strain_reference(self):
        k=np.arange(1.,7.);matrix=stiffness_matrix(self.points,self.pairs,k)
        u=self.points.copy()*1e-7
        linear=.5*u.reshape(-1)@(matrix@u.reshape(-1))
        self.assertAlmostEqual(finite_spring_energy(self.points,u,self.pairs,k)/linear,1.,places=7)

    def test_invalid_stiffness_or_length_rejected(self):
        with self.assertRaises(ValueError):stiffness_matrix(self.points,[[0,1]],[-1.])
        with self.assertRaises(ValueError):stiffness_matrix(self.points,[[0,0]],[1.])

    def test_orientation_fit_does_not_create_missing_shear_directions(self):
        with self.assertRaises(ValueError):isotropic_orientation_weights(np.eye(3),np.full(3,1/3))


if __name__=='__main__':unittest.main()
