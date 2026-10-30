"""Finite-face contact and sparse weighted equality solver regression tests."""
import sys,json,unittest
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix,eye
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_triangle_contact import triangle_geometry,swept_triangle_gap,blade_resistance,nodal_blade_multipliers,solve_triangle_contact
from tomato_linear_contact import affine_space,solve_linear_contact,independent_rows
from tomato_coupled_contact import cut_pairs
from tomato_blade_damage import BLADE

class Quadratic:
    def __init__(self,target):self.target=np.asarray(target)
    def evaluate(self,x,*,tangent=False):
        g=x-self.target;s={'energy_j':float(.5*np.sum(g*g)),'gradient_n':g,'min_cell_ratio':1.,'min_length_ratio':1.}
        if tangent:s['tangent_n_m']=eye(x.size,format='csr')
        return s

class WeightedContact(unittest.TestCase):
    def test_pair_constraint_matches_exact_solution(self):
        C=csr_matrix([[.25,0,0,.75,0,0]])
        r=solve_linear_contact(Quadratic(np.zeros((2,3))),np.zeros((2,3)),{},C,np.array([1.]))
        x,lam,_,_,ok,*_=r;self.assertTrue(ok)
        np.testing.assert_allclose(x[:,0],[.4,1.2],atol=1e-8);self.assertAlmostEqual(lam[0],1.6,places=8)
    def test_dependent_active_rows_are_filtered(self):
        C=csr_matrix([[1.,0,0],[2.,0,0]])
        r=solve_linear_contact(Quadratic(np.zeros((1,3))),np.zeros((1,3)),{},C,np.array([1.,2.]))
        self.assertTrue(r[4]);self.assertAlmostEqual(r[0][0,0],1.)
    def test_stale_contacts_release_without_attraction(self):
        C=csr_matrix([[.5,0,0,.5,0,0]])
        r=solve_linear_contact(Quadratic(np.array([[1.,0,0],[1.,0,0]])),np.zeros((2,3)),{},C,np.array([0.]))
        self.assertTrue(r[4]);np.testing.assert_allclose(r[0][:,0],1.,atol=1e-8);self.assertAlmostEqual(r[1][0],0.)
    def test_graph_cycles_and_fixed_dofs(self):
        C=csr_matrix([[1.,1.,0.],[0.,1.,1.],[1.,0.,1.]])
        o,T=affine_space(C,np.array([3.,5.,4.]),{},3)
        self.assertEqual(T.shape[1],0);np.testing.assert_allclose(o,[1.,2.,3.])
        with self.assertRaises(ValueError):affine_space(C,np.array([3.,5.,4.]),{0:2.},3)
    def test_non_diagonal_nullspace_matches_dense_reference(self):
        C=csr_matrix([[.2,.8,0.,0.],[0.,.3,.7,0.]])
        o,T=affine_space(C,np.array([1.,2.]),{3:0.},4)
        np.testing.assert_allclose(C@o,[1.,2.],atol=1e-12);np.testing.assert_allclose((C@T).toarray(),0.,atol=1e-12)
        np.testing.assert_allclose((T.T@T).toarray(),np.eye(T.shape[1]),atol=1e-12)

class FiniteFaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2];cls.root=root
        cls.design=json.loads((root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text())
        cls.points=np.array([n['position_m'] for n in cls.design['nodes']]);cls.pairs=cut_pairs(cls.design)
        cls.top=cls.points[cls.pairs[:,0],2].max()
    def test_saved_counterexample_is_now_rejected(self):
        tip=self.top-.008125;g=triangle_geometry(self.design,self.points,self.pairs,tip);x=self.points.copy();w=g['widths']
        x[self.pairs[:,0],0]-=w/2;x[self.pairs[:,1],0]+=w/2
        gap=g['matrix']@x.ravel()-g['bounds'];n=len(self.pairs)
        self.assertGreaterEqual(gap[:3*n].min(),-1e-12)
        self.assertAlmostEqual(-gap.min(),5.7965994149161964e-05,places=12)
    def test_synthetic_mesh_counterexample_is_resolved_by_solver(self):
        # Six nodes forming matched triangles, with a cap crossing their edges.
        z=np.array([0.,.001,.001]);p=np.array([[0.,-.001,z[0]],[0.,.001,z[1]],[0.,0.,z[2]]]*2)
        d={'cut_x_m':0.,'pieces':[{'triangles':[[0,1,2]],'face_tags':['cut']}]};pairs=np.array([[0,3],[1,4],[2,5]])
        g=triangle_geometry(d,p,pairs,.0005-.008);fixed={3*i+j:p[i,j] for i in range(6) for j in [1,2]}
        x,lam,state,trace,ok,*_=solve_triangle_contact(Quadratic(p),p,fixed,g)
        self.assertTrue(ok);self.assertGreaterEqual((g['matrix']@x.ravel()-g['bounds']).min(),-1e-10);self.assertGreater(lam[9:].sum(),0.);self.assertTrue(np.all(lam[~g['active']]==0.))
    def test_blade_miss_and_back_edge_are_rejected(self):
        p=self.points.copy();p[self.pairs[:,0],1]+=.3
        with self.assertRaises(ValueError):triangle_geometry(self.design,p,self.pairs,self.top-.008)
        with self.assertRaises(ValueError):triangle_geometry(self.design,self.points,self.pairs,self.top-.051)
    def test_virtual_work_includes_changing_barycentric_weights(self):
        tip=self.top-.008125;g=triangle_geometry(self.design,self.points,self.pairs,tip);eps=1e-8
        minus=triangle_geometry(self.design,self.points,self.pairs,tip+eps);plus=triangle_geometry(self.design,self.points,self.pairs,tip-eps)
        x=self.points.copy();x[:,0]+=.03*x[:,2];mask=g['active']&minus['active']&plus['active'];lam=mask.astype(float)
        exact=blade_resistance(g,x,lam)
        fd=lam@((plus['physical']-minus['physical']-(plus['matrix']-minus['matrix'])@x.ravel())/(2*eps))
        self.assertAlmostEqual(exact,fd,places=6)
    def test_cut_face_nonpenetration_remains_independent_of_blade(self):
        g=triangle_geometry(self.design,self.points,self.pairs,self.top);n=len(self.pairs)
        np.testing.assert_array_equal(g['bounds'][:n],0.);self.assertTrue(np.all(g['widths']==0.));self.assertFalse(np.any(g['active'][n:3*n]&np.repeat(self.points[self.pairs[:,0],2]<self.top,2)))
    def test_swept_gap_catches_interior_time_minimum(self):
        # Constant x nodal feasible witness: detects cap crossing in the path.
        old=self.points.copy();new=self.points.copy();width=BLADE['max_thickness_m']/2
        for x in [old,new]:x[self.pairs[:,0],0]-=width;x[self.pairs[:,1],0]+=width
        self.assertGreaterEqual(swept_triangle_gap(self.design,self.points,self.pairs,old,new,self.top-.0079,self.top-.0082),-1e-12)
        g=triangle_geometry(self.design,self.points,self.pairs,self.top-.008125)
        bad=self.points.copy();bad[self.pairs[:,0],0]-=g['widths']/2;bad[self.pairs[:,1],0]+=g['widths']/2
        self.assertLess(swept_triangle_gap(self.design,self.points,self.pairs,bad,bad,self.top-.008125,self.top-.008125),-1e-5)
    def test_finite_entry_edge_detects_penetration_ahead_of_loaded_vertices(self):
        p=np.array([[0.,-.001,0.],[0.,.001,.001],[0.,0.,.001]]*2)
        d={'cut_x_m':0.,'pieces':[{'triangles':[[0,1,2]],'face_tags':['cut']}]};pairs=np.array([[0,3],[1,4],[2,5]])
        g=triangle_geometry(d,p,pairs,.0005);x=p.copy();w=g['widths'];x[:3,0]=-w/2;x[3:,0]=w/2
        x[0,0]=.001;x[3,0]=.002
        gaps=g['matrix']@x.ravel()-g['bounds']
        self.assertGreaterEqual(gaps[:9].min(),-1e-12);self.assertLess(gaps[9:].min(),-1e-4)

    def test_safe_endpoints_can_hide_midpath_cap_penetration(self):
        z=np.array([0.,.001,.001]);p=np.array([[0.,-.001,z[0]],[0.,.001,z[1]],[0.,0.,z[2]]]*2)
        d={'cut_x_m':0.,'pieces':[{'triangles':[[0,1,2]],'face_tags':['cut']}]};pairs=np.array([[0,3],[1,4],[2,5]])
        h=BLADE['max_thickness_m']/2;old=p.copy();new=p.copy()
        old[3:,0]=h+np.array([-.00005,.0002,.0002]);new[3:,0]=h+np.array([-.000265,.000105,.000105])
        old[:3,0]=-old[3:,0];new[:3,0]=-new[3:,0]
        a=.00025-.008;b=.00075-.008
        for x,tip in [(old,a),(new,b)]:
            g=triangle_geometry(d,p,pairs,tip)
            self.assertGreaterEqual((g['matrix']@x.ravel()-g['bounds']).min(),-1e-12)
        self.assertAlmostEqual(swept_triangle_gap(d,p,pairs,old,new,a,b),-2.5e-6,places=12)

    def test_interior_loads_are_distributed_without_creating_force(self):
        g=triangle_geometry(self.design,self.points,self.pairs,self.top-.008125);lam=np.zeros(len(g['bounds']));n=len(self.pairs)
        for j,m in enumerate(g['cap_rows']):
            if m['active']:lam[3*n+j]=1.;break
        nodal=nodal_blade_multipliers(g,self.pairs,lam)
        self.assertAlmostEqual(nodal[n:].sum(),1.);self.assertTrue(np.all(nodal>=0.))
if __name__=='__main__':unittest.main()
