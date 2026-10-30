import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contact_load_model import solve_contact_load


def pads(xs):
    return [{'part':part,'point':[x,y,0.],'normal':[0.,sign,0.]}
            for part,y,sign in [('left',-.01,-1),('right',.01,1)] for x in xs]


class FiniteContactLoadTests(unittest.TestCase):
    def test_budget_relaxation_is_reported_without_claiming_nominal_feasibility(self):
        r=solve_contact_load(pads([0.]),[0,0,0],[0,0,-2.4525],normal_cap=1.,minimize_budget_scale=True)
        self.assertFalse(r['feasible']);self.assertAlmostEqual(r['required_budget_scale'],2.4525/1.2,places=6)

    def test_centred_load_and_friction_budget(self):
        contacts=pads([0.])
        r=solve_contact_load(contacts,[0,0,0],[0,0,-2.4525],required_parts=['left','right'])
        self.assertTrue(r['feasible'])
        self.assertLess(r['force_balance_residual_n'],1e-7);self.assertLess(r['torque_balance_residual_nm'],1e-7)
        for c,n,f in zip(contacts,r['normal_force_per_point_n'],r['force_per_point_on_object_n']):
            outward=np.array(c['normal']);f=np.array(f)
            self.assertAlmostEqual(-f@outward,n)
            self.assertLessEqual(np.linalg.norm(f+n*outward),.6*n+1e-8)

    def test_equilibrium_is_preserved_under_a_rigid_coordinate_change(self):
        from scipy.spatial.transform import Rotation
        r=Rotation.from_euler('xyz',[13,-27,44],degrees=True).as_matrix();offset=np.array([-2.,1.,.9])
        contacts=pads([-.04,.04]);com=np.array([.1,0,0]);gravity=np.array([0,0,-2.4525])
        rotated=[{**c,'point':(r@c['point']+offset).tolist(),'normal':(r@c['normal']).tolist()} for c in contacts]
        result=solve_contact_load(rotated,r@com+offset,r@gravity)
        self.assertTrue(result['feasible']);self.assertLess(result['torque_balance_residual_nm'],1e-7)

    def test_extended_surface_can_balance_a_moment_without_more_force_budget(self):
        one=solve_contact_load(pads([0.]),[.1,0,0],[0,0,-2.4525],required_parts=['left','right'])
        force_only=solve_contact_load(pads([0.]),[.1,0,0],[0,0,-2.4525],balance_moments=False)
        many=solve_contact_load(pads([-.04,.04]),[.1,0,0],[0,0,-2.4525],required_parts=['left','right'])
        self.assertFalse(one['feasible']);self.assertTrue(force_only['feasible']);self.assertTrue(many['feasible'])
        self.assertTrue(all(n<=10+1e-8 for n in many['normal_force_per_part_n'].values()))

    def test_duplicate_points_do_not_invent_force_or_a_contact_couple(self):
        repeated=pads([0.]*8)
        self.assertFalse(solve_contact_load(repeated,[.1,0,0],[0,0,-2.4525])['feasible'])
        self.assertFalse(solve_contact_load(pads([-.04,.04]),[0,0,0],[0,0,-2.4525],normal_cap=1.)['feasible'])

    def test_actuator_and_inner_contact_requirements_can_block_solution(self):
        contacts=pads([0.])
        for c in contacts:c['jacobian']=[[0.],[0.],[1.]]
        self.assertFalse(solve_contact_load(contacts,[0,0,0],[0,0,-2.4525],torque_caps=[.1])['feasible'])
        self.assertFalse(solve_contact_load(contacts,[0,0,0],[0,0,-2.4525],required_inner=['left'])['feasible'])

    def test_invalid_budget_and_normal_are_rejected(self):
        with self.assertRaises(ValueError):solve_contact_load(pads([0]),[0,0,0],[0,0,-1],normal_cap=-1)
        bad=pads([0]);bad[0]['normal']=[0,0,0]
        with self.assertRaises(ValueError):solve_contact_load(bad,[0,0,0],[0,0,-1])


if __name__=='__main__':unittest.main()
